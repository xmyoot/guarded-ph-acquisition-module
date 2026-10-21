"""Drawing-derived Amphenol 031-5431-1010 visualization, NOT vendor mechanical CAD.
Major envelope/pin dimensions follow Rev E; small socket/thread details illustrative.
Explicit IndexedFaceSet meshes avoid KiCad VRML primitive rendering limitations.
"""
from pathlib import Path
import math,sexpdata as sx
R=Path(__file__).resolve().parents[1];D=R/'hardware/Soil_pH_AFE'
parts=['#VRML V2.0 utf8\n# Drawing-derived visualization; major dimensions per Rev E, details approximate.\n']
metal=(.66,.69,.73);white=(.84,.84,.79);gold=(.78,.57,.17);dark=(.055,.065,.075)
def mesh(verts,faces,color,shine=.25):
 vs=', '.join(' '.join(f'{v/2.54:.6f}' for v in p) for p in verts);fs=', '.join(' '.join(map(str,f))+ ' -1' for f in faces)
 parts.append('Shape { appearance Appearance { material Material { diffuseColor '+ ' '.join(map(str,color))+' specularColor .65 .65 .65 shininess '+str(shine)+' } } geometry IndexedFaceSet { solid FALSE convex FALSE creaseAngle .6 coord Coordinate { point [ '+vs+' ] } coordIndex [ '+fs+' ] } }\n')
def tube(center,rout,rin,length,color,axis='y',n=80):
 verts=[]
 for rad,ax in [(rout,-length/2),(rout,length/2),(rin,-length/2),(rin,length/2)]:
  for i in range(n):
   a=2*math.pi*i/n;u,v=rad*math.cos(a),rad*math.sin(a)
   q=[u,ax,v] if axis=='y' else [u,v,ax] if axis=='z' else [ax,u,v]
   verts.append([q[j]+center[j] for j in range(3)])
 faces=[]
 for i in range(n):
  j=(i+1)%n
  faces.extend([[i,j,n+j,n+i],[2*n+i,3*n+i,3*n+j,2*n+j],[i,2*n+i,2*n+j,j],[n+i,n+j,3*n+j,3*n+i]])
 if axis=='y':faces=[list(reversed(f)) for f in faces]
 mesh(verts,faces,color,.65 if color==metal else .15)
def box(c,s,col):
 verts=[[c[0]+x*s[0]/2,c[1]+y*s[1]/2,c[2]+z*s[2]/2] for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 mesh(verts,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],col)
# Profile of white insulated right-angle housing, with a rear terminal recess.
yz=[(-1.22,.76),(12.58,.76),(12.58,16.36),(-1.22,16.36),(-1.22,12.1),(1.5,12.1),(1.5,6.1),(-1.22,6.1)]
verts=[[x,y,z] for x in [-7.25,7.25] for y,z in yz];n=len(yz)
faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
mesh(verts,faces,white,.08)
# Metal shoulder and threaded panel-mount section, axis 8.18mm above board.
tube((0,13.0,8.18),6.50,.01,.85,metal)
tube((0,17.1,8.18),6.05,.01,8.9,metal)
for i in range(13):tube((0,12.9+i*.66,8.18),6.415,5.98,.24,metal)
# Outer bayonet barrel with open bore and lip; internal dielectric/contact recessed.
tube((0,27.45,8.18),4.75,4.08,11.96,metal)
tube((0,33.30,8.18),4.97,4.08,.36,metal)
tube((0,30.8,8.18),4.04,.85,.30,white)
tube((0,31.03,8.18),.82,.42,.52,gold)
tube((0,30.5,8.18),.40,.01,.10,dark)
# Opposed bayonet pins.
for sign in [-1,1]:tube((sign*4.88,29.9,8.18),1.0,.01,1.15,metal,axis='x',n=32)
# Pin tails at the actual footprint positions; visible below the PCB.
for x,y in [(0,0),(-2.54,0)]:box((x,-y,-1.2),(.5,.65,4.0),gold if x==0 else metal)
for x in [-5.08,5.08]:box((x,5.08,-1.25),(1.0,.65,4.0),metal)
model=D/'models/BNC_031-5431-1010.wrl';model.write_text(''.join(parts))
S=sx.Symbol
for p in [D/'Soil_pH_AFE.kicad_pcb',D/'Soil_pH.pretty/BNC_031-5431-1010.kicad_mod']:
 d=sx.loads(p.read_text());fp=d if p.suffix=='.kicad_mod' else next(a for a in d if isinstance(a,list) and str(a[0])=='footprint' and a[1].endswith('BNC_031-5431-1010'))
 fp[:]=[a for a in fp if not(isinstance(a,list) and str(a[0])=='model')]
 fp.append([S('model'),'${KIPRJMOD}/models/BNC_031-5431-1010.wrl',[S('offset'),[S('xyz'),0,0,0]],[S('scale'),[S('xyz'),1,1,1]],[S('rotate'),[S('xyz'),0,0,0]]]);p.write_text(sx.dumps(d))
print('Wrote explicit-mesh BNC connector model')
