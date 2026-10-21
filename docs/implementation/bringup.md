# Bring-up and acceptance plan

Rev A, 21 October 2026. **Every physical step below is pending.** Record serial number, board revision, firmware hash, instruments, ambient/sample temperatures and results. Targets are engineering acceptance objectives, not measured specifications.

## Equipment and wiring

Use a current-limited isolated bench supply, DMM, oscilloscope for low-impedance nodes only, external ESP32-S3 development board, a floating battery-powered precision voltage simulator, shielded/guarded high-value resistors and fresh pH buffers. A conventional grounded generator can short the driven BNC shell to earth; use an appropriate floating source.

J2 (PCB pin numbering): 1 +5 V, 2 ground, 3 SDA, 4 SCL, 5 ground, 6 NC. Host defaults are GPIO8 SDA / GPIO9 SCL at 100 kHz; adapt these to the specific development board. Power the ESP32-S3 from its own USB supply. I²C is 3.3 V open drain; never apply 5 V logic. Power down before changing wiring. Do not drive an unpowered module. Keep host cable short and start with only the local 4.7 kΩ pullups; remove R5/R6 if host pullups make the combined pullup excessive.

J1 center = PH_IN; shell = driven PH_VCM (~1.024 V), not ground. Only a floating sample, no additional grounded or conductive sensor connection. Product integration needs qualified isolation outside this board.

## 1. Unpowered inspection

Check package orientation, solder bridges, misplaced values and both guard faces. Measure input-supply resistance for hard shorts, allowing capacitors to charge. Confirm BNC shell is isolated from chassis/ground mechanically and electrically; do not apply a high-voltage insulation tester to attached ICs. Do not expect resistance measurements across the input buffer to characterize femtoampere leakage.

## 2. First power

Disconnect host signals and electrode. Apply 5.0 V with a 20 mA current limit. Stop if the supply limits or any part warms unexpectedly; 10 mA is an allocation, not a measured limit. Do not raise the limit to conceal a fault.

| Test pad | Net | Initial expectation |
|---|---|---|
| TP1 | GND_A | Measurement reference |
| TP2 | +5V_IN | 4.75–5.25 V |
| TP3 | +3V3_A | Approximately 3.3 V; 3.2505–3.3495 V preliminary ±1.5% bound |
| TP4 | REF_2V048 | Approximately 2.048 V, after delayed enable; check with calibrated DMM |
| TP5 | PH_VCM | Approximately 1.024 V |
| TP6 | PH_VOUT | Floating input may be arbitrary; not a useful open-probe diagnostic |
| TP7 | PH_VOCM | Approximately 1.024 V |
| TP8 | AFE_READY | Low during startup, then near 3.3 V |
| TP9 / TP10 | SDA / SCL | Idle near 3.3 V with powered host attached |
| TP11 | ADC_DRDY_N | Conversion data-ready observation |

Scope 3.3 V, READY and reference simultaneously. Confirm delay (120–350 ms after the supervisor threshold), monotonic reference settling and no ADC acceptance before firmware diagnostics pass. Exercise fast/slow ramps, power interruption and brownout. Test load steps and capacitor DC-bias/temperature effects; confirm the LDO's effective output capacitance requirement. Measure rail ripple with short probe grounding.

## 3. Firmware and electrical conversion

Install Arduino-ESP32 3.x (implementation compiled with 3.3.12), select the actual ESP32-S3 board, and build/upload firmware/SoilPH_Bringup/SoilPH_Bringup.ino. Serial is 115200 baud; USB CDC settings depend on the host board. Prior compile evidence is retained; no board has been flashed/tested for this design.

The sketch resets ADS112C04 at address 0x40, writes/readbacks register image **02 02 00 00**, waits 600 ms at startup, and polls DRDY with a 250 ms conversion timeout. It uses single-shot nominal 20 SPS, differential AIN0–AIN1, gain 2 and external 2.048 V reference. Sample interval includes polling/serial overhead, so exact 20 Hz output is not guaranteed. Reference/4 and AVDD/4 diagnostics use the internal reference and repeat every 60 seconds. Diagnostic windows (1.90–2.15 V reference; 3.15–3.45 V rail) are broad fault checks.

Apply a floating voltage source between J1 center (+) and shell (−), initially low impedance. Never drive outside ±600 mV relative to the shell. Measure source voltage independently.

| Applied voltage | Ideal code | Reported raw mV |
|---|---:|---:|
| −600 mV | −19200 | −600 |
| −300 mV | −9600 | −300 |
| 0 | 0 | 0 |
| +300 mV | +9600 | +300 |
| +600 mV | +19200 | +600 |

Log at least 60 seconds at each point. Fit offset/gain, check monotonicity and hysteresis, and measure residuals rather than comparing to ideal codes as an uncalibrated accuracy requirement. The proposed calibrated residual objective is ≤591.6 µV (0.01 pH equivalent at 25°C), not yet demonstrated. Quantify noise both per sample and with an explicitly defined one-second average. Check settling after source steps and reference diagnostic mode changes.

## 4. Leakage and interference

Repeat source tests through 100 MΩ and 1 GΩ guarded resistors using suitable fixtures. Account for resistor tolerance, settling, source leakage and instrument loading. Compare low/high source-resistance offsets and repeat after cleaning, drying, handling and controlled humidity/temperature exposures. Additional board/connector leakage allocation is ≤100 fA (100 µV at 1 GΩ); a casual DMM measurement cannot prove this. Guard tracking and capacitance stability also need measurement.

Compare records with ESP32 radio off/on, host activity, cable movement and representative external motor/converter operation. No motor/converter exists on this module. Measure I²C rise times: predicted ~398 ns at 100 pF and ~796 ns at 200 pF with 4.7 kΩ; do not assume 400 kHz support. Assess ground return and RFI experimentally. Do not conduct field ESD tests without a protection strategy; input protection is absent by design.

## 5. Probe calibration

After electronics checks, connect a passive combination pH electrode and a calibrated external sample thermometer. Use fresh buffers spanning the intended sample range and the buffer manufacturer's temperature table. Allow the probe to equilibrate; rinse between solutions, blot according to probe instructions, and record stable raw mV.

Serial commands (newline terminated):

```text
temp 25
cal 7.00 0.10 4.00 177.60 25
clear
```

The numbers are syntax examples only; replace them with actual buffer pH, observed mV and measured temperature. Calibration supports either polarity, checks a 40–70 mV/pH slope, and stores two points in host NVS. Reported pH uses the measured slope/intercept. It is invalid until calibration and sample temperature are provided, outside 0–14 pH or ±600 mV, or if sample temperature differs from calibration by more than 2°C. There is no automatic temperature compensation. Test an independent third buffer and repeatability/drift before assigning probe-system accuracy. Open probes can retain plausible voltages; the firmware cannot reliably detect that condition.

## Faults and release gate

No I²C response: inspect J2 pin orientation, common ground, power, pullups, GPIO selection and 0x40 address. Reference/rail fault: inspect U3/U4/U5, capacitor values and startup waveform. Large offset only with high source resistance: investigate cleanliness, guard tracking, connector leakage and fixture leakage before software correction. Unstable pH: check floating-sample requirement, probe hydration, settling, sample temperature and interference.

The next release needs measured noise/linearity/leakage/startup records, first-article connector fit, thermal/current results and independent probe calibration. Field deployment additionally requires engineered isolation, ESD/EMC protection and enclosure/environment qualification. None is claimed complete here.
