"""Build placed PCB and manually engineered analog copper. KiCad Python only.
Rebuilding replaces the placed board; final routed release is separate.
"""
from pathlib import Path
import json,math,uuid
import wx
app=wx.App(False)
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'hardware/Soil_pH_AFE'; C=json.loads((ROOT/'scripts/components.json').read_text()); b=p.BOARD(); b.SetCopperLayerCount(2)
mm=p.FromMM; V=lambda x,y:p.VECTOR2I(mm(x),mm(y))
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'soil-ph-afe-reva/'+s))
nets={}
for n in sorted({v for c in C for v in c['nets'].values() if v}):
 ni=p.NETINFO_ITEM(b,n);b.Add(ni);nets[n]=ni
fps={}; pads={}
for c in C:
 f=p.FootprintLoad(str(OUT/'Soil_pH.pretty'),c['fp'].split(':')[1]); assert f,c['ref']
 f.SetReference(c['ref']);f.SetValue(c['value']);f.SetFPID(p.LIB_ID(*c['fp'].split(':'))); f.SetPosition(V(*c['xy']));f.SetOrientationDegrees(c['rot'])
 path=p.KIID_PATH();path.push_back(p.KIID(uid('sheet')));path.push_back(p.KIID(c['uuid']));f.SetPath(path)
 if c['dnp']:f.SetAttributes(f.GetAttributes()|p.FP_DNP)
 if c['mpn']=='PCB_FEATURE':f.SetAttributes(f.GetAttributes()|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
 f.Reference().SetTextSize(V(.8,.8));f.Reference().SetTextThickness(mm(.12)); f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
 f.Value().SetVisible(False)
 b.Add(f);fps[c['ref']]=f
 for pad in f.Pads():
  no=pad.GetNumber();n=c['nets'].get(no)
  if n:
   pad.SetNet(nets[n])
   if n=='GND_A' and pad.GetAttribute()==p.PAD_ATTRIB_SMD: pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
  pads.setdefault((c['ref'],no),[]).append(pad)
 if c['ref'] in ('U1','J1'):f.SetLocked(True)
for f in fps.values(): f.Reference().SetVisible(False)
# Reference layout is deliberately adjusted after visual review.
refplaces={'J1':(103,109),'J2':(147.8,113),'U1':(119,113.9),'U2':(131,120.4),'U3':(128.5,105.5),'U4':(141,122),'U5':(135.8,125.5)}
for ref,f in fps.items():
 if ref in refplaces: f.Reference().SetPosition(V(*refplaces[ref]))
 elif ref.startswith('TP'): f.Reference().SetPosition(f.GetPosition()+V(0,-1.35))
 elif next(c for c in C if c['ref']==ref)['rot']==90:
  f.Reference().SetPosition(f.GetPosition()+V(-1.6,0)); f.Reference().SetTextAngle(p.EDA_ANGLE(90,p.DEGREES_T))
 else:f.Reference().SetPosition(f.GetPosition()+V(0,-1.5))
def pt(ref,no):
 a=pads[(ref,str(no))][0].GetPosition();return (p.ToMM(a.x),p.ToMM(a.y))
def line(n,points,layer=p.F_Cu,w=.2,lock=True):
 for a,z in zip(points,points[1:]):
  if math.dist(a,z)<.000001:continue
  t=p.PCB_TRACK(b);t.SetStart(V(*a));t.SetEnd(V(*z));t.SetLayer(layer);t.SetWidth(mm(w));t.SetNet(nets[n]);t.SetLocked(lock);b.Add(t)
def via(n,xy,lock=True):
 v=p.PCB_VIA(b);v.SetPosition(V(*xy));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[n]);v.SetLocked(lock);b.Add(v)
def connect(n,a,z,mid=[],layer=p.F_Cu,w=.2):line(n,[pt(*a)]+mid+[pt(*z)],layer,w)
def silk(text,xy,size=1,layer=p.F_SilkS):
 t=p.PCB_TEXT(b);t.SetText(text);t.SetPosition(V(*xy));t.SetTextSize(V(size,size));t.SetTextThickness(mm(.14));t.SetLayer(layer);b.Add(t)
def rect(layer,a,z,width=.12,filled=False):
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_RECT);s.SetStart(V(*a));s.SetEnd(V(*z));s.SetLayer(layer);s.SetWidth(mm(width))
 if filled:s.SetFilled(True)
 b.Add(s)
