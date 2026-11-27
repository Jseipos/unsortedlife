#!/usr/bin/env python3
"""Swap the Amazon Associates tag everywhere the site and pipeline carry it.
Usage: python3 swap_tag.py <old-tag> <new-tag>   e.g. python3 swap_tag.py unsortedlife-20 unsortedlife0c-20
Rewrites products.json and rebuilds index.html; also edits the workspace pipeline's topic JSON files and any
text files under to_post/*/ (facebook_reel.txt, pinterest_pin.txt, youtube.txt) so future reposts carry the new tag.
Prints what changed. Run from to_post/_site. The Sunday task prompts and the playbook doc are updated by hand."""
import os, re, sys, glob, subprocess
old, new = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
root = os.environ.get("UNSORTEDLIFE_ROOT") or os.path.abspath(os.path.join(here, "..", ".."))   # unsortedlife/ (override when to_post is mounted on its own)
targets = [os.path.join(here, "products.json"), os.path.join(here, "AMAZON_LISTS.md")]
targets += glob.glob(os.path.join(root, "to_post", "w*", "*.txt"))
targets += glob.glob(os.path.join(root, "to_post", "_pins", "**", "*.txt"), recursive=True)
targets += glob.glob(os.path.join(root, "topics", "*.json")) + glob.glob(os.path.join(root, "schedule", "*.json"))
targets += glob.glob(os.path.join(root, "*.py")) + glob.glob(os.path.join(root, "*.md")) + [os.path.join(root, "config.json")]
targets += glob.glob(os.path.join(root, "out", "*.json")) + glob.glob(os.path.join(root, "build", "**", "*.json"), recursive=True)
n = 0
for t in sorted(set(targets)):
    try: s = open(t, encoding="utf-8").read()
    except Exception: continue
    if old in s:
        open(t, "w", encoding="utf-8").write(s.replace(old, new)); n += 1; print("updated", os.path.relpath(t, root))
print(f"{n} files updated; rebuilding the page")
subprocess.run([sys.executable, os.path.join(here, "build_site.py"), here, os.path.join(root, "photos", "inbox")], check=True)
