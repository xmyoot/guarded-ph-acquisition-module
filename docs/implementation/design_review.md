# Rev A design review

**21 October 2026 · scope: unbuilt, nonisolated bench pH acquisition module**

## Verdict and open gates

No unresolved CAD connectivity defect or obvious package/pin mismatch was identified in this review. The native schematic and PCB pass KiCad ERC and schematic-parity DRC. This supports a controlled first-article build; it does **not** establish functional performance, production readiness, environmental suitability or electrical safety isolation.

| Priority | Finding | Disposition |
|---|---|---|
| Field release blocker | No onboard isolation; driven BNC shell is not grounded | Bench use only with floating sample. Product integration needs qualified isolated power/I²C and mechanical insulation. |
| Field release blocker | PH_IN has no ESD clamp or connector filter | Intentional to avoid unqualified leakage; handle in controlled ESD conditions. Develop and measure a field protection solution separately. |
| Hardware acceptance gate | Leakage, guard stability, high-source-resistance settling | Unmeasured. Clean/dry both faces and measure with guarded fixtures at temperature/humidity. |
| Hardware acceptance gate | Noise, linearity, startup and reference stability | Calculations and configuration review only. Follow bring-up tests; no accuracy claim. |
| Hardware acceptance gate | Connector fit, crimp, solder process and MLCC effective capacitance | Drawings reviewed; real-part fit and process still pending. |
| Portfolio disclosure | Complete original soil instrument not reconstructed | Present as a pH analog front-end engineering prototype. No motor, battery, radio, onboard ESP32 or original Altium retrofit claimed. |

## Evidence and native checks

Final CAD: hardware/Soil_pH_AFE/Soil_pH_AFE.kicad_sch and .kicad_pcb. Review/export command records are in analysis/export_commands.json; native reports in analysis/native.

| Check | Final result / basis |
|---|---|
| Native schematic ERC | 0 errors, 0 warnings |
| Native PCB DRC + schematic parity | 0 violations, 0 unconnected pads, 0 footprint/parity errors |
| Native netlist → PCB | Every pad of all 39 schematic components matches; values/MPNs also match construction inventory |
| Physical parts | 28 purchased parts, 17 unique MPNs; 11 PCB test pads. Board additionally has 2 mounting holes and 3 fiducials (44 total footprints). |
| Input copper | 4.143 mm top-only PH_IN, zero vias; guard copper unchanged from locked placement baseline |
| Input ground exclusion | Raw filled foreign-zone polygon intersection with PH_IN is zero, on both faces; keepout enforces future pour exclusion |
| Via/paste audit | 47 ordinary through vias; zero intersections with component paste apertures |
| Manufacturing geometry | Routed widths 0.20/0.25/0.35/0.40 mm; vias 0.60/0.30 mm; native 0.20 mm clearance and 0.30 mm edge constraints |
| Fabrication export | Nine Gerber layers, separate PTH/NPTH Excellon files, drill maps/report, job metadata; independently parsed |
| Firmware | Arduino-ESP32 3.3.12 ESP32-S3 compile succeeded (329705 bytes flash, 23200 bytes RAM); no physical execution |

The independent audit is scripts/validate_release.py; its full record is analysis/connectivity_and_geometry.json. Critical pin data were manually transcribed from manufacturer PDFs, not inferred from symbol names. The extraction cache is partial: it does not establish all dynamic behavior, noise, stability or process limits. For final geometry checks, the raw KiCad-10 string net names take precedence over third-party parser net indices.

## Per-IC and connector review

