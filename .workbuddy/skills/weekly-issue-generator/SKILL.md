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
2. **Period rule (continuity — avoid duplicate weeks):** the new issue continues directly after the latest issue's period.
   - Read the latest `weekly/VolXXX.md` header `>时间：<start> - <end>`.
   - New period **starts the day after `<end>`** (normally a Monday) and runs 7 days (Mon–Sun, aligned to the ISO week).
   - New 周数 = ISO week number of the new start (`date -d '<monday>' +%V` or Python `date.isocalendar()[1]`).
   - This guarantees no overlap with the previous issue. The earlier "use last week" wording caused a duplicate-week bug (the previous week was already taken by the prior issue), so always continue from the latest issue instead.
   - Example: latest = Vol098 `2026/07/20 - 2026/07/26` (week 30) → new = `2026/07/27 - 2026/08/02`, 第 31 周 (Vol099).

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
- **Underflow rule:** if a section has fewer entries than the quota, take all of them. If it has 0 entries in store.md, take none **but** write the placeholder `本周偷懒了(T_T)` as the section body in the issue (applies to every section whose store.md counterpart is empty, e.g. 文章/资料&博文). Do NOT leave the section blank.
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

**Consistency rule (all four archives):** the split into archive files must mirror the issue exactly. For every section in the issue — including a section whose only content is the placeholder `本周偷懒了(T_T)` — write a corresponding `## 【周数】YYYYMMDD - YYYYMMDD` block into its mapped archive file (article/software/website/blogs.md) with the same body. Never skip an archive file just because that section's store.md was empty; the placeholder must still be archived so the four files stay in sync with the issue.

### Step 7 — Clean consumed entries from archives/store.md

After archiving, delete from `store.md` exactly the entries moved into the issue (same top-N per section). Keep the 4 section headers and remaining entries. Do NOT delete from the issue file or category archives.

**Preferred: run the bundled script** (self-verifying — it fails loudly if the write did not actually persist):

```
python .workbuddy/skills/weekly-issue-generator/references/clean_store.py
```

It deletes the top-N `#### ` entries per section according to `DEFAULT_QUOTA` (kept in sync with the Step 4 table below), then **re-reads `store.md` and asserts the deleted entries are gone**, exiting non-zero if any survived.

**One-shot alternative:** `references/generate_weekly.py` runs Steps 1–7 end-to-end (defaults to `--dry-run`; remove it to actually write). It reuses `clean_store.py`'s logic for the cleanup, so the same verification applies.

> ⚠️ **QUOTA must stay in sync:** `DEFAULT_QUOTA` in `clean_store.py` and the Step 4 quota table below are two copies of the same numbers. If you change one, change the other. If they drift, the script will delete the wrong number of entries.

**MANDATORY verification (never skip):** after ANY cleanup, use the **Read tool** on `archives/store.md` and confirm:
- the deleted entries are truly absent, and
- the new top entry of each consumed section is the entry that should follow (e.g. after consuming 4, the 5th entry is now top).
Do NOT trust script stdout or printed counts alone — a prior run printed "success" while the deletions had NOT actually been written to disk. The Read-back is the only reliable confirmation.

### Step 8 — Verify

- `weekly/Vol0XX.md` exists with correct header (time + 周数) and the right number of entries per section (respecting underflow).
- README.md has the new top index line with correct link and title rule.
- Each category file (`article/software/website/blogs.md`) has a new `## 【周数】...` block; article.md uses `本周偷懒了(T_T)` when empty.
- **`store.md` cleanup — HARD GATE:** Read `archives/store.md` directly and confirm the moved entries are gone (the new top of each consumed section is the entry that should follow). This Read-back is mandatory and is the real proof the cleanup succeeded — see the ⚠️ note in Step 7. Do not mark the task done until you have physically read the file and seen the deletions.

## Notes / conventions

- All dates in the issue header and README use `yyyy/mm/dd`; dates inside archive category files use `YYYYMMDD - YYYYMMDD` (no slashes).
- 周数: issue header writes `第 xx 周`; archive category files write `【xx】` (no 第/周).
- Preserve verbatim Markdown, including inline links and nested bracketed links inside entry bodies.
- Keep section header emojis exactly as in `template.md`.

## Bundled scripts (references/)

- `references/clean_store.py` — **the reliable way to do Step 7.** Deletes the top-N entries per section per `DEFAULT_QUOTA`, then re-reads `store.md` and asserts the deletions persisted (exits non-zero on failure). Run from repo root:
  `python .workbuddy/skills/weekly-issue-generator/references/clean_store.py`
- `references/generate_weekly.py` — optional one-shot pipeline for Steps 1–7. **Defaults to `--dry-run`** (prints the plan + issue preview, writes nothing). Remove `--dry-run` to actually generate, update README, archive, and clean (cleanup uses `clean_store.py` internally with the same verification).
- Both scripts are stdlib-only (Python 3) and require no installs.

## ⚠️ Known incident (why verification is mandatory)

A prior run reported "store.md cleaned (counts dropped)" but the deletions had **not** actually been written to disk — the next session found all 8 consumed entries still present. Root cause: trusting the script's printed counts instead of reading the file. Fix encoded here:
1. `clean_store.py` now re-reads and asserts post-write (non-zero exit on failure).
2. Steps 7 & 8 require a physical **Read** of `store.md` as the hard gate.
Never skip the Read-back.
