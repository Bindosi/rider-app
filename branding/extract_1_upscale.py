import cv2, numpy as np, sys, time
from PIL import Image
S=sys.argv[1]
sheet=cv2.imread('branding/zenjijet_design_sheet.png')
sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(S+'/EDSR_x4.pb'); sr.setModel('edsr',4)
parts={'mark':(48,108,690,462),'word':(44,462,718,606),'tag':(360,600,700,650),'zbadge':(1410,779,1512,880)}
for name,(x0,y0,x1,y1) in parts.items():
    t=time.time(); up=sr.upsample(sheet[y0:y1,x0:x1]); cv2.imwrite(f'{S}/up_{name}.png',up); print(name,up.shape,round(time.time()-t,1),'s',flush=True)