| Part | Manufacturer basis and implementation review |
|---|---|
| U1 LMP91200MTX/NOPB | SNAS571E p.3 pin functions, pp.14–17 buffer/guard application. Pins 1/14 supply; 10/13/15/16 ground; 4/6 guard; 5 input; 8 probe-reference VCM; 9 external reference; 11/12 buffered outputs. Pins 2/3 and high-impedance VCMHI left open. Guard is not BNC shell or chassis ground. |
| U2 ADS112C04IPWR | SBAS894A p.3 PW package, pp.23–25 low-gain input limits, pp.35–45 address/protocol/registers. Address straps grounded, reset tied to delayed READY, unused AIN2/3 grounded, REFN grounded, REFP 2.048 V, AIN0/1 differential. Registers 02 02 00 00 select gain2/external reference/20 SPS; burnout/IDAC off. |
| U3 REF3220AIDBVT | SBVS058D p.3 pin table and enable/startup guidance. Both ground pins connected; output force/sense terminate at C11. The sense/force ground connections use the shared local plane and are not separately Kelvin-routed. Enabled only after 3.3 V supervisor release. |
| U4 TPS7A2033PDBVR | SBVS338H p.4 DBV pin map; p.6 thermal data and output-capacitance requirements. IN/EN to 5 V, ground pin2, NC pin4, output pin5. Nominal 4.7 µF output selected for ≥1 µF effective requirement; manufacturer bias curves/actual stability remain qualification items. |
| U5 TPS3839K33DBZT | SBVS193D DBZ pin map and threshold/delay table. Ground1, push-pull reset2, supply3. 2.93 V nominal threshold, 120–350 ms delay; READY enables reference/releases ADC reset. R8 controls initial undefined low-voltage interval. No unsafe assumption that reset release means reference settled: firmware waits and diagnoses. |
| J1 | Amphenol 031-5431-1010 Rev E drawing. Signal/shell offset 2.54 mm; fork positions ±5.08 mm and −5.08 mm. Insulated BNC, deliberate left-edge overhang. Holes enlarged to 1.0/2.1 mm. All shell/fork pads connect to PH_VCM. Detailed connector/enclosure fit is pending real-part trial; 3D body is only an envelope. |
| J2 | JST PH drawing: 2 mm six-position header, 0.75 mm PCB holes. Pin1=5 V, 2/5=ground, 3=SDA, 4=SCL, 6=NC. Cable pin mapping must be checked from PCB numbering, not mirrored mating view. |

Passive inventory, sizes and pin nets match the final BOM and frozen footprints. R1/R2 are 1 kΩ 0.1% parts; C13 is 10 nF C0G; R3/R4 are 4.7 kΩ pullups through removable R5/R6 0 Ω links. All ceramic supply capacitors are X7R with specified voltage ratings. Manufacturer curves and production availability were not exhaustively qualified for every passive; correct assembly and effective capacitance remain first-article checks.

## Electrical calculations and thermal bounds

Nominal VCM is 1.024 V. At ±600 mV input, VOUT spans 0.424–1.624 V and VOCM stays near 1.024 V. With 10 mV allocated common-mode uncertainty and 3.2505 V minimum analog rail, ADS112C04 Equation 6 retains 214 mV lower margin at gain2. Differential range is ±1.024 V. Calculated LSB is 31.25 µV, or 0.000528 pH equivalent at 25°C; neither is an accuracy specification.

The 2 kΩ differential source resistance and 10 nF capacitor give 7.96 kHz. This is an RF/interference pole, not a 10 Hz anti-alias brick wall. Test modulator-alias interference and settling after diagnostic mux changes. Reference initial ±0.2% error alone is ~1.2 mV at 600 mV, exceeding the 0.01 pH objective before calibration. Two-point calibration cannot remove variable leakage, temperature error or probe aging.

At worst proposed input 5.25 V and lower analog rail 3.2505 V, LDO dissipation is approximately 20 mW at the allocated 10 mA and 100 mW at 50 mA. Datasheet DBV θJA=187.1°C/W gives approximate rises of 3.7°C and 18.7°C. These JEDEC-board estimates are not actual-board measurements and exclude small regulator quiescent dissipation. Measure current and temperature; 50 mA is connector allocation, not a measured operating draw. Automated thermal analysis ran but assessed zero components because it lacked a quantifiable dissipation estimate; its empty findings are not a thermal pass.

## Analyzer triage

All final analyzer outputs are under analysis/final. They remain visible, including generic warnings; this table records engineering disposition instead of suppressing them globally.

