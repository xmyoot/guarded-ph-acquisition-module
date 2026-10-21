from pathlib import Path
import wx,json
app=wx.App(False)
import pcbnew as p
D=Path(__file__).resolve().parents[2]/'hardware/Soil_pH_AFE';b=p.LoadBoard(str(D/'Soil_pH_AFE_repair.kicad_pcb'));mm=p.FromMM
V=lambda xy:p.VECTOR2I(mm(xy[0]),mm(xy[1]))
f=next(f for f in b.GetFootprints() if f.GetReference()=='U1')
for no,net,xy in [('14','+3V3_A',(119.6,116.025)),('10','GND_A',(120.8,118.625))]:
 pad=next(a for a in f.Pads() if a.GetNumber()==no);t=p.PCB_TRACK(b);t.SetStart(pad.GetPosition());t.SetEnd(V(xy));t.SetLayer(p.F_Cu);t.SetWidth(mm(.2));t.SetNet(pad.GetNet());t.SetLocked(True);b.Add(t)
 v=p.PCB_VIA(b);v.SetPosition(V(xy));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetNet(pad.GetNet());v.SetLocked(True);b.Add(v)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'Soil_pH_AFE_repair.kicad_pcb'),b)
(D/'Soil_pH_AFE_repair.kicad_pro').write_text((D/'Soil_pH_AFE.kicad_pro').read_text());(D/'Soil_pH_AFE_repair.kicad_dru').write_text((D/'Soil_pH_AFE.kicad_dru').read_text())
