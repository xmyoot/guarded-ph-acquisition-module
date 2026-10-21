"""Conservative visual envelope, not a vendor detailed mechanical model.
Dimensions from Amphenol 31-5431-1010 Rev E. VRML units 2.54mm in KiCad.
"""
from pathlib import Path
import sexpdata as sx
R=Path(__file__).resolve().parents[2];D=R/'hardware/Soil_pH_AFE';model=D/'models/BNC_031-5431-1010_envelope.wrl'
def v(a):return ' '.join(str(round(x/2.54,6)) for x in a)
def shape(xyz,kind,size,color):
 geom=('Box { size '+v(size)+' }') if kind=='box' else ('Cylinder { radius '+str(size[0]/2.54)+' height '+str(size[1]/2.54)+' }')
 return 'Transform { translation '+v(xyz)+' children [ Shape { appearance Appearance { material Material { diffuseColor '+color+' } } geometry '+geom+' } ] }\n'
s='#VRML V2.0 utf8\n# DRAWING ENVELOPE ONLY - not vendor CAD; see docs/implementation/decisions.md\n'
s+=shape([0,6.1,8.56],'box',[14.5,14.5,15.6],'.9 .9 .84')
s+=shape([0,23,8.18],'cyl',[6.415,20.9],'.65 .67 .69')
s+=shape([0,33.48,8.18],'cyl',[4.7,.05],'.12 .12 .12')
# Cylinders here face forward, along Y; footprint holes/pins authoritative in PCB.
model.write_text(s)
S=sx.Symbol
for P in [D/'Soil_pH_AFE.kicad_pcb',D/'Soil_pH.pretty/BNC_031-5431-1010.kicad_mod']:
 d=sx.loads(P.read_text());fp=d if P.suffix=='.kicad_mod' else next(a for a in d if isinstance(a,list) and str(a[0])=='footprint' and a[1].endswith('BNC_031-5431-1010'))
 fp[:]=[a for a in fp if not(isinstance(a,list) and str(a[0])=='model')]
 fp.append([S('model'),'${KIPRJMOD}/models/BNC_031-5431-1010_envelope.wrl',[S('offset'),[S('xyz'),0,0,0]],[S('scale'),[S('xyz'),1,1,1]],[S('rotate'),[S('xyz'),0,0,0]]]);P.write_text(sx.dumps(d))
