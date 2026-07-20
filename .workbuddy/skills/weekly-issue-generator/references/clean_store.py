#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_store.py — 从 archives/store.md 删除"已搬入本期周刊"的条目。

这是 weekly-issue-generator skill 的固化脚本，专门解决"清理未真正落盘"的历史
问题。关键安全机制：

1. 删除每个 section 顶部的 TOP-N 条 `#### ` 条目（N 见 DEFAULT_QUOTA）。
2. 写回文件后**重新读取并断言**被删条目确实已消失。
3. 若写回失败（文件被锁、沙箱隔离等），脚本以非零码退出并打印残留条目，
   绝不"假装成功"。

用法（在仓库根目录执行）：
    python .workbuddy/skills/weekly-issue-generator/references/clean_store.py
指定路径：
    python clean_store.py /abs/path/to/store.md

注意：DEFAULT_QUOTA 必须与 SKILL.md Step 4 的配额表保持一致；若改配额，两边都要改。
"""

import os
import re
import sys

# 仓库根目录：skill 位于 <repo>/.workbuddy/skills/weekly-issue-generator/references/
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SKILL_DIR))))
STORE_DEFAULT = os.path.join(REPO_ROOT, "archives", "store.md")

# 必须与 SKILL.md Step 4 的配额表完全一致。
DEFAULT_QUOTA = {
    "📜有价值的文章": 0,
    "🛸开源项目": 4,
    "🚀网站&工具": 4,
    "⛵资料&博文": 0,
}


def parse_sections(lines):
    """返回 {section_name: line_index}。"""
    sections = {}
    for i, line in enumerate(lines):
        m = re.match(r"^## (.+)$", line)
        if m:
            sections[m.group(1).strip()] = i
    return sections


def collect_entries(lines, start, end):
    """返回该 section 内每条 `#### ` 条目的 (整行文本, 起始行, 结束行)。"""
    entries = []
    cur = None
    for j in range(start + 1, end):
        if lines[j].startswith("#### "):
            if cur is not None:
                entries.append((cur[0], cur[1], j))
            cur = (lines[j].rstrip("\n"), j, None)
    if cur is not None:
        entries.append((cur[0], cur[1], end))
    return entries


def clean(path, quota):
    """按 quota 删除各 section 顶部条目，返回 {section: [被删条目的标题行]}。"""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    sections = parse_sections(lines)
    deleted = {name: [] for name in quota}

    # 从高索引 section 开始删除，保证低索引位置不被打乱。
    for name in sorted(quota, key=lambda n: -sections.get(n, 0)):
        n = quota.get(name, 0)
        if n <= 0 or name not in sections:
            continue
        start = sections[name]
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## "):
                end = j
                break
        entries = collect_entries(lines, start, end)
        to_remove = entries[:n]
        deleted[name] = [t for t, s, e in to_remove]
        for _, s, e in reversed(to_remove):
            del lines[s:e]

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return deleted


def verify(path, deleted):
    """重读文件，断言被删条目确实已不在对应 section 内。失败则 sys.exit(1)。"""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    sections = parse_sections(lines)
    errors = []
    for name, titles in deleted.items():
        if not titles:
            continue
        if name not in sections:
            errors.append(f"section `{name}` 在清理后消失")
            continue
        start = sections[name]
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## "):
                end = j
                break
        block = "".join(lines[start:end])
        for t in titles:
            key = t.split("]")[0] + "]"  # "#### [handmux]"
            if key in block:
                errors.append(f"已删条目仍残留在 `{name}`：{t}")

    # 报告剩余条数 + 各 section 新顶部
    secs, cur, cnt = {}, None, 0
    for line in lines:
        if line.startswith("## "):
            if cur:
                secs[cur] = cnt
            cur = line.strip()
            cnt = 0
        elif line.startswith("#### "):
            cnt += 1
    if cur:
        secs[cur] = cnt

    print("remaining entries per section:")
    for k, v in secs.items():
        print(f"  {k}: {v}")

    if errors:
        print("\nVERIFICATION FAILED（清理未真正落盘，请检查文件权限/沙箱）：")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    print("\nVERIFICATION PASSED：所有已搬入周刊的条目均已从 store.md 删除。")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else STORE_DEFAULT
    if not os.path.exists(path):
        print(f"ERROR: store.md 不存在：{path}")
        sys.exit(1)
    print(f"store.md: {path}\n")
    deleted = clean(path, DEFAULT_QUOTA)
    print("deleted entries:")
    any_deleted = False
    for name, titles in deleted.items():
        if titles:
            any_deleted = True
            print(f"  {name}:")
            for t in titles:
                print(f"    - {t}")
    if not any_deleted:
        print("  （无，quota 均为 0 或 section 为空）")
    verify(path, deleted)


if __name__ == "__main__":
    main()
