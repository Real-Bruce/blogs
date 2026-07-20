#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_weekly.py — weekly-issue-generator skill 的端到端生成脚本。

覆盖 SKILL.md 的 Step 1–7 全流程：
  1. 计算下一期编号与周期（接续上一期，避免重复上一周）
  2. 读取 store.md 顶部条目（按配额）
  3. 生成 weekly/Vol0XX.md
  4. 更新 README.md 的 📰weekly 索引
  5. 归档到 article/software/website/blogs.md
  6. 调用 clean_store 清理 store.md，并强制回读校验

用法（仓库根目录）：
  dry-run（只打印计划，不写文件）：
    python .workbuddy/skills/weekly-issue-generator/references/generate_weekly.py --dry-run
  正式生成：
    python .workbuddy/skills/weekly-issue-generator/references/generate_weekly.py

安全：默认开启 --dry-run，必须显式去掉该参数才会真正写文件。
"""

import os
import re
import sys
import datetime
from pathlib import Path

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SKILL_DIR))))
sys.path.insert(0, SKILL_DIR)
from clean_store import (  # noqa: E402
    DEFAULT_QUOTA, parse_sections, collect_entries, clean, verify,
)

ARCHIVES = os.path.join(REPO_ROOT, "archives")
WEEKLY_DIR = os.path.join(REPO_ROOT, "weekly")
README = os.path.join(REPO_ROOT, "README.md")
STORE = os.path.join(ARCHIVES, "store.md")

# 周刊 section 顺序与映射（与 SKILL.md / template.md 一致）
SECTIONS = ["📜有价值的文章", "🛸开源项目", "🚀网站&工具", "⛵资料&博文"]
ARCHIVE_FILE = {
    "📜有价值的文章": "article.md",
    "🛸开源项目": "software.md",
    "🚀网站&工具": "website.md",
    "⛵资料&博文": "blogs.md",
}
PLACEHOLDER = "本周偷懒了(T_T)"


def dt(s):
    return datetime.datetime.strptime(s, "%Y/%m/%d").date()


def fmt(d):
    return d.strftime("%Y/%m/%d")


def compact(d):
    return d.strftime("%Y%m%d")


def find_latest_vol():
    nums = []
    for p in os.listdir(WEEKLY_DIR):
        m = re.match(r"Vol(\d+)\.md$", p)
        if m:
            nums.append(int(m.group(1)))
    if not nums:
        return 0, None
    return max(nums), os.path.join(WEEKLY_DIR, f"Vol{max(nums):03d}.md")


def parse_period(vol_path):
    with open(vol_path, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r">时间：(\d{4}/\d{2}/\d{2})\s*-\s*(\d{4}/\d{2}/\d{2})", txt)
    if not m:
        return None, None
    return dt(m.group(1)), dt(m.group(2))


def next_period(prev_end):
    # 接续上一期：上一期周日 +1 天 = 本周一；对齐到 ISO 周（周一~周日）。
    candidate = prev_end + datetime.timedelta(days=1)
    monday = candidate - datetime.timedelta(days=candidate.weekday())
    return monday, monday + datetime.timedelta(days=6)


def pull_entries(store_lines, quota):
    """返回 {section: (raw_lines_or_None, is_placeholder)}。"""
    sections = parse_sections(store_lines)
    result = {}
    for name in SECTIONS:
        n = quota.get(name, 0)
        if name not in sections:
            result[name] = ([], n == 0)
            continue
        start = sections[name]
        end = len(store_lines)
        for j in range(start + 1, len(store_lines)):
            if store_lines[j].startswith("## "):
                end = j
                break
        entries = collect_entries(store_lines, start, end)
        if not entries:
            result[name] = ([], True)  # 空 → 占位
        else:
            taken = entries[:n]
            # 拼接原始行（含标题行、正文、空行）
            block_lines = []
            for _, s, e in taken:
                block_lines.extend(store_lines[s:e])
            result[name] = (block_lines, False)
    return result


def build_issue(vol, start, end, week_no, pulled):
    head = (
        ">收集整理每周看到的好玩有趣的内容，包含技术文章、资料博客，开源项目和网站工具\n"
        ">\n"
        f">时间：{fmt(start)} - {fmt(end)}\n"
        ">\n"
        f">周数：第 {week_no} 周\n"
    )
    body = []
    for name in SECTIONS:
        lines, is_ph = pulled[name]
        body.append(f"## {name}\n")
        if is_ph:
            body.append(f"\n{PLACEHOLDER}\n\n")
        else:
            body.append("\n")
            body.extend(lines)
            if not lines[-1].endswith("\n"):
                body.append("\n")
            body.append("\n")
    return head + "\n" + "".join(body)


def update_readme(start, end, vol, article_title):
    with open(README, encoding="utf-8") as f:
        lines = f.readlines()
    label = f"Vol.{vol:03d}"
    if article_title:
        label += f" {article_title}"
    new_line = f"#### {fmt(start)} - {fmt(end)} [{label}](./weekly/Vol{vol:03d}.md)\n"
    # 在 ### 📰weekly 之后的第一条 #### 之前插入
    out = []
    inserted = False
    for i, line in enumerate(lines):
        out.append(line)
        if not inserted and line.strip().startswith("### 📰weekly"):
            # 找下一条 #### 前插入
            # 先记录，下一轮在首个 #### 前插
            pass
        elif not inserted and line.startswith("#### ") and any(
            l.strip().startswith("### 📰weekly") for l in lines[:i]
        ):
            out.insert(len(out) - 1, new_line)
            inserted = True
    if not inserted:
        # fallback：直接在 📰weekly 后追加
        for i, line in enumerate(out):
            if line.strip().startswith("### 📰weekly"):
                out.insert(i + 1, new_line)
                inserted = True
    with open(README, "w", encoding="utf-8") as f:
        f.writelines(out)


def archive(start, end, week_no, pulled):
    for name in SECTIONS:
        fname = ARCHIVE_FILE[name]
        path = os.path.join(ARCHIVES, fname)
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        lines_block = pulled[name][0]
        if pulled[name][1]:  # placeholder
            block = f"## 【{week_no}】{compact(start)} - {compact(end)}\n\n{PLACEHOLDER}\n\n"
        else:
            block = f"## 【{week_no}】{compact(start)} - {compact(end)}\n\n" + "".join(lines_block) + "\n"
        # 在 # 标题后、首个 ## 前插入
        insert_at = None
        for i, line in enumerate(lines):
            if line.startswith("## "):
                insert_at = i
                break
        if insert_at is None:
            insert_at = len(lines)
        lines.insert(insert_at, block)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)


def main():
    dry = "--dry-run" in sys.argv
    latest_num, latest_path = find_latest_vol()
    new_num = latest_num + 1
    if latest_path and os.path.exists(latest_path):
        prev_start, prev_end = parse_period(latest_path)
    else:
        prev_end = datetime.date.today() - datetime.timedelta(days=1)
    start, end = next_period(prev_end)
    week_no = start.isocalendar()[1]

    with open(STORE, encoding="utf-8") as f:
        store_lines = f.readlines()
    pulled = pull_entries(store_lines, DEFAULT_QUOTA)
    article_title = ""
    if not pulled["📜有价值的文章"][1] and pulled["📜有价值的文章"][0]:
        first = pulled["📜有价值的文章"][0][0].strip()
        m = re.match(r"#### \[(.+?)\]", first)
        if m:
            article_title = m.group(1)

    print(f"DRY-RUN 计划" if dry else "正式生成")
    print(f"  新刊：Vol{new_num:03d}  ({fmt(start)} - {fmt(end)}，第 {week_no} 周)")
    print(f"  接续上一期结束日：{fmt(prev_end)}")
    print("  各 section 取条数：")
    for name in SECTIONS:
        lines, is_ph = pulled[name]
        if is_ph:
            print(f"    {name}: 占位（{PLACEHOLDER}）")
        else:
            print(f"    {name}: {len([1 for l in lines if l.startswith('#### ')])} 条")

    issue = build_issue(new_num, start, end, week_no, pulled)
    if dry:
        print("\n--- weekly/Vol%03d.md 预览 ---" % new_num)
        print(issue[:1200] + ("\n...(truncated)" if len(issue) > 1200 else ""))
        print("\n(DRY-RUN 未写入任何文件。去掉 --dry-run 以正式生成。)")
        return

    # 正式写入
    with open(os.path.join(WEEKLY_DIR, f"Vol{new_num:03d}.md"), "w", encoding="utf-8") as f:
        f.write(issue)
    update_readme(start, end, new_num, article_title)
    archive(start, end, week_no, pulled)
    # 清理 store.md 并强制回读校验
    deleted = clean(STORE, DEFAULT_QUOTA)
    verify(STORE, deleted)
    print(f"\n✅ 已生成 Vol{new_num:03d} 并完成归档与 store.md 清理。")


if __name__ == "__main__":
    main()
