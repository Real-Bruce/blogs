---
name: weekly-issue-generator
description: 自动生成 Bruce's Blogs 周刊。This skill should be used when the user asks to create a new weekly issue (周刊/Volxxx), archive its content into the archives/ category files, update README.md index, and clean the consumed entries from archives/store.md. It encodes the exact layout, naming, date/week-number rules, per-section content quotas, and the lazy-week placeholder.
agent_created: true
---

# Weekly Issue Generator (Bruce's Blogs)

Automate the end-to-end weekly issue pipeline for this blog repo. The repo layout:

```
archives/
  template.md   # 周刊模板（4 个二级标题）
  store.md      # 待分发的内容池（4 个二级标题，#### [title](url) 条目）
  article.md    # 有价值的文章归档   <- 周刊「📜有价值的文章」
  software.md   # 开源项目归档       <- 周刊「🛸开源项目」
  website.md    # 网站&工具归档      <- 周刊「🚀网站&工具」
  blogs.md      # 资料&博文归档      <- 周刊「⛵资料&博文」
weekly/
  VolXXX.md     # 每期周刊（Vol070, Vol071, ... 递增）
README.md       # weekly 区块为每期建立索引链接
```

## When to use

Trigger when the user requests any of: 生成新一期周刊 / 新建 Vol / 整理本周内容 / 把 store.md 的内容做成周刊 / 更新周刊索引 / 归档周刊内容。

## Pipeline (execute in order)

### Step 1 — Determine the target issue number & period

1. List `weekly/` and find the highest existing `VolXXX.md` (e.g. `Vol096`). The new issue is `Vol0XX+1` (e.g. `Vol097`).
2. Compute "上周"（前一周）= the Monday–Sunday week immediately before **today**.
   - Use `date` to get ISO week number: `date -d '<monday>' +%V`. The weekly "周数" uses this ISO week number, written as `第 XX 周`.
   - Date format in the issue header: `yyyy/mm/dd`. Period = `上周一 - 上周日`.
   - Example: today 2026/07/20 (Mon, week 30) → last week = `2026/07/13 - 2026/07/19`, 第 29 周.

### Step 2 — Read template, store, and last issue

- `archives/template.md`: 4 section headers (`## 📜有价值的文章` / `## 🛸开源项目` / `## 🚀网站&工具` / `## ⛵资料&博文`) plus a top blockquote with 时间 / 周数.
- `archives/store.md`: pick entries from the TOP of each section.
- Confirm naming/format from the latest `weekly/VolXXX.md`.

### Step 3 — Build the new issue file `weekly/Vol0XX.md`

Top blockquote (match template, dates use `yyyy/mm/dd`, no weekday):

```
>收集整理每周看到的好玩有趣的内容，包含技术文章、资料博客，开源项目和网站工具
>
>时间：yyyy/mm/dd - yyyy/mm/dd
>
>周数：第 xx 周
```

Then the 4 section headers, filled with content pulled from `store.md` according to the **quota rules** below.

### Step 4 — Content quota (pull from top of each store.md section)

| 周刊标题 | 取条数 | 来源 section |
|---|---|---|
| 📜有价值的文章 | 1 | `## 📜有价值的文章` |
| 🛸开源项目 | 4 | `## 🛸开源项目` |
| 🚀网站&工具 | 4 | `## 🚀网站&工具` |
| ⛵资料&博文 | 2 | `## ⛵资料&博文` |

- Take entries **from the top** of each section, preserving each entry's `#### [title](url)` heading and its body text (copy verbatim, including nested links).
- **Underflow rule:** if a section has fewer entries than the quota, take all of them. If it has 0, take none (leave the section empty in the issue).
- Do NOT modify store.md in this step.

### Step 5 — Update README.md index

- In the `### 📰weekly` block, insert a new line at the TOP (above the previous issue), format:
  `#### <上周一> - <上周日> [Vol.0XX< + 文章标题>](./weekly/Vol0XX.md)`
  - Date format here is `yyyy/mm/dd` with a single space around `-` (e.g. `2026/07/13 - 2026/07/19`).
  - Title suffix: append the first 有价值的文章 entry's title inside the brackets. **If 文章 is empty, keep only `Vol.0XX` (no title text).**
- Match the spacing/style of the existing most-recent entry.

### Step 6 — Archive content into archives/ category files (COPY only, never delete from the issue)

Mapping: `article.md←📜有价值的文章`, `software.md←🛸开源项目`, `website.md←🚀网站&工具`, `blogs.md←⛵资料&博文`.

For each category file:
1. Prepend a new section **right after the `#` title line, before the existing `## 【..】` block**:
   `## 【周数】YYYYMMDD - YYYYMMDD` (NO slashes in the date; 周数 without `第/周`, e.g. `## 【29】20260713 - 20260719`).
2. Under it, paste the same entries copied from the issue.
3. **Do NOT remove the content from `weekly/Vol0XX.md`.**

**Lazy-week rule (article.md only):** if the issue's `📜有价值的文章` section is empty, still create the `## 【周数】YYYYMMDD - YYYYMMDD` block in `article.md`, with body text exactly: `本周偷懒了(T_T)`.

### Step 7 — Clean consumed entries from archives/store.md

After archiving, delete from `store.md` exactly the entries that were moved into the issue (the same top-N entries per section). Keep `store.md`'s 4 section headers and any remaining entries. Do NOT delete anything from the issue file or the category archives.

### Step 8 — Verify

- `weekly/Vol0XX.md` exists with correct header (time + 周数) and the right number of entries per section (respecting underflow).
- README.md has the new top index line with correct link and title rule.
- Each category file (`article/software/website/blogs.md`) has a new `## 【周数】...` block; article.md uses `本周偷懒了(T_T)` when empty.
- `store.md` no longer contains the moved entries; remaining counts match expectation.

## Notes / conventions

- All dates in the issue header and README use `yyyy/mm/dd`; dates inside archive category files use `YYYYMMDD - YYYYMMDD` (no slashes).
- 周数: issue header writes `第 xx 周`; archive category files write `【xx】` (no 第/周).
- Preserve verbatim Markdown, including inline links and nested bracketed links inside entry bodies.
- Keep section header emojis exactly as in `template.md`.
