# Render live blog pages (body is client-side on GoDaddy) and save the DOM. Read-only.
import sys,re,os
from playwright.sync_api import sync_playwright
urls=[l.strip() for l in open(sys.argv[1]) if l.strip()]
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--headless=new','--no-sandbox']); pg=b.new_page(viewport={'width':1440,'height':1000})
  for u in urls:
    pg.goto(u,wait_until='load',timeout=60000); pg.wait_for_timeout(4000)
    f=re.sub(r'https://codex-hive.com/?','',u).replace('/','_') or 'home'
    open('rendered/'+f+'.html','w').write(pg.content()); print('ok',u)
  b.close()
