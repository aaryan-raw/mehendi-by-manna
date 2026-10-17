"""Content, claims, link, metadata and build checks. Run from the project root with the built site served
(python3 -m http.server 4399 -d dist) and dist/ already built. Needs Python Playwright + Chromium."""
import re,os,glob,subprocess,json,struct
from playwright.sync_api import sync_playwright
URL=os.environ.get('QA_URL','http://localhost:4399/'); R=[]
def ok(n,c,x=''):
    R.append((n,bool(c))); print(('PASS ' if c else 'FAIL ')+n+((' | '+str(x)) if x else ''))
IG='https://www.instagram.com/mehndi_by_manna_/'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':900}); reqs=[]
    pg.on('request',lambda r:reqs.append(r.url)); pg.goto(URL,wait_until='networkidle')
    txt=pg.evaluate("(()=>{const c=document.body.cloneNode(true);c.querySelectorAll('script,style').forEach(e=>e.remove());return c.textContent.replace(/\\s+/g,' ')})()")  # includes closed FAQ answers + screen-reader text
    def absent(name,pat,flags=re.I):
        m=re.findall(pat,txt,flags=flags); ok(f'text: no {name}',not m,m[:4])
    absent('currency / price figures',r'₹|\bRs\.?\s?\d|\bINR\b|\$\s?\d|\b\d{3,}\s?(rupees|/-)')
    absent('discounts / percentages',r'\d\s?%|discount|\bsale\b|special offer|free\b')
    absent('testimonials / awards / credentials / client counts',r'testimonial|\breviews\b|five.star|\brated\b|award|certified|qualified|years of experience|happy clients|\d+\+? (brides|clients|customers)')
    absent("artist's personal name (either spelling)",r'Zamana|Samana')
    absent('phone / email / WhatsApp / tel:',r'whatsapp|wa\.me|mailto:|\btel:|\+?\d[\d\s\-]{8,}\d|[\w.]+@[\w-]+\.[a-z]{2,}')
    absent('other clients brands or services',r'myst(?:)ique|rehearsal|jam room|recording studio')
    absent('placeholder / draft text',r'lorem|ipsum|\bTODO\b|\bTBD\b|\[[^\]]*\]|insert |placeholder|xxx')
    absent('live-system claims',r'real-time|live availability|instant(ly)? (book|confirm)|book now')
    absent('gendered pronouns for the artist',r'\b(she|her|hers)\b')
    absent('inconsistent capitalisation of service names / US spelling',r'Bridal henna|Non-bridal Henna|Non-Bridal henna|Customisable designs|customiz',0)
    # confirmation wording must only appear negated / as 'to be confirmed'
    lines=re.split(r'(?<=[.!?])\s+',txt); bad=[l for l in lines if re.search(r'\b(booked|confirmed|reserved|scheduled|confirmation)\b',l,re.I) and not re.search(r"\b(no|not|nothing|never|books nothing|to be confirmed|not been confirmed)\b",l,re.I)]
    ok('text: booked/confirmed/reserved only appear negated or as "to be confirmed"',not bad,bad[:3])
    print('   (all sentences using those words:',[l[:90] for l in lines if re.search(r'\b(booked|confirmed|reserved)\b',l,re.I)],')')
    # location wording always attributed to the profile
    for m in re.finditer(r'Trivandrum|Kochi',txt): 
        ctx=txt[max(0,m.start()-170):m.end()+170]
        if 'rofile' not in ctx: ok('location wording attributed to profile',False,ctx); break
    else: ok('every Trivandrum/Kochi mention sits next to "as listed on / profile lists" attribution',True)
    # headings / CTAs / links
    hs=pg.evaluate("[...document.querySelectorAll('main h1,main h2,footer h2')].map(h=>h.textContent.trim())"); ok('no duplicated h1/h2 headings',len(hs)==len(set(hs)),hs)
    links=pg.evaluate("[...document.querySelectorAll('a')].map(a=>({h:a.getAttribute('href'),t:(a.getAttribute('aria-label')||a.textContent).replace(/\\s+/g,' ').trim(),x:a.target,r:a.rel}))")
    ok('no empty / bare "#" hrefs',all(l['h'] and l['h']!='#' for l in links))
    ext=[l for l in links if l['h'].startswith('http')]
    ok('external links: Instagram profile only, _blank + noopener noreferrer, announce new tab',all(l['h']==IG and l['x']=='_blank' and 'noopener' in l['r'] and 'noreferrer' in l['r'] and 'new tab' in l['t'] for l in ext) and len(ext)==5,[l['t'] for l in ext])
    ok('Instagram CTA labels consistent ("Message on Instagram" / handle / "More work…")',all(l['t'].startswith(('Message on Instagram','@mehndi_by_manna_','More work on Instagram')) for l in ext),[l['t'][:40] for l in ext])
    ids=set(pg.evaluate("[...document.querySelectorAll('[id]')].map(e=>e.id)")); ok('every internal anchor resolves',all(l['h'][1:] in ids for l in links if l['h'].startswith('#')))
    nameless=pg.evaluate("[...document.querySelectorAll('a,button,select,textarea,input')].filter(e=>!e.closest('dialog:not([open])')&&!(e.textContent.trim()||e.getAttribute('aria-label')||e.getAttribute('title')||(e.labels&&e.labels.length))).map(e=>e.outerHTML.slice(0,60))"); ok('every link/control has an accessible name',not nameless,nameless[:3])
    imgs=pg.evaluate("[...document.images].map(i=>[i.alt,!!i.closest('button,a[aria-label]')])"); ok('images: all have alt; informative ones are descriptive',all(a is not None for a,_ in imgs) and all(len(a)>25 or 'logo' in a.lower() for a,dec in imgs if a),len(imgs))
    ok('title / description / lang present',bool(pg.title()) and pg.evaluate("document.querySelector('meta[name=description]').content.length>40") and pg.evaluate("document.documentElement.lang")=='en')
    ok('description + og text say concept demonstration / not official','Not an official website' in pg.evaluate("document.querySelector('meta[name=description]').content") and 'not an official website' in pg.evaluate("document.querySelector('meta[property=\"og:description\"]').content").lower())
    fonts=[u for u in reqs if re.search(r'\.woff2?(\?|$)',u)]; ok('fonts: self-hosted only, woff2 subsets',all(u.startswith('http://localhost') for u in fonts) and fonts,[u.split('/')[-1] for u in fonts])
    ok('no non-local requests at load',all(u.startswith('http://localhost') or u.startswith('data:') for u in reqs),[u for u in reqs if not u.startswith(('http://localhost','data:'))])
    b.close()
