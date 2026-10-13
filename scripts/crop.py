"""Crop a library painting to the inner-slide image frame (510x500, saved at 1020x1000).
usage: python3 scripts/crop.py <file in library/> <out.jpg>
Reads focus_x, focus_y, zoom for the file from library/library.csv (defaults 0.5, 0.4, 1.0)."""
import csv, sys, pathlib
from PIL import Image
R = 510 / 500
root = pathlib.Path(__file__).resolve().parent.parent
name, out = sys.argv[1], sys.argv[2]
row = next((r for r in csv.DictReader(open(root/'library/library.csv')) if r['file'] == name), {})
fx = float(row.get('focus_x') or 0.5); fy = float(row.get('focus_y') or 0.4); zoom = float(row.get('zoom') or 1.0)
im = Image.open(root/'library'/name).convert('RGB'); W, H = im.size
if W / H > R: h = H * zoom; w = h * R
else: w = W * zoom; h = w / R
if h > H: h = H; w = h * R
x = min(max(fx * W - w / 2, 0), W - w); y = min(max(fy * H - h / 2, 0), H - h)
im.crop((int(x), int(y), int(x + w), int(y + h))).resize((1020, 1000), Image.LANCZOS).save(out, quality=88)
