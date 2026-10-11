import numpy as np, cv2, sys
from PIL import Image
S=sys.argv[1]; OUT='branding'
def unmatte(rgb, alpha, bg):
    a=alpha[...,None].astype(np.float32)/255.0
    return np.clip((rgb.astype(np.float32)-(1-a)*bg)/np.maximum(a,1e-3),0,255).astype(np.uint8)

up=cv2.cvtColor(cv2.imread(f'{S}/up_mark.png'),cv2.COLOR_BGR2RGB).astype(np.int32)
bg=np.median(np.concatenate([up[0],up[-1],up[:,0],up[:,-1]]),axis=0)
dist=np.abs(up-bg).sum(2)
tol,soft=38,70
near=(dist<soft).astype(np.uint8)
n,lab=cv2.connectedComponents(near,connectivity=4)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
# enclosed areas that are background showing through (leg gap, space between wheels)
GAPS={3,47}
assert lab.max()>=47
bgmask=np.isin(lab,list(border|GAPS))
alpha=np.full(dist.shape,255,np.float32)
alpha[bgmask]=np.clip((dist[bgmask]-tol)/(soft-tol),0,1)*255
alpha=cv2.GaussianBlur(alpha,(3,3),0).astype(np.uint8)
rgb=unmatte(up,alpha,bg)
def save(r,a,path):
    im=Image.fromarray(np.dstack([r,a]),'RGBA'); im=im.crop(im.getbbox()); im.save(path); return im
print('full',save(rgb,alpha,f'{OUT}/zj_mark_full.png').size)
# icon version: rider + scooter + box only (no speed lines)
op=(alpha>128).astype(np.uint8)
n2,lab2,st,_=cv2.connectedComponentsWithStats(op,connectivity=8)
big=np.argsort(-st[1:,cv2.CC_STAT_AREA])[:3]+1          # scooter/rider, box, helmet
keep=cv2.dilate(np.isin(lab2,big).astype(np.uint8),np.ones((9,9),np.uint8))
print('icon',save(rgb,(alpha*keep).astype(np.uint8),f'{OUT}/zj_mark_icon.png').size)

# tagline: drop the speck from the letter above (anything in the top 25% that isn't text)
tag=np.array(Image.open(f'{OUT}/zj_tag.png'))
a=(tag[:,:,3]>60).astype(np.uint8)
n3,l3,st3,_=cv2.connectedComponentsWithStats(a,connectivity=8)
h=tag.shape[0]
for i in range(1,n3):
    x,y,w,hh,ar=st3[i]
    if y+hh < h*0.30: tag[l3==i,3]=0
Image.fromarray(tag,'RGBA').crop(Image.fromarray(tag,'RGBA').getbbox()).save(f'{OUT}/zj_tag.png')

# white-text wordmark for dark backgrounds: navy 'Zenji' -> white, orange/blue accents kept
w=np.array(Image.open(f'{OUT}/zj_word.png')).astype(np.int32)
r,g,b=w[:,:,0],w[:,:,1],w[:,:,2]
lum=(r+g+b)/3
navy=(b>r+25)&(lum<95)          # the dark navy letters (not the bright blue speed dash)
ww=w.copy(); ww[navy,0]=255; ww[navy,1]=255; ww[navy,2]=255
Image.fromarray(ww.astype(np.uint8),'RGBA').save(f'{OUT}/zj_word_white.png')
t=np.array(Image.open(f'{OUT}/zj_tag.png')).astype(np.int32); t[:,:,:3]=np.maximum(t[:,:,:3],200)
Image.fromarray(t.astype(np.uint8),'RGBA').save(f'{OUT}/zj_tag_light.png')
print('done')
