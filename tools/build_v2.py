#!/usr/bin/env python3
"""Build the v2 static copy of codex-hive.com from the Nov 19 live snapshot.
Input : ../live-snapshot (raw HTML + rendered blog DOM), /workspace/codex-hive-backup (asset cache),
        /workspace/academy-preview/divisions-embed.html
Output: ../docs ONLY (GitHub Pages /docs folder). Never writes outside codex-hive-site-v2.
"""
import re,os,json,hashlib,shutil,html as H,urllib.parse as up,requests
from bs4 import BeautifulSoup,NavigableString,Tag
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assert ROOT.endswith('codex-hive-site-v2')
SNAP=ROOT+'/live-snapshot';OUT=os.path.abspath(os.environ.get('V2_OUT',ROOT+'/docs'));assert OUT.startswith(ROOT+'/');BK='/workspace/codex-hive-backup'
LIVE='https://codex-hive.com';NEWZ='https://newz.codex-hive.com/'
S=requests.Session();S.headers['User-Agent']='Mozilla/5.0 (X11; Linux x86_64) Chrome/124'
man={}
for l in open(BK+'/assets_manifest.tsv'):
  n,u=l.rstrip('\n').split('\t');man[u]=n
def safe(n): return re.sub(r'[^A-Za-z0-9._-]','_',n)
USED=set()
def asset(u):
  if not u: return u
  if u.startswith('//'):u='https:'+u
  if 'wsimg.com' not in u: return u
  b=re.sub(r'/:/.*','',u).split('?')[0]
  if '/:/cr=' in u and 'cr=t:0%25,l:0%25,w:100%25,h:100%25' not in u: b=re.sub(r'(/:/[^/]*cr=[^/]*)/.*$',r'\1',u)  # keep GoDaddy crop (e.g. founder photo)
  n=man.get(b)
  if n:
    s=safe(n)
    if not os.path.exists(OUT+'/assets/'+s): shutil.copy(BK+'/assets/'+n,OUT+'/assets/'+s)
  else:
    s=hashlib.sha1(b.encode()).hexdigest()[:8]+'_'+safe(up.unquote(re.sub(r'/:/.*','',b).rsplit('/',1)[-1]))
    if not os.path.exists(OUT+'/assets/'+s):
      r=S.get(b,timeout=60);r.raise_for_status();open(OUT+'/assets/'+s,'wb').write(r.content);print('downloaded',b)
  USED.add(s);return '/assets/'+s
PAGES={'/','/blog/','/music/','/podcasts/','/apps-1/','/interactive/','/ufft/','/ftf/','/lsfm-vs-hl-3/','/technology-stack-draft/',
 '/fractalfs/','/correction-notice/','/daphnis-wake/','/contact/','/intro/','/rules-for-use/','/research/'}
def fixhref(h):
  h=h.strip()
  if 'hive-buzz-newz.netlify.app' in h or re.match(r'^(https://codex-hive\.com)?/newz/?$',h): return NEWZ
  if 'wsimg.com' in h: return asset(h)
  if h.startswith(LIVE): h=h[len(LIVE):] or '/'
  if h.startswith('/') and not h.startswith('//'):
    p,_,q=h.partition('?');p,_,frag=p.partition('#')
    if p and not p.endswith('/') and (p+'/') in PAGES: p+='/'
    if p.startswith('/blog/f/') and not p.endswith('/'): p+='/'
    h=p+('#'+frag if frag else '')
  return h
def fix_embed(d):
  d=re.sub(r'https?://img1\.wsimg\.com/[^"\'\s)]+',lambda m:asset(H.unescape(m.group(0))),d)
  d=re.sub(r'href="([^"]+)"',lambda m:'href="'+fixhref(m.group(1))+'"',d)
  return d.replace('hive-buzz-newz.netlify.app','newz.codex-hive.com')
