# Headless Chrome test of the cookie banner + Consent Mode v2 (local server only).
import json,re
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:18741/'
def consent(pg): return pg.evaluate("()=>dataLayer.filter(a=>a[0]==='consent').map(a=>[a[1],JSON.stringify(a[2])])")
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--headless=new','--no-sandbox'])
  ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);pg=ctx.new_page()
  hits=[];pg.on('request',lambda r:hits.append(r.url) if '/g/collect' in r.url else None)
  pg.goto(U,wait_until='load');pg.wait_for_timeout(3000)
  print('1 banner visible on first visit:',pg.is_visible('#ch-cookie'),'| role:',pg.get_attribute('#ch-cookie','role'),'| aria-label:',pg.get_attribute('#ch-cookie','aria-label'))
  print('  consent:',consent(pg))
  print('  gcs before accept:',sorted(set(re.findall(r'gcs=([^&]+)',' '.join(hits)))))
  pg.screenshot(path='/workspace/codex-hive-site-v2/screenshots/home-v2-390-cookie-banner.png')
  hits.clear();pg.click('#ch-cookie .ch-accept');pg.wait_for_timeout(2500)
  print('2 after Accept visible:',pg.is_visible('#ch-cookie'),'| stored:',pg.evaluate("localStorage.getItem('ch_cookie_consent')"))
  print('  consent:',consent(pg))
  pg.reload(wait_until='load');hits.clear();pg.wait_for_timeout(3000)
  print('3 after reload visible:',pg.is_visible('#ch-cookie'),'| consent:',consent(pg))
  print('  gcs after reload:',sorted(set(re.findall(r'gcs=([^&]+)',' '.join(hits)))))
  pg.goto(U+'contact/',wait_until='load');pg.wait_for_timeout(1000);print('4 other page visible:',pg.is_visible('#ch-cookie'))
  ctx2=b.new_context();p2=ctx2.new_page();p2.goto(U+'nope-404-test/');p2.wait_for_timeout(500)
  ctx.close();ctx2.close();b.close()
