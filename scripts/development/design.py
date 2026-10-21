"""Source of explicit design intent. Writes native schematic and component map.
Run with project .venv Python, then build_board.py with KiCad Python.
"""
from pathlib import Path
import uuid,json,csv,shutil
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'hardware/Soil_pH_AFE'; OUT.mkdir(parents=True,exist_ok=True)
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'soil-ph-afe-reva/'+s))
def q(s): return json.dumps(str(s))
def eff(size=1.0): return f'(effects (font (size {size} {size})))'
C=[]
def add(ref,val,fp,mpn,nets,xy,sch,rot=0,dnp=False,ds='',pins=None):
 C.append(dict(ref=ref,value=val,fp=fp,mpn=mpn,nets={str(i):v for i,v in enumerate(nets,1)} if isinstance(nets,list) else nets,xy=xy,sch=sch,rot=rot,dnp=dnp,ds=ds,pins=pins,uuid=uid(ref)))
TI=lambda n:'https://www.ti.com/lit/ds/symlink/'+n.lower()+'.pdf'
add('U1','LMP91200','Package_SO:TSSOP-16_4.4x5mm_P0.65mm','LMP91200MTX/NOPB',['+3V3_A',None,None,'PH_GUARD','PH_IN','PH_GUARD',None,'PH_VCM','REF_2V048','GND_A','PH_VOCM','PH_VOUT','GND_A','+3V3_A','GND_A','GND_A'],[119,117],[80,65],ds=TI('lmp91200'),pins=[('VDD','power_in'),('NC','no_connect'),('NC','no_connect'),('GUARD1','passive'),('INP','input'),('GUARD2','passive'),('VCMHI','output'),('VCM','output'),('VREF','input'),('GND','power_in'),('VOCM','output'),('VOUT','output'),('GND','power_in'),('VDD','power_in'),('GND','power_in'),('GND','power_in')])
add('U2','ADS112C04','Package_SO:TSSOP-16_4.4x5mm_P0.65mm','ADS112C04IPWR',['GND_A','GND_A','AFE_READY','GND_A','GND_A','GND_A','GND_A','GND_A','REF_2V048','ADC_N','ADC_P','+3V3_A','+3V3_A','ADC_DRDY_N','I2C_SDA','I2C_SCL'],[130,116.5],[228,65],rot=180,ds=TI('ads112c04'),pins=[('A0','input'),('A1','input'),('~{RESET}','input'),('DGND','power_in'),('AVSS','power_in'),('AIN3','input'),('AIN2','input'),('REFN','input'),('REFP','input'),('AIN1','input'),('AIN0','input'),('AVDD','power_in'),('DVDD','power_in'),('~{DRDY}','open_collector'),('SDA','bidirectional'),('SCL','input')])
add('U3','REF3220 / 2.048V','Package_TO_SOT_SMD:SOT-23-6','REF3220AIDBVT',['GND_A','GND_A','AFE_READY','+3V3_A','REF_2V048','REF_2V048'],[128.5,108],[187,183],ds=TI('ref3220'),pins=[('GND_F','power_in'),('GND_S','input'),('ENABLE','input'),('IN','power_in'),('OUT_S','input'),('OUT_F','power_out')])
add('U4','TPS7A2033 / 3.3V','Package_TO_SOT_SMD:SOT-23-5','TPS7A2033PDBVR',['+5V_IN','GND_A','+5V_IN',None,'+3V3_A'],[141,124.5],[68,183],ds=TI('tps7a20'),pins=[('IN','power_in'),('GND','power_in'),('EN','input'),('NC','no_connect'),('OUT','power_out')])
add('U5','TPS3839K33 / 2.93V','Package_TO_SOT_SMD:SOT-23','TPS3839K33DBZT',['GND_A','AFE_READY','+3V3_A'],[136,127.5],[302,183],ds=TI('tps3839'),pins=[('GND','power_in'),('~{RESET}','output'),('VDD','power_in')])
add('J1','INSULATED BNC','Soil_pH:BNC_031-5431-1010','031-5431-1010',['PH_IN','PH_VCM'],[112,117.5],[38,88],rot=90,ds='https://www.amphenolrf.com/en-us/assets/file/4065788069/',pins=[('CENTER','passive'),('SHELL','passive')])
add('J2','HOST / JST PH6','Connector_JST:JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical','B6B-PH-K-S(LF)(SN)',['+5V_IN','GND_A','I2C_SDA','I2C_SCL','GND_A',None],[145.5,108],[348,65],rot=270,ds='https://www.jst.com/wp-content/uploads/2021/08/ePH-new.pdf',pins=[('+5V','passive'),('GND','passive'),('SDA','passive'),('SCL','passive'),('GND','passive'),('RESERVED','passive')])
def res(r,v,n,xy,sch,mpn=None,rot=0):
 add(r,v,'Resistor_SMD:R_0603_1608Metric',mpn or {'1k':'TNPW06031K00BEEA','4.7k':'CRCW06034K70FKEA','10k':'CRCW060310K0FKEA','100k':'CRCW0603100KFKEA','0R':'CRCW06030000Z0EA'}[v],n,xy,sch,rot)
