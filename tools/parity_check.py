#!/usr/bin/env python3
"""Page-by-page parity: fresh live snapshot vs v2 docs/. Text, images, embeds (iframes and media inside srcdoc), CTA links."""
import re,os,json,difflib,urllib.parse as up
from bs4 import BeautifulSoup
R='/workspace/codex-hive-site-v2';L=R+'/live-snapshot-nov19f';D=R+'/docs'
crawl=json.load(open(L+'/crawl.json'))
NEWZ='https://newz.codex-hive.com/'
def norm_href(h):
  h=h.strip()
  if 'hive-buzz-newz.netlify.app' in h: return NEWZ
  if h.startswith('https://codex-hive.com'): h=h[22:] or '/'
  if h.startswith('/') and not h.startswith('//'):
    h=h.split('?')[0].split('#')[0].rstrip('/') or '/'
  if 'wsimg.com' in h: return 'ASSET:'+up.unquote(re.sub(r'/:/.*','',h).rsplit('/',1)[-1])
  return h
def v2href(h):
  h=h.strip()
  if h.startswith('/assets/'): return 'ASSET:'+re.sub(r'^[0-9a-f]{8}_','',up.unquote(h.rsplit('/',1)[-1]))
  if h.startswith('/') : return h.split('#')[0].rstrip('/') or '/'
  return h
def ext_links_in(html,conv):
  out=set()
  for m in re.finditer(r'(?:href|src)=["\']([^"\']+)["\']',html):
    u=conv(m.group(1))
    if u and not u.startswith(('data:','#','javascript')) : out.add(u)
  return out
def words(t): return re.sub(r'\s+',' ',t).strip().split()
rows=[]
for u,v in sorted(crawl['pages'].items()):
  if v.get('status')!=200: continue
  path=up.urlparse(u).path.rstrip('/') or '/'
  vpath=D+up.unquote(path)+('/index.html' if path!='/' else 'index.html')
  r={'live':path,'v2':os.path.exists(vpath)}
  if not r['v2']: rows.append(r);continue
  blog=path.startswith('/blog/f/')
  if blog:
    sp=BeautifulSoup(open(L+'/rendered/'+path.strip('/').replace('/','_')+'.html').read(),'html.parser');m=sp.find(attrs={'data-ux':'BlogMain'})
    for t in m.find_all(['svg']): t.decompose()
    ltxt=m.get_text(' ',strip=True).replace('All Posts','').replace('Share this post:','');lhtml=str(m);secs=[m]
  else:
    sp=BeautifulSoup(open(L+'/html/'+v['file']).read(),'html.parser')
    secs=[s for s in sp.select('[data-ux=Section],[data-ux=SectionBanner]') if not s.find_parent(attrs={'data-ux':re.compile('^Section')}) and not s.find(attrs={'data-aid':re.compile('FOOTER')})]
    for s in secs:
      for t in s(['script','style','noscript']): t.decompose()
    ltxt=' '.join(s.get_text(' ',strip=True) for s in secs);lhtml=''.join(str(s) for s in secs)
  vs=BeautifulSoup(open(vpath).read(),'html.parser');main=vs.find('main')
  vt=main.get_text(' ',strip=True)
  # embeds: concatenate v2 embed files referenced
  vemb=''.join(open(D+i['src']).read() for i in main.find_all('iframe') if i.get('src','').startswith('/embeds/'))
  inline_div=main.find(class_='divisions')
  # live embeds
  lif=[i for s in secs for i in s.find_all('iframe')]
  lemb=''.join(i.get('srcdoc','') for i in lif)
  ltext_emb=BeautifulSoup(lemb,'html.parser').get_text(' ',strip=True);vtext_emb=BeautifulSoup(vemb,'html.parser').get_text(' ',strip=True)
  lw=words(ltxt);vw=words(vt)
  r['text_ratio']=round(difflib.SequenceMatcher(None,lw,vw).ratio(),3)
  r['missing_words']=[w for w in set(lw)-set(vw)][:15]
  r['embed_text_same']=words(ltext_emb)==words(vtext_emb) if lemb else None
  if path=='/' : r['embed_text_same']='inline divisions (approved embed)'
  r['iframes_live']=len(lif);r['iframes_v2']=len(main.find_all('iframe'))+(1 if inline_div else 0)
  # images
  limgs=set(norm_href(i.get('data-srclazy') or i.get('src') or '') for s in secs for i in s.find_all('img') if 'wsimg' in (i.get('data-srclazy') or i.get('src') or ''))
  limgs|=set(x for x in ext_links_in(lemb,norm_href) if x.startswith('ASSET:'))
  vimgs=set(v2href(i.get('src','')) for i in main.find_all('img'))|set(x for x in ext_links_in(vemb+str(main),v2href) if x.startswith('ASSET:'))
  r['images_live']=len(limgs);r['images_missing']=sorted(x for x in limgs-vimgs if not any(y.startswith(x) for y in vimgs))
  # links/CTAs (section anchors + embed hrefs/srcs)
  ll=set(norm_href(a['href']) for s in secs for a in s.find_all('a',href=True))|set(norm_href(x) for x in ext_links_in(lemb,lambda x:x))
  ll={x for x in ll if x and x!='#' and not x.startswith(('ASSET:','data:'))}
  vl=set(v2href(a['href']) for a in main.find_all('a',href=True))|set(v2href(x) for x in ext_links_in(vemb,lambda x:x))
  if inline_div: vl|=set(v2href(a['href']) for a in inline_div.find_all('a',href=True))
  vl={x.rstrip('/') if x.startswith('/') else x for x in vl}
  r['links_live']=len(ll);r['links_missing']=sorted(x for x in ll if x not in vl and x.rstrip('/') not in vl)
  rows.append(r)
json.dump(rows,open(R+'/audit/parity.json','w'),indent=1,ensure_ascii=False)
for r in rows: print(json.dumps(r,ensure_ascii=False)[:600])
