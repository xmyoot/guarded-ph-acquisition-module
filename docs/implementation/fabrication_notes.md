# Rev A fabrication and assembly notes

**Engineering prototype only. No board has been manufactured or tested.** Review the hardware acceptance plan before ordering a batch. Files correspond to the native CAD checked on 21 October 2026.

## Fabrication specification

| Item | Requirement |
|---|---|
| Outline | 50.00 × 35.00 mm, closed Edge.Cuts centerline; drawing stroke can produce 50.05 × 35.05 mm bounding boxes |
| Stack | Two copper layers, 1.6 mm nominal FR-4, 1 oz copper per layer |
| Finish | ENIG preferred for exposed guards/test pads; do not coat the guard/input region without leakage qualification |
| Copper rules | Minimum trace/clearance 0.20/0.20 mm; copper to edge 0.30 mm |
| Vias | Standard through vias, pad 0.60 mm / finished hole 0.30 mm; no filled or capped via-in-pad process required |
| Component holes | BNC signal/shell 1.0 mm and retention forks 2.1 mm; JST 0.75 mm; verify drill report |
| Mounting | Two 2.2 mm NPTH mounting holes, for M2 hardware; check washer/enclosure clearance |
| Mask | Both faces include intentional rectangular guard openings. Preserve them; no paste in exposed guard area. |
| Stencil | Top only; 100–120 µm candidate, subject to assembler paste/process review. No bottom SMD components. |
| Impedance | No controlled-impedance requirement |

Gerber X2 includes F/B copper, solder mask, paste, silkscreen and Edge.Cuts. Excellon files separate plated and nonplated holes; both must be supplied. PDF drill maps are visual aids. Empty bottom paste is expected. Bottom silkscreen carries the insulated-BNC/cleanliness notes. Do not rescale the Gerbers to match the nominal outline.

The BNC intentionally projects beyond the left board edge. Its drawing-derived VRML connector model includes the threaded barrel, lugs, socket and housing, but remains a visualization aid rather than a tolerance-qualified mechanical acceptance model. Confirm panel, cable, shell insulation, fork solderability and first-article fit with real parts. FID3 has 0.75 mm edge clearance to its footprint; panel-level fiducials/rails may be needed for assembly equipment. Placement CSV coordinates and rotations must be checked in the assembler's viewer against the top assembly drawing; they are native KiCad conventions, not a turnkey machine program.

## Assembly

1. Verify BOM package suffixes and pin-1 orientation, especially the two TSSOP-16 ICs (opposite board rotations), SOT-23 regulators/reference/supervisor and J2 pin 1.
2. Reflow top SMD parts with a qualified profile. Fit the through-hole JST and BNC with the process suitable for their plastics; hand solder after reflow if needed.
3. Avoid solder/flux trapped beneath the BNC and buffer input. Clean the guarded region and both board faces with a validated electronics cleaning process, rinse/dry as appropriate to chemistry, and inspect at magnification. “No-clean” flux is not evidence of sufficiently low leakage.
4. Keep fingerprints, ordinary adhesive, conformal coating and grounded metal away from the exposed input/guard cell. Do not probe PH_IN with an ordinary oscilloscope probe.
5. Carry out the bring-up sequence before attaching a real probe. Do not power the host from the module's 3.3 V rail.

Sourcing, panelization, stencil thickness, component effective-capacitance curves, and actual assembly yield have not been qualified. No fabrication or assembly order has been placed.
