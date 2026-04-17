#!/usr/bin/env python3
"""
rename-vault-posts.py
把 vault/posts 的檔名從 yyyymmdd-slug.md 改成 yyyy-mm-dd 中文title.md

用法：
  python3 rename-vault-posts.py          # dry-run
  python3 rename-vault-posts.py --write  # 實際改名
"""

import os
import re
import sys

VAULT_POSTS = "/Users/kongtat/Library/Mobile Documents/iCloud~md~obsidian/Documents/puh-inn/2 kt-lab.tw/posts"
DRY_RUN = "--write" not in sys.argv

def parse_frontmatter(content):
    title = None
    date = None
    if not content.startswith("---"):
        return title, date
    end = content.find("---", 3)
    if end == -1:
        return title, date
    fm = content[3:end]
    for line in fm.splitlines():
        if line.startswith("title:"):
            title = line[6:].strip().strip('"').strip("'")
        elif line.startswith("date:"):
            date = line[5:].strip()[:10]  # 只取 yyyy-mm-dd
    return title, date

def date_from_filename(stem):
    m = re.match(r"^(\d{4})(\d{2})(\d{2})", stem)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None

skipped = []
renames = []

for fname in sorted(os.listdir(VAULT_POSTS)):
    if not fname.endswith(".md"):
        continue
    stem = fname[:-3]
    fpath = os.path.join(VAULT_POSTS, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    title, date = parse_frontmatter(content)

    if not date:
        date = date_from_filename(stem)

    if not title:
        skipped.append((fname, "缺少 title"))
        continue
    if not date:
        skipped.append((fname, "缺少 date"))
        continue

    # 清理 title 裡不能用於檔名的字元
    safe_title = re.sub(r'[/\\:*?"<>|]', "", title).strip()
    new_fname = f"{date} {safe_title}.md"

    if fname == new_fname:
        continue  # 已經是目標格式

    renames.append((fname, new_fname))

print(f"{'[Dry-run] ' if DRY_RUN else ''}共 {len(renames)} 個檔案需要改名\n")
for old, new in renames:
    print(f"  {old}")
    print(f"  → {new}\n")

if skipped:
    print(f"\n略過 {len(skipped)} 個檔案：")
    for fname, reason in skipped:
        print(f"  {fname}  ({reason})")

if DRY_RUN and renames:
    print("\n確認無誤後執行：python3 rename-vault-posts.py --write")
elif not DRY_RUN:
    for old, new in renames:
        old_path = os.path.join(VAULT_POSTS, old)
        new_path = os.path.join(VAULT_POSTS, new)
        if os.path.exists(new_path):
            print(f"  [略過] 目標已存在：{new}")
        else:
            os.rename(old_path, new_path)
            print(f"  改名完成：{new}")
