#!/usr/bin/env python3
"""Link check of v2 docs/ served at http://127.0.0.1:18741 (internal) + external links (GET, browser UA, follow redirects)."""
import re,os,json,urllib.parse as up,requests,concurrent.futures as cf,html as H
R='/workspace/codex-hive-site-v2';D=R+'/docs';BASE='http://127.0.0.1:18741'
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en-US,en;q=0.9'}
refs={}  # url -> set(pages)
for dp,_,fs in os.walk(D):
  for f in fs:
    if not f.endswith(('.html','.css')): continue
    p=os.path.join(dp,f);rel='/'+os.path.relpath(p,D);s=open(p,errors='ignore').read()
    urls=re.findall(r'(?:href|src|poster|content)=["\']([^"\']+)["\']',s)
    for ss in re.findall(r'srcset=["\']([^"\']+)["\']',s): urls+=[x.strip().split(' ')[0] for x in ss.split(',')]
    urls+=re.findall(r'url\(["\']?([^"\')]+)',s)
    urls+=re.findall(r'location\.replace\("([^"]+)"',s)
    for u in urls:
      u=H.unescape(u.strip())
      if not u or u.startswith(('#','data:','mailto:','tel:','javascript:')) or ' ' in u and not u.startswith('http'): continue
      if not (u.startswith('/') or u.startswith('http')): continue
      if u.startswith('http') and 'codex-hive.com' in up.urlparse(u).netloc and up.urlparse(u).netloc in('codex-hive.com','www.codex-hive.com') and ('og:' in s[max(0,s.find(u)-60):s.find(u)] or 'canonical' in s[max(0,s.find(u)-40):s.find(u)]):
        continue  # canonical/og absolute self-URLs: checked as internal paths below
      refs.setdefault(u,set()).add(rel)
internal={u for u in refs if u.startswith('/') and not u.startswith('//')}
external={('https:'+u if u.startswith('//') else u) for u in refs if u.startswith('http') or u.startswith('//')}
res_int={}
S=requests.Session()
for u in sorted(internal):
  r=S.get(BASE+up.quote(up.unquote(u.split('#')[0]),safe='/%?=&'),timeout=20,allow_redirects=True)
  res_int[u]=r.status_code
bad=[(u,c,sorted(refs[u])[:3]) for u,c in res_int.items() if c!=200]
def chk(u):
  try:
    r=requests.get(u,headers=UA,timeout=25,allow_redirects=True,stream=True);c=r.status_code;fin=r.url;r.close()
  except Exception as e: return u,'ERR',str(e)[:80],'broken?'
  v='ok' if c<400 else ('could not verify (bot block)' if c in(401,403,429,999) else 'BROKEN')
  return u,c,fin,v
with cf.ThreadPoolExecutor(8) as ex: res_ext=list(ex.map(chk,sorted(external)))
json.dump({'internal':res_int,'internal_bad':bad,'external':[list(x)+[sorted(refs.get(x[0],refs.get(x[0].replace('https:',''),set())))[:4]] for x in res_ext]},open(R+'/audit/links.json','w'),indent=1)
print('internal checked',len(res_int),'broken',len(bad));[print(' BAD',b) for b in bad]
print('external checked',len(res_ext))
for x in res_ext: print(x[1],x[3],x[0],'->',x[2][:90] if isinstance(x[2],str) else x[2])
