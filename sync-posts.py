#!/usr/bin/env python3
"""
sync-posts.py
從 Obsidian vault 清理非法字元，再 cp 到 Hugo content/posts/
"""

import os
import shutil

VAULT = "/Users/kongtat/Library/Mobile Documents/iCloud~md~obsidian/Documents/puh-inn/2 kt-lab.tw/posts"
HUGO = "/Users/kongtat/website/kt-lab/content/posts"

INVALID_CHARS = ['\x08']  # backspace，以後可以加其他字元

cleaned = []
copied = []

for fname in os.listdir(VAULT):
    if not fname.endswith(".md"):
        continue

    src = os.path.join(VAULT, fname)
    dst = os.path.join(HUGO, fname)

    with open(src, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for char in INVALID_CHARS:
        content = content.replace(char, "")

    if content != original:
        with open(src, "w", encoding="utf-8") as f:
            f.write(content)
        cleaned.append(fname)

    shutil.copy2(src, dst)
    copied.append(fname)

if cleaned:
    print(f"清除非法字元（{len(cleaned)} 篇）：")
    for f in cleaned:
        print(f"  {f}")
else:
    print("沒有發現非法字元")

print(f"\n複製完成，共 {len(copied)} 篇文章")