def conv(node,slug,emb):
  out=[]
  for c in node.children:
    if isinstance(c,NavigableString):
      t=str(c)
      if t.strip(): out.append(H.escape(t))
      continue
    if not isinstance(c,Tag) or c.name in('script','style','noscript','svg','button') and not c.get_text(strip=True): continue
    n=c.name
    if n in('script','style','noscript','svg'): continue
    if n=='iframe':
      d=c.get('srcdoc');s=c.get('src')
      if d:
        fn=f'{safe(slug)}_{len(emb)}.html';emb.append(fn);open(OUT+'/embeds/'+fn,'w').write(fix_embed(d))
        out.append(f'<iframe class="embed" src="/embeds/{fn}" loading="lazy" title="{H.escape(slug)} embed {len(emb)}"></iframe>')
      elif s and not s.startswith('javascript'): out.append(f'<iframe class="embed" src="{H.escape(s)}" loading="lazy"></iframe>')
      continue
    if n=='img':
      s=c.get('data-srclazy') or c.get('src') or ''
      if 'wsimg' in s: out.append(f'<img src="{asset(s)}" alt="{H.escape(c.get("alt",""))}" loading="lazy">')
      continue
    if n in('video','source'):
      s=c.get('src')
      if s: out.append(f'<video controls preload="metadata" src="{asset(s)}"></video>')
      elif n=='video': out.append(conv(c,slug,emb))
      continue
    if n=='form': out.append('<p class="note">Contact form: email or call us using the details on this page.</p>');continue
    inner=conv(c,slug,emb)
    if n=='a':
      h=fixhref(c.get('href',''))
      if h in('#','') and not inner.strip(): continue
      if not inner.strip() and c.get('aria-label'): inner=H.escape(c['aria-label'].replace(' Social Link',''))
      out.append(f'<a href="{H.escape(h)}">{inner}</a>' if inner.strip() else '');continue
    if n in('h1','h2','h3','h4','p','ul','ol','li','strong','em','blockquote','table','tr','td','th','thead','tbody','pre','code'):
      out.append(f'<{n}>{inner}</{n}>' if inner.strip() else '');continue
    if n=='br': out.append('<br>');continue
    if 'Button' in (c.get('data-ux') or ''): out.append(f'<span class="btn">{inner}</span>');continue
    if n in('div','section') and inner.strip(): out.append(f'<div>{inner}</div>');continue
    out.append(inner)
  return ''.join(out)
NAV=[('Home','/',[]),('Blog','/blog/',[]),('Hive Buzz',None,[('Music','/music/'),('Podcasts','/podcasts/'),('Newz',NEWZ)]),
 ('Interactive',None,[('APPS','/apps-1/'),('Interactive','/interactive/')]),
 ('Research',None,[('UFFT','/ufft/'),('FTF','/ftf/'),('LSFM vs HL-3','/lsfm-vs-hl-3/'),('Technology stack (draft)','/technology-stack-draft/'),('FractalFS','/fractalfs/'),('Correction Notice','/correction-notice/'),('Daphnis Wake','/daphnis-wake/')]),
 ('Contact','/contact/',[])]
def header():
  s=['<header class="site-header"><a class="brand" href="/"><img src="/assets/logo-header.png" alt="Codex Hive Labs logo" width="48" height="43"><span>Codex Hive Labs</span></a><input type="checkbox" id="m" aria-label="Menu"><label for="m" class="burger" aria-hidden="true">☰</label><nav class="nav"><ul>']
  for t,h,sub in NAV:
    if sub: s.append(f'<li class="dd"><span tabindex="0">{t} ▾</span><ul>'+''.join(f'<li><a href="{u}">{n}</a></li>' for n,u in sub)+'</ul></li>')
    else: s.append(f'<li><a href="{h}">{t}</a></li>')
  s.append('</ul></nav></header>');return ''.join(s)
