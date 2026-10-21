"""Independent consistency + geometry checks on exported native CAD.
Does not replace datasheet review, native ERC/DRC or electrical measurements.
"""
from pathlib import Path
import sexpdata as sx,json,math,collections
from shapely.geometry import box,Polygon,Point,LineString
from shapely import affinity
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];D=R/'hardware/Soil_pH_AFE';g=lambda a,k:next((x for x in a if isinstance(x,list) and str(x[0])==k),None)
b=sx.loads((D/'Soil_pH_AFE.kicad_pcb').read_text());nl=sx.loads((R/'analysis/native/Soil_pH_AFE.net').read_text());C={c['ref']:c for c in json.loads((R/'scripts/components.json').read_text())};expected={}
for n in g(nl,'nets')[1:]:
 for node in n:
  if isinstance(node,list) and str(node[0])=='node':expected[(g(node,'ref')[1],g(node,'pin')[1])]=g(n,'name')[1]
fps={};pads=[];errs=[];via_paste=[];rows=[]
for f in b:
 if not(isinstance(f,list) and str(f[0])=='footprint'):continue
 ref=next(x[2] for x in f if isinstance(x,list) and str(x[0])=='property' and x[1]=='Reference');fps[ref]=f
 at=g(f,'at');x,y=map(float,at[1:3]);fa=float(at[3]) if len(at)>3 else 0
 def center(px,py):
  a=math.radians(fa);return (x+math.cos(a)*px+math.sin(a)*py,y-math.sin(a)*px+math.cos(a)*py)
 for p in f:
  if not(isinstance(p,list) and str(p[0])=='pad'):continue
  pos=g(p,'at');cx,cy=center(*map(float,pos[1:3]));pa=float(pos[3]) if len(pos)>3 else 0;w,h=map(float,g(p,'size')[1:3]);sh=str(p[3]);geom=box(-w/2,-h/2,w/2,h/2)
  if sh=='circle':geom=Point(0,0).buffer(w/2,quad_segs=32)
  elif sh=='oval':geom=box(-max(w-h,0)/2,-max(h-w,0)/2,max(w-h,0)/2,max(h-w,0)/2).buffer(min(w,h)/2) if w!=h else Point(0,0).buffer(w/2)
  elif sh=='roundrect':
   rr=g(p,'roundrect_rratio');rad=min(w,h)*(float(rr[1]) if rr else .25);geom=geom.buffer(-rad).buffer(rad,quad_segs=16)
  geom=affinity.translate(affinity.rotate(geom,-pa,origin=(0,0)),cx,cy);net=g(p,'net');net=net[1] if net else None
  pads.append(dict(ref=ref,pin=p[1],net=net,geom=geom,type=str(p[2]),xy=[cx,cy],paste='F.Paste' in g(p,'layers')[1:]))
  if ref in C:
   want=expected[(ref,p[1])]
   if net!=want:errs.append(f'{ref}.{p[1]}: {net} != {want}')
 if ref in C:
  props={a[1]:a[2] for a in f if isinstance(a,list) and str(a[0])=='property'}
  for k,v in [('Value',C[ref]['value']),('MPN',C[ref]['mpn'])]:
   if props.get(k)!=v:errs.append(f'{ref}.{k} mismatch')
  rows.append({'reference':ref,'pads':len([p for p in pads if p['ref']==ref]),'all_pad_nets_match':not any(e.startswith(ref+'.') for e in errs),'footprint':f[1],'MPN':props.get('MPN')})
