"""Package reviewed manufacturing artifacts and hash the controlled project files."""
from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parents[1];O=R/'output'
with zipfile.ZipFile(O/'Soil_pH_AFE_RevA_fabrication.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((O/'fabrication').glob('*')):
  if f.is_file():z.write(f,'fabrication/'+f.name)
 z.write(R/'docs/implementation/fabrication_notes.md','fabrication_notes.md')
rows=[]
for root in ['hardware/Soil_pH_AFE','firmware','docs','output/fabrication','output/assembly','output/review']:
 for f in sorted((R/root).rglob('*')):
  if f.is_file() and f.suffix not in ['.kicad_prl'] and f.name!='.DS_Store' and 'build' not in f.relative_to(R).parts:rows.append(f)
rows += [O/'Soil_pH_AFE_RevA_fabrication.zip',R/'README.md',R/'analysis/native/erc.rpt',R/'analysis/native/drc.rpt',R/'analysis/connectivity_and_geometry.json']
(O/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(R))+'\n' for f in sorted(set(rows))))
print(f'Packaged fabrication ZIP and hashed {len(set(rows))} controlled files')