HEADER=header()
FOOT=('<footer><p><a href="https://www.facebook.com/100265876391121">Facebook</a> · <a href="https://www.linkedin.com/in/valentin-voineag-0b39942a/">LinkedIn</a> · <a href="https://www.x.com/voineag40013">X</a></p>'
 '<p><a href="tel:+12693503043">(269) 350-3043</a></p>'
 '<p class="legal">© 2026 Codex Hive Labs LLC. All rights reserved. All research, media, publications, and related materials are independently produced by Codex Hive Labs LLC. The views expressed are solely those of the authors and contributors and do not necessarily reflect the views of any client, partner, affiliate, or other third party. All content is provided for informational purposes only, is subject to change without notice, and does not constitute legal, financial, investment, technical, or other professional advice.</p></footer>')
GA_ID='G-DW4D6JPPB4'
# Consent Mode v2: everything denied by default; a stored "granted" is applied before config.
GA=('<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
 'gtag("consent","default",{analytics_storage:"denied",ad_storage:"denied",ad_user_data:"denied",ad_personalization:"denied"});'
 'try{if(localStorage.getItem("ch_cookie_consent")==="granted"){gtag("consent","update",{analytics_storage:"granted"});}}catch(e){}'
 f'gtag("js",new Date());gtag("config","{GA_ID}");</script>'
 f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>')
# Cookie banner: wording and single "Accept" button copied from the live GoDaddy banner (FOOTER_COOKIE_* in live-snapshot/html/home.html).
SHOW_DECLINE = True  # live has no Decline button; set True to add one (label not on live)
COOKIE_TITLE='This website uses cookies.'
COOKIE_MSG='We use cookies to analyze website traffic and optimize your website experience. By accepting our use of cookies, your data will be aggregated with all other user data.'
BANNER=('<div id="ch-cookie" class="ch-cookie" role="dialog" aria-live="polite" aria-label="Cookie consent" aria-describedby="ch-cookie-msg" hidden>'
 f'<h4 class="ch-cookie-t">{COOKIE_TITLE}</h4><p id="ch-cookie-msg">{COOKIE_MSG}</p><div class="ch-cookie-b">'
 +('<button type="button" class="ch-decline" data-c="denied">Decline</button>' if SHOW_DECLINE else '')+
 '<button type="button" class="ch-accept" data-c="granted">Accept</button></div></div>'
 '<style>.ch-cookie{position:fixed;left:16px;right:16px;bottom:16px;z-index:1000;max-width:380px;margin-left:auto;background:#1b1c22;color:#e9e9ea;border:1px solid #c99a4b;border-radius:10px;padding:14px 16px;box-shadow:0 8px 24px rgba(0,0,0,.55);font:14px/1.45 Roboto,system-ui,sans-serif}'
 '.ch-cookie[hidden]{display:none}.ch-cookie-t{margin:0 0 6px;color:#f2a900;font-size:15px}.ch-cookie p{margin:0 0 12px;font-size:13px;color:#cfd0d3}'
 '.ch-cookie-b{display:flex;gap:8px;justify-content:flex-end}.ch-cookie button{font:600 13px Roboto,system-ui,sans-serif;letter-spacing:.5px;text-transform:uppercase;border-radius:6px;padding:9px 18px;cursor:pointer;min-height:40px}'
 '.ch-accept{background:#f2a900;color:#111;border:1px solid #f2a900}.ch-accept:hover{background:#d99700}.ch-decline{background:transparent;color:#e9e9ea;border:1px solid #777}'
 '.ch-cookie button:focus-visible{outline:2px solid #fff;outline-offset:2px}@media(max-width:480px){.ch-cookie{left:10px;right:10px;bottom:10px;max-width:none}.ch-cookie-b button{flex:1}}</style>'
 '<script>(function(){var k="ch_cookie_consent",b=document.getElementById("ch-cookie");var v=null;try{v=localStorage.getItem(k)}catch(e){}'
 'if(!v){b.hidden=false;}b.addEventListener("click",function(e){var c=e.target.getAttribute&&e.target.getAttribute("data-c");if(!c)return;'
 'try{localStorage.setItem(k,c)}catch(x){}if(c==="granted"){gtag("consent","update",{analytics_storage:"granted"});}b.hidden=true;});})();</script>')
FIT="<script>(function(){var f=[].slice.call(document.querySelectorAll('iframe.embed'));function fit(i){try{var d=i.contentDocument;if(d&&d.body){i.style.height=Math.max(d.documentElement.scrollHeight,d.body.scrollHeight)+'px';}}catch(e){i.style.height='800px'}}f.forEach(function(i){i.addEventListener('load',function(){fit(i);setTimeout(function(){fit(i)},800);setTimeout(function(){fit(i)},2500)});});window.addEventListener('resize',function(){f.forEach(fit)});})();</script>"
def head(path,sp,extra=''):
  title=sp.title.get_text(strip=True) if sp.title else 'Codex Hive Labs'
  m={}
  for t in sp.find_all('meta'):
    k=t.get('property') or t.get('name')
    if k and t.get('content') is not None and k not in m: m[k]=t['content']
  og=''.join(f'<meta property="{k}" content="{H.escape(((lambda u:LIVE+u if u.startswith('/') else u)(fixhref(v))) if k=="og:image" else v)}">' for k,v in m.items() if k.startswith('og:') and k!='og:url')
  og+=f'<meta property="og:url" content="{LIVE}{path}">'
  return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{GA}'
   f'<title>{H.escape(title)}</title><meta name="description" content="{H.escape(m.get("description",""))}">{og}'
   f'<link rel="canonical" href="{LIVE}{path}"><link rel="icon" href="/assets/logo-header.png"><link rel="stylesheet" href="/style.css?v=20261119">{extra}</head><body>'),title
