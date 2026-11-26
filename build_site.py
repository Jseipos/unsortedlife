#!/usr/bin/env python3
"""Build The Unsorted Life link page: site/index.html from site/products.json.

Usage: python3 build_site.py <site_dir> [<photos_inbox_dir>]
Photos, in order of preference:
  1. an inbox file whose name ends in _a (or _a2, _a3) before the extension, e.g.
     "crate_a.HEIC", "dawn powerwash_a.jpg": an affiliate product shot. It is matched to
     the product whose "match" words appear in the file name. First match wins.
  2. the item's explicit "photo" file name in products.json (older mapping).
Converted copies land in <site_dir>/img/<slug>.jpg (Pillow, with pillow-heif for HEIC).
Items without a usable photo render as a plain card (no image), never a stock image.
Files without the _a suffix are filler/b-roll for the shorts pipeline and are ignored here.
"""
import json, os, re, sys, html

site_dir = sys.argv[1]
inbox = sys.argv[2] if len(sys.argv) > 2 else None
data = json.load(open(os.path.join(site_dir, "products.json")))
img_dir = os.path.join(site_dir, "img")
os.makedirs(img_dir, exist_ok=True)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]

AFFILIATE_SUFFIX = re.compile(r"_a\d*$", re.I)   # crate_a.HEIC, crate_a2.jpg

def affiliate_photos():
    """Inbox files whose stem ends in _a (optionally _a2, _a3): product shots for the link page."""
    if not inbox or not os.path.isdir(inbox):
        return []
    out = []
    for f in sorted(os.listdir(inbox)):
        stem, ext = os.path.splitext(f)
        if ext.lower() in (".jpg", ".jpeg", ".png", ".heic") and AFFILIATE_SUFFIX.search(stem):
            out.append(f)
    return out

AFF = affiliate_photos()

def find_affiliate_photo(item):
    """First _a photo whose name contains one of the item's match words (or its first name word)."""
    if "match" in item and not item["match"]:
        return None  # explicit empty match: never auto-pick a photo (gift list items)
    words = [w.lower() for w in item.get("match", [])] or [item["name"].split()[0].lower()]
    for f in AFF:
        stem = AFFILIATE_SUFFIX.sub("", os.path.splitext(f)[0]).lower().replace("-", " ").replace("_", " ")
        if any(w in stem for w in words):
            return f
    return None

def ensure_photo(item):
    name = find_affiliate_photo(item) or item.get("photo") or ""
    if not name:
        return None
    out = os.path.join(img_dir, slug(name) + ".jpg")
    if os.path.exists(out):
        return "img/" + os.path.basename(out)
    if not inbox:
        return None
    src = os.path.join(inbox, name)
    if not os.path.exists(src):
        return None
    try:
        from PIL import Image, ImageOps
        try:
            import pillow_heif  # noqa
            pillow_heif.register_heif_opener()
        except Exception:
            pass
        im = Image.open(src)
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((900, 900))
        im.save(out, "JPEG", quality=82, optimize=True)
        return "img/" + os.path.basename(out)
    except Exception as e:
        sys.stderr.write(f"skip {name}: {e}\n")
        return None

