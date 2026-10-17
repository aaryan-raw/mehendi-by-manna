"""axe-core automated accessibility scan across states. axe is NOT a project dependency:
   npm install --no-save axe-core   (or set AXE_PATH to any axe.min.js)   then run from the project root."""
import os,json,sys
from playwright.sync_api import sync_playwright
AXE=os.environ.get('AXE_PATH','node_modules/axe-core/axe.min.js'); URL=os.environ.get('QA_URL','http://localhost:4399/')
src=open(AXE).read(); TOTAL=0; INC={}; DET={}
OPTS={'runOnly':{'type':'tag','values':['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}}
def scan(pg,label,ctx='document'):
    global TOTAL
    r=pg.evaluate("([ctx,o])=>axe.run(document.querySelector(ctx)||document,o).then(r=>({v:r.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,t:v.nodes[0].target.join(' '),h:v.help})),inc:r.incomplete.map(i=>i.id),incd:r.incomplete.map(i=>({id:i.id,t:i.nodes[0].target.join(' ').slice(0,60),m:((i.nodes[0].any[0]||i.nodes[0].all[0]||i.nodes[0].none[0]||{}).message||'').slice(0,110)})),p:r.passes.length}))",[ctx if ctx!='document' else 'html',OPTS])
    TOTAL+=len(r['v']); print(f"{'PASS' if not r['v'] else 'FAIL'}  axe {label}: {len(r['v'])} violations, {r['p']} rules passed, incomplete(manual review): {sorted(set(r['inc']))}")
    for v in r['v']: print('      -',v['id'],v['impact'],f"x{v['n']}",v['t'][:70],'|',v['h'])
    for i in r['inc']: INC[i]=INC.get(i,0)+1
    for d in r['incd']: DET.setdefault(d['id'],set()).add((d['t'],d['m']))
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in((375,812),(1280,900)):
        pg=b.new_page(viewport={'width':w,'height':h}); pg.goto(URL,wait_until='networkidle'); pg.add_style_tag(content='.js .rv{opacity:1!important;transform:none!important}'); pg.add_script_tag(content=src)
        for y in range(0,pg.evaluate('document.body.scrollHeight'),500): pg.evaluate(f'scrollTo(0,{y})'); pg.wait_for_timeout(50)
        pg.wait_for_timeout(1200); scan(pg,f'@{w} full page (booking step 1)')
        if w==375: pg.evaluate('scrollTo(0,0)'); pg.click('#menu-btn'); scan(pg,f'@{w} mobile menu open'); pg.keyboard.press('Escape')
        pg.locator('.tile').first.click(); pg.wait_for_timeout(400); scan(pg,f'@{w} lightbox open'); pg.keyboard.press('Escape')
        pg.locator('details').first.locator('summary').click(); scan(pg,f'@{w} FAQ item expanded')
        pg.locator('#booking').scroll_into_view_if_needed(); pg.click('text=Continue'); pg.wait_for_timeout(250); scan(pg,f'@{w} booking: date step','.demo')
        pg.click('text=Continue'); pg.locator('.slot:not([disabled])').nth(0).click(); scan(pg,f'@{w} booking: time step (slot selected)','.demo')
        pg.click('text=Continue'); pg.click('text=Continue'); pg.wait_for_timeout(200); scan(pg,f'@{w} booking: details step with validation errors','.demo')
        pg.fill('#f-name','Demo Person'); pg.select_option('#f-event','Wedding'); pg.click('text=Continue'); scan(pg,f'@{w} booking: review step','.demo')
        pg.click('text=Complete demo request'); pg.wait_for_timeout(200); scan(pg,f'@{w} booking: demo receipt','.demo'); pg.close()
    b.close()
print('TOTAL VIOLATIONS:',TOTAL,'| rules needing manual review:',INC)
for k,v in DET.items():
    print('MANUAL-REVIEW',k,'->',sorted(v)[:3])