# Text overrides approved by Valentin (Nov 19, 10:14 ET, via Webster): soften two CombOS lines.
# Applied to every generated page (post body, meta description, og:description); each must hit at least once.
TEXT_OVERRIDES=[
 ("CombOS is our swarm operating system project, and it's now running as an interactive demo.",
  "CombOS is our swarm operating system project, and it's still in development. Here's the idea behind it."),
 ("It's built on rules and values taken from our real CombOS kernel code.",
  "Its rules and values follow the CombOS design, which is still in development."),
 ("this week's first look at CombOS running as a self-healing swarm",
  "this week's first look at the self-healing swarm design behind CombOS"),
]
_OV_HITS={i:0 for i in range(len(TEXT_OVERRIDES))}
def apply_overrides(html):
  for i,(old,new) in enumerate(TEXT_OVERRIDES):
    for o,n in ((old,new),(H.escape(old),H.escape(new)),(old.replace("'","&#39;"),new.replace("'","&#39;"))):
      if o in html: html=html.replace(o,n);_OV_HITS[i]+=1
  return html
def write(path,html):
  html=apply_overrides(html)
  if GA in html: html=html.replace('</body>',BANNER+'</body>',1)
  d=OUT+path;os.makedirs(d,exist_ok=True);open(d+'index.html','w').write(html)
def sections(sp):
  secs=[s for s in sp.select('[data-ux=Section],[data-ux=SectionBanner]') if not s.find_parent(attrs={'data-ux':re.compile('^Section')})]
  return [s for s in secs if not s.find_parent('footer') and s.name!='footer' and not s.find(attrs={'data-aid':re.compile('FOOTER')})]
def clean(b):
  b=re.sub(r'(<div>)+\s*(</div>)+','',b)
  for _ in range(3): b=re.sub(r'<div>\s*</div>','',b)
  return b