s = data["site"]
parts = []
parts.append(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(s['title'])}: what I actually use</title>
<meta name="description" content="{html.escape(s['tagline'])}">
<meta name="p:domain_verify" content="be38e078cec140b060eb7cad3dee5145"/>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fbf4ee;--bg2:#f6e7df;--ink:#3a2e2a;--muted:#8a7470;--card:#fffaf6;--line:#ecd9d0;--accent:#c76c84;--accent-2:#9fb49a;--accent-ink:#ffffff;--shadow:0 6px 18px rgba(120,70,80,.10)}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#221a1b;--bg2:#2c2123;--ink:#f3e9e6;--muted:#b89da0;--card:#2b2124;--line:#4a373b;--accent:#e58aa3;--accent-2:#8fae8c;--accent-ink:#2a1a1f;--shadow:0 6px 18px rgba(0,0,0,.35)}}}}
:root[data-theme="dark"]{{--bg:#221a1b;--bg2:#2c2123;--ink:#f3e9e6;--muted:#b89da0;--card:#2b2124;--line:#4a373b;--accent:#e58aa3;--accent-2:#8fae8c;--accent-ink:#2a1a1f;--shadow:0 6px 18px rgba(0,0,0,.35)}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);background-image:radial-gradient(circle at 20% 0%,var(--bg2),transparent 55%),radial-gradient(circle at 100% 30%,var(--bg2),transparent 40%);color:var(--ink);font:16px/1.55 "Nunito",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
header{{padding:34px 16px 14px;max-width:720px;margin:0 auto;text-align:center}}
h1{{font-family:"Playfair Display",Georgia,serif;font-style:italic;font-weight:600;font-size:38px;margin:0 0 6px;letter-spacing:-.01em;color:var(--accent)}}
h1::after{{content:"";display:block;width:84px;height:3px;margin:12px auto 0;border-radius:3px;background:linear-gradient(90deg,var(--accent),var(--accent-2))}}
.tag{{color:var(--muted);margin:0 0 16px;font-size:17px}}
.social{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:0 0 16px}}
.social a{{border:1.5px solid var(--line);border-radius:999px;padding:7px 14px;color:var(--ink);text-decoration:none;font-size:14px;font-weight:600;background:var(--card);box-shadow:var(--shadow)}}
.social a:hover{{border-color:var(--accent);color:var(--accent)}}
.disc{{font-size:13px;color:var(--muted);background:var(--card);border:1px dashed var(--line);border-radius:14px;padding:10px 14px;margin:0;text-align:left}}
nav{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}}
nav .tabs{{max-width:720px;margin:0 auto;padding:8px 16px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}}
nav a{{white-space:nowrap;font-size:15px;font-weight:700;color:var(--muted);text-decoration:none;padding:8px 16px;border-radius:999px;border:1.5px solid transparent}}
nav a:hover{{color:var(--accent)}}
nav a.active{{color:var(--accent);border-color:var(--accent);background:var(--card)}}
section,.card,.row{{scroll-margin-top:72px}}
.start h2::before{{content:"\u2740"}}
.grid.start-grid{{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}
.start-grid .card img{{aspect-ratio:4/3}}
.start-grid .note{{display:none}}
main{{max-width:720px;margin:0 auto;padding:8px 16px 48px}}
section{{margin:30px 0}}
h2{{font-family:"Playfair Display",Georgia,serif;font-weight:600;font-size:28px;margin:0 0 2px;padding-top:14px;text-align:center}}
h2::before{{content:"❦";display:block;color:var(--accent-2);font-size:20px;margin-bottom:2px}}
h3{{font-family:"Playfair Display",Georgia,serif;font-weight:600;font-style:italic;font-size:20px;margin:22px 0 2px;color:var(--accent)}}
.intro{{color:var(--muted);margin:0 0 12px}}
.sec-intro{{color:var(--muted);margin:0 0 4px;text-align:center}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;display:flex;flex-direction:column;box-shadow:var(--shadow)}}
.card img{{width:100%;aspect-ratio:1/1;object-fit:cover;display:block;background:var(--line)}}
.body{{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}}
.name{{font-weight:700;line-height:1.3}}
.note{{font-size:14px;color:var(--muted);flex:1}}
.btn{{display:inline-block;background:var(--accent);color:var(--accent-ink);text-decoration:none;border-radius:999px;padding:9px 14px;font-size:14px;font-weight:700;text-align:center;box-shadow:0 3px 10px rgba(199,108,132,.28)}}
.btn:hover{{filter:brightness(1.07)}}
.tile{{aspect-ratio:4/3;background:linear-gradient(135deg,var(--bg2),var(--card));border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:center;padding:14px;text-align:center}}
.tile span{{font-family:"Playfair Display",Georgia,serif;font-style:italic;font-weight:600;font-size:22px;color:var(--accent);line-height:1.2}}
.listbtn{{margin:0 0 14px}}
.btn.alt{{background:var(--accent-2);box-shadow:0 3px 10px rgba(159,180,154,.35)}}
.group .body{{gap:10px}}
.row{{display:flex;flex-direction:column;gap:4px}}
.card.group{{grid-column:1 / -1}}
.card.group img{{width:100%;aspect-ratio:auto;height:auto;max-height:520px;object-fit:cover}}
.card.group .body{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}
.card.group .row{{padding:10px;border:1px solid var(--line);border-radius:12px;background:var(--bg)}}
.card.group.portrait{{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,3fr)}}
.card.group.portrait img{{height:auto;max-height:none;object-fit:unset;align-self:stretch}}
.card.group.portrait .body{{grid-template-columns:1fr;align-content:center}}
@media (max-width:600px){{.card.group.portrait{{grid-template-columns:1fr}}.card.group.portrait img{{max-height:none}}}}
.empty{{border:1.5px dashed var(--line);border-radius:18px;padding:16px;color:var(--muted);font-size:14px;text-align:center;background:var(--card)}}
footer{{max-width:720px;margin:0 auto;padding:0 16px 40px;font-size:12px;color:var(--muted);text-align:center}}
</style>
</head>
<body>
<header>
<h1>{html.escape(s['title'])}</h1>
<p class="tag">{html.escape(s['tagline'])}</p>
<div class="social">{''.join(f'<a href="{html.escape(l["url"])}" rel="noopener">{html.escape(l["label"])}</a>' for l in s['links'])}</div>
<p class="disc">{html.escape(s['disclosure'])}</p>
</header>
<nav><div class="tabs">{''.join(f'<a href="#{sec["slug"]}">{html.escape(sec["title"])}</a>' for sec in data['sections'])}</div></nav>
<main>
""")

featured = sorted([it for sec in data["sections"] for lst in sec["lists"] for it in lst["items"] if it.get("featured") and it.get("url")], key=lambda i: i["featured"])
if featured:
    parts.append(f'<section id="start-here" class="start"><h2>{html.escape(s.get("start_here","Start here"))}</h2><p class="sec-intro">{html.escape(s.get("start_here_intro",""))}</p><div class="grid start-grid">')
    for it in featured:
        photo = ensure_photo(it)
        img = f'<img src="{photo}" alt="{html.escape(it["name"])}, my own photo" loading="lazy">' if photo else ""
        parts.append(
            f'<article class="card">{img}<div class="body"><div class="name">{html.escape(it["name"])}</div>'
            f'<div class="note">{html.escape(it["note"])}</div>'
            f'<a class="btn" href="{html.escape(it["url"])}" rel="nofollow sponsored noopener" target="_blank">{html.escape(it.get("short") or it["name"])} on Amazon #ad</a></div></article>')
    parts.append('</div></section>')

for sec in data["sections"]:
  parts.append(f'<section id="{sec["slug"]}"><h2>{html.escape(sec["title"])}</h2><p class="sec-intro">{html.escape(sec["intro"])}</p>')
  for lst in sec["lists"]:
    parts.append(f'<div class="list" id="{lst["slug"]}"><h3>{html.escape(lst["title"])}</h3>' + (f'<p class="intro">{html.escape(lst["intro"])}</p>' if lst.get("intro") else ""))
    if lst.get("amazon_list"):
        parts.append(f'<p class="listbtn"><a class="btn alt" href="{html.escape(lst["amazon_list"])}" rel="nofollow sponsored noopener" target="_blank">See the whole list on Amazon, with photos #ad</a></p>')
    if not lst["items"]:
        parts.append('<div class="empty">Nothing here yet. Only things I have bought and would buy again go on this list.</div>')
    else:
        parts.append('<div class="grid">')
        # group adjacent items that share one photo (a collage) into a single card with one CTA per product
        groups = []
        shown = 0
        for it in lst["items"]:
            if not it.get("url"):
                continue   # pending: photo in, link not yet; stays off the page until the url is filled
            if lst.get("limit") and shown >= lst["limit"]:
                break      # wish lists show only the first N cards; the rest stay in products.json and on the Amazon list
            shown += 1
            photo = ensure_photo(it)
            if groups and photo and groups[-1][0] == photo:
                groups[-1][1].append(it)
            else:
                groups.append([photo, [it]])
        for photo, items in groups:
            if len(items) == 1:
                it = items[0]
                img = f'<img src="{photo}" alt="{html.escape(it["name"])}, my own photo" loading="lazy">' if photo else (f'<div class="tile" aria-hidden="true"><span>{html.escape(it.get("short") or it["name"])}</span></div>' if lst.get("wishlist") else "")
                parts.append(
                    f'<article class="card" id="{slug(it.get("short") or it["name"])}">{img}<div class="body"><div class="name">{html.escape(it["name"])}</div>'
                    f'<div class="note">{html.escape(it["note"])}</div>'
                    f'<a class="btn" href="{html.escape(it["url"])}" rel="nofollow sponsored noopener" target="_blank">See it on Amazon #ad</a></div></article>'
                )
            else:
                alt = ", ".join(i.get("short") or i["name"] for i in items)
                rows = "".join(
                    f'<div class="row" id="{slug(i.get("short") or i["name"])}"><div class="name">{html.escape(i["name"])}</div><div class="note">{html.escape(i["note"])}</div>'
                    f'<a class="btn" href="{html.escape(i["url"])}" rel="nofollow sponsored noopener" target="_blank">{html.escape(i.get("short") or i["name"])} on Amazon #ad</a></div>'
                    for i in items)
                cls = "card group"
                try:
                    from PIL import Image as _I
                    _w, _h = _I.open(os.path.join(site_dir, photo)).size
                    if _h > _w * 1.1:
                        cls += " portrait"   # tall photo: image left, product rows stacked on the right
                except Exception:
                    pass
                parts.append(f'<article class="{cls}"><img src="{photo}" alt="{html.escape(alt)}, my own photo" loading="lazy"><div class="body">{rows}</div></article>')
        parts.append('</div>')
    parts.append('</div>')
  parts.append('</section>')

parts.append(f"""</main>
<footer>No prices on purpose: Amazon's change daily. Photos are my own house. {html.escape(s['disclosure'].split('.')[0])}.</footer>
<script>
(function(){{
  var links=[].slice.call(document.querySelectorAll('nav a'));
  var secs=links.map(function(a){{return document.querySelector(a.getAttribute('href'));}});
  function mark(){{
    var y=window.scrollY+70, cur=0;
    secs.forEach(function(sec,i){{ if(sec && sec.offsetTop<=y) cur=i; }});
    links.forEach(function(a,i){{ a.classList.toggle('active', i===cur); }});
  }}
  window.addEventListener('scroll', mark, {{passive:true}}); window.addEventListener('load', mark); mark();
}})();
</script>
</body>
</html>
""")

open(os.path.join(site_dir, "index.html"), "w").write("".join(parts))
print("wrote", os.path.join(site_dir, "index.html"))