assert set(C).issubset(fps)
tracks=[a for a in b if isinstance(a,list) and str(a[0])=='segment'];vias=[a for a in b if isinstance(a,list) and str(a[0])=='via'];inn=[a for a in tracks if g(a,'net')[1]=='PH_IN'];guard=[a for a in tracks if g(a,'net')[1]=='PH_GUARD']
inshape=unary_union([LineString([g(t,'start')[1:3],g(t,'end')[1:3]]).buffer(float(g(t,'width')[1])/2) for t in inn]); inlen=sum(math.dist(g(t,'start')[1:3],g(t,'end')[1:3]) for t in inn)
for v in vias:
 xy=list(map(float,g(v,'at')[1:3]));n=g(v,'net')[1];shape=Point(*xy).buffer(float(g(v,'size')[1])/2,quad_segs=32)
 for p in pads:
  if p['paste'] and shape.intersection(p['geom']).area>1e-6:via_paste.append({'via':xy,'pad':p['ref']+'.'+p['pin'],'via_net':n,'overlap_mm2':round(shape.intersection(p['geom']).area,6)})
 if n=='PH_IN':errs.append('PH_IN via found')
 if float(g(v,'size')[1])<.59999 or float(g(v,'drill')[1])<.29999:errs.append('Via below project manufacturing floor')
for t in tracks:
 if float(g(t,'width')[1])<.19999:errs.append('Track below 0.20mm floor')
# Actual filled polygons, not zone bounding boxes.
copper_under=[]
for z in b:
 if not(isinstance(z,list) and str(z[0])=='zone' and g(z,'net')):continue
 net=g(z,'net')[1]
 if net in ['PH_GUARD','PH_IN']:continue
 for poly in z:
  if not(isinstance(poly,list) and str(poly[0])=='filled_polygon'):continue
  pts=g(poly,'pts');shape=Polygon([a[1:3] for a in pts[1:]]).buffer(0)
  if shape.intersection(inshape).area>1e-7:copper_under.append({'net':net,'layer':g(poly,'layer')[1]})
# Preserve geometric copper, irrespective of UUIDs or serialisation order.
def critical(d):
 out=set()
 for a in d:
  if not(isinstance(a,list) and str(a[0]) in ['segment','via'] and g(a,'net')[1] in ['PH_IN','PH_GUARD']):continue
  if str(a[0])=='segment':out.add((g(a,'net')[1],g(a,'layer')[1],tuple(sorted([tuple(g(a,'start')[1:3]),tuple(g(a,'end')[1:3])])),g(a,'width')[1]))
  else:out.add((g(a,'net')[1],'via',tuple(g(a,'at')[1:3]),g(a,'size')[1],g(a,'drill')[1]))
 return out
preserved=critical(sx.loads((R/'analysis/stages/Soil_pH_AFE_placed.kicad_pcb').read_text()))==critical(b)
# Core pin labels independently transcribed from PDF cache, joined to native netlist.
pdf_checks=[]
for c in C.values():
 if c['ref'][0]!='U':continue
 e=json.loads(next((R/'datasheets/extracted').glob(c['mpn'].replace('/','_')+'_*.json')).read_text())
 for p in e['pins']:
  name=c['pins'][int(p['number'])-1][0].replace('~{','').replace('}','')
  if name!=p['name']:errs.append(f"PDF pin name mismatch {c['ref']}.{p['number']}")
 pdf_checks.append({'ref':c['ref'],'MPN':c['mpn'],'source':e['extraction_metadata']['source_pdf'],'page':e['extraction_metadata']['pin_table_page'],'pins_checked':len(e['pins'])})
report=dict(component_count=len(C),board_footprints=len(fps),all_native_pad_nets_match=not errs,pad_net_errors=errs,PH_IN_length_mm=round(inlen,4),PH_IN_top_only=all(g(t,'layer')[1]=='F.Cu' for t in inn),PH_IN_via_count=sum(g(v,'net')[1]=='PH_IN' for v in vias),critical_guard_geometry_preserved=preserved,foreign_zone_copper_under_input=copper_under,via_paste_overlaps=via_paste,via_count=len(vias),track_widths=sorted(set(float(g(t,'width')[1]) for t in tracks)),pin_checks=pdf_checks,components=rows)
(R/'analysis/connectivity_and_geometry.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['components','pin_checks']},indent=2))
assert not errs and preserved and not copper_under and not via_paste and inn and all(g(t,'layer')[1]=='F.Cu' for t in inn)