def about_html(sec):
  t=sec.find(attrs={'data-aid':'ABOUT_SECTION_TITLE_RENDERED'})
  rows=[]
  for i in range(10):
    img=sec.find(attrs={'data-aid':f'ABOUT_IMAGE_RENDERED{i}'})
    if not img: break
    hd=sec.find(attrs={'data-aid':f'ABOUT_HEADLINE_RENDERED{i}'});ds=sec.find(attrs={'data-aid':f'ABOUT_DESCRIPTION_RENDERED{i}'})
    cta=sec.find(attrs={'data-aid':f'ABOUT_CTA_BTN_RENDERED{i}'})
    src=asset(img.get('data-srclazy') or img.get('src'))
    shape=' round' if i%2 else ''
    txt=f'<div class="about-txt"><h4>{H.escape(hd.get_text(strip=True))}</h4>{clean(conv(ds,"home",[]))}'
    if cta: txt+=f'<p><a class="btn-ghost" href="{H.escape(fixhref(cta.get("href","")))}">{H.escape(cta.get_text(strip=True))}</a></p>'
    txt+='</div>'
    im=f'<div class="about-img{shape}"><img src="{src}" alt="{H.escape(img.get("alt",""))}" loading="lazy" width="532" height="532"></div>'
    rows.append(f'<div class="about-row{" rev" if i%2 else ""}">{im}{txt}</div>')
  return f'<section class="about"><h2 id="about">{H.escape(t.get_text(strip=True))}</h2>'+''.join(rows)+'</section>'
def contact_html(sp):
  g=lambda a:sp.find(attrs={'data-aid':a})
  intro=g('CONTACT_INTRO_DESC_REND').find('p').get_text(' ',strip=True)
  email=next(a['href'][7:] for a in sp.find_all('a',href=True) if a['href'].startswith('mailto:'))
  rows=''.join(f'<tr><td>{H.escape(tr.find_all("td")[0].get_text(strip=True))}</td><td>{H.escape(tr.find_all("td")[1].get_text(strip=True))}</td></tr>' for tr in g('CONTACT_HOURS_REND').find_all('tr'))
  return (f'<section class="contact"><h1>{H.escape(g("CONTACT_SECTION_TITLE_REND").get_text(strip=True))}</h1>'
   f'<h4>{H.escape(g("CONTACT_INTRO_HEADING_REND").get_text(strip=True))}</h4><p>{H.escape(intro)}</p>'
   f'<p><strong>Email:</strong> <a href="mailto:{email}">{email}</a><br><strong>Phone:</strong> <a href="tel:+12693503043">(269) 350-3043</a></p>'
   f'<h4>{H.escape(g("CONTACT_HOURS_TITLE_REND").get_text(strip=True))}</h4><table class="hours">{rows}</table></section>'
   '<section class="contact"><h2>Connect With Us</h2><p><a href="https://www.facebook.com/100265876391121">Facebook</a><a href="https://www.linkedin.com/in/valentin-voineag-0b39942a/">LinkedIn</a><a href="https://www.x.com/voineag40013">X</a></p></section>')
# reset generated dirs (inside v2/docs only)
for d in os.listdir(OUT):
  p=OUT+'/'+d
  if d in('assets','style.css'): continue
  shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
os.makedirs(OUT+'/embeds')
manifest=[]
slugs={'ftf':'/ftf/','technology-stack-draft':'/technology-stack-draft/','music':'/music/','apps-1':'/apps-1/','intro':'/intro/','fractalfs':'/fractalfs/','ufft':'/ufft/','podcasts':'/podcasts/','interactive':'/interactive/','rules-for-use':'/rules-for-use/','correction-notice':'/correction-notice/','daphnis-wake':'/daphnis-wake/','research':'/research/','lsfm-vs-hl-3':'/lsfm-vs-hl-3/','contact':'/contact/'}
for slug,path in slugs.items():
  sp=BeautifulSoup(open(f'{SNAP}/html/{slug}.html').read(),'html.parser')
  emb=[];body=clean(''.join(f'<section>{conv(s,slug,emb)}</section>' for s in sections(sp)))
  if slug=='contact': body=contact_html(sp)
  h,title=head(path,sp);write(path,h+HEADER+f'<main>{body}</main>'+FOOT+(FIT if emb else '')+'</body></html>')
  manifest.append((path,title))
