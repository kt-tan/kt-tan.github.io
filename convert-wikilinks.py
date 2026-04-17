#!/usr/bin/env python3
"""
convert-wikilinks.py
把 website/content/posts 裡的 [[yyyy-mm-dd 中文title|文字]] 轉成絕對網址 markdown 連結
不修改 vault 的原始檔案
"""

import os
import re

POSTS = "/Users/kongtat/website/kt-lab/content/posts"
BASE_URL = "https://kt-lab.tw"

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

def url_from_filename(stem):
    """從 website 檔名 yyyymmdd-slug 推算 /yyyy/mm/slug/"""
    m = re.match(r"^(\d{4})(\d{2})\d{2}-(.+)$", stem)
    if m:
        return f"/{m.group(1)}/{m.group(2)}/{m.group(3)}/"
    return None

# 建立 lookup：vault_stem -> absolute_url
# vault_stem 格式："yyyy-mm-dd 中文title"（來自 frontmatter date + title 重組）
lookup = {}

for fname in os.listdir(POSTS):
    if not fname.endswith(".md"):
        continue
    stem = fname[:-3]
    fpath = os.path.join(POSTS, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    title, date, url, slug = parse_frontmatter(content)

    # 推算 url_path
    if not url:
        if slug and date:
            year, month = date[:4], date[5:7]
            url = f"/{year}/{month}/{slug}/"
        else:
            url = url_from_filename(stem)

    if not url:
        continue

    abs_url = BASE_URL + url

    # vault_stem = "yyyy-mm-dd 中文title"
    if title and date:
        vault_stem = f"{date} {title}"
        lookup[vault_stem] = {"title": title, "abs_url": abs_url}

    # 也保留舊格式 yyyymmdd-slug 支援過渡期
    lookup[stem] = {"title": title or stem, "abs_url": abs_url}

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
        if ref.endswith(".md"):
            ref = ref[:-3]
        entry = lookup.get(ref)
        if not entry or not entry["abs_url"]:
            return m.group(0)
        text = display.strip() if display else entry["title"]
        return f"[{text}]({entry['abs_url']})"

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
