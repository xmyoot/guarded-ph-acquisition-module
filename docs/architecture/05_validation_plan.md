# Validation and bring-up plan

**Execution status: every physical test below is NOT RUN.** No board exists. Thresholds are proposed prototype acceptance criteria, not recorded results or customer specifications.

Equipment: current-limited low-noise 5 V supply, calibrated DMM, oscilloscope/logic analyzer, floating differential voltage source or electrode simulator, clean guarded 100 MΩ and 1 GΩ resistor fixtures, calibrated thermometer, appropriate pH buffers and probe. Document equipment accuracy/calibration dates and fixture leakage. Ordinary DMM/scope inputs load PH_IN severely.

## Before power

Inspect solder joints, polarity, component marks, reference sense wiring, BNC insulation and guard mask windows. Clean/dry the assembly. Check for shorts between power and ground, between guard and input, and between BNC shell and ground. An ordinary continuity test can find shorts but cannot prove teraohm insulation.

Verify all core IC pin/pad mappings against the assembled MPN. Check the package-specific TPS7A20 layout and the supervisor output net. Do not connect a probe until power rails and bias are correct.

## Electrical acceptance sequence

| Test | Method | Proposed acceptance / record |
|---|---|---|
| T01 Supply current | Start at 5 V with 20 mA limit and no host/probe; monitor current and heat | No limit activation; steady core <10 mA allocation; investigate higher draw |
| T02 Rail range | Measure +3V3_A from 4.75–5.25 V input | 3.2505–3.3495 V, allowing DMM uncertainty separately |
| T03 Reference and bias | Measure reference, VCM/VOCM with high-impedance DMM after settling | REF initially within ±0.3% screening band; VCM near REF/2 within 5 mV; no sustained oscillation |
| T04 Startup/brownout | Fast/slow ramps, interrupted ramps, repeated power cycling; scope +3V3_A, AFE_READY and REF | ENABLE held low until reference supply valid; reference recovers; no accepted readings before stable |
| T05 Unpowered interface | Controlled host/module sequencing; watch unpowered rail rise/current | No unintended powered state; revise interface if host pullups inject current |
| T06 I²C integrity | 100 kHz init/readback, measure SDA/SCL rise and low levels | Address 0x40; correct register readback; no NACK/timeouts over 10,000 conversions |
| T07 ADC zero | Short ADC inputs via supported mux diagnostic, then short probe input to probe reference with a clean fixture | Record ADC-only and full-buffer offsets separately; no saturation or oscillation |
| T08 Polarity/range | Floating source at −600, −400, −200, 0, +200, +400, +600 mV relative to VCM | Correct sign; monotonic; no clipping; nominal ±600 mV ≈±19,200 counts |
| T09 Electrical calibration | Fit gain/offset using traceable ±400 mV points; validate separate intermediate/end points | Residual ≤0.5916 mV (0.01 pH equivalent at 25°C) across ±600 mV |
| T10 Noise | Quiet input, 10-minute raw 20 SPS record; also evaluate one-second nonoverlapping means | Proposed ≤100 µV RMS on one-second means; report raw RMS, peak-to-peak, drift and outliers |
| T11 Source impedance | Compare low-Z, 100 MΩ and 1 GΩ source fixtures at zero and ±400 mV | Added 1 GΩ error ≤0.25 mV target at 25°C after fixture correction; log settling time |
| T12 Humidity/cleanliness | Compare cleaned/dried baseline with controlled humidity exposure in intended use envelope | Preserve T09/T11 limits; if environment undefined, report characterization rather than qualification |
| T13 ADC filter/buffer behavior | Step input; observe buffered outputs/ADC settling and spectra | No sustained oscillation; final value returns inside T09 budget; characterize time to settle |
| T14 Disconnect/fault response | Unplug probe, remove reference power, corrupt settings, force I²C failure and saturation | Invalid state for diagnosable faults; document that open probe can remain plausible |
| T15 Thermal drift | Fixed simulated voltage with board/sample at controlled 0, 25 and 50°C | Report calibrated drift separately; no industrial-temperature qualification claimed |

For T11, estimate input-current change as ΔV/ΔR only after correcting fixture leakage, source drift and settling. At 1 GΩ, a 0.25 mV change corresponds to 250 fA total; it does not independently prove the PCB-only 100 fA target. Use a leakage blank/coupon or component subtraction with uncertainty to isolate that contribution.

U3's 1 µF output capacitor changes startup settling relative to no-load datasheet conditions. T04 must include that real capacitor, probe loading and actual power ramp. A nominal 500 ms software wait is a starting policy, not a measured settling guarantee.

## Probe calibration

Use the probe manufacturer's storage/rinsing protocol and fresh certified buffers. Record buffer lot, expiry, temperature and specified temperature-corrected pH. Wait for stable readings rather than a fixed arbitrary dwell. Use at least two calibration points and a separate third check point.

Record fitted slope, offset, slope sign, temperature, standard uncertainty and time. Reject implausible slopes with a threshold derived from the probe supplier's specification; do not invent a universal pass band. Repeatability in one buffer does not establish absolute pH accuracy across soil samples.

For the first prototype, sample temperature comes from an external thermometer entered into the record. Report temperature compensation disabled/assumed whenever no valid sample temperature is available. Soil chemistry and buffer pH temperature dependence are separate from the electrode's Nernst slope.

## System interference matrix

Run first with the floating source, then with a stable probe/buffer setup. Repeat with actual host electronics when the original design becomes available.

| Condition | Compare against quiet baseline |
|---|---|
| Host idle versus sustained Wi-Fi transmit | Mean shift, RMS noise, communication faults |
| DC/DC supplies at minimum/maximum operating load | Ripple correlation and supply/reference stability |
| Motor stopped, starting, PWM sweep and stall/current-limited state | Mean shift, burst errors and reset events |
| USB/charger disconnected versus connected | Ground-loop shift and isolation integrity |
| Other immersed sensor connected/active | Sample-current interaction and offset |
| Isolated interface and isolated power active | Converter spectral pickup, bus margins and shield leakage |

The motor test requires the actual rated motor/driver and safe current limits; no motor type, current or PWM frequency is specified here. Proposed initial electronics target: interference-induced mean shift below 0.2 mV and no resets/data loss. Combined error still must meet T09; passing individual tests does not guarantee the combined worst case.

## Field/production gates

Select an ESD/input-protection approach only with leakage, capacitance and surge data. Test connector strikes and cable transients against an agreed standard/level with proper equipment. Component HBM ratings do not demonstrate connector-level immunity.

Isolation validation requires the recovered working voltage and required insulation class, exact converter/isolator ratings, board spacing and test plan. Do not perform improvised high-voltage testing on the prototype.

A release record must include serial/revision IDs, exact BOM and firmware revision, raw samples, test conditions, calibration coefficients and an explicit pass/fail/not-run row for each requirement. Store failures as evidence; do not erase them by averaging or recalibrating without reporting the change.