# home: keep the static intro hero from the Nov 16 build, regenerate content from live
old=open('/workspace/codex-hive-site/index.html').read()
sp=BeautifulSoup(open(f'{SNAP}/html/home.html').read(),'html.parser')
emb=[];body=clean(''.join(about_html(s) if s.find(attrs={'data-aid':'ABOUT_IMAGE_RENDERED0'}) else f'<section>{conv(s,"home",emb)}</section>' for s in sections(sp)))
div=open('/workspace/academy-preview/divisions-embed.html').read()
div=fix_embed(div).replace(' target="_top"','')
body=re.sub(r'<iframe class="embed" src="/embeds/home_\d+\.html"[^>]*></iframe>','<div class="divisions" id="divisions">'+div+'</div>',body,count=1)
h,title=head('/',sp)
intro=old[old.find('<div id="intro"'):old.find('<main')]
intro=intro.replace('data-line="Learning from the Hive · Science · AI · Creativity · Coming Soon" aria-label="Hive Academy: Learning from the Hive · Science · AI · Creativity · Coming Soon"','data-line="Learning from the Hive · Science · AI · Creativity · Preview" aria-label="Hive Academy: Learning from the Hive · Science · AI · Creativity · Preview"')
# Hero (Nov 19): cropped globe video (no baked text/button) + real stacked logo + HTML Join button
PATREON='https://www.patreon.com/c/Codex_Hive_Labs'
# Hero logo (Nov 19 v3): transparent cutout of the official metallic reference (tools/logo/cutout.py), sized 1x/2x
from PIL import Image as _Img, ImageFilter as _IF
LOGO_SRC=ROOT+'/tools/logo/codex-hive-logo-metallic-bigtext.png'   # 1105x889 "bigtext" master (Webster, Nov 19 09:49)
HERO_W=(210,240,310,356,420,480,620,712)
HERO_CSS_W,HERO_CSS_W_M=353,239          # css width desktop / <=760px (Valentin still deciding size)
def hero_logo_files():
  src=_Img.open(LOGO_SRC).convert('RGBA');sw,sh=src.size
  for w in HERO_W:
    h=round(sh*w/sw)
    for ext in ('png','webp'):
      f=f'{OUT}/assets/hero/codex-hive-logo-bt-{w}.{ext}'
      if os.path.exists(f): continue          # keep the existing hand-made files byte-for-byte
      im=src.convert('RGBa').resize((w,h),_Img.LANCZOS).convert('RGBA')   # premultiplied resample: no dark fringes
      rgb=im.convert('RGB').filter(_IF.UnsharpMask(radius=0.6,percent=35,threshold=2));im=_Img.merge('RGBA',(*rgb.split(),im.getchannel('A')))
      im.save(f,optimize=True) if ext=='png' else im.save(f,quality=92,method=6,alpha_quality=100)
  return round(sh*HERO_CSS_W/sw)
LOGO_H=hero_logo_files()
_srcset=lambda ext:', '.join(f'/assets/hero/codex-hive-logo-bt-{w}.{ext} {w}w' for w in HERO_W)
_sizes=f'(max-width:760px) {HERO_CSS_W_M}px, {HERO_CSS_W}px'
S1=('<div class="scr s1 on" id="s1"><h1 class="sr">Codex Hive Labs: Intelligent Systems. Built Together.</h1>'
 f'<div class="hero-logo"><picture><source type="image/webp" srcset="{_srcset("webp")}" sizes="{_sizes}">'
 f'<img src="/assets/hero/codex-hive-logo-bt-356.png" srcset="{_srcset("png")}" sizes="{_sizes}" alt="Codex Hive Labs" width="{HERO_CSS_W}" height="{LOGO_H}" decoding="async"></picture></div>'
 '<video id="lv" autoplay muted loop playsinline preload="auto" poster="/assets/hero/landing-poster.jpg?v=20261119" aria-hidden="true">'
 '<source src="/assets/hero/landing.webm?v=20261119" type="video/webm"><source src="/assets/hero/landing.mp4?v=20261119" type="video/mp4"></video>'
 f'<div class="hero-cta"><a class="join-btn" href="{PATREON}" target="_blank" rel="noopener">Join the Hive</a>'
 '<a class="explore" href="#hive" data-act="explore">Choose your division →</a></div></div>\n')
