#!/usr/bin/env python3
"""
vault-links-to-wikilinks.py
把 vault/posts 內文裡的 [文字](https://kt-lab.tw/year/month/slug/) 轉成 [[yyyy-mm-dd 中文title|文字]]
在 rename-vault-posts.py --write 執行之後才能跑。

用法：
  python3 vault-links-to-wikilinks.py          # dry-run
  python3 vault-links-to-wikilinks.py --write  # 實際寫入
"""

import os
import re
import sys

VAULT_POSTS = "/Users/kongtat/Library/Mobile Documents/iCloud~md~obsidian/Documents/puh-inn/2 kt-lab.tw/posts"
DRY_RUN = "--write" not in sys.argv

def parse_frontmatter(content):
    title = None
    date = None
    url = None
    slug = None
    if not content.startswith("---"):
        return title, date, url, slug
    end = content.find("---", 3)
    if end == -1:
        return title, date, url, slug
    fm = content[3:end]
    for line in fm.splitlines():
        if line.startswith("title:"):
            title = line[6:].strip().strip('"').strip("'")
        elif line.startswith("date:"):
            date = line[5:].strip()[:10]
        elif line.startswith("url:"):
            url = line[4:].strip().rstrip("/") + "/"
        elif line.startswith("slug:"):
            slug = line[5:].strip().strip('"').strip("'")
    return title, date, url, slug

# 建立 lookup：url_path -> vault_stem
# vault 檔名現在是 yyyy-mm-dd 中文title.md
url_to_vault_stem = {}

for fname in os.listdir(VAULT_POSTS):
    if not fname.endswith(".md"):
        continue
    stem = fname[:-3]  # "yyyy-mm-dd 中文title"
    fpath = os.path.join(VAULT_POSTS, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    title, date, url, slug = parse_frontmatter(content)

    # 從檔名取日期（備用）
    if not date:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", stem)
        if m:
            date = m.group(1)

    if url:
        url_to_vault_stem[url] = stem
    elif slug and date:
        year, month = date[:4], date[5:7]
        url_to_vault_stem[f"/{year}/{month}/{slug}/"] = stem

# 轉換內文連結
LINK_RE = re.compile(r'\[([^\]]+)\]\(https://kt-lab\.tw(/[^)]+/)\)')

converted = []
unmatched = []

for fname in sorted(os.listdir(VAULT_POSTS)):
    if not fname.endswith(".md"):
        continue
    fpath = os.path.join(VAULT_POSTS, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    file_unmatched = []

    def replace_link(m):
        text = m.group(1)
        path = m.group(2)
        vault_stem = url_to_vault_stem.get(path)
        if not vault_stem:
            file_unmatched.append(path)
            return m.group(0)
        return f"[[{vault_stem}|{text}]]"

    content = LINK_RE.sub(replace_link, content)

    if file_unmatched:
        unmatched.append((fname, file_unmatched))

    if content != original:
        converted.append((fname, original, content))
        if not DRY_RUN:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)

# 輸出結果
if DRY_RUN:
    for fname, orig, new in converted:
        orig_lines = orig.splitlines()
        new_lines = new.splitlines()
        print(f"\n{'='*60}")
        print(f"  {fname}")
        for i, (o, n) in enumerate(zip(orig_lines, new_lines)):
            if o != n:
                print(f"  行{i+1} - {o.strip()[:120]}")
                print(f"       + {n.strip()[:120]}")
    print(f"\n[Dry-run] 會修改 {len(converted)} 篇文章")
    if converted:
        print("確認無誤後執行：python3 vault-links-to-wikilinks.py --write")
else:
    print(f"轉換完成（{len(converted)} 篇）")

if unmatched:
    print(f"\n找不到對應的連結（保留原樣）：")
    for fname, paths in unmatched:
        print(f"  {fname}：")
        for p in paths:
            print(f"    {p}")
