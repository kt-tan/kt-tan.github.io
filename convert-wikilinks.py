#!/usr/bin/env python3
"""
convert-wikilinks.py
把 website/content/posts 裡的 Obsidian [[wikilinks]] 轉成 Hugo markdown 連結
不修改 vault 的原始檔案
"""

import os
import re

POSTS = "/Users/kongtat/website/kt-lab/content/posts"

def parse_frontmatter(content):
    """取出 frontmatter 的 title 和 url"""
    title = None
    url = None
    if not content.startswith("---"):
        return title, url
    end = content.find("---", 3)
    if end == -1:
        return title, url
    fm = content[3:end]
    for line in fm.splitlines():
        if line.startswith("title:"):
            title = line[6:].strip().strip('"').strip("'")
        elif line.startswith("url:"):
            url = line[4:].strip().rstrip("/") + "/"
    return title, url

def url_from_filename(stem):
    """從檔名 YYYYMMDD-slug 推算 /YYYY/MM/slug/"""
    m = re.match(r"^(\d{4})(\d{2})\d{2}-(.+)$", stem)
    if m:
        return f"/{m.group(1)}/{m.group(2)}/{m.group(3)}/"
    return None

# 建立 lookup table：檔名 stem → {title, url}
lookup = {}
for fname in os.listdir(POSTS):
    if not fname.endswith(".md"):
        continue
    stem = fname[:-3]  # 去掉 .md
    fpath = os.path.join(POSTS, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    title, url = parse_frontmatter(content)
    if not url:
        url = url_from_filename(stem)
    lookup[stem] = {"title": title or stem, "url": url}

# 轉換每篇文章的 wikilinks
converted = []
for fname in os.listdir(POSTS):
    if not fname.endswith(".md"):
        continue
    fpath = os.path.join(POSTS, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    def replace_wikilink(m):
        inner = m.group(1)
        if "|" in inner:
            ref, display = inner.split("|", 1)
        else:
            ref, display = inner, None
        ref = ref.strip()
        # 去掉可能帶的 .md 副檔名
        if ref.endswith(".md"):
            ref = ref[:-3]
        entry = lookup.get(ref)
        if not entry or not entry["url"]:
            return m.group(0)  # 找不到就保留原樣
        text = display.strip() if display else entry["title"]
        return f"[{text}]({entry['url']})"

    content = re.sub(r"\[\[([^\]]+)\]\]", replace_wikilink, content)

    if content != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        converted.append(fname)

if converted:
    print(f"轉換 wikilinks（{len(converted)} 篇）：")
    for f in converted:
        print(f"  {f}")
else:
    print("沒有發現 wikilinks")