HERO_CSS=('<style id="hero-v2-css">.stage{container-type:inline-size}'
 '.s1{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:clamp(10px,2.4cqw,30px);background:radial-gradient(ellipse at 50% 62%,#0b1424 0,#05070b 72%)}'
 f'.s1 .hero-logo img{{width:{HERO_CSS_W}px;max-width:32cqw;height:auto;object-fit:contain;display:block;filter:drop-shadow(0 4px 18px rgba(0,0,0,.6))}}'
 '.s1 video{width:100%;height:auto;aspect-ratio:1280/332;object-fit:cover;-webkit-mask-image:linear-gradient(transparent,#000 14%,#000 86%,transparent);mask-image:linear-gradient(transparent,#000 14%,#000 86%,transparent)}'
 '.hero-cta{display:flex;flex-direction:column;align-items:center;gap:10px}'
 '.join-btn{display:inline-block;padding:12px 34px;border:2px solid #f2a900;border-radius:6px;color:#ffd77a;background:rgba(5,7,11,.55);text-decoration:none;font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:clamp(.85rem,1.1vw,1.05rem);box-shadow:0 0 14px rgba(242,169,0,.35);transition:background .2s,box-shadow .2s,color .2s}'
 '.join-btn:hover,.join-btn:focus-visible{background:rgba(242,169,0,.16);color:#fff;box-shadow:0 0 0 2px rgba(242,169,0,.5),0 0 26px rgba(242,169,0,.6);outline:none}'
 '.explore{color:#cfd0d3;font-size:.9rem;text-decoration:none;letter-spacing:.04em}.explore:hover,.explore:focus-visible{color:#f2a900}'
 f'@media(max-width:760px){{.stage{{aspect-ratio:4/5}}.s1{{gap:14px;justify-content:center;padding-bottom:36px}}.s1 .hero-logo img{{width:{HERO_CSS_W_M}px;max-width:64vw}}.join-btn{{padding:11px 28px;font-size:.85rem}}}}'
 '@media(min-width:761px){.s1 .hero-logo{position:relative;z-index:2;transform:translateY(clamp(10px,2.2cqw,32px))}}'
 '</style>')
oldstyle=''.join(re.findall(r'<style[^>]*>.*?</style>',old[:old.find('<body')],flags=re.S))
scripts=''.join(re.findall(r'<script>.*?</script>',old[old.find('</main>'):],flags=re.S))
scripts=scripts.replace(FIT,'')
intro=re.sub(r'<div class="scr s1 on" id="s1">.*?</div>\n?',lambda m:S1,intro,count=1,flags=re.S)
assert 'class="join"' not in intro and 'hero-logo' in intro
h=h.replace('</head>',oldstyle+HERO_CSS+'</head>')
write('/',h+HEADER+intro+f'<main id="content">{body}</main>'+FOOT+scripts+(FIT if emb else '')+'</body></html>')
manifest.append(('/',title))
# blog posts from rendered DOM
posts=[]
for u in [l.strip() for l in open(SNAP+'/blogurls.txt') if '/blog/f/' in l]:
  slug=up.unquote(u.rsplit('/',1)[1]);f=SNAP+'/rendered/'+u.replace(LIVE+'/','').replace('/','_')+'.html'
  sp=BeautifulSoup(open(f).read(),'html.parser');raw=BeautifulSoup(open(SNAP+'/html/'+u.replace(LIVE+'/','').replace('/','_')+'.html').read(),'html.parser')
  m=sp.find(attrs={'data-ux':'BlogMain'});t=m.find('h3').get_text(strip=True)
  date=m.find(attrs={'data-aid':'RSS_POST_DATE'}) or m.find('h3').find_next('div')
  ds=date.get_text(strip=True);content=date.find_next_sibling('div') if date.name=='div' else date.find_parent('div').find_next_sibling('div')
  bd=clean(conv(content,'post',[]))
  img=re.search(r'<img src="([^"]+)"',bd)
  path=f'/blog/f/{slug}/';h,title=head(path,raw)
  art=f'<article class="post"><p><a href="/blog/">← All Posts</a></p><h1>{H.escape(t)}</h1><p class="date">{H.escape(ds)}</p>{bd}</article>'
  write(path,h+HEADER+f'<main>{art}</main>'+FOOT+'</body></html>')
  posts.append((path,t,ds,img.group(1) if img else None));manifest.append((path,title))