# 50 x35mm outline
for a,z in [((100,100),(150,100)),((150,100),(150,135)),((150,135),(100,135)),((100,135),(100,100))]:
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(V(*a));s.SetEnd(V(*z));s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
# Two nonplated mechanical holes: clearance independent of ground and shell.
LIB=Path('/Users/hector/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
for i,xy in enumerate([(103,103),(147,103)],1):
 f=p.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_2.2mm_M2');f.SetReference('H'+str(i));f.SetValue('M2 NPTH');f.SetPosition(V(*xy));f.SetAttributes(f.GetAttributes()|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);f.Reference().SetVisible(False);f.Value().SetVisible(False);b.Add(f)
for i,xy in enumerate([(107,103),(143,103),(148,132)],1):
 f=p.FootprintLoad(str(LIB/'Fiducial.pretty'),'Fiducial_1mm_Mask2mm');f.SetReference('FID'+str(i));f.SetValue('OPTICAL');f.SetPosition(V(*xy));f.SetAttributes(f.GetAttributes()|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);f.Reference().SetVisible(False);f.Value().SetVisible(False);b.Add(f)
# Electrode path: no via and no branches. Guard follows through pin 4/6 escapes.
connect('PH_IN',('J1',1),('U1',5),mid=[(114.8,117.325)],w=.25)
a=pt('U1',4);z=pt('U1',6)
guard=[a,(114.9,a[1]),(114.9,115.7),(110.6,115.7),(110.6,118.77),(114.9,118.77),(114.9,z[1]),z]
line('PH_GUARD',guard,w=.35)
for layer in [p.B_Cu]:line('PH_GUARD',[(110.6,115.7),(114.9,115.7),(114.9,118.77),(110.6,118.77),(110.6,115.7)],layer,w=.35)
for xy in [(110.6,115.7),(114.9,115.7),(110.6,118.77),(114.9,118.77)]:via('PH_GUARD',xy)
# Explicit zone keepout on both layers; allowed tracks are separately audited.
layers=p.LSET();layers.AddLayer(p.F_Cu);layers.AddLayer(p.B_Cu)
k=p.ZONE(b);k.SetIsRuleArea(True);k.SetZoneName('guard_cell');k.SetLayerSet(layers);k.SetDoNotAllowZoneFills(True);k.SetDoNotAllowTracks(False);k.SetDoNotAllowVias(False);k.SetDoNotAllowPads(False);k.SetDoNotAllowFootprints(False)
k.Outline().NewOutline()
for xy in [(109.5,114.7),(115.3,114.7),(115.3,120),(109.5,120)]:k.Outline().Append(int(mm(xy[0])),int(mm(xy[1])))
b.Add(k)
# Top/bottom exposed guard + input mask windows. NO paste windows.
for layer in [p.F_Mask,p.B_Mask]:rect(layer,(110.1,115.15),(115.25,119.15),0,True)
# Local reference force/sense branches terminate at C11 adjacent to ADC REFP.
load=pt('C11',1);gload=pt('C11',2)
line('REF_2V048',[pt('U3',6),(130.8,107.05),(130.8,110.5),(126.275,110.5),load],w=.2)
line('REF_2V048',[pt('U3',5),(131.6,108)],w=.2);via('REF_2V048',(131.6,108))
line('REF_2V048',[(131.6,108),(131.6,111),(129,111),(127.5,112.5)],p.B_Cu,w=.2);via('REF_2V048',(127.5,112.5));line('REF_2V048',[(127.5,112.5),load])
connect('REF_2V048',('C11',1),('U2',9),mid=[(126.275,113.4)],w=.2)
# Short low-impedance bypass escape stubs, under U1 body and off paste pads.
for no,n,xy in [(14,'+3V3_A',(119.6,116.025)),(10,'GND_A',(120.8,118.625))]:
 line(n,[pt('U1',no),xy],w=.2);via(n,xy)
# Remaining low-impedance analog paths are explicitly allowed one by one;
# the guarded path and pre-routed reference branches stay locked.
# Plane spans only low-impedance right-hand region; no copper under BNC input.
for layer in [p.F_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets['GND_A']);z.SetLocalClearance(mm(.25));z.SetThermalReliefGap(mm(.25));z.SetThermalReliefSpokeWidth(mm(.25));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetMinThickness(mm(.2));z.Outline().NewOutline()
 for xy in [(116,100.5),(149.5,100.5),(149.5,134.5),(116,134.5)]:z.Outline().Append(mm(xy[0]),mm(xy[1]))
 b.Add(z)
# Label large quiet spaces and host mapping; keep silkscreen out of guard window.
silk('SOIL / pH AFE',(124.5,102.5),1.1);silk('REV A  /  BENCH',(125,104.3),.8)
silk('HOST',(146,105),.8)
silk('INSULATED',(106,127),.7);silk('SHELL=VCM',(106,128.5),.7)
silk('CLEAN / DRY',(107.5,131.5),.75);silk('NO INPUT TVS',(107.5,133),.7)
silk('FLOATING SAMPLE ONLY',(126,133.5),.7)
silk('3V3 I2C / NO ISOLATION',(125,130),.7)
# No silkscreen in the exposed guard cell.
# Ground area stitching; all outside guarded cell.
for xy in [(117,103),(133,103),(147,105),(148,125),(138,132),(117,132),(134,122),(120,121)]:via('GND_A',xy,False)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(OUT/'Soil_pH_AFE_placed.kicad_pcb'),b)
# placed board and project must travel together
(OUT/'Soil_pH_AFE_placed.kicad_pro').write_text((OUT/'Soil_pH_AFE.kicad_pro').read_text())
print('Placed board:',len(list(b.GetFootprints())),'footprints')
print(json.dumps({r:{n:pt(r,n) for rr,n in pads if rr==r} for r in ['U1','U2','U3','U4','J1','J2']},indent=2))