# ---- built-output scans ----
files=glob.glob('dist/**/*.html',recursive=True)+glob.glob('dist/_astro/*.js')+glob.glob('dist/_astro/*.css')+['dist/robots.txt']
blob=''.join(open(f,errors='ignore').read() for f in files)
hosts=set(re.findall(r'https?://([a-z0-9.-]+)',blob)); print('   hosts mentioned in build output:',sorted(hosts))
ok('build output: only Instagram profile, SVG namespace and React error-doc strings are referenced',hosts<= {'www.instagram.com','www.w3.org','react.dev','reactjs.org'},sorted(hosts))
ok('build output: no analytics/tracker/pixel/chat widget strings',not re.search(r'google-analytics|googletagmanager|gtag\(|fbq\(|hotjar|segment\.com|plausible|clarity\.ms|intercom|crisp\.chat',blob,re.I))
first=[f for f in files if not f.endswith('.js')]+[f for f in glob.glob('src/**/*.*',recursive=True)+['astro.config.mjs','package.json','README.md'] if os.path.isfile(f)]
fp=''.join(open(f,errors='ignore').read() for f in first); js=''.join(open(f,errors='ignore').read() for f in glob.glob('dist/_astro/*.js'))
ok('first-party files + bundles: no other-brand, WhatsApp, mailto or tel: links',not re.search(r'myst(?:)ique|wa\.me|whatsapp|mailto:|href=.?tel:',fp+js,re.I))
ok('first-party files: no keys/secrets/passwords; JS bundles: no API-key/bearer/credential patterns (React library internals excluded)',not re.search(r'api[_-]?key|secret|bearer |password|AKIA[0-9A-Z]{8}|sk-[A-Za-z0-9]{16}',fp,re.I) and not re.search(r'api[_-]?key|bearer |AKIA[0-9A-Z]{8}|sk-[A-Za-z0-9]{16}',js,re.I))
ok('source: no fetch/XHR/beacon/storage/cookie/form code',not re.search(r'fetch\(|XMLHttpRequest|sendBeacon|localStorage|sessionStorage|indexedDB|document\.cookie|<form',''.join(open(f).read() for f in glob.glob('src/**/*.*',recursive=True) if os.path.isfile(f))))
ok('robots.txt disallows all',open('dist/robots.txt').read().strip().splitlines()[-1]=='Disallow: /')
h=open('dist/index.html').read(); ok('no canonical link, no JSON-LD in default build','rel="canonical"' not in h and 'ld+json' not in h)
ok('noindex meta in default build','noindex' in h)
ok('default build emits no og:image / og:url (no domain yet)','og:image' not in re.sub(r'<!--.*?-->','',h,flags=re.S) and 'og:url' not in h)
# ---- SITE_URL build ----
env=dict(os.environ,SITE_URL='https://example.invalid',NPM_CONFIG_USERCONFIG='/dev/null')
r=subprocess.run(['npx','astro','build','--outDir','/tmp/dist-site'],env=env,capture_output=True,text=True); ok('SITE_URL build succeeds',r.returncode==0 and 'Complete' in r.stdout+r.stderr)
h2=open('/tmp/dist-site/index.html').read()
ok('SITE_URL build: og:image + og:url are absolute and use the configured origin',re.search(r'og:image" content="https://example\.invalid/img/og\.jpg"',h2) and re.search(r'og:url" content="https://example\.invalid/"',h2))
ok('SITE_URL build: still noindex, still no canonical',('noindex' in h2) and 'rel="canonical"' not in h2)
d=open('/tmp/dist-site/img/og.jpg','rb').read(); 
from PIL import Image; w,hh=Image.open('/tmp/dist-site/img/og.jpg').size; ok('og.jpg exists and is 1200x630',(w,hh)==(1200,630),(w,hh))
print('FAILS:',[n for n,c in R if not c])
