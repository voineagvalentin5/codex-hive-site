# Headless screenshots of v2 (local) vs live codex-hive.com. Read-only on live.
from playwright.sync_api import sync_playwright
OUT='/workspace/codex-hive-site-v2/screenshots/'
import sys
pages={'home':'/','apps':'/apps-1/','contact':'/contact/'}
if len(sys.argv)>1: pages={k:v for k,v in pages.items() if k in sys.argv[1:]}
src={'v2':'http://127.0.0.1:18741'}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--headless=new','--no-sandbox'])
  for w in (1440,390):
    ctx=b.new_context(viewport={'width':w,'height':900},device_scale_factor=1,is_mobile=(w==390),has_touch=(w==390))
    ctx.add_init_script("try{if(location.port==='18741')localStorage.setItem('ch_cookie_consent','denied')}catch(e){}")  # hide cookie banner for layout shots
    pg=ctx.new_page()
    for s,base in src.items():
      for n,path in pages.items():
        url=base+(path if s=='v2' else path.rstrip('/') or '/')
        pg.goto(url,wait_until='load',timeout=90000);pg.wait_for_timeout(5000)
        pg.evaluate("window.scrollTo(0,document.body.scrollHeight)");pg.wait_for_timeout(1500);pg.evaluate("window.scrollTo(0,0)");pg.wait_for_timeout(800)
        f=f'{OUT}{n}-{s}-{w}.png';pg.screenshot(path=f,full_page=True);print(f)
    ctx.close()
  b.close()
