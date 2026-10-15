"""Render a carousel from a spec JSON (blue-board design).
usage: python3 scripts/render.py spec.json
spec: {"date":"YYYY-MM-DD", "region":"us"|"eu", "outdir":"posts/<date>-<slot>",
       "cover":{"sub","title","steps":[one short label per inner slide],"hook","image":"painting-....jpg"},
       "inner":[{"title","body","label","image":"painting-....jpg"}...],
       "closer":{"HEADLINE","TONIGHT","THIS_WEEK","NEXT_WEEK","CTA","NEXT_TITLE"}}
cover.title: wrap the keyword in <span class="y">...</span>. inner title: wrap one word in <span class="hl">...</span>.
closer.HEADLINE: two lines with <br>, reframe word(s) in <span class="y">...</span>. closer.CTA: keyword in <b>...</b>.
Needs: npm i geist (repo root), pip install playwright pillow. Paintings are cropped with scripts/crop.py.
Specs in the old white design (cover.image = cover-N.svg) render with templates/classic/ unchanged.
Prints per-slide layout metrics as JSON lines for checking."""
import json, sys, pathlib, asyncio, subprocess, tempfile
from playwright.async_api import async_playwright
R = pathlib.Path(__file__).resolve().parent.parent
spec = json.load(open(sys.argv[1]))
out = pathlib.Path(spec['outdir']) if spec.get('outdir') else R/'posts'/(spec['date'] + ('-' + spec['region'] if spec.get('region') else ''))
out.mkdir(parents=True, exist_ok=True)
tmp = pathlib.Path(tempfile.mkdtemp())
c = spec['cover']
classic = c.get('image', '').startswith('cover-')

def crop(img, name):
    dst = tmp/name
    subprocess.run([sys.executable, str(R/'scripts/crop.py'), img, str(dst)], check=True, cwd=R)
    return 'file://' + str(dst)

if classic:
    font = 'file://' + str(R/'node_modules/geist/dist/fonts/geist-sans/Geist-Regular.woff2')
    def fill(tpl, d):
        h = (R/'templates/classic'/tpl).read_text()
        for k, v in dict(d, FONT_REGULAR=font).items(): h = h.replace('{{'+k+'}}', v)
        assert '{{' not in h, tpl
        return h
    pages = [fill('cover.html', {'TITLE': c['title'], 'COVER_IMAGE': 'file://'+str(R/'covers'/c['image']), 'HOOK': c['hook'], 'FEN_NEUTRAL': 'file://'+str(R/'brand/fen-neutral.svg')})]
    for i, s in enumerate(spec['inner']):
        pages.append(fill('inner.html', {'TITLE': s['title'], 'BODY': s['body'], 'IMAGE': crop(s['image'], f'img{i}.jpg')}))
    pages.append(fill('closer.html', dict({'CTA': ''}, **spec['closer'])))
else:
    base = (R/'templates/base.css').read_text().replace('{{FONT_DIR}}', 'file://' + str(R/'node_modules/geist/dist/fonts/geist-sans'))
    def fill(tpl, d):
        h = (R/'templates'/tpl).read_text().replace('{{BASE_CSS}}', base)
        for k, v in d.items(): h = h.replace('{{'+k+'}}', v)
        assert '{{' not in h, tpl
        return h
    steps = ''.join(f'<div class="col"><div class="box st"><span class="tag">{t}</span></div><div class="num">{i+1}</div></div>' for i, t in enumerate(c['steps']))
    pages = [fill('cover.html', {'SUB': c['sub'], 'TITLE': c['title'], 'STEPS': steps, 'HOOK': c['hook'], 'IMAGE': crop(c['image'], 'cover.jpg')})]
    for i, s in enumerate(spec['inner']):
        pages.append(fill('inner.html', {'NUM': str(i+1), 'TITLE': s['title'], 'BODY': s['body'], 'LABEL': s['label'], 'IMAGE': crop(s['image'], f'img{i}.jpg')}))
    pages.append(fill('closer.html', spec['closer']))

JS_CLASSIC = '''()=>{const r=x=>{const e=document.querySelector(x);return e?e.getBoundingClientRect().toJSON():null};
const h=document.querySelector('h1,h2');const lh=parseFloat(getComputedStyle(h).lineHeight);
const im=document.querySelector('img.img');
return {lines:Math.round(h.getBoundingClientRect().height/lh),text_bottom:(r('.s > p')||{}).bottom,img_top:(r('.img')||{}).top,
hook_bottom:(r('.hook')||{}).bottom,fen_top:(r('img.fen')||{}).top,img_loaded:im?im.naturalWidth>0:null,font:document.fonts.check('40px Geist')}}'''
JS = '''()=>{const r=x=>{const e=document.querySelector(x);return e?e.getBoundingClientRect():null};
const h=document.querySelector('h1,h2');const ims=[...document.querySelectorAll('img')];
const o={font_px:parseFloat(getComputedStyle(h).fontSize),title_bottom:Math.round(h.getBoundingClientRect().bottom),
img_loaded:ims.length?ims.every(i=>i.naturalWidth>0):null,font:document.fonts.check('900 40px G')};
const b=r('.b');if(b){o.body_bottom=Math.round(b.bottom);o.body_ok=b.bottom<1000}
const fl=r('.flow');if(fl){o.flow_top=Math.round(fl.top);o.title_clear=h.getBoundingClientRect().bottom<fl.top-20}
const cta=r('.cta');if(cta){o.cta_lines=Math.round(cta.height/(parseFloat(getComputedStyle(document.querySelector('.cta')).fontSize)*1.4))}
const pb=[...document.querySelectorAll('.pb p,.st .tag')];o.boxes_ok=pb.every(e=>{const p=e.parentElement.getBoundingClientRect(),q=e.getBoundingClientRect();return q.bottom<=p.bottom&&q.right<=p.right+1&&q.left>=p.left-1});
return o}'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for i, h in enumerate(pages, 1):
            f = tmp/f'slide-{i:02d}.html'; f.write_text(h)
            await pg.goto('file://'+str(f)); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
            print(json.dumps({'slide': i, **await pg.evaluate(JS_CLASSIC if classic else JS)}))
            await pg.screenshot(path=str(out/f'slide-{i:02d}.png'))
        await b.close()
asyncio.run(main())
