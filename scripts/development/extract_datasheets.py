"""Reviewed partial legacy cache. Facts transcribed from archived TI PDFs.
Missing fields stay missing and are scored by kicad-happy, not invented.
"""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[2]
S=Path('/Users/hector/Documents/KiCAD_Projects/ESP32_C6_EPaperDisplayDriver/tools/kicad-happy/skills/datasheets/scripts');sys.path.insert(0,str(S))
from datasheet_extract_cache import cache_extraction,validate_v2_extraction
from datasheet_score import score_extraction
# Pinouts are independently transcribed from manufacturer pin tables.
D=[('LMP91200MTX/NOPB','LMP91200','sensor','TSSOP-16 PW',3,['VDD','NC','NC','GUARD1','INP','GUARD2','VCMHI','VCM','VREF','GND','VOCM','VOUT','GND','VDD','GND','GND'],1.8,5.5,6,{'input_bias_fa_25C_max':125},'VDD bypass: 10uF,1uF,100nF; both guards; no connection NC pins; see sections 8-10'),('ADS112C04IPWR','ADS112C04','adc','TSSOP-16 PW',3,['A0','A1','RESET','DGND','AVSS','AIN3','AIN2','REFN','REFP','AIN1','AIN0','AVDD','DVDD','DRDY','SDA','SCL'],2.3,5.5,7,{'resolution_bits':16,'external_reference_min_v':.75},'100nF on each supply; pullup SDA,SCL,DRDY; sections 8.5,8.6 and 11'),('REF3220AIDBVT','REF3220','voltage_reference','SOT23-6 DBV',3,['GND_F','GND_S','ENABLE','IN','OUT_S','OUT_F'],2.10,5.5,7.5,{'vref_v':2.048,'initial_accuracy_pct':.2},'Connect force and sense at load; ENABLE low during slow input ramp; sections 6.1.1,7'),('TPS7A2033PDBVR','TPS7A20','linear_regulator','SOT23-5 DBV',4,['IN','GND','EN','NC','OUT'],1.6,6,6.5,{'vref_v':3.3,'quiescent_current_ua':6.5,'output_current_max_ma':300,'dropout_mv':145},'CIN,COUT effective >=1uF; EN to IN for always on; DBV pin table p4'),('TPS3839K33DBZT','TPS3839','power_management','SOT23-3 DBZ',5,['GND','RESET','VDD'],.9,6.5,7,{'threshold_typ_v':2.93,'reset_delay_min_ms':120,'reset_delay_max_ms':350},'0.1uF VDD bypass; reset push-pull; pin functions p5, timing p8')]
for mpn,pdf,cat,pkg,page,names,vmin,vmax,absmax,ec,app in D:
 pins=[]
 for i,name in enumerate(names,1):
  typ='no_connect' if name=='NC' else 'ground' if name in ['GND','GND_F','GND_S','DGND','AVSS'] else 'power' if name in ['VDD','AVDD','DVDD','IN'] else 'digital' if name in ['RESET','ENABLE','EN','SCL','SDA','DRDY','A0','A1'] else 'analog'
  pins.append(dict(number=str(i),name=name,type=typ,description=f'{pdf} manufacturer pin function table p{page}; {name}',direction='input' if typ=='power' else 'passive' if typ in ['ground','no_connect'] else None,required_external='Do not connect' if typ=='no_connect' else None))
 e=dict(mpn=mpn,manufacturer='Texas Instruments',category=cat,package=pkg,description=pdf,topology='ldo' if cat=='linear_regulator' else 'adc' if cat=='adc' else 'other',pins=pins,absolute_maximum_ratings={'vin_max_v':absmax,'junction_temp_max_c':85 if pdf=='TPS3839' else 150},recommended_operating_conditions={'vin_min_v':vmin,'vin_max_v':vmax,'temp_min_c':-40,'temp_max_c':85 if pdf=='TPS3839' else 125},electrical_characteristics=ec,application_circuit={'notes':app,'source_section':'See pin table and application/layout sections in archived PDF'},extraction_metadata={'source_pdf':pdf+'.pdf','method':'Manual transcription; partial facts; manufacturer PDF is authoritative','pin_table_page':page})
 e['extraction_metadata']['quality']=score_extraction(e,len(names));e['extraction_metadata']['extraction_score']=e['extraction_metadata']['quality']['total']
 assert not validate_v2_extraction(e)
 cache_extraction(R/'datasheets/extracted',mpn,e,R/'datasheets'/f'{pdf}.pdf')
 print(mpn,e['extraction_metadata']['quality'])
