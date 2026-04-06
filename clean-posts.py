#!/usr/bin/env python3
"""
clean-posts.py
清除 Obsidian vault 裡 posts 的非法字元
"""

import os

VAULT = "/Users/kongtat/Library/Mobile Documents/iCloud~md~obsidian/Documents/puh-inn/2 kt-lab.tw/posts"

INVALID_CHARS = ['\x08']  # backspace，以後可以加其他字元

cleaned = []

for fname in os.listdir(VAULT):
    if not fname.endswith(".md"):
        continue

    src = os.path.join(VAULT, fname)

    with open(src, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for char in INVALID_CHARS:
        content = content.replace(char, "")

    if content != original:
        with open(src, "w", encoding="utf-8") as f:
            f.write(content)
        cleaned.append(fname)

if cleaned:
    print(f"清除非法字元（{len(cleaned)} 篇）：")
    for f in cleaned:
        print(f"  {f}")
else:
    print("沒有發現非法字元")
