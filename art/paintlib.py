import numpy as np, cv2, math, random
from PIL import Image, ImageDraw, ImageFilter
S=100  # px per square
def fbm(h,w,scale,oct=5,seed=0,pers=0.5):
    rng=np.random.default_rng(seed); out=np.zeros((h,w),np.float32); amp=1; tot=0; s=scale
    for o in range(oct):
        gh,gw=max(2,int(h/s)+3),max(2,int(w/s)+3)
        g=rng.random((gh,gw)).astype(np.float32)
        up=cv2.resize(g,(int(gw*s),int(gh*s)),interpolation=cv2.INTER_CUBIC)[:h,:w]
        out+=up*amp; tot+=amp; amp*=pers; s/=2
        if s<2: break
    return (out/tot).astype(np.float32)
def lerp(a,b,t): return a+(b-a)*t[...,None]
def col(c): return np.array(c,np.float32)
def mask_poly(h,w,polys,blur=0):
    m=Image.new('L',(w,h),0); d=ImageDraw.Draw(m)
    for p in polys: d.polygon([(x*S,y*S) for x,y in p],fill=255)
    a=np.asarray(m,np.float32)/255
    return cv2.GaussianBlur(a,(0,0),blur) if blur else a
def mask_line(h,w,pts,width,blur=0):
    m=Image.new('L',(w,h),0); d=ImageDraw.Draw(m); P=[(x*S,y*S) for x,y in pts]
    d.line(P,fill=255,width=int(width*S),joint='curve')
    for x,y in P: r=width*S/2; d.ellipse([x-r,y-r,x+r,y+r],fill=255)
    a=np.asarray(m,np.float32)/255
    return cv2.GaussianBlur(a,(0,0),blur) if blur else a
def ragged(pts,amp,step=0.6,seed=1):
    """densify polyline and jitter perpendicular"""
    rng=random.Random(seed); out=[]
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        L=math.hypot(x1-x0,y1-y0); n=max(1,int(L/step)); nx,ny=-(y1-y0)/L,(x1-x0)/L
        for i in range(n):
            t=i/n; j=rng.uniform(-amp,amp); out.append((x0+(x1-x0)*t+nx*j,y0+(y1-y0)*t+ny*j))
    out.append(pts[-1]); return out
def shade_from_height(hgt,strength=1.0,light=(-1,-1)):
    hgt=np.ascontiguousarray(hgt,np.float32)
    gx=cv2.Sobel(hgt,cv2.CV_32F,1,0,ksize=5); gy=cv2.Sobel(hgt,cv2.CV_32F,0,1,ksize=5)
    lx,ly=light; n=math.hypot(lx,ly); s=-(gx*lx+gy*ly)/n
    return np.clip(s*strength,-1,1)
def pine(d,sh,x,y,r,rng,tone=0):
    # shadow
    sh.ellipse([x-r*0.9+r*0.45,y-r*0.9+r*0.5,x+r*0.9+r*0.45,y+r*0.9+r*0.5],fill=150)
    base=[(22,34,28),(28,44,34),(36,55,40),(48,66,46)]
    rot=rng.uniform(0,6.28)
    for li,(k,c) in enumerate(zip((1,0.78,0.55,0.3),base)):
        n=rng.randint(9,13); pts=[]
        for i in range(n*2):
            a=rot+li*0.4+i*math.pi/n; rr=r*k*(1 if i%2==0 else 0.55)*rng.uniform(0.85,1.08)
            pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
        cc=tuple(int(v*(1+tone)+rng.randint(-4,4)) for v in c)
        d.polygon(pts,fill=cc+(255,))
def dead_tree(d,sh,x,y,r,rng):
    sh.ellipse([x-r*0.5+r*0.4,y-r*0.5+r*0.4,x+r*0.5+r*0.4,y+r*0.5+r*0.4],fill=110)
    for i in range(rng.randint(5,8)):
        a=rng.uniform(0,6.28); L=r*rng.uniform(0.6,1.0)
        d.line([(x,y),(x+math.cos(a)*L,y+math.sin(a)*L)],fill=(38,32,28,255),width=max(2,int(r*0.08)))
    d.ellipse([x-r*0.14,y-r*0.14,x+r*0.14,y+r*0.14],fill=(46,38,32,255))
