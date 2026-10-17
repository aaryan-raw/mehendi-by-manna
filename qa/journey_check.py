"""First-time-visitor journey check at five viewports (Chromium). Run from the project root with the build served on :4399.
   python3 -m http.server 4399 -d dist &  then  python3 qa/journey_check.py"""
import os
from playwright.sync_api import sync_playwright
URL=os.environ.get('QA_URL','http://localhost:4399/'); R=[]
def ok(n,c,x=''):
    R.append((n,bool(c))); print(('PASS ' if c else 'FAIL ')+n+((' | '+str(x)) if x else ''))
VP=[(375,812),(430,932),(768,1024),(1280,800),(1440,900)]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in VP:
        pg=b.new_page(viewport={'width':w,'height':h}); pg.goto(URL,wait_until='networkidle'); pg.wait_for_timeout(500)
        nav=pg.evaluate("document.querySelector('#nav').getBoundingClientRect().height")
        t=f'@{w}'
        # 1-2 landing: headline + primary CTA + nav CTA in the first screen
        r=pg.evaluate("(()=>{const q=s=>document.querySelector(s).getBoundingClientRect();const h1=q('h1'),c=[...document.querySelectorAll('.hero .btn')][0].getBoundingClientRect(),n=[...document.querySelectorAll('.nav .btn')][0].getBoundingClientRect();return {h1:h1.bottom<innerHeight&&h1.top>0,cta:c.bottom<=innerHeight,nav:n.top>=0&&n.bottom<=80&&n.right<=innerWidth,lines:Math.round(h1.height/parseFloat(getComputedStyle(document.querySelector('h1')).lineHeight))}})()")
        ok(f'{t} landing: headline, primary CTA and nav CTA all visible without scrolling',r['h1'] and r['cta'] and r['nav'],r)
        ok(f'{t} headline wraps to <= 3 lines',r['lines']<=3,r['lines'])
        # 3 CTA -> collection lands clear of the sticky nav
        pg.click('.hero .btn >> nth=0'); pg.wait_for_timeout(1200)
        top=pg.evaluate("document.querySelector('#work h2').getBoundingClientRect().top"); ok(f'{t} "Explore the collection" lands with the heading clear of the nav',top>=nav and top<h,round(top))
        # 4 gallery photos keep natural proportions (no distorting crop)
        pg.locator('#work').scroll_into_view_if_needed(); pg.wait_for_timeout(800)
        d=pg.evaluate("[...document.querySelectorAll('.tile img')].map(i=>{const r=i.getBoundingClientRect();return Math.abs((r.width/r.height)/(i.naturalWidth/i.naturalHeight)-1)})")
        ok(f'{t} gallery: all 5 photos shown at natural aspect ratio (no crop/distortion)',len(d)==5 and max(d)<0.02,[round(x,3) for x in d])
        # 5 services visible; 6 service CTA -> demo with that service preselected
        pg.locator('.card .btn >> nth=0').scroll_into_view_if_needed(); pg.click('.card:first-child .btn >> nth=0'); pg.wait_for_timeout(1500)
        sel=pg.evaluate("document.querySelector('input[name=svc]:checked')?.parentElement.innerText.split('\\n')[0]"); bt=pg.evaluate("document.querySelector('#booking .demo-banner').getBoundingClientRect().top>=0")
        ok(f'{t} service CTA opens the demo with "Bridal Henna" preselected and the Demo banner in view',sel=='Bridal Henna' and bt,sel)
        # 7 Enquire -> pricing/enquiry section
        pg.evaluate("document.querySelector('#services').scrollIntoView({behavior:'instant'})"); pg.click('.card:first-child .btn--ghost'); pg.wait_for_timeout(1200)
        top=pg.evaluate("document.querySelector('#pricing').getBoundingClientRect().top"); ok(f'{t} "Enquire" reaches the pricing/enquiry section',top<h*0.5,round(top))
        # 8 FAQ: every answer opens, fits, and nothing is clipped/overflowing
        pg.locator('#faq').scroll_into_view_if_needed()
        for i in range(8): pg.locator('#faq details').nth(i).locator('summary').click()
        o=pg.evaluate("[...document.querySelectorAll('#faq details')].every(d=>d.open&&d.querySelector('div').getBoundingClientRect().right<=innerWidth)"); ok(f'{t} all 8 FAQ answers expand within the viewport',o)
        # clipping + line length + overflow across the whole page
        pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
        clip=pg.evaluate("[...document.querySelectorAll('h1,h2,h3,.btn,.eyebrow')].filter(e=>e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflow!=='visible').map(e=>e.textContent.trim().slice(0,30))"); ok(f'{t} no clipped headings, buttons or labels',not clip,clip)
        ll=pg.evaluate("Math.max(...[...document.querySelectorAll('main p')].filter(p=>p.getBoundingClientRect().height>0).map(p=>{const cs=getComputedStyle(p),lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.5,lines=Math.max(1,Math.round(p.getBoundingClientRect().height/lh));return p.textContent.trim().length/lines}))"); ok(f'{t} body copy averages <= 90 characters per line',ll<=90,round(ll))
        ok(f'{t} no horizontal overflow',pg.evaluate('document.documentElement.scrollWidth')<=w)
        # 9 footer reachable with disclaimer + Instagram link visible
        pg.locator('footer').scroll_into_view_if_needed(); f=pg.evaluate("(()=>{const l=document.querySelector('.legal');return l.innerText.includes('Independent concept demonstration · Not an official website')&&l.getBoundingClientRect().right<=innerWidth})()"); ok(f'{t} footer shows the concept disclaimer fully inside the viewport',f)
        pg.close()

    # ---- booking demo: every screen must say it is a demo; nothing may claim a request was sent/received; no payment fields ----
    import re
    for w,h in ((375,812),(1280,900)):
        pg=b.new_page(viewport={'width':w,'height':h}); pg.goto(URL,wait_until='networkidle'); pg.locator('#booking').scroll_into_view_if_needed(); pg.wait_for_timeout(1300)
        screens=[]
        def snap(): 
            screens.append(pg.evaluate("({banner:document.querySelector('.demo-banner')&&document.querySelector('.demo-banner').getBoundingClientRect().height>0&&document.querySelector('.demo-banner').innerText,text:document.querySelector('.demo').innerText,inputs:[...document.querySelectorAll('.demo input,.demo select,.demo textarea')].map(e=>(e.type||e.tagName)+':'+(e.autocomplete||'')+':'+(e.name||e.id))})"))
        snap(); pg.click('text=Continue'); snap(); pg.click('text=Continue'); pg.locator('.slot:not([disabled])').nth(0).click(); snap(); pg.click('text=Continue'); snap()
        pg.fill('#f-name','Demo Person'); pg.select_option('#f-event','Wedding'); pg.click('text=Continue'); snap(); pg.click('text=Complete demo request'); pg.wait_for_timeout(200); snap()
        ok(f'@{w} demo: all 6 screens (service, date, time, details, review, receipt) show the Booking Demo / sample-data banner',len(screens)==6 and all(s['banner'] and 'Booking Demo' in s['banner'] and 'illustrative sample data' in s['banner'] and 'Nothing is sent, saved or booked' in s['banner'] for s in screens))
        bad=[]
        for i,s in enumerate(screens):
            for sent in re.split(r'(?<=[.!?])\s+|\n',s['text']):
                if re.search(r'\b(request|enquiry|booking|appointment|message)\b.{0,40}\b(has been|was|is|have been|were)\b.{0,20}\b(sent|received|submitted|delivered|confirmed|booked|reserved|accepted)\b',sent,re.I) and not re.search(r'\b(no|not|nothing|never)\b',sent,re.I): bad.append((i,sent[:80]))
        ok(f'@{w} demo: no screen affirmatively says a request/appointment was sent, received, booked or confirmed',not bad,bad)
        rc=screens[5]['text']; ok(f'@{w} demo receipt: exact demonstration wording + DEMO- reference','Demo request completed' in rc and 'This is a website demonstration. No request was sent to the artist, and no appointment has been booked or confirmed.' in rc and re.search(r'DEMO-[A-Z0-9]{6}',rc) is not None)
        types=sorted({i.split(':')[0] for s in screens for i in s['inputs']}); fields=' '.join(i for s in screens for i in s['inputs'])
        ok(f'@{w} demo: no payment or credential fields (only radio/text/number/select/textarea; no card/cvv/password/email/tel)',set(types)<={'radio','text','number','select-one','textarea'} and not re.search(r'cc-|card|cvv|password|email|tel',fields,re.I),types)
        pg.click('text=Start again and clear details'); pg.wait_for_timeout(200)
        ok(f'@{w} demo: Start again returns to the example state (Guest Henna, Friday 23 October 2026, step 1)','Choose a service' in pg.inner_text('.d-main') and 'Guest Henna' in pg.inner_text('.d-side') and 'Friday 23 October 2026' in pg.inner_text('.d-side'))
        pg.close()
    b.close()
print('FAILS:',[n for n,c in R if not c])
