/* Soil pH AFE Rev A - external ESP32-S3, Arduino-ESP32 3.x.
 * Protocol: TI ADS112C04 SBAS894A sections 8.5.3 / 8.6.
 * Host pin numbers are chosen defaults; check your development board pinout.
 * No motor, cloud, or ADC die-temperature compensation is implied.
 */
#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include <math.h>
constexpr int SDA_PIN=8, SCL_PIN=9;
constexpr uint8_t ADC_ADDR=0x40;
constexpr uint8_t CFG[4]={0x02,0x02,0x00,0x00};
Preferences prefs;
struct Calibration { float ph1,e1,ph2,e2,temp; uint32_t id; } cal;
float sampleTemp=NAN; bool calibrated=false; char commandLine[100]; size_t commandLen=0;
const char *fault="STARTUP"; unsigned long lastDiag=0; float refVolts=NAN,railVolts=NAN;
bool command(uint8_t c){Wire.beginTransmission(ADC_ADDR); Wire.write(c); return Wire.endTransmission()==0;}
bool writeReg(uint8_t r,uint8_t v){Wire.beginTransmission(ADC_ADDR);Wire.write(0x40|(r<<2));Wire.write(v);return Wire.endTransmission()==0;}
bool readReg(uint8_t r,uint8_t &v){Wire.beginTransmission(ADC_ADDR);Wire.write(0x20|(r<<2));if(Wire.endTransmission(false))return false;if(Wire.requestFrom(ADC_ADDR,uint8_t(1))!=1)return false;v=Wire.read();return true;}
bool configure(const uint8_t *regs){for(int r=0;r<4;r++)if(!writeReg(r,regs[r]))return false;for(int r=0;r<4;r++){uint8_t v;if(!readReg(r,v)||(v & (r==2?0x7f:0xff))!=regs[r])return false;}return true;}
bool convert(int16_t &code){
 if(!command(0x08)){fault="I2C_START";return false;}
 unsigned long start=millis();uint8_t v=0;
 do {if(!readReg(2,v)){fault="I2C_POLL";return false;}if(v&0x80)break;delay(1);}while(millis()-start<250);
 if(!(v&0x80)){fault="CONVERSION_TIMEOUT";return false;}
 if(!command(0x10)||Wire.requestFrom(ADC_ADDR,uint8_t(2))!=2){fault="I2C_DATA";return false;}
 uint8_t hi=Wire.read(),lo=Wire.read();code=int16_t((uint16_t(hi)<<8)|lo);return true;
}
bool diagnose(){
 // Use internal reference and gain1 for reference/4 and AVDD/4 monitors.
 // This is a broad fault check, not a precision reference calibration.
 int16_t v; uint8_t diag[4]={0xC1,0,0,0};
 if(!configure(diag)||!convert(v))return false; refVolts=v*(2.048f/32768)*4;
 diag[0]=0xD1;if(!configure(diag)||!convert(v))return false;railVolts=v*(2.048f/32768)*4;
 if(!configure(CFG)){fault="CONFIG_READBACK";return false;}
 if(refVolts<1.90f||refVolts>2.15f){fault="REF_MONITOR";return false;}
 if(railVolts<3.15f||railVolts>3.45f){fault="RAIL_MONITOR";return false;}
 fault="OK";lastDiag=millis();return true;
}
void serialCommand(){
 while(Serial.available()){
  char ch=Serial.read();if(ch=='\r')continue;
  if(ch!='\n'){if(commandLen<sizeof(commandLine)-1)commandLine[commandLen++]=ch;else commandLen=0;continue;}
  commandLine[commandLen]=0;commandLen=0;float a,b,c,d,t;
  if(sscanf(commandLine,"temp %f",&t)==1&&isfinite(t)&&t>=0&&t<=50){sampleTemp=t;Serial.println("# sample temperature set; use a calibrated external thermometer");}
  else if(sscanf(commandLine,"cal %f %f %f %f %f",&a,&b,&c,&d,&t)==5&&isfinite(a)&&isfinite(b)&&isfinite(c)&&isfinite(d)&&isfinite(t)&&a>=0&&a<=14&&c>=0&&c<=14&&fabsf(c-a)>=1&&fabsf(d-b)>=20&&fabsf(b)<=600&&fabsf(d)<=600&&t>=0&&t<=50){
   float slope=fabsf((d-b)/(c-a));
   if(slope<40||slope>70){Serial.println("# rejected: calibration slope outside 40..70 mV/pH");continue;}
   cal={a,b,c,d,t,cal.id+1};calibrated=prefs.putBytes("cal",&cal,sizeof(cal))==sizeof(cal);Serial.println(calibrated?"# calibration saved":"# storage error");
  }else if(!strcmp(commandLine,"clear")){prefs.remove("cal");calibrated=false;Serial.println("# calibration cleared");}
  else Serial.println("# commands: temp <C> | cal <pH1> <mV1> <pH2> <mV2> <cal_C> | clear");
 }
}
void setup(){
 Serial.begin(115200);Wire.begin(SDA_PIN,SCL_PIN,100000);Wire.setTimeOut(50);prefs.begin("soil-ph",false);
 if(prefs.getBytesLength("cal")==sizeof(cal)){prefs.getBytes("cal",&cal,sizeof(cal));float slope=fabsf((cal.e2-cal.e1)/(cal.ph2-cal.ph1));calibrated=isfinite(slope)&&slope>=40&&slope<=70&&fabsf(cal.ph2-cal.ph1)>=1&&cal.temp>=0&&cal.temp<=50;}
 delay(600); // includes supervisor maximum delay, then reference settling allowance
 if(!command(0x06))fault="I2C_RESET";else if(!diagnose())fault="STARTUP_DIAGNOSTIC";
 Serial.println("# Soil pH AFE Rev A; raw mV remains uncalibrated electronics measurement");
 Serial.println("ms,code,raw_mV,ph,sample_C,cal_id,status,ref_V,rail_V");
}
void loop(){
 serialCommand();
 if(strcmp(fault,"OK")){Serial.printf("%lu,,,,,%lu,%s,%.4f,%.4f\n",millis(),(unsigned long)cal.id,fault,refVolts,railVolts);delay(1000);if(command(0x06))diagnose();return;}
 if(millis()-lastDiag>=60000&&!diagnose()){fault="PERIODIC_DIAGNOSTIC";return;}
 int16_t code;if(!convert(code))return;
 float mv=code*0.03125f;const char *status="OK";float ph=NAN;
 // ±600mV is the designed electrode envelope; invalidate, never clamp.
 if(fabsf(mv)>600)status="OUTSIDE_INPUT_ENVELOPE";
 else if(!calibrated)status="UNCALIBRATED";
 else if(!isfinite(sampleTemp))status="SAMPLE_TEMP_UNKNOWN";
 else if(fabsf(sampleTemp-cal.temp)>2)status="RECALIBRATE_AT_SAMPLE_TEMP";
 else {ph=cal.ph1+(mv-cal.e1)*(cal.ph2-cal.ph1)/(cal.e2-cal.e1);if(ph<0||ph>14){ph=NAN;status="OUTSIDE_CALIBRATED_PH";}}
 Serial.printf("%lu,%d,%.5f,%.4f,%.2f,%lu,%s,%.4f,%.4f\n",millis(),code,mv,ph,sampleTemp,(unsigned long)cal.id,status,refVolts,railVolts);
}