| Analyzer finding | Raw-file check and disposition |
|---|---|
| PU-001 missing SDA/SCL pullups | False positive: R3/R4 reach 3.3 V through R5/R6 links. Measure actual rise time and combined host pullups. |
| KO-001 guard vias/J1 in keepout | Parser treats a pour-only area as an absolute keepout. Raw flags explicitly allow footprints/tracks/vias and prohibit pours; custom net rule prevents foreign tracks/vias. Four guard vias are intentional. |
| PM-002 J1 edge overhang | Intentional edge connector, checked against drawing. Enclosure/mating fit remains open. |
| PM-002 FID3 0.75 mm from edge | Assembly-process recommendation, native copper-edge rule passes. Assembler may require rails/panel fiducials. |
| TE-001 test coverage 8/19 | Generic count misses the purpose of the 11 low-impedance test pads. PH_IN deliberately has no test stub; NC/guard nets are not ordinary probe points. |
| RP-002 / PS-002 “3.3 V plane split” | KiCad-10 net-index interpretation error. Raw PCB contains only two GND_A pours; there is no +3V3_A plane. Do not add capacitors to an imaginary split plane. |
| EMC GP-001 input plane gaps / BE-002 incomplete edge ground | Input and driven probe-reference region deliberately exclude ground. Ordinary continuous-ground advice conflicts with the guarded input. Return path/interference risk on other routes still needs measurement. |
| EMC IO-001 no J1 filtering | True and accepted only for controlled bench scope. Field protection is a release blocker, not a dismissed false positive. |
| EMC RP-001 transition stitching | Guard must not be stitched to ground. Other analog and 100 kHz I²C returns have no characterized EMC margin; evaluate physical interference rather than treating heuristic severity as a compliance result. |
| EMC DP-001 / DP-003 skew/layer changes | ADC_P/N are slow analog signals with a 7.96 kHz external pole, not a timing-critical high-speed differential bus. Layer changes do not imply protocol failure; noise/settling still require hardware. |
| GR-002 layer extents differ | Top/bottom copper need not fill identical bounding boxes because the input is guarded. Common coordinates, holes and outline align in independent Gerbonara renders; nominal outline is 50×35 mm (50.05×35.05 including line stroke). |
| Gerbonara G90 warning | Parser accepts KiCad Excellon files but warns about G90 after the header. Both drill files parse with a total of 59 holes; inspect drill maps with the fabricator. |

The EMC heuristic score is not an immunity/emissions test or a compliance rating. No compliance claim is made.

## DRC/ERC exceptions

The only custom ignored rule is the intentional bridged solder-mask opening at the guard rectangle position (110.1,115.15 mm) on F.Mask/B.Mask. Electrical clearance is not waived. The guard-cell net restriction forbids foreign tracks/vias while allowing PH_IN and PH_GUARD.

Project-level ignored DRC categories are missing courtyard, track endpoint centering on via, tuning-profile geometry, footprint filters and component-type mismatch; these are disclosed in the native report. PCB-only holes/fiducials/test features and frozen custom symbols need manual package/geometry review, which was performed as described above. ERC ignores single-use global labels, four-way joins, SPICE model issues and footprint filters. Therefore “0 violations” means zero enabled native checks, not absence of all possible manufacturing concerns.

## Previous review delta and corrections

The earlier review found vias overlapping C4/C7 solder-paste apertures. The offending vias were removed, the C4 ground connection moved outside paste, adjacent ADC routing adjusted and clearance rechecked. Final geometry finds zero overlaps; native DRC/parity pass.

Stale architecture-only README, stale manufacturing exports, a 0 Ω BOM tolerance note, missing implementation/bring-up instructions and machine-specific export setup were corrected before publication. Intermediate board variants were removed from the main CAD folder. The raw client screenshot folder is excluded from public publication; the technical requirement summary remains.

A kicad-happy cache run reused the earlier PCB result while updating its source hash. Fresh explicit final output files were used to avoid relying on that cache. Generic prior-diff reported no changes, which does not capture these local route edits; that delta result is not accepted as proof. Native final checks and the independent geometric audit are the final basis. No earlier deep-review file existed.

## Coverage, lifecycle and skipped analyses

Ran: schematic analyzer; full PCB analyzer; cross-analysis; EMC; thermal (unquantified/skipped result); Gerber analyzer; native ERC/DRC/parity/export; raw pad-net/geometry audit; partial PDF pin cross-reference; firmware compile; calculation script; independent Gerber parse/render; visual schematic/3D review. The evidence-linked manual deep-review pass is in analysis/deep_review.json.

Lifecycle audit was attempted on the earlier same core BOM using LCSC only; it returned unknown status and no usable lifecycle source. It omitted/failed to classify the connector, so it is not a complete sourcing audit. TI core-part manufacturer pages were consulted during implementation, but live stock, all passive/connector lifecycle states and substitutes remain purchase-time checks. No pricing/availability guarantee.

SPICE not run: ngspice, LTspice and Xyce were unavailable. Numerical range/filter/leakage checks are calculations, not simulations. No complete transistor-level buffer/guard dynamic model is asserted. No bench tests, EMC/ESD tests, humidity qualification, calibrated probe measurements, assembly inspection or original-product integration could be completed without physical hardware/original files. Follow bringup.md before making performance or field-readiness claims.
