# Rev A implementation decisions

21 October 2026. Final native CAD and output/assembly/BOM.csv supersede the Phase 1 proposal.

| Decision | Rationale / consequence |
|---|---|
| Standalone 50 × 35 mm bench daughterboard | Missing original CAD prevents an honest product retrofit. ESP32-S3, motor, battery and isolation remain external. |
| LMP91200MTX/NOPB | Correct TSSOP-16 orderable suffix; package-compatible substitution requires lifecycle and electrical review. |
| ADS112C04IPWR, A0/A1 grounded | 7-bit address 0x40; PGA enabled, total gain 2, AIN0–AIN1, external reference, 20 SPS. Do not use ADS1115 firmware. |
| REF3220AIDBVT | 2.048 V reference. Force/sense output branches meet at the ADC reference capacitor; ground force/sense share the local ground plane. This is not a separate four-wire ground-return layout. |
| TPS3839K33DBZT supervisor | 2.93 V nominal threshold, 120–350 ms delay. Drives reference enable and ADC reset; 100 kΩ pulldown controls early startup. Selected operating range ends at +85°C; sample target is 0–50°C. |
| TPS7A2033PDBVR LDO | 5 V input, 3.3 V output; 4.7 µF 25 V X7R input/output capacitors. Effective output capacitance and transient stability still require qualification. |
| Amphenol 031-5431-1010 insulated BNC | Pin pattern checked against manufacturer drawing Rev E. Signal/shell holes 1.0 mm, fork holes 2.1 mm; intentional edge overhang. Verify real connector fit before batch assembly. |
| JST B6B-PH-K-S(LF)(SN) | Keyed six-position 2 mm host interface. PHR-6 housing and five SPH-002T-P0.5S contacts; pin 6 empty. Check wire gauge and crimp tooling against JST drawing. |
| Guard width 0.35 mm near input | Practical TSSOP packing replaces proposed 0.5 mm width; short input and continuous driven guard take priority. Guard vias only; PH_IN has none. |
| No PH_IN test pad, clamp or ordinary TVS | Parasitic leakage would consume the femtoampere input budget. This is an explicitly unprotected bench input, not field-qualified connector protection. |
| Omit optional C14/C15 sites | No populated common-mode shunt capacitors; keeps minimal baseline and avoids an unqualified loading change. |
| Autoroute buffered analog nets | Unlike the initial all-manual analog plan, low-impedance analog and digital nets were routed using KiCadRoutingTools. PH_IN, guard, and reference branches were locked/manual and geometry checked after routing. |
| Router manufacturing limits held fixed | 0.20 mm minimum routing/clearance, 0.60/0.30 mm vias, no automatic relaxation/escalation. Native DRC is the final connectivity gate. |
| No vias in paste apertures | Two overlap sites identified during review were removed; ground connection and adjacent ADC routes corrected. Final independent geometry audit finds none. |
| No solder mask over guard cell | Intentional openings on both faces require one narrowly scoped bridged-mask rule exception. Electrical clearance is unchanged. |
| Explicit temperature / two-point calibration | External calibrated sample thermometer required. Firmware never treats ADC die temperature as sample temperature, and does not implement automatic temperature compensation. |

The reference/rail monitor is a broad fault diagnostic, not traceable calibration. Firmware stores calibration in ESP32 NVS and emits raw readings even before valid pH calibration. One-second display averaging remains a host application task; the sketch logs individual conversions.

No cost or live-stock guarantee is attached to the BOM. Reel/tape carrier alternatives (for example ADS112C04IPW vs IPWR, REF3220AIDBVR vs AIDBVT) require matching package and electrical grade; no substitute is automatically approved for the high-impedance buffer or connector.

## Portfolio review correction — 21 October 2026

KiCadRoutingTools octolinear smoothing was applied with 0.20 mm clearance and 0.30 mm edge clearance. Final routed segment count fell from 352 to 257 (95 fewer), with 8.203 mm shorter total track length. All locked tracks, the input/guard and reference routes were preserved. A candidate PH_VCM shortcut violated the net-specific guard-cell rule during native DRC and was reverted; the final output passes native DRC/parity and the independent guard/paste audit.

The old BNC model used Box/Cylinder VRML primitives. Its cylinders failed to display in the initial KiCad render, leaving only a white rectangular body. It was replaced with explicit face meshes representing the insulated housing, metal shoulder/threaded section, bayonet barrel, opposed lugs, open socket, contact and PCB tails. Overall 34.7 mm length, 14.5 mm width, housing height and pin positions follow the reviewed Rev E drawing. Small thread/bore/contact details are illustrative. This improves visualization; it is not first-article mechanical validation.
