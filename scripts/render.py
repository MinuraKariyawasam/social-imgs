"""Render a carousel from a spec JSON.
usage: python3 scripts/render.py spec.json
spec: {"date":"YYYY-MM-DD", "region":"us"|"nordic" (output goes to posts/<date>-<region>/), "cover":{"title","image":"cover-N.svg","hook"},
       "inner":[{"title","body","image":"painting-....jpg"}...],
       "closer":{"HEADLINE","SUBLINE","TONIGHT","THIS_WEEK","NEXT_WEEK","NEXT_TITLE","CTA"}, "outdir": optional}
  CTA (optional): one comment prompt on the last slide; wrap the keyword in <b>…</b>.
Needs: npm i geist (in the repo root), pip install playwright pillow. Paintings are cropped with scripts/crop.py.
Prints per-slide layout metrics as JSON lines for checking."""
import json, sys, pathlib, asyncio, subprocess, tempfile
from playwright.async_api import async_playwright
R = pathlib.Path(__file__).resolve().parent.parent
spec = json.load(open(sys.argv[1]))
out = pathlib.Path(spec['outdir']) if spec.get('outdir') else R/'posts'/(spec['date'] + ('-' + spec['region'] if spec.get('region') else ''))
out.mkdir(parents=True, exist_ok=True)
tmp = pathlib.Path(tempfile.mkdtemp())
font = 'file://' + str(R/'node_modules/geist/dist/fonts/geist-sans/Geist-Regular.woff2')
def fill(tpl, d):
    h = (R/'templates'/tpl).read_text()
    for k, v in dict(d, FONT_REGULAR=font).items(): h = h.replace('{{'+k+'}}', v)
    assert '{{' not in h, tpl
    return h
c = spec['cover']
pages = [fill('cover.html', {'TITLE': c['title'], 'COVER_IMAGE': 'file://'+str(R/'covers'/c['image']), 'HOOK': c['hook'], 'FEN_NEUTRAL': 'file://'+str(R/'brand/fen-neutral.svg')})]
for i, s in enumerate(spec['inner']):
    crop = tmp/f'img{i}.jpg'
    subprocess.run([sys.executable, str(R/'scripts/crop.py'), s['image'], str(crop)], check=True)
    pages.append(fill('inner.html', {'TITLE': s['title'], 'BODY': s['body'], 'IMAGE': 'file://'+str(crop)}))
pages.append(fill('closer.html', dict({'CTA': ''}, **spec['closer'])))
JS = '''()=>{const r=x=>{const e=document.querySelector(x);return e?e.getBoundingClientRect().toJSON():null};
const h=document.querySelector('h1,h2');const lh=parseFloat(getComputedStyle(h).lineHeight);
const im=document.querySelector('img.img');
return {lines:Math.round(h.getBoundingClientRect().height/lh),text_bottom:(r('.s > p')||{}).bottom,img_top:(r('.img')||{}).top,
hook_bottom:(r('.hook')||{}).bottom,fen_top:(r('img.fen')||{}).top,img_loaded:im?im.naturalWidth>0:null,font:document.fonts.check('40px Geist')}}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1080,'height':1350})
        for i, h in enumerate(pages, 1):
            f = tmp/f'slide-{i:02d}.html'; f.write_text(h)
            await pg.goto('file://'+str(f)); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
            print(json.dumps({'slide': i, **await pg.evaluate(JS)}))
            await pg.screenshot(path=str(out/f'slide-{i:02d}.png'))
        await b.close()
asyncio.run(main())
