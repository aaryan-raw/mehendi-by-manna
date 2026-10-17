from playwright.sync_api import sync_playwright
import json,re,os
os.makedirs('qa/shots',exist_ok=True)
URL='http://localhost:4399/'
R=[]
def ok(n,c,x=''):
    R.append((n,bool(c))); print(('PASS ' if c else 'FAIL ')+n+((' | '+str(x)) if x else ''))
CONTRAST=open('qa/contrast.js').read()
VPS=[(375,812),(430,932),(768,1024),(1280,800),(1440,900)]
allreq=[];allerr=[];aborted=[]
def mk(b,w,h,**k):
    pg=b.new_context(viewport={'width':w,'height':h},**k).new_page()
    pg.on('request',lambda r:allreq.append((r.method,r.url,r.resource_type)))
    pg.on('console',lambda m:allerr.append(m.text) if m.type in('error','warning') else None)
    pg.on('pageerror',lambda e:allerr.append(str(e)))
    pg.on('requestfailed',lambda r:(aborted if r.failure=='net::ERR_ABORTED' else allerr).append('REQFAIL '+r.url+' '+str(r.failure)))
    return pg
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---------- 1. layout / perf per viewport ----------
    for w,h in VPS:
        pg=mk(b,w,h); pg.add_init_script("window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true})")
        start=len(allreq); pg.goto(URL,wait_until='networkidle'); pg.wait_for_timeout(400)
        init=[r for r in allreq[start:]]
        react=[r[1] for r in init if 'Booking' in r[1] or 'client.' in r[1]]
        imgs=[r[1].split('/')[-1] for r in init if r[2]=='image']
        ok(f'@{w} React/booking JS not loaded before scroll',not react,react)
        print(f'   @{w} initial images: {imgs}')
        for y in range(0,pg.evaluate('document.body.scrollHeight'),400): pg.evaluate(f'scrollTo(0,{y})'); pg.wait_for_timeout(70)
        pg.wait_for_timeout(600)
        sw=pg.evaluate('document.documentElement.scrollWidth'); ok(f'@{w} no horizontal overflow',sw<=w,sw)
        bad=pg.evaluate("[...document.images].filter(i=>i.getAttribute('src')&&!(i.complete&&i.naturalWidth>0)).map(i=>i.src)"); ok(f'@{w} all images loaded',not bad,bad)
        cls=pg.evaluate('window.__cls'); ok(f'@{w} layout shift (CLS) < 0.1',cls<0.1,round(cls,4))
        pg.close()
    # ---------- 2. links / meta ----------
    pg=mk(b,1280,800); pg.goto(URL,wait_until='networkidle')
    ids=pg.evaluate("[...document.querySelectorAll('[id]')].map(e=>e.id)")
    hrefs=pg.evaluate("[...document.querySelectorAll('a[href^=\"#\"]')].map(a=>a.getAttribute('href').slice(1)).filter(Boolean)")
    ok('internal anchors all resolve',all(h in ids for h in set(hrefs)),[h for h in set(hrefs) if h not in ids])
    ok('no duplicate ids',len(ids)==len(set(ids)))
    ext=pg.evaluate("[...document.querySelectorAll('a[href^=http]')].map(a=>[a.href,a.target,a.rel])")
    ok('external links: only the Instagram profile, new tab, noopener',all(e[0]=='https://www.instagram.com/mehndi_by_manna_/' and e[1]=='_blank' and 'noopener' in e[2] for e in ext) and ext,f'{len(ext)} links')
    ok('robots meta noindex',pg.evaluate("document.querySelector('meta[name=robots]').content").startswith('noindex'))
    ok('no og:image/url emitted without domain (no relative URL)',pg.evaluate("!document.querySelector('meta[property=\"og:image\"]')"))
    ok('no JSON-LD structured data',pg.evaluate("document.querySelectorAll('script[type=\"application/ld+json\"]').length")==0)
    ok('lang attr + title',pg.evaluate("document.documentElement.lang")=='en' and pg.title()!='')
    ok('no <form> elements (nothing can natively submit)',pg.evaluate("document.forms.length")==0)
    # ---------- 3. a11y structure ----------
    heads=pg.evaluate("[...document.querySelectorAll('h1,h2,h3,h4')].map(h=>[+h.tagName[1],h.textContent.trim().slice(0,28)])")
    skips=[(heads[i-1],heads[i]) for i in range(1,len(heads)) if heads[i][0]>heads[i-1][0]+1]
    ok('exactly one h1; no skipped heading levels',sum(1 for h in heads if h[0]==1)==1 and not skips,skips)
    lm=pg.evaluate("({header:document.querySelectorAll('header').length,main:document.querySelectorAll('main').length,footer:document.querySelectorAll('footer').length,nav:document.querySelectorAll('nav[aria-label]').length})"); ok('landmarks present',lm['header']==1 and lm['main']==1 and lm['footer']==1 and lm['nav']>=2,lm)
    ok('every img has alt attr',pg.evaluate("[...document.images].every(i=>i.hasAttribute('alt'))"))
    ok('no positive tabindex',pg.evaluate("![...document.querySelectorAll('[tabindex]')].some(e=>+e.getAttribute('tabindex')>0)"))
    # tab walk desktop
    pg.evaluate("scrollTo(0,0)"); pg.keyboard.press('Tab'); first=pg.evaluate("document.activeElement.className"); ok('first Tab stop is skip link',first=='skip',first)
    stops=[];invis=[]
    for i in range(140):
        d=pg.evaluate("""(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const t=e.closest('label.opt')||e;const cs=getComputedStyle(t),cs0=getComputedStyle(e);
          const vis=(cs.outlineStyle!=='none'&&parseFloat(cs.outlineWidth)>0)||(cs0.outlineStyle!=='none'&&parseFloat(cs0.outlineWidth)>0)||cs.boxShadow!=='none';
          const r=e.getBoundingClientRect();return {n:e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+':'+(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,18),vis,inview:r.bottom>0&&r.top<innerHeight}})()""")
        if d is None: break
        stops.append(d['n']); 
        if not d['vis']: invis.append(d['n'])
        pg.keyboard.press('Tab')
    ok(f'tab walk: {len(stops)} stops, all show a focus indicator',not invis and len(stops)>25,invis)
    ok('hidden mobile-menu links not tabbable on desktop',not any('Mobile' in s for s in stops) and not any(s.startswith('button#menu-btn') for s in stops))
    print('   order sample:',stops[:9],'...',stops[-4:])
    # contrast desktop initial
    pg.add_style_tag(content='.js .rv{opacity:1!important;transform:none!important}')
    c=pg.evaluate(CONTRAST); ok('contrast (static page, desktop): no text below AA',not c,c[:6])
    pg.close()
    # mobile: contrast + target size + menu
    pg=mk(b,375,812); pg.goto(URL,wait_until='networkidle'); pg.add_style_tag(content='.js .rv{opacity:1!important;transform:none!important}')
    c=pg.evaluate(CONTRAST); ok('contrast (static page, mobile)',not c,c[:6])
    small=pg.evaluate("""[...document.querySelectorAll('a,button,input,select,textarea,summary')].filter(e=>{const r=e.getBoundingClientRect(),cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&!e.closest('.sr,.skip,dialog:not([open]),.menu:not([data-open=true])')&&(r.width<44||r.height<44)&&!(e.tagName==='A'&&e.closest('p,small,li:not(.links li)')&&!e.classList.contains('btn')&&getComputedStyle(e.parentElement).display!=='flex')}).map(e=>e.tagName+':'+(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,20)+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height))""")
    print('   targets <44px (inline text links excluded):',small)
    ok('touch targets >= 24px (WCAG 2.2 min) for all controls',not pg.evaluate("[...document.querySelectorAll('button,input,select,textarea,summary,.btn')].some(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.height<24||r.width<24)&&!e.closest('.sr,dialog:not([open])')})"))
    pg.click('#menu-btn'); ok('menu aria-expanded true',pg.get_attribute('#menu-btn','aria-expanded')=='true')
    pg.keyboard.press('Escape'); ok('Escape closes menu + returns focus to button',pg.get_attribute('#menu-btn','aria-expanded')=='false' and pg.evaluate("document.activeElement.id")=='menu-btn')
    pg.click('#menu-btn'); pg.click('#menu a[href="#services"]'); pg.wait_for_timeout(900)
    top=pg.evaluate("document.querySelector('#services').getBoundingClientRect().top"); ok('anchor target clears sticky nav',top>=70,round(top))
    pg.close()
    # reduced motion
    pg=mk(b,1280,800,reduced_motion='reduce') if False else None
    ctx=b.new_context(viewport={'width':1280,'height':800},reduced_motion='reduce'); pg=ctx.new_page(); pg.goto(URL,wait_until='networkidle')
    rm=pg.evaluate("({op:getComputedStyle(document.querySelector('.rv')).opacity,td:getComputedStyle(document.querySelector('.btn')).transitionDuration,sb:getComputedStyle(document.documentElement).scrollBehavior})")
    ok('reduced motion: content visible, no transitions, no smooth scroll',rm['op']=='1' and rm['td'] in('0s','0.001s') and rm['sb']=='auto',rm); pg.close()
    # ---------- 4. lightbox every viewport ----------
    for w,h in VPS:
        pg=mk(b,w,h); pg.goto(URL,wait_until='networkidle'); pg.locator('#work').scroll_into_view_if_needed(); pg.wait_for_timeout(500)
        t=pg.locator('.tile').nth(1); t.focus(); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
        o=pg.evaluate("document.querySelector('#lb').open"); f=pg.evaluate("document.activeElement.id")
        ok(f'@{w} lightbox opens via keyboard, focus moves inside',o and f.startswith('lb-'),f)
        inside=True
        for _ in range(7):
            pg.keyboard.press('Tab'); inside&=pg.evaluate("!!document.activeElement.closest('#lb')")
        ok(f'@{w} focus stays trapped in dialog',inside)
        pg.keyboard.press('ArrowRight'); pg.keyboard.press('ArrowLeft'); pg.keyboard.press('ArrowLeft'); n=pg.inner_text('#lb-c'); pg.keyboard.press('ArrowLeft'); n2=pg.inner_text('#lb-c'); ok(f'@{w} arrow keys navigate and wrap (2->1->5)',n=='1 / 5' and n2=='5 / 5',(n,n2))
        done=[]
        for _ in range(5):
            pg.keyboard.press('ArrowRight'); pg.wait_for_function("document.querySelector('#lb-img').complete&&document.querySelector('#lb-img').naturalWidth>0",timeout=5000); done.append(pg.evaluate("document.querySelector('#lb-img').naturalWidth"))
        ok(f'@{w} all 5 full-size lightbox images load',len(done)==5 and min(done)>=600,done)
        box=pg.evaluate("(()=>{const r=document.querySelector('#lb-img').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight})()"); ok(f'@{w} lightbox image within viewport',box)
        if w in(375,1440): pg.screenshot(path=f'qa/shots/lb-{w}.png')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok(f'@{w} Escape closes, focus returns to opener',not pg.evaluate("document.querySelector('#lb').open") and pg.evaluate("document.activeElement.classList.contains('tile')"))
        pg.close()
    # ---------- 5. booking QA ----------
    for vw,vh in ((1280,900),(375,812)):
        print(f'--- booking @{vw}')
        pg=mk(b,vw,vh); pg.goto(URL,wait_until='networkidle'); pg.add_style_tag(content='.js .rv{opacity:1!important;transform:none!important}')
        pg.locator('#booking').scroll_into_view_if_needed(); pg.wait_for_timeout(1500)
        side=lambda: pg.inner_text('.d-side'); main=lambda: pg.inner_text('.d-main')
        ok('Booking Demo label + sample-data statement visible',pg.is_visible('.demo-banner') and 'Booking Demo' in pg.inner_text('.demo-banner') and 'illustrative sample data' in pg.inner_text('.demo-banner'))
        ok('preloaded example: Guest Henna / Friday 23 October 2026','Guest Henna' in side() and 'Friday 23 October 2026' in side())
        pg.click('label.opt:has-text("Bridal Henna") >> nth=0'); ok('select Bridal Henna -> summary','Service\nBridal Henna' in side().replace('SERVICE','Service') or 'Bridal Henna' in side())
        pg.click('label.opt:has-text("Non-Bridal Henna")'); ok('select Non-Bridal Henna -> summary (no stale Bridal)','Non-Bridal Henna' in side() and 'Guest' not in side())
        pg.click('text=Continue'); pg.wait_for_timeout(200)
        pg.click('.dchip[data-k="2026-10-26"]'); ok('date strip: select 26 Oct -> summary','Monday 26 October 2026' in side())
        full=pg.locator('.dchip.full').first; lab=full.get_attribute('data-k'); full.click(force=True); ok('unavailable strip date cannot be selected',full.get_attribute('aria-pressed')=='false' and 'Monday 26 October 2026' in side(),lab)
        pg.click('[aria-label="Next month"]'); ok('calendar next month = November 2026','November 2026' in pg.inner_text('.cal-h'))
        pg.locator('.cd.open:not([aria-disabled=true])').first.click(); ok('calendar click selects a November date','November 2026' in side())
        pg.click('[aria-label="Previous month"]'); ok('calendar previous month = October 2026','October 2026' in pg.inner_text('.cal-h'))
        pg.click('.dchip[data-k="2026-10-23"]')
        pg.focus('.cd[data-k="2026-10-23"]'); pg.keyboard.press('ArrowRight'); pg.keyboard.press('ArrowDown'); k1=pg.evaluate("document.activeElement.dataset.k"); ok('keyboard: Right+Down -> 31 Oct',k1=='2026-10-31',k1)
        pg.keyboard.press('PageDown'); k2=pg.evaluate("document.activeElement.dataset.k"); ok('keyboard: PageDown from 31 Oct clamps to 30 Nov (not Dec)',k2=='2026-11-30',k2)
        pg.keyboard.press('PageUp'); pg.keyboard.press('ArrowLeft'); pg.keyboard.press('ArrowLeft'); k3=pg.evaluate("document.activeElement.dataset.k"); ok('keyboard: PageUp then Left x2 -> 28 Oct',k3=='2026-10-28',k3)
        pg.keyboard.press('Enter'); pg.wait_for_timeout(100); ok('keyboard Enter selects focused date',pg.get_attribute('.cd[data-k="2026-10-28"]','aria-pressed')=='true' and 'Wednesday 28 October 2026' in side())
        ok('selected date announced via live region',pg.get_attribute('.d-main p.note[aria-live]','aria-live')=='polite' and 'Wednesday 28 October 2026' in pg.inner_text('p.note[aria-live]'))
        pg.click('.dchip[data-k="2026-10-23"]'); pg.click('text=Continue'); pg.wait_for_timeout(150)
        pg.click('text=Continue'); ok('continue without slot -> helpful error','sample time slot' in pg.inner_text('[role=alert]'))
        dis=pg.locator('.slot[disabled]').count(); ok('unavailable slots are disabled controls',dis>=1,dis)
        pg.locator('.slot:not([disabled])').nth(0).click(); pg.locator('.slot:not([disabled])').nth(2).click(); ok('slot selection exclusive (one aria-pressed)',pg.locator('.slot[aria-pressed=true]').count()==1)
        slot_txt=pg.locator('.slot[aria-pressed=true]').inner_text().split('\n')[0]; ok('summary shows chosen slot',slot_txt in side(),slot_txt)
        pg.click('text=Back'); pg.click('.dchip[data-k="2026-10-24"]')
        ok('changing date clears time + explains why','Not chosen yet' in side() and 'cleared' in pg.inner_text('[role=status]'))
        pg.click('text=Continue'); ok('time step shows no stale selection',pg.locator('.slot[aria-pressed=true]').count()==0)
        pg.locator('.slot:not([disabled])').nth(0).click(); pg.click('text=Continue'); pg.wait_for_timeout(150)
        pg.click('text=Continue'); e1=pg.inner_text('.d-main'); ok('empty details -> name + occasion errors','at least 2 characters' in e1 and 'Choose an occasion type' in e1)
        try: pg.wait_for_function("document.activeElement&&document.activeElement.id==='f-name'",timeout=2000); _foc=True
        except Exception: _foc=False
        ok('focus moved to first invalid field (waits up to 2s; app moves it ~15ms after click)',_foc)
        ok('labels marked required + aria-required',pg.locator('.req').count()==3 and pg.get_attribute('#f-name','aria-required')=='true')
        pg.fill('#f-name','A'); pg.select_option('#f-event','Wedding'); pg.fill('#f-guests','0'); pg.click('text=Continue'); t=pg.inner_text('.d-main'); ok('1-char name + 0 guests -> errors','at least 2 characters' in t and 'whole number from 1 to 50' in t)
        pg.fill('#f-guests','51'); pg.click('text=Continue'); ok('51 guests -> error','whole number from 1 to 50' in pg.inner_text('.d-main'))
        pg.fill('#f-guests',''); pg.click('text=Continue'); ok('blank guests -> error','whole number from 1 to 50' in pg.inner_text('.d-main'))
        pg.fill('#f-guests','4'); pg.fill('#f-name','Demo Person'); pg.fill('#f-notes','x'*301); pg.click('text=Continue'); ok('301-char notes -> error','300 characters' in pg.inner_text('.d-main'))
        ok('errors expose aria-invalid + describedby',pg.get_attribute('#f-notes','aria-invalid')=='true' and pg.get_attribute('#f-notes','aria-describedby')=='e-notes')
        pg.fill('#f-notes','Floral style'); pg.select_option('#f-event','Engagement'); pg.click('text=Continue'); pg.wait_for_timeout(150)
        rv=pg.inner_text('.d-main'); ok('review shows all details','Review your demo request' in rv and 'Non-Bridal Henna' in rv and 'Saturday 24 October 2026' in rv and 'Demo Person' in rv and 'Engagement' in rv and 'Floral style' in rv)
        pg.click('text=Edit details'); ok('edit details keeps entered values',pg.input_value('#f-name')=='Demo Person' and pg.input_value('#f-guests')=='4')
        pg.click('text=Continue'); pg.click('text=Edit service/date/time'); ok('edit service returns to step 1 with selection kept',pg.is_checked('label.opt:has-text("Non-Bridal Henna") input'))
        pg.click('label.opt:has-text("Bridal Henna") >> nth=0'); 
        for _ in range(4): pg.click('text=Continue'); pg.wait_for_timeout(100)
        rv=pg.inner_text('.d-main'); ok('changed service reflected in review (no stale)','Review your demo request' in rv and re.search(r'Service\s+Bridal Henna',rv,re.I) is not None and 'Non-Bridal' not in rv)
        before=len(allreq); pg.click('text=Complete demo request'); pg.wait_for_timeout(400); rc=pg.inner_text('.d-main')
        ok('receipt wording preserved exactly','Demo request completed' in rc and 'This is a website demonstration. No request was sent to the artist, and no appointment has been booked or confirmed.' in rc)
        ok('demo reference labelled + DEMO- prefix',re.search(r'Demo reference: DEMO-[A-Z0-9]{6}',rc) is not None)
        ok('receipt never says booked/confirmed/requested affirmatively','has been booked' not in rc.replace('no appointment has been booked or confirmed','') and 'confirmed!' not in rc.lower())
        ok('no network requests on submit',len(allreq)==before,allreq[before:])
        ok('no storage/cookies/IndexedDB',pg.evaluate("localStorage.length+sessionStorage.length")==0 and pg.evaluate("document.cookie")=='' and pg.evaluate("indexedDB.databases().then(d=>d.length)")==0)
        ok('focus lands on receipt heading',pg.evaluate("document.activeElement.textContent")=='Demo request completed')
        pg.locator('.demo').screenshot(path=f'qa/shots/receipt-{vw}.png')
        pg.click('text=Start again and clear details'); pg.wait_for_timeout(200)
        ok('start again: step 1, example state restored','Choose a service' in main() and 'Guest Henna' in side() and 'Friday 23 October 2026' in side())
        for _ in range(2): pg.click('text=Continue'); pg.wait_for_timeout(100)
        pg.locator('.slot:not([disabled])').nth(0).click(); pg.click('text=Continue'); pg.wait_for_timeout(150)
        ok('start again: all entered details cleared',pg.input_value('#f-name')=='' and pg.input_value('#f-notes')=='' and pg.input_value('#f-event')=='' and pg.input_value('#f-guests')=='2')
        ok('no overflow in booking',pg.evaluate("document.documentElement.scrollWidth")<=vw)
        pg.close()
    b.close()
bad=[r for r in allreq if r[0]!='GET' or (r[1].startswith('http') and 'localhost' not in r[1])]
ok('ENTIRE RUN: no non-GET and no external requests',not bad,bad[:3]); ok(f'ENTIRE RUN: console clean, no failed requests ({len(allreq)} requests; {len(aborted)} browser-cancelled image loads from rapid lightbox flipping)',not allerr,sorted(set(allerr))[:5])
print('FAILS:',[r[0] for r in R if not r[1]])