def stone_blocks(w,h,bw,bh,seed=0,base=(70,68,66),var=14,mortar=(28,26,26)):
    rng=np.random.default_rng(seed); im=Image.new('RGB',(w,h),mortar); d=ImageDraw.Draw(im)
    y=0;row=0
    while y<h:
        x=-(bw//2 if row%2 else 0)
        while x<w:
            v=rng.integers(-var,var); c=tuple(int(b+v) for b in base)
            d.rectangle([x+2,y+2,x+bw-2,y+bh-2],fill=c); x+=bw
        y+=bh;row+=1
    a=np.asarray(im,np.float32); a*= (0.85+0.3*fbm(h,w,24,4,seed+3))[...,None]
    return a
def composite(base,layer,alpha):
    return base*(1-alpha[...,None])+layer*alpha[...,None]
def finish(img,seed=9,vign=0.45):
    h,w,_=img.shape; yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    r=np.sqrt(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2); v=1-vign*np.clip(r-0.55,0,1)
    g=(fbm(h,w,3,2,seed)-0.5)*14
    out=img*v[...,None]+g[...,None]
    return np.clip(out,0,255).astype(np.uint8)

# ---------- v2 painterly helpers ----------
from scipy.spatial import cKDTree
def smooth(e0,e1,x): t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
def pine_sprite(R,seed,hue=(30,46,34),tiers=4):
    rng=np.random.default_rng(seed); n=2*R+8; yy,xx=np.mgrid[0:n,0:n].astype(np.float32)-n/2
    r=np.hypot(xx,yy)/R; th=np.arctan2(yy,xx)
    alpha=np.zeros((n,n),np.float32); shade=np.zeros((n,n),np.float32)
    ang_noise=cv2.resize(rng.random((1,140)).astype(np.float32),(720,1),interpolation=cv2.INTER_CUBIC)[0]
    idx=((th+np.pi)/(2*np.pi)*719).astype(int)
    for t in range(tiers):
        k=1-t*0.2; spikes=rng.integers(13,19); ph=rng.uniform(0,6.28)
        edge=k*(0.64+0.26*np.abs(np.cos(spikes*th/2+ph))**1.1+0.16*ang_noise[(idx*3+t*97)%720])
        a=smooth(edge,edge-0.06,r)
        loc=np.clip(1-r/np.maximum(edge,1e-3),0,1)
        sh=-0.55*(xx+yy)/(R*1.4)+0.25*t+0.35*loc   # lit from NW, upper tiers brighter
        shade=np.where(a>0.01, sh*a+shade*(1-a), shade); alpha=np.maximum(alpha,a)
    streak=cv2.resize(rng.random((1,240)).astype(np.float32),(1440,1),interpolation=cv2.INTER_LINEAR)[0][((th+np.pi)/(2*np.pi)*1439).astype(int)]
    needles=0.55*streak+0.45*cv2.GaussianBlur(cv2.resize(rng.random((n//3,n//3)).astype(np.float32),(n,n),interpolation=cv2.INTER_NEAREST),(0,0),0.8)
    shade=shade+0.25*(streak-0.5)*np.clip(r,0,1)
    base=np.array(hue,np.float32)
    rgb=base[None,None,:]*(0.65+0.75*np.clip(shade,-0.5,1.2)[...,None])*(0.8+0.4*needles[...,None])
    rgb+=np.array([0,6,2],np.float32)*np.clip(shade,0,1)[...,None]
    out=np.dstack([np.clip(rgb,0,255),alpha*255]).astype(np.uint8)
    return Image.fromarray(out,'RGBA')
def dome_sprite(rx,ry,seed,base=(70,70,72),rough=0.35,jag=0.25,tex_scale=5):
    rng=np.random.default_rng(seed); n=int(2*max(rx,ry)+8); yy,xx=np.mgrid[0:n,0:n].astype(np.float32)-n/2
    th=np.arctan2(yy/ry,xx/rx); rn=cv2.resize(rng.random((1,12)).astype(np.float32),(360,1),interpolation=cv2.INTER_LINEAR)[0]
    jit=1-jag/2+jag*rn[((th+np.pi)/(2*np.pi)*359).astype(int)]
    r=np.hypot(xx/rx,yy/ry)/jit; a=smooth(1.0,0.96,r)
    h=np.clip(1-r**2,0,1)**0.5
    lit=0.45+0.45*h+0.45*np.clip(-(xx/rx+yy/ry)/2.2,-1,1)*h**0.5
    tex=cv2.resize(rng.random((max(2,n//tex_scale),max(2,n//tex_scale))).astype(np.float32),(n,n),interpolation=cv2.INTER_CUBIC)
    rgb=np.array(base,np.float32)[None,None]*(lit*(1-rough/2+rough*tex))[...,None]
    return Image.fromarray(np.dstack([np.clip(rgb,0,255),a*255]).astype(np.uint8),'RGBA')
def rock_sprite(R,seed,base=(64,64,66)):
    return dome_sprite(R,R*0.82,seed,base,0.45,0.35,4)
def voronoi_stones(h,w,cell,seed,base=(72,68,64),var=16,mortar=(30,27,25),light=(-1,-1),gap=0.12,mask=None):
    rng=np.random.default_rng(seed)
    gy,gx=np.mgrid[0:h+cell:cell,0:w+cell:cell].astype(np.float32)
    pts=np.stack([gx.ravel()+rng.uniform(-0.4,0.4,gx.size)*cell,gy.ravel()+rng.uniform(-0.4,0.4,gy.size)*cell],1)
    tree=cKDTree(pts); out=np.zeros((h,w,3),np.float32)
    ys,xs=(np.nonzero(mask>0.01) if mask is not None else np.mgrid[0:h,0:w].reshape(2,-1))
    q=np.stack([xs,ys],1).astype(np.float32); d,i=tree.query(q,k=2)
    edge=(d[:,1]-d[:,0])/cell
    tone=rng.integers(-var,var+1,len(pts)).astype(np.float32)
    c=pts[i[:,0]]; v=(q-c)/cell; L=np.array(light,np.float32)/math.hypot(*light)
    sh=-(v@L)*0.55
    st=np.clip(edge/gap,0,1); bevel=np.clip(edge/(gap*3),0,1)
    col_=np.array(base,np.float32)[None]+tone[i[:,0],None]
    rgb=col_*(0.85+sh[:,None]*(1-bevel[:,None]*0.6)+0.15*bevel[:,None])
    rgb=rgb*st[:,None]+np.array(mortar,np.float32)[None]*(1-st[:,None])
    out[ys,xs]=rgb
    n=fbm(h,w,8,3,seed+5); out*=(0.85+0.3*n)[...,None]
    return out
def ground_strokes(img,mask,seed,n=40000,length=(6,16),cols=((38,48,34),(58,62,44),(26,32,26)),width=2):
    rng=random.Random(seed); h,w,_=img.shape; im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    for _ in range(n):
        x=rng.randrange(w); y=rng.randrange(h)
        if mask[y,x]<0.5: continue
        L=rng.uniform(*length); a=rng.uniform(-2.2,-0.9)
        c=rng.choice(cols); c=tuple(int(v+rng.randint(-6,6)) for v in c)
        d.line([(x,y),(x+math.cos(a)*L,y+math.sin(a)*L)],fill=c,width=width)
    return np.asarray(im,np.float32)
def paste_sprite(im,sp,x,y,shadow=True,off=(0.35,0.45),sa=150,blur=10):
    w,h=sp.size
    if shadow:
        a=sp.split()[3].point(lambda v:sa if v>40 else 0).filter(ImageFilter.GaussianBlur(blur))
        s=Image.new('RGBA',sp.size,(0,0,0,0)); s.putalpha(a)
        im.alpha_composite(s,(int(x-w/2+w*off[0]*0.5),int(y-h/2+h*off[1]*0.5)))
    im.alpha_composite(sp,(int(x-w/2),int(y-h/2)))
def bevel_box(im,X0,Y0,X1,Y1,top,rim=None,depth=26,seed=0):
    """square tower/wall block seen from above, with battlement rim & cast shadow"""
    w,h=int(X1-X0),int(Y1-Y0)
    sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle([X0+depth*1.6,Y0+depth*2,X1+depth*1.6,Y1+depth*2],fill=(0,0,0,170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(depth)))
    t=Image.fromarray(np.clip(top,0,255).astype(np.uint8)).convert('RGBA'); im.alpha_composite(t,(int(X0),int(Y0)))
    d=ImageDraw.Draw(im)
    R=rim or 22
    # walls of battlement ring: light NW, dark SE
    d.rectangle([X0,Y0,X1,Y0+R],fill=(92,90,88,255)); d.rectangle([X0,Y0,X0+R,Y1],fill=(86,84,82,255))
    d.rectangle([X0,Y1-R,X1,Y1],fill=(48,46,46,255)); d.rectangle([X1-R,Y0,X1,Y1],fill=(54,52,52,255))
    step=R*2.2;k=0
    while X0+k*step<X1-R:
        xx=X0+R+k*step+R*0.3
        for yy in (Y0,Y1-R): d.rectangle([xx,yy+3,xx+R*0.9,yy+R-3],fill=(40,38,38,255))
        k+=1
    k=0
    while Y0+k*step<Y1-R:
        yy=Y0+R+k*step+R*0.3
        for xx in (X0,X1-R): d.rectangle([xx+3,yy,xx+R-3,yy+R*0.9],fill=(40,38,38,255))
        k+=1
    d.rectangle([X0+R,Y0+R,X1-R,Y0+R+6],fill=(0,0,0,60)); d.rectangle([X0+R,Y0+R,X0+R+6,Y1-R],fill=(0,0,0,60))
