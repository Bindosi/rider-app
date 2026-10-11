import cv2, numpy as np, sys
from PIL import Image
S=sys.argv[1]; OUT='branding'
def unmatte(rgb, alpha, bg):
    a=alpha[...,None].astype(np.float32)/255.0
    c=(rgb.astype(np.float32)-(1-a)*bg)/np.maximum(a,1e-3)
    return np.clip(c,0,255).astype(np.uint8)

def flood_alpha(img, tol=38, soft=70):
    """Background = near-white region connected to the image border (keeps enclosed whites)."""
    rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB).astype(np.int32)
    h,w,_=rgb.shape
    bg=np.median(np.concatenate([rgb[0],rgb[-1],rgb[:,0],rgb[:,-1]]),axis=0)
    dist=np.abs(rgb-bg).sum(2)
    near=(dist<soft).astype(np.uint8)
    n,lab=cv2.connectedComponents(near,connectivity=4)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bgmask=np.isin(lab,list(border))
    alpha=np.full((h,w),255,np.float32)
    alpha[bgmask]=np.clip((dist[bgmask]-tol)/(soft-tol),0,1)*255
    alpha=cv2.GaussianBlur(alpha,(3,3),0)
    return unmatte(rgb,alpha,bg), alpha.astype(np.uint8), bg

def white_alpha(img, tol=30, soft=110):
    rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB).astype(np.int32)
    bg=np.median(np.concatenate([rgb[0],rgb[-1],rgb[:,0],rgb[:,-1]]),axis=0)
    dist=np.abs(rgb-bg).sum(2)
    alpha=(np.clip((dist-tol)/(soft-tol),0,1)*255).astype(np.uint8)
    return unmatte(rgb,alpha,bg), alpha, bg

def save(rgb,alpha,path):
    im=Image.fromarray(np.dstack([rgb,alpha]),'RGBA'); im=im.crop(im.getbbox()); im.save(path); return im

mark=cv2.imread(f'{S}/up_mark.png')
mrgb,malpha,bg=flood_alpha(mark)
full=save(mrgb,malpha,f'{OUT}/zj_mark_full.png'); print('mark full',full.size)

# split speed lines from the scooter: connected components of the opaque mask
op=(malpha>128).astype(np.uint8)
n,lab,stats,cent=cv2.connectedComponentsWithStats(op,connectivity=8)
order=np.argsort(-stats[1:,cv2.CC_STAT_AREA])+1
main=order[0]
print('components',n-1,'largest',stats[main].tolist())
for i in order[:12]:
    x,y,w,h,a=stats[i]; print('  comp',i,'x',x,'y',y,'w',w,'h',h,'area',a)
np.save(f'{S}/mark_lab.npy',lab)

w=cv2.imread(f'{S}/up_word.png'); wrgb,walpha,_=white_alpha(w); print('word',save(wrgb,walpha,f'{OUT}/zj_word.png').size)
t=cv2.imread(f'{S}/up_tag.png'); trgb,talpha,_=white_alpha(t); print('tag',save(trgb,talpha,f'{OUT}/zj_tag.png').size)

# Z badge: white Z on a navy rounded square
z=cv2.cvtColor(cv2.imread(f'{S}/up_zbadge.png'),cv2.COLOR_BGR2RGB).astype(np.int32)
lum=z.mean(2); sat=z.max(2)-z.min(2)
zal=np.clip((lum-120)/(220-120),0,1)*np.clip((80-sat)/60,0,1)*255
# keep only inside the badge (ignore the white page around it)
navy=((z[:,:,2]>z[:,:,0]+15)&(lum<120)).astype(np.uint8)
ys,xs=np.where(navy); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
pad=int((x1-x0)*0.06)
inside=np.zeros_like(lum,bool); inside[y0+pad:y1-pad,x0+pad:x1-pad]=True
zal[~inside]=0
zw=np.zeros(z.shape,np.uint8)+255
print('Z',save(zw,zal.astype(np.uint8),f'{OUT}/zj_z_white.png').size)
