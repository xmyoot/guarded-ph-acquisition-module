"""Shorten staircase routes using KiCadRoutingTools, preserving all locked copper.
Set ROUTING_TOOLS to a checkout of the documented tool revision. Refill and run
native DRC + scripts/validate_release.py after this mutating operation.
"""
from pathlib import Path
import os,sys,json,uuid
import sexpdata as sx
R=Path(__file__).resolve().parents[1]
T=Path(os.environ['ROUTING_TOOLS']);sys.path.insert(0,str(T/'py_router'))
from kicad_parser import parse_kicad_pcb
from pcb_modification import smooth_octolinear_chains
B=R/'hardware/Soil_pH_AFE/Soil_pH_AFE.kicad_pcb'
S=sx.Symbol;g=lambda a,k:next((x for x in a if isinstance(x,list) and str(x[0])==k),None)
d=sx.loads(B.read_text());orig={str(g(n,'uuid')[1]):n for n in d if isinstance(n,list) and str(n[0])=='segment'}
p=parse_kicad_pcb(str(B));before=len(p.segments)
results=[{'new_segments':[s for s in p.segments if not s.locked and p.nets[s.net_id].name not in ['PH_IN','PH_GUARD','PH_VCM','REF_2V048']]}]
passes=[]
for i in range(4):
 n,nets,removed,added,stats=smooth_octolinear_chains(results,p,clearance=.2,keep_input_copper=True,board_edge_clearance=.3,skip_net_ids={i for i,n in p.nets.items() if n.name in ['PH_IN','PH_GUARD','PH_VCM','REF_2V048']},min_gain=.005)
 passes.append(stats)
 if not n:break
nodes=[]
for seg in p.segments:
 if seg.uuid in orig:nodes.append(orig[seg.uuid]);continue
 name=p.nets[seg.net_id].name
 nodes.append([S('segment'),[S('start'),round(seg.start_x,6),round(seg.start_y,6)],[S('end'),round(seg.end_x,6),round(seg.end_y,6)],[S('width'),seg.width],[S('layer'),seg.layer],[S('net'),name],[S('uuid'),str(uuid.uuid4())]])
d[:]=[n for n in d if not(isinstance(n,list) and str(n[0])=='segment')];d.extend(nodes)
B.write_text(sx.dumps(d))
report={'tool':'KiCadRoutingTools smooth_octolinear_chains','tool_revision':'fd59a050e258581d5938c4d9456bbfeb13240e67','segments_before':before,'segments_after':len(nodes),'clearance_mm':.2,'board_edge_clearance_mm':.3,'protected':'all locked tracks + PH_IN/PH_GUARD/REF_2V048','passes':passes}
(R/'analysis/route_cleanup.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