res('R1','1k',['PH_VOUT','ADC_P'],[124.5,110],[153,52])
res('R2','1k',['PH_VOCM','ADC_N'],[122.5,122.7],[153,75])
res('R3','4.7k',['PULLUP_SDA','I2C_SDA'],[136.8,112],[319,105],rot=90)
res('R4','4.7k',['PULLUP_SCL','I2C_SCL'],[139.6,112],[354,105],rot=90)
res('R5','0R',['+3V3_A','PULLUP_SDA'],[136.8,109],[319,92],rot=90)
res('R6','0R',['+3V3_A','PULLUP_SCL'],[139.6,109],[354,92],rot=90)
res('R7','10k',['+3V3_A','ADC_DRDY_N'],[135,111],[265,104],rot=90)
res('R8','100k',['AFE_READY','GND_A'],[135.5,130.5],[331,206])
# Nominal capacitor choices; effective capacitance and leakage remain physical gates.
cap_mpn={'100n':'GRM188R71H104KA93D','1u':'GRM188R71C105KA12D','4.7u':'GRM21BR71E475KA73L','10u':'GRM31CR71C106KA12L','10n C0G':'GRM1885C1H103JA01D','470p C0G':'GRM1885C1H471JA01D'}
def cap(ref,v,n,xy,sch,rot=0,dnp=False):
 size='1206_3216' if v=='10u' else '0805_2012' if v=='4.7u' else '0603_1608'
 add(ref,v,'Capacitor_SMD:C_'+size+'Metric',cap_mpn[v],n,xy,sch,rot,dnp)
cap('C1','10u',['+3V3_A','GND_A'],[118,108],[42,112])
cap('C2','1u',['+3V3_A','GND_A'],[117,110.5],[76,112])
cap('C3','100n',['+3V3_A','GND_A'],[120,112],[110,112])
cap('C4','100n',['+3V3_A','GND_A'],[124.4,116.25],[144,112])
cap('C5','100n',['+3V3_A','GND_A'],[124.8,119.8],[216,112],rot=90)
cap('C6','100n',['+3V3_A','GND_A'],[128.5,121.5],[253,112])
cap('C7','1u',['+3V3_A','GND_A'],[133.5,121.5],[288,125])
cap('C8','100n',['+3V3_A','GND_A'],[132.5,108],[211,211],rot=90)
cap('C9','4.7u',['+5V_IN','GND_A'],[137,122.5],[42,211],rot=90)
cap('C10','4.7u',['+3V3_A','GND_A'],[145,126],[100,211],rot=90)
cap('C11','1u',['REF_2V048','GND_A'],[125.5,112.5],[161,211],rot=180)
cap('C12','100n',['+3V3_A','GND_A'],[139,129.5],[302,223],rot=90)
cap('C13','10n C0G',['ADC_P','ADC_N'],[124.5,114],[180,92],rot=0)
# Optional common-mode capacitor sites omitted in Rev A.

