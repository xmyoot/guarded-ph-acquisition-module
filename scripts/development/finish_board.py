"""Final native CAD finishing: metadata sync, no-connect names, legible silk.
Run once on routed board. Uses exact geometry, then native DRC is required.
"""
from pathlib import Path
import sexpdata as sx,math,json,uuid
from shapely.geometry import box,Polygon
from shapely import affinity
R=Path(__file__).resolve().parents[2];D=R/'hardware/Soil_pH_AFE';P=D/'Soil_pH_AFE.kicad_pcb';d=sx.loads(P.read_text());S=sx.Symbol
get=lambda a,k:next((x for x in a if isinstance(x,list) and str(x[0])==k),None)
cs={c['ref']:c for c in json.loads((R/'scripts/components.json').read_text())}
netlist=sx.loads((R/'analysis/native/Soil_pH_AFE.net').read_text());nn={}
for n in get(netlist,'nets')[1:]:
 name=get(n,'name')[1]
 for node in n:
  if isinstance(node,list) and str(node[0])=='node':nn[(get(node,'ref')[1],get(node,'pin')[1])]=(name,get(node,'pinfunction')[1],get(node,'pintype')[1])
d=[a for a in d if not(isinstance(a,list) and str(a[0])=='gr_text' and a[1] in cs)]
obstacles=[]; fdata=[]
for f in d:
 if not(isinstance(f,list) and str(f[0])=='footprint'):continue
 ref=next(x[2] for x in f if isinstance(x,list) and str(x[0])=='property' and x[1]=='Reference');at=get(f,'at');x,y=map(float,at[1:3]);ang=float(at[3]) if len(at)>3 else 0
 def trans(g):return affinity.translate(affinity.rotate(g,-ang,origin=(0,0)),x,y)
 # Courtyard segments include body, pads and assembly clearance.
 pts=[]
 for a in f:
  if not isinstance(a,list):continue
  la=get(a,'layer')
  if la and la[1]=='F.CrtYd':
   for k in ['start','end','center']:
    v=get(a,k)
    if v:pts.append((float(v[1]),float(v[2])))
 if pts:
  xs,ys=zip(*pts);g=trans(box(min(xs),min(ys),max(xs),max(ys)));obstacles.append(g.buffer(.15))
 else:g=box(x-.7,y-.7,x+.7,y+.7);obstacles.append(g.buffer(.15))
 for pad in f:
  if not(isinstance(pad,list) and str(pad[0])=='pad'):continue
  if (ref,pad[1]) in nn:
   n,pn,pt=nn[(ref,pad[1])]
   for key,value in [('net',n),('pinfunction',pn),('pintype',pt)]:
    v=get(pad,key)
    if v:v[:]=[S(key),value]
    else:pad.append([S(key),value])
 if ref in cs:
  c=cs[ref]
  for key,value in [('MPN',c['mpn']),('Datasheet',c['ds'])]:
   prop=next((a for a in f if isinstance(a,list) and str(a[0])=='property' and a[1]==key),None)
   if prop:prop[2]=value
   else:f.append([S('property'),key,value,[S('at'),0,0,0],[S('layer'),'F.Fab'],[S('hide'),S('yes')],[S('effects'),[S('font'),[S('size'),1,1]]]])
  fdata.append((ref,x,y,g))
 else:
  att=get(f,'attr')
  if S('board_only') not in att:att.append(S('board_only'))
# Keep any copper out of the immediate guarded pin escape on both layers.
for z in d:
 if isinstance(z,list) and str(z[0])=='zone' and get(z,'name') and get(z,'name')[1]=='guard_cell':
  get(get(z,'polygon'),'pts')[:]=[S('pts')]+[[S('xy'),x,y] for x,y in [(109.5,114.7),(115.3,114.7),(115.3,116.3),(116.5,116.3),(116.5,118.3),(115.3,118.3),(115.3,120),(109.5,120)]]
for a in d:
 if isinstance(a,list) and str(a[0])=='gr_rect' and get(a,'layer')[1] in ('F.Mask','B.Mask'):
  get(a,'end')[1]=115.8
# Existing board titles are obstacles for new labels.
for a in d:
 if isinstance(a,list) and str(a[0])=='gr_text' and get(a,'layer')[1]=='F.SilkS':
  x,y=map(float,get(a,'at')[1:3]);size=get(get(get(a,'effects'),'font'),'size');h=float(size[1]);w=len(a[1])*h*.7
  obstacles.append(box(x-w/2-.2,y-h/2-.2,x+w/2+.2,y+h/2+.2))
# No silk on high-Z cell or over connector body. Components keep their native
# fab-layer reference placeholders; these new labels improve service access.
obstacles.append(box(109.3,114.5,116.8,120.2))
placed=[]
for ref,x,y,g in sorted(fdata,key=lambda f: (0 if f[0].startswith('U') else 1,len(f[0]))):
 size=.7;w=len(ref)*size*.68;h=size;minx,miny,maxx,maxy=g.bounds
 candidates=[]
 for dist in [.6,1,1.5,2,3,4,5]:
  for xx,yy in [(x,miny-dist),(x,maxy+dist),(minx-dist-w/2,y),(maxx+dist+w/2,y)]:candidates.append((xx,yy))
 # Search within 6mm if crowded.
 for dy in range(-12,13):
  for dx in range(-12,13):candidates.append((x+dx*.5,y+dy*.5))
 candidates.sort(key=lambda a: math.dist(a,(x,y)))
 for xx,yy in candidates:
  bb=box(xx-w/2-.15,yy-h/2-.15,xx+w/2+.15,yy+h/2+.15)
  if not box(100.5,100.5,149.5,134.5).contains(bb):continue
  if any(bb.intersects(o) for o in obstacles):continue
  a=[S('gr_text'),ref,[S('at'),round(xx,4),round(yy,4),0],[S('layer'),'F.SilkS'],[S('uuid'),str(uuid.uuid5(uuid.NAMESPACE_URL,'soil-silk/'+ref))],[S('effects'),[S('font'),[S('size'),size,size],[S('thickness'),.1]]]]
  d.append(a);obstacles.append(bb);placed.append((ref,xx,yy));break
 else:raise RuntimeError('No legible label position for '+ref)
P.write_text(sx.dumps(d));(R/'analysis/silkscreen_positions.json').write_text(json.dumps(placed,indent=2));print('Added',len(placed),'reference labels')