# blog index (order = live sitemap order, newest first)
sp=BeautifulSoup(open(SNAP+'/html/blog.html').read(),'html.parser');h,title=head('/blog/',sp)
cards=''.join(f'<a class="card" href="{p}">'+(f'<img src="{i}" alt="" loading="lazy">' if i else '')+f'<h3>{H.escape(t)}</h3><p class="date">{H.escape(d)}</p></a>' for p,t,d,i in posts)
body=('<section><h1>The Codex Frontier</h1><div class="grid">'+cards+'</div></section>'
 '<section class="subscribe"><h2>Subscribe</h2><p>Subscribe for research notes, game and music updates, and new posts from the Hive.</p></section>')
write('/blog/',h+HEADER+f'<main>{body}</main>'+FOOT+'</body></html>');manifest.append(('/blog/',title))
# redirect stubs (GitHub Pages has no _redirects)
RED={'/architecture-2/':'/technology-stack-draft/','/architecture/':'/technology-stack-draft/','/games/':'/interactive/','/apps/':'/apps-1/',
 '/home/':'/','/papers/':'/research/','/blog/f/':'/blog/','/newz/':NEWZ,'/hive-buzz/':NEWZ,
 '/m/login/':'/','/m/create/':'/','/m/create-account/':'/','/m/reset/':'/','/m/account/':'/'}
for src,dst in RED.items():
  can=dst if dst.startswith('http') else LIVE+dst
  write(src,f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Redirecting…</title><meta name="robots" content="noindex"><link rel="canonical" href="{can}"><meta http-equiv="refresh" content="0; url={dst}"><script>location.replace("{dst}"+location.hash)</script></head><body><p>This page has moved to <a href="{dst}">{can}</a>.</p></body></html>')
# 404
open(OUT+'/404.html','w').write(('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Codex Hive Labs</title><meta name="robots" content="noindex">'+GA+'<link rel="icon" href="/assets/logo-header.png"><link rel="stylesheet" href="/style.css?v=20261119"></head><body>'+HEADER+'<main><section><h1>Page not found</h1><p>That page isn\'t on codex-hive.com. <a href="/">Back to Codex Hive Labs</a></p></section></main>'+FOOT+'</body></html>').replace('</body>',BANNER+'</body>',1))
open(OUT+'/CNAME','w').write('codex-hive.com\n');open(OUT+'/.nojekyll','w').write('')
open(OUT+'/robots.txt','w').write('User-agent: *\nAllow: /\nSitemap: https://codex-hive.com/sitemap.xml\n')
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{LIVE}{up.quote(p)}</loc></url>' for p,_ in sorted(manifest))+'</urlset>\n')
json.dump(sorted(manifest),open(ROOT+'/pages.json','w'),indent=1,ensure_ascii=False)
# prune assets no longer referenced
refs=set()
for dp,_,fs in os.walk(OUT):
  for f in fs:
    if f.endswith(('.html','.css')): refs|=set(re.findall(r'/assets/([^"\'\s)?#]+)',open(os.path.join(dp,f),errors='ignore').read()))
pruned=[]
for dp,_,fs in os.walk(OUT+'/assets'):
  for f in fs:
    rel=os.path.relpath(os.path.join(dp,f),OUT+'/assets')
    if rel.startswith('hero/codex-hive-logo-bt-'): continue   # hero final (Nov 19): keep bt-* sizes
    if up.unquote(rel) not in refs and rel not in refs: os.remove(os.path.join(dp,f));pruned.append(rel)
json.dump(sorted(pruned),open(ROOT+'/tools/pruned-assets.json','w'),indent=1)
assert all(_OV_HITS.values()),('text override not applied',_OV_HITS)
print(len(manifest),'pages;',len(RED),'redirect stubs;',len(pruned),'unreferenced assets pruned')
