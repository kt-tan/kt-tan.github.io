#!/usr/bin/env python3
"""
ktlab-sync.py
把 vault/posts 的文章同步到 website/content/posts/
vault 檔名格式：yyyy-mm-dd 中文title.md
website 檔名格式：yyyymmdd-slug.md（slug 從 frontmatter url 或 slug 欄位取得）

最後自動執行 convert-wikilinks.py 把 [[wikilinks]] 轉成絕對網址。

用法：
  python3 ktlab-sync.py          # dry-run
  python3 ktlab-sync.py --write  # 實際同步
"""

import os
import re
import shutil
import subprocess
import sys

VAULT_POSTS = "/Users/kongtat/Library/Mobile Documents/iCloud~md~obsidian/Documents/puh-inn/2 kt-lab.tw/posts"
WEBSITE_POSTS = "/Users/kongtat/website/kt-lab/content/posts"
CONVERT_SCRIPT = "/Users/kongtat/website/kt-lab/convert-wikilinks.py"
DRY_RUN = "--write" not in sys.argv

def parse_frontmatter(content):
    date = None
    url = None
    slug = None
    if not content.startswith("---"):
        return date, url, slug
    end = content.find("---", 3)
    if end == -1:
        return date, url, slug
    fm = content[3:end]
    for line in fm.splitlines():
        if line.startswith("date:"):
            date = line[5:].strip()[:10]
        elif line.startswith("url:"):
            url = line[4:].strip().rstrip("/") + "/"
        elif line.startswith("slug:"):
            slug = line[5:].strip().strip('"').strip("'")
    return date, url, slug

def derive_website_filename(vault_fname):
    stem = vault_fname[:-3]  # 去掉 .md
    # 從檔名取 yyyy-mm-dd
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2}) ", stem)
    if not m:
        return None
    year, month, day = m.group(1), m.group(2), m.group(3)
    date_compact = f"{year}{month}{day}"

    fpath = os.path.join(VAULT_POSTS, vault_fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    _, url, slug = parse_frontmatter(content)

    if url:
        # 從 url 路徑最後一段取 slug，例如 /2026/04/feels-like-regressing/
        parts = url.strip("/").split("/")
        slug = parts[-1] if parts else None

    if not slug:
        return None

    return f"{date_compact}-{slug}.md"

# 建立 vault 所有文章的對應表
vault_files = [f for f in os.listdir(VAULT_POSTS) if f.endswith(".md")]
mapping = {}  # vault_fname -> website_fname

for vf in sorted(vault_files):
    wf = derive_website_filename(vf)
    if wf:
        mapping[vf] = wf
    else:
        print(f"  [警告] 無法推算 website 檔名：{vf}")

# 目前 website 的檔案
existing_website = set(f for f in os.listdir(WEBSITE_POSTS) if f.endswith(".md"))
expected_website = set(mapping.values())

# 需要複製的檔案（新增或更新）
to_copy = []
for vf, wf in mapping.items():
    src = os.path.join(VAULT_POSTS, vf)
    dst = os.path.join(WEBSITE_POSTS, wf)
    if not os.path.exists(dst):
        to_copy.append((vf, wf, "新增"))
    else:
        # 比對內容是否有變化
        with open(src, "r", encoding="utf-8") as f:
            src_content = f.read()
        with open(dst, "r", encoding="utf-8") as f:
            dst_content = f.read()
        if src_content != dst_content:
            to_copy.append((vf, wf, "更新"))

# 需要刪除的孤兒檔案
to_delete = sorted(existing_website - expected_website)

# 輸出
if to_copy:
    print(f"{'[Dry-run] ' if DRY_RUN else ''}複製 {len(to_copy)} 個檔案：")
    for vf, wf, action in to_copy:
        print(f"  [{action}] {vf}")
        print(f"         → {wf}")
    if not DRY_RUN:
        for vf, wf, _ in to_copy:
            shutil.copy2(os.path.join(VAULT_POSTS, vf), os.path.join(WEBSITE_POSTS, wf))
else:
    print("沒有需要更新的文章")

if to_delete:
    print(f"\n{'[Dry-run] ' if DRY_RUN else ''}刪除 {len(to_delete)} 個孤兒檔案：")
    for wf in to_delete:
        print(f"  {wf}")
    if not DRY_RUN:
        for wf in to_delete:
            os.remove(os.path.join(WEBSITE_POSTS, wf))

if not DRY_RUN:
    print("\n執行 convert-wikilinks.py ...")
    subprocess.run(["python3", CONVERT_SCRIPT], check=True)
else:
    print("\n確認無誤後執行：python3 ktlab-sync.py --write")
