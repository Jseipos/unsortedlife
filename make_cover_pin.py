#!/usr/bin/env python3
"""Cover pin (1000x1500) from a square gift-guide illustration that has a blank center.
Usage: python3 make_cover_pin.py <illustration> <out.jpg> "<title>" "<subtitle>"
Title goes in the illustration's blank center; a cream band below carries the subtitle, handle and page URL."""
import sys
from PIL import Image, ImageDraw, ImageFont
src, out, title, sub = sys.argv[1:5]
W,H = 1000,1500
CREAM=(251,244,238); INK=(58,46,42); ACCENT=(199,108,132); MUTED=(138,116,112)
F_BIG="/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"; F_SM="/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
im = Image.open(src).convert("RGB").resize((W,W), Image.LANCZOS)
pin = Image.new("RGB",(W,H),CREAM); pin.paste(im,(0,0))
d = ImageDraw.Draw(pin)
# blank center of these illustrations sits at roughly 29..71% x, 33..67% y
cx0,cy0,cx1,cy1 = int(W*.30), int(W*.34), int(W*.70), int(W*.66)
def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font) <= maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines
size=64
while size>30:
    font=ImageFont.truetype(F_BIG,size); lines=wrap(title,font,cx1-cx0-30)
    if len(lines)*size*1.2 <= (cy1-cy0)-30 and all(d.textlength(l,font=font)<=cx1-cx0-30 for l in lines): break
    size-=3
th=len(lines)*size*1.2; y=cy0+((cy1-cy0)-th)//2
for l in lines:
    tw=d.textlength(l,font=font); d.text(((W-tw)//2,y),l,font=font,fill=ACCENT); y+=int(size*1.2)
d.rectangle((0,W,W,W+8),fill=ACCENT)
f2=ImageFont.truetype(F_BIG,46); sl=wrap(sub,f2,W-120); y=W+60
for l in sl:
    tw=d.textlength(l,font=f2); d.text(((W-tw)//2,y),l,font=f2,fill=INK); y+=58
small=ImageFont.truetype(F_SM,30)
d.text((60,H-70),"@theunsortedlife",font=small,fill=ACCENT)
url="jseipos.github.io/unsortedlife"; d.text((W-60-d.textlength(url,font=small),H-70),url,font=small,fill=MUTED)
pin.save(out,"JPEG",quality=88); print("wrote",out,"title size",size)
