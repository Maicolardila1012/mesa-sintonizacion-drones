"""Renderiza el ensamble CAD (STL) en dos vistas. Uso: python3 render_cad.py [carpeta_stl] [salida.png]
Antes de correrlo, descomprima cad/stl/aro_exterior.zip y cad/stl/aro_interior.zip en la misma carpeta.
Si se agregan los STL de terceros (chumaceras, rodamientos SKF, brazo F450) a la carpeta, también se dibujan."""
import sys, os, struct, numpy as np
def load(p):
    with open(p,'rb') as f: data=f.read()
    if data[:5]==b'solid' and b'facet' in data[:400]:
        v=[]; 
        for line in data.decode('latin1').splitlines():
            t=line.split()
            if t and t[0]=='vertex': v.append([float(x) for x in t[1:4]])
        return np.array(v).reshape(-1,3,3)
    n=struct.unpack('<I',data[80:84])[0]
    a=np.frombuffer(data,dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]),count=n,offset=84)
    return a['v'].reshape(-1,3,3).astype(float)

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
AQUI=os.path.dirname(os.path.abspath(__file__))
d=sys.argv[1] if len(sys.argv)>1 else os.path.join(AQUI,"..","cad","stl")
out=sys.argv[2] if len(sys.argv)>2 else os.path.join(AQUI,"..","imagenes","resultados","fig06_modelo_cad.png")
rng=np.random.default_rng(0)
COL={'Cuerpo 17.stl':('#4d4d4d','Soporte en U'),
     'SKF BALL BEARING 6004 20x42x12.STEP (1).stl':('#1757ac','Aro exterior + rodamientos 6004'),
     'aro_exterior.stl':('#1757ac','Aro exterior'),
     'aro_interior.stl':('#257de0','Aro interior'),
     'Cuerpo 61 (1).stl':('#257de0','Aro interior'),
     'Cuerpo 15 (2).stl':('#8a8a8a','Base (tubo cuadrado 1")'),
     'F450 Arm.stp (Importado).stl':('#f2a600','Dron de referencia (F450)'),
     'Cuerpo 36.stl':('#c0392b','Guía del soporte del dron'),
     'chumacera de 20 mm.igs.stl':('#2e8b57','Chumaceras y rodamientos'),
     'chumacera de 20 mm.igs (1).stl':('#2e8b57',None),'SKF_FY 1_ TF.stp.stl':('#2e8b57',None),
     'SKF BALL BEARING 6004 20x42x12.STEP.stl':('#2e8b57',None)}
parts=[]
for fn in sorted(os.listdir(d)):
    t=load(os.path.join(d,fn))
    lim = 600000 if ('STEP (1)' in fn or 'aro_' in fn) else (120000 if 'F450' in fn else 40000)
    if len(t)>lim: t=t[rng.choice(len(t),lim,replace=False)]
    c,l=COL.get(fn,('#b0b0b0',None)); parts.append((fn,t,c,l))
allv=np.concatenate([t.reshape(-1,3) for _,t,_,_ in parts]); mn,mx=allv.min(0),allv.max(0)
cen=(mn+mx)/2; r=(mx-mn).max()/2*0.78
L=np.array([0.3,-0.6,0.75]); L/=np.linalg.norm(L)
fig=plt.figure(figsize=(12,6.6))
for k,(el,az,tt) in enumerate([(18,-55,'(a) Vista isométrica'),(0,-90,'(b) Vista frontal')]):
    ax=fig.add_subplot(1,2,k+1,projection='3d')
    for fn,t,c,l in parts:
        n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12
        sh=0.5+0.5*np.abs(n@L); base=np.array(matplotlib.colors.to_rgb(c))
        ax.add_collection3d(Poly3DCollection(t,facecolors=np.clip(base*sh[:,None],0,1),edgecolors='none',linewidths=0))
        if l and k==0: ax.plot([],[],color=c,lw=4,label=l)
    ax.set_xlim(cen[0]-r,cen[0]+r); ax.set_ylim(cen[1]-r,cen[1]+r); ax.set_zlim(cen[2]-r,cen[2]+r)
    ax.set_box_aspect((1,1,1)); ax.view_init(elev=el,azim=az); ax.set_axis_off()
    ax.text2D(0.02,0.97,tt,transform=ax.transAxes,fontsize=11,color='#191919')
fig.suptitle('Modelo CAD de la mesa (ensamble del autor, exportado en STL)',x=0.02,ha='left',fontsize=13,fontweight='bold',color='#191919')
fig.text(0.02,0.93,'Pose de modelado con los dos aros en el mismo plano; en uso, el aro exterior queda horizontal y el interior vertical.',fontsize=9,color='#666666')
h,l=fig.axes[0].get_legend_handles_labels()
fig.legend(h,l,loc='lower center',ncol=4,frameon=False,fontsize=9.5,bbox_to_anchor=(0.5,-0.02))
fig.subplots_adjust(left=0,right=1,bottom=0.08,top=0.92,wspace=0)
fig.savefig(out,dpi=150,bbox_inches='tight',facecolor='white')
