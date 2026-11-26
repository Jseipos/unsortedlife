#!/usr/bin/env python3
"""Usage: python3 check_lists.py dump.txt  (lines of 'ASIN | name' from an Amazon list).
Prints the items whose ASIN is not yet linked anywhere in products.json."""
import json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, "products.json")))
have = set()
for s in d["sections"]:
    for l in s["lists"]:
        for it in l["items"]:
            m = re.search(r"/dp/([A-Z0-9]{10})", it.get("url", ""))
            if m: have.add(m.group(1))
new = 0
for line in open(sys.argv[1]):
    if "|" not in line: continue
    asin, name = [x.strip() for x in line.split("|", 1)]
    if asin not in have:
        print("NEW ", asin, name); new += 1
print(f"{new} not on the page yet; {len(have)} ASINs already linked.")
