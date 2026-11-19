#!/usr/bin/env python3
"""Fresh public crawl of codex-hive.com (read-only). One GET per URL, no redirect following.
Seeds: home, nav/menus/footer links, sitemap.xml + child sitemaps; BFS over same-host links."""
import re,json,sys,os,urllib.parse as up,requests
from bs4 import BeautifulSoup
OUT=sys.argv[1];os.makedirs(OUT+'/html',exist_ok=True)
B='https://codex-hive.com';S=requests.Session()
S.headers['User-Agent']='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
SKIP=re.compile(r'\.(pdf|png|jpe?g|gif|webp|svg|mp3|mp4|zip|xml|ico|css|js|webmanifest)$',re.I)
def norm(u):
  u=up.urldefrag(u)[0].split('?')[0]
  p=up.urlparse(u)
  if p.netloc not in('codex-hive.com','www.codex-hive.com'): return None
  path=p.path.rstrip('/') or '/'
  return B+(path if path=='/' else up.quote(up.unquote(path),safe='/%'))
res={};seen=set();q=[B+'/'];src={B+'/':'seed:home'}
sm=[B+'/sitemap.xml'];locs=[]
while sm:
  u=sm.pop(0);r=S.get(u,timeout=30);x=re.findall(r'<loc>([^<]+)</loc>',r.text)
  for l in x:
    if l.endswith('.xml'): sm.append(l)
    else: locs.append(l)
for l in locs:
  n=norm(l)
  if n and n not in src: src[n]='sitemap';q.append(n)
nav=set();footer=set()
while q:
  u=q.pop(0)
  if u in seen: continue
  seen.add(u)
  if '/m/' in u or SKIP.search(u): res[u]={'status':'skipped (member/asset)','from':src.get(u)};continue
  r=S.get(u,timeout=30,allow_redirects=False)
  loc=r.headers.get('location','')
  res[u]={'status':r.status_code,'location':loc,'from':src.get(u)}
  if r.status_code!=200: continue
  slug=up.unquote(up.urlparse(u).path.strip('/')).replace('/','_') or 'home'
  slug=up.urlparse(u).path.strip('/').replace('/','_') or 'home'
  open(f'{OUT}/html/{slug}.html','w').write(r.text);res[u]['file']=slug+'.html'
  sp=BeautifulSoup(r.text,'html.parser')
  res[u]['title']=sp.title.get_text(strip=True) if sp.title else ''
  for a in sp.find_all('a',href=True):
    n=norm(up.urljoin(u,a['href']))
    if u==B+'/':
      if a.find_parent(attrs={'data-ux':'Nav'}) or a.find_parent(attrs={'data-ux':re.compile('NavigationDrawer|NavMenu')}): nav.add(a['href'])
      if a.find_parent(attrs={'data-aid':re.compile('FOOTER')}) or a.find_parent('footer'): footer.add(a['href'])
    if n and n not in seen and n not in q: src.setdefault(n,u);q.append(n)
json.dump({'pages':res,'sitemap_locs':locs,'nav_hrefs':sorted(nav),'footer_hrefs':sorted(footer)},open(OUT+'/crawl.json','w'),indent=1,ensure_ascii=False)
for u,v in sorted(res.items()): print(v['status'],u,v.get('location',''),'<-',v.get('from'))
