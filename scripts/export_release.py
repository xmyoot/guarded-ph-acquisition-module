"""Regenerate manufacturing outputs from reviewed native CAD. No ordering."""
from pathlib import Path
import subprocess,json,csv,collections,hashlib,os,shutil
R=Path(__file__).resolve().parents[1];D=R/'hardware/Soil_pH_AFE';O=R/'output';F=O/'fabrication';A=O/'assembly';V=O/'review'
for p in [F,A,V]:p.mkdir(parents=True,exist_ok=True)
CLI=os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or '/Users/hector/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli';B=str(D/'Soil_pH_AFE.kicad_pcb');S=str(D/'Soil_pH_AFE.kicad_sch')
cmds=[['sch','export','netlist',S,'--format','kicadsexpr','-o',str(R/'analysis/native/Soil_pH_AFE.net')],['sch','erc',S,'-o',str(R/'analysis/native/erc.rpt'),'--exit-code-violations'],['pcb','drc',B,'--schematic-parity','-o',str(R/'analysis/native/drc.rpt'),'--exit-code-violations'],['sch','export','pdf',S,'-o',str(V/'schematic.pdf')],['pcb','export','gerbers',B,'-o',str(F),'--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts','--subtract-soldermask'],['pcb','export','drill',B,'-o',str(F),'--format','excellon','--excellon-units','mm','--excellon-separate-th','--generate-map','--map-format','pdf','--generate-report'],['pcb','export','pos',B,'-o',str(A/'placement_all.csv'),'--format','csv','--units','mm','--exclude-dnp'],['pcb','export','pos',B,'-o',str(A/'placement_smd.csv'),'--format','csv','--units','mm','--smd-only','--exclude-dnp'],['pcb','export','pdf',B,'-o',str(A/'assembly_top.pdf'),'--layers','F.Fab,Edge.Cuts','--mode-single','--include-border-title'],['pcb','export','pdf',B,'-o',str(V/'layer_review.pdf'),'--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,F.SilkS,Edge.Cuts','--mode-multipage'],['pcb','export','svg',B,'-o',str(V/'layers'),'--mode-multi','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,F.SilkS,F.Fab,Edge.Cuts','--page-size-mode','2','--exclude-drawing-sheet']]
with (R/'analysis/export.log').open('w') as log:
 for cmd in cmds:
  log.write(json.dumps([CLI]+cmd)+'\n');log.flush();subprocess.run([CLI]+cmd,stdout=log,stderr=log,check=True)
(R/'analysis/export_commands.json').write_text(json.dumps([[CLI]+c for c in cmds],indent=2))
C=json.loads((R/'scripts/components.json').read_text());groups=collections.defaultdict(list)
for c in C:
 if c['mpn']!='PCB_FEATURE':groups[(c['mpn'],c['value'],c['fp'])].append(c['ref'])
with (A/'BOM.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['References','Quantity','Value','Manufacturer','MPN','Footprint','Population','Notes'])
 for (mpn,val,fp),refs in groups.items():
  manu='Texas Instruments' if refs[0][0]=='U' else 'Amphenol RF' if refs[0]=='J1' else 'JST' if refs[0]=='J2' else 'Murata' if refs[0][0]=='C' else 'Vishay'
  note='0.1%,25ppm/K' if mpn.startswith('TNPW') else 'jumper; remove R5/R6 to disable local bus pullups' if refs[0] in ['R5','R6'] else '1%' if refs[0] in ['R3','R4','R7','R8'] else 'C0G,50V,5%' if val=='10n C0G' else 'X7R,50V,10%' if val=='100n' else 'X7R,16V,10%' if val in ['1u','10u'] else 'X7R,25V,10%' if val=='4.7u' else ''
  w.writerow([','.join(refs),len(refs),val,manu,mpn,fp,'FIT',note])
with (A/'mating_parts.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Qty','Manufacturer','MPN','Use']);w.writerow([1,'JST','PHR-6','Host cable housing']);w.writerow([5,'JST','SPH-002T-P0.5S','Contacts, suitable wire per JST drawing; pin6 left empty']);w.writerow([1,'External','ESP32-S3 development board','Host, USB power separate; default GPIO8/9']);w.writerow([1,'External','Passive combination pH probe with BNC','Validate polarity, leakage and physical fit'])
print('Exported native checks, Gerbers/drills, assembly drawings, BOM and placements')