for i,(n,xy) in enumerate([('GND_A',[143.5,132]),('+5V_IN',[147,123]),('+3V3_A',[144,129.5]),('REF_2V048',[125,127.5]),('PH_VCM',[110,128]),('PH_VOUT',[120,125]),('PH_VOCM',[120,128]),('AFE_READY',[133,132]),('I2C_SDA',[136.8,116]),('I2C_SCL',[139.6,117]),('ADC_DRDY_N',[135,118.5])],1):
 add('TP'+str(i),n,'TestPoint:TestPoint_Pad_D1.0mm','PCB_FEATURE',[n],xy,[35+(i-1)%6*60,247+(i-1)//6*18],pins=[('TEST','passive')])
# Local footprint copies remove dependence on library table versions.
LIB=Path('/Users/hector/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
for c in C:
 old=c['fp']; lib,name=old.split(':'); dest=OUT/'Soil_pH.pretty'/f'{name}.kicad_mod'
 if lib!='Soil_pH':
  shutil.copyfile(LIB/(lib+'.pretty')/(name+'.kicad_mod'),dest)
 else:
  s=(LIB/'Connector_Coaxial.pretty/BNC_Amphenol_B6252HB-NPP3G-50_Horizontal.kicad_mod').read_text().replace('BNC_Amphenol_B6252HB-NPP3G-50_Horizontal',name)
  s=s.replace('http://www.farnell.com/datasheets/612848.pdf','Amphenol 31-5431-1010 Rev E; 2.54/5.08/10.16mm pattern; holes enlarged to 1.0/2.1mm')
  s=s.replace('(size 1.6 2.5)','(size 1.7 1.7)').replace('(size 3.5 7)','(size 3.5 3.5)')
  s=s.replace('(drill 0.89)','(drill 1.0)').replace('(drill 2.01)','(drill 2.1)')
  dest.write_text(s)
 c['source_fp']=old; c['fp']='Soil_pH:'+name
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Soil_pH") (type "KiCad") (uri "${KIPRJMOD}/Soil_pH.pretty") (options "") (descr "Frozen prototype footprints")))\n')
# Custom symbols: independent explicit manufacturer pin maps, embedded + project library.
for c in C: c['sch']=[round(round(v/1.27)*1.27,4) for v in c['sch']]
libsyms=[]; placed=[]; wires=[]; labels=[]; nc=[]
for c in C:
 ref=c['ref']; typ='ic' if ref[0]=='U' else 'connector' if ref[0]=='J' else 'tp' if ref.startswith('TP') else 'passive'
 name=ref if typ in ('ic','connector','tp') else ('R' if ref[0]=='R' else 'C')
 if c['pins'] is None: c['pins']=[('1','passive'),('2','passive')]
 c['symbol']=name
 N=len(c['pins']); coords=[]
 if typ in ('ic','connector'):
  left=(N+1)//2; right=N-left; h=max(left,right)*2.54/2
  # left ascending, right ascending: human readable logical pin table
  for i in range(N):
   side=0 if i<left else 1; j=i if side==0 else i-left
   coords.append((-17.78 if not side else 17.78, round((max(left,right)-1)*1.27-j*2.54,4),0 if not side else 180))
  draw=f'(rectangle (start -12.7 {h+1.27}) (end 12.7 {-h-1.27}) (stroke (width 0.254) (type default)) (fill (type background)))'
 elif typ=='tp': coords=[(0,0,90)]; draw='(circle (center 0 1.27) (radius 1.0) (stroke (width 0.2) (type default)) (fill (type none)))'
 else:
  coords=[(-5.08,0,0),(5.08,0,180)]
  if ref[0]=='R': draw='(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))'
  else: draw='(polyline (pts (xy -0.508 1.524) (xy -0.508 -1.524)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.508 1.524) (xy 0.508 -1.524)) (stroke (width 0.254) (type default)) (fill (type none)))'
 # pin length for C to plate, R to rectangle; body left/right pin length5.08
 pins=''
 for i,((pn,pt),(px,py,pa)) in enumerate(zip(c['pins'],coords),1):
  length=5.08 if typ in ('ic','connector') else 0 if typ=='tp' else 2.54 if ref[0]=='R' else 4.572
  pins+=f'(pin {pt} line (at {px} {py} {pa}) (length {length}) (name {q(pn)} {eff(.9)}) (number "{i}" {eff(.9)}))'
 sym=f'(symbol {q(name)} (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "{ref.rstrip("0123456789")}" (at 0 0 0) {eff()}) (property "Value" {q(c["value"])} (at 0 2.54 0) {eff()}) (symbol "{name}_0_1" {draw}) (symbol "{name}_1_1" {pins}))'
 if name not in [n for n,s in libsyms]: libsyms.append((name,sym))
 x,y=c['sch']; top=max(p[1] for p in coords)
 props=f'(property "Reference" {q(ref)} (at {x} {y-top-6.35} 0) {eff(1.27)}) (property "Value" {q(c["value"])} (at {x} {y-top-3.81} 0) {eff(1.0)})'
 for k,v in [('Footprint',c['fp']),('Datasheet',c['ds']),('MPN',c['mpn'])]: props+=f'(property {q(k)} {q(v)} (at {x} {y} 0) (effects (font (size 1 1)) hide))'
 instance=f'(instances (project "Soil_pH_AFE" (path "/{uid("sheet")}" (reference {q(ref)}) (unit 1))))'
 placed.append(f'(symbol (lib_id "Soil_pH:{name}") (at {x} {y} 0) (unit 1) (in_bom {"no" if c["mpn"]=="PCB_FEATURE" else "yes"}) (on_board yes) (dnp {"yes" if c["dnp"] else "no"}) (uuid {q(c["uuid"])}) {props} '+''.join(f'(pin "{i}" (uuid "{uid(ref+"pin"+str(i))}"))' for i in range(1,N+1))+instance+')')
 for i,(px,py,pa) in enumerate(coords,1):
  a=(round(x+px,4),round(y-py,4)); net=c['nets'][str(i)]
  if net is None: nc.append(f'(no_connect (at {a[0]} {a[1]}) (uuid "{uid(ref+"nc"+str(i))}"))'); continue
  dx=-5.08 if px<0 else 5.08
  if typ=='tp': dx=5.08
  b=(round(a[0]+dx,4),a[1])
  wires.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid(ref+"wire"+str(i))}"))')
  labels.append(f'(global_label {q(net)} (shape input) (at {b[0]} {b[1]} {180 if dx<0 else 0}) {eff(.85)} (uuid "{uid(ref+"label"+str(i))}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {b[0]} {b[1]} 0) (effects (font (size 1 1)) hide)))')
# Power flag symbols supply external5V and ground only
for j,net in enumerate(['+5V_IN','GND_A']):
 name='PWR_FLAG'; ref='#FLG0'+str(j+1); x=round((45+j*35)/1.27)*1.27; y=158.75
 if j==0:
  libsyms.append((name,'(symbol "PWR_FLAG" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes) (property "Reference" "#FLG" (at 0 0 0) (effects (font (size 1 1)) hide)) (property "Value" "PWR_FLAG" (at 0 2 0) (effects (font (size 1 1)))) (symbol "PWR_FLAG_0_1" (polyline (pts (xy 0 0) (xy -1.27 1.27) (xy 0 2.54) (xy 1.27 1.27) (xy 0 0)) (stroke (width 0.2) (type default)) (fill (type none)))) (symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))'))
 placed.append(f'(symbol (lib_id "Soil_pH:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(ref)}") (property "Reference" "{ref}" (at {x} {y} 0) (effects (font (size 1 1)) hide)) (property "Value" "PWR_FLAG" (at {x} {y-4} 0) {eff()}) (pin "1" (uuid "{uid(ref+"pin")}")) (instances (project "Soil_pH_AFE" (path "/{uid("sheet")}" (reference "{ref}") (unit 1)))))')
 labels.append(f'(global_label "{net}" (shape input) (at {x} {y} 0) {eff(.85)} (uuid "{uid(ref+"label")}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) (effects (font (size 1 1)) hide)))')
notes=[]
for x,y,t,s in [(25,20,'SOIL / pH AFE     Rev A     |     Bench engineering prototype',2.5),(25,29,'5V regulated input / 3.3V I2C / external ESP32-S3 host / no onboard galvanic isolation',1.3),(25,39,'01  GUARDED ELECTRODE BUFFER',1.5),(203,39,'02  DIFFERENTIAL CONVERSION',1.5),(309,39,'03  HOST INTERFACE',1.5),(25,140,'BNC shell = driven PH_VCM. Insulate from chassis. Floating sample only.',1.2),(25,146,'PH_IN: no test point, TVS or ordinary probe. Exposed guards on both faces; clean and dry.',1.2),(25,173,'04  QUIET 3.3V SUPPLY',1.5),(146,173,'05  KELVIN REFERENCE',1.5),(270,173,'06  DELAYED ENABLE / RESET',1.5),(25,235,'07  LOW-IMPEDANCE TEST ACCESS  |  Ground clip: TP1  |  No common-mode filter caps  |  R5/R6 removable pullup links',1.2),(145,154,'ADC: 0x40 / AIN0-AIN1 / gain2 / ext 2.048V / 20SPS',1.2),(145,160,'Register image: 02 02 00 00. Wait >=500ms after power; check readback.',1.2)]:
 notes.append(f'(text {q(t)} (at {x} {y} 0) (effects (font (size {s} {s})) (justify left)) (uuid "{uid(t)}"))')
lib='(kicad_symbol_lib (version 20231120) (generator "soil_design") '+''.join(s for n,s in libsyms)+')'
(OUT/'Soil_pH.kicad_sym').write_text(lib)
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Soil_pH") (type "KiCad") (uri "${KIPRJMOD}/Soil_pH.kicad_sym") (options "") (descr "Manufacturer pin maps")))')
embedded=''.join(s.replace('(symbol '+q(n), '(symbol '+q('Soil_pH:'+n),1) for n,s in libsyms)
sch=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("sheet")}") (paper "A3") (title_block (title "Soil pH Acquisition Module") (date "2026-10-20") (rev "A") (company "Engineering prototype - hardware validation pending")) (lib_symbols {embedded}) '+''.join(placed+wires+labels+nc+notes)+')'
(OUT/'Soil_pH_AFE.kicad_sch').write_text(sch)
(ROOT/'scripts/components.json').write_text(json.dumps(C,indent=2))
protected=['PH_IN','PH_GUARD','PH_VCM','PH_VOUT','PH_VOCM','ADC_P','ADC_N','REF_2V048']
project={'meta':{'filename':'Soil_pH_AFE.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_text_height':.7,'min_text_thickness':.1,'min_clearance':.2,'min_track_width':.2,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_via_annular_width':.15,'min_copper_edge_clearance':.3,'min_hole_to_hole':.25},'defaults':{'copper_line_width':.2,'copper_text_size_h':1,'copper_text_size_v':1},'rule_severities':{}}},'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.2,'via_diameter':.6,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.2,'diff_pair_via_gap':.25}],'meta':{'version':4}},'kicad_routing_tools':{'protected_nets':{n:'Manual analog route; locked copper; do not target' for n in protected}}}
(OUT/'Soil_pH_AFE.kicad_pro').write_text(json.dumps(project,indent=2))
print(f'{len(C)} components; schematic and frozen libraries written')
