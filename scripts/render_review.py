"""Regenerate independent Gerber previews and a framed KiCad assembly render."""
from pathlib import Path
import os,shutil,subprocess
from gerbonara import LayerStack
import cairosvg
R=Path(__file__).resolve().parents[1];V=R/'output/review'
stack=LayerStack.open(R/'output/fabrication')
for side in ['top','bottom']:
 colors={side+' copper':'#b77929','mechanical outline':'#111111','drill pth':'#ffffff','drill npth':'#ffffff'}
 svg=V/('gerber-'+side+'.svg');svg.write_text(str(stack.to_svg(side_re=side+'|mechanical',force_bounds=((99.5,-135.5),(150.5,-99.5)),colors=colors)))
 cairosvg.svg2png(url=str(svg),write_to=str(svg.with_suffix('.png')),output_width=1600,background_color='white')
cli=os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or '/Users/hector/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
subprocess.run([cli,'pcb','render',str(R/'hardware/Soil_pH_AFE/Soil_pH_AFE.kicad_pcb'),'--output',str(V/'assembly_3d.png'),'--width','1600','--height','1100','--rotate','330,0,25','--zoom','0.74','--background','opaque','--quality','high','--floor'],check=True)
