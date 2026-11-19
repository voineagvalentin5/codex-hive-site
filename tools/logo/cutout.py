#!/usr/bin/env python3
"""Transparent cutout of Valentin's official metallic logo reference (no redraw).
Key: background plate estimated by inpainting the object area (smooth vignette + texture),
alpha = solid object mask (bg-difference > 45, specks removed, holes kept) + soft AA ramp at the
boundary (difference 12..60), then edge decontamination C=(I-(1-a)B)/a."""
import cv2,numpy as np,os,sys
from PIL import Image
SRC='/workspace/branding/codex-hive-logo-official-metallic-ref.png'
OUT=os.path.dirname(os.path.abspath(__file__))
I=cv2.imread(SRC,cv2.IMREAD_COLOR).astype(np.float32)          # BGR
H,W=I.shape[:2]
# 1) rough object mask -> background plate
med=cv2.medianBlur(I.astype(np.uint8),5).astype(np.float32)
glob_bg=np.median(med.reshape(-1,3),0)
rough=(np.abs(med-glob_bg).max(2)>28).astype(np.uint8)
rough=cv2.dilate(rough,np.ones((25,25),np.uint8))
small=cv2.resize(I.astype(np.uint8),(W//4,H//4),interpolation=cv2.INTER_AREA)
msk=cv2.resize(rough,(W//4,H//4),interpolation=cv2.INTER_NEAREST)
plate=cv2.inpaint(small,msk,15,cv2.INPAINT_TELEA)
plate=cv2.GaussianBlur(plate,(0,0),6)
B=cv2.resize(plate,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)
# 2) difference from background (max over channels, signed: objects are brighter than bg; shadows are darker -> ignored)
D=(I-B).max(2)
Dm=cv2.medianBlur(np.clip(D,0,255).astype(np.uint8),3).astype(np.float32)
core=(Dm>45).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(core,8)
keep=np.zeros(n,bool);keep[1:]=st[1:,cv2.CC_STAT_AREA]>=150   # drop texture specks
core=keep[lab].astype(np.uint8)
core=cv2.morphologyEx(core,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
inner=cv2.erode(core,np.ones((3,3),np.uint8))
band=cv2.dilate(core,np.ones((5,5),np.uint8))
ramp=np.clip((D-12)/(60-12),0,1)
A=np.where(inner>0,1.0,np.where(band>0,np.maximum(ramp,core*0.0+ramp),0.0))
A=np.where(core>0,np.maximum(A,np.clip((D-12)/(45-12),0,1)),A)
A[A<0.04]=0
n,lab,st,_=cv2.connectedComponentsWithStats((A>0).astype(np.uint8),8)   # final speck sweep
ok=np.zeros(n,bool);ok[1:]=st[1:,cv2.CC_STAT_AREA]>=150;A=np.where(ok[lab],A,0.0)
# 3) decontaminate edges
a=A[...,None]
F=np.where(a>0,(I-(1-a)*B)/np.maximum(a,1e-3),0)
F=np.clip(F,0,255)
rgba=np.dstack([F[...,2],F[...,1],F[...,0],A*255]).round().astype(np.uint8)
ys,xs=np.where(A>0);pad=6
y0,y1,x0,x1=max(ys.min()-pad,0),min(ys.max()+pad+1,H),max(xs.min()-pad,0),min(xs.max()+pad+1,W)
img=Image.fromarray(rgba[y0:y1,x0:x1],'RGBA')
img.save(OUT+'/codex-hive-logo-metallic-cutout.png',optimize=True)
img.save(OUT+'/codex-hive-logo-metallic-cutout.webp',lossless=True,quality=100,method=6)
print('crop',(x0,y0,x1,y1),'size',img.size)
# test composites
for name,col in (('black',(0,0,0)),('gray',(128,128,128)),('hero',(5,7,11))):
  bg=Image.new('RGBA',img.size,col+(255,));bg.alpha_composite(img);bg.convert('RGB').save(OUT+f'/test-on-{name}.png')
