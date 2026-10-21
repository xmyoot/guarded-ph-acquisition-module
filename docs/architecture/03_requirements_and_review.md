# Requirements, architecture review and remaining gates

**Verdict:** the core signal-chain architecture is sufficiently defined for a reviewed prototype implementation handoff. The original-board retrofit and any manufacturing release remain blocked by missing inputs and unperformed implementation checks.

## Input record and traceability

| ID | Source | Requirement or fact | Response and validation |
|---|---|---|---|
| C01 | IMG_7255.PNG | Existing functional ESP32-S3 board; replace pH circuitry only | Preserve external host boundary; original CAD needed for net/geometry diff |
| C02 | IMG_7255.PNG | Old AD7793 + ADuM5401 architecture | Isolation decision explicitly retained as product gate |
| C03 | IMG_7255.PNG | Replacement schematic will be provided | Absent; current architecture is our proposal, not a validation of that schematic |
| C04 | IMG_7256.PNG | LMP91200, ADS112C04, REF3220 | Selected as core; archived primary datasheets |
| C05 | IMG_7256.PNG | Guard-ring high-impedance input | Manual top/bottom guard plan; leakage test required |
| C06 | IMG_7256.PNG | I²C to ESP32-S3 | 3.3 V/100 kHz/address 0x40 interface; actual GPIOs still unassigned |
| C07 | IMG_7256.PNG | Motor driver, multiple DC/DCs and Wi-Fi exist | No invented replacements; preserve/recover source design |
| C08 | IMG_7256–7257.PNG | Reduce noise coupling, verify power/reference | Spatial/return-path plan plus motor/RF/supply test matrix |
| C09 | IMG_7257.PNG | ERC/DRC | Required in phase 2; not run against nonexistent CAD |
| C10 | IMG_7257.PNG | Updated Altium project, layout, review, Gerbers, BOM | Screenshot contract remains Altium; this user-selected KiCad workflow is not an Altium deliverable |
| U01 | Current task | Practical minimal PCB and eventual full deliverables | Propose daughterboard first; complete soil-device scope not fulfilled by module |
| U02 | Current task | kicad-happy design/review; KiCadRoutingTools routing | Local tools located; workflows and protection constraints in handoff |
| U03 | Current task | Astra architecture, pause, 6.1 Sol implementation | Phase 1 documents only; explicit stop before CAD |

Screenshots also describe a job advertisement's experience, proposal and price terms. These are not electrical or manufacturing requirements and no application/submission is being performed.

## Decisions and rationale

| Decision | Reason | Tradeoff |
|---|---|---|
| Daughterboard demonstrator first | Source board/schematic absent; isolates measurable analog task | Does not demonstrate full-device integration |
| External ESP32-S3 | Avoids duplicating radio, USB and power hardware without a requirement | Needs a dev board or recovered host for bring-up |
| 5 V input → quiet 3.3 V LDO | Practical bench input and analog rail headroom | Cannot take arbitrary battery or motor voltage |
| Supervisor-controlled reference enable | Accommodates slow ramp requirement without relying on a typical LDO rise time | Adds one small IC |
| Gain 2 instead of 4 baseline | ±600 mV range with margin | One fewer nominal bit than gain 4 |
| Differential VOUT–VOCM | Rejects shared bias movement in principle | ADC/reference/VCM mismatch still needs characterization |
| Two-layer module | Low-speed, no onboard RF or switcher | Guard geometry consumes area; not a stackup decision for original PCB |
| No generic PH_IN protection | Avoids unknown leakage overwhelming electrode signal | Controlled bench ESD environment only; production protection still open |
| Isolated product path | Existing architecture strongly suggests intentional isolation | Adds I²C isolation and retained/replacement isolated power |

## Review findings

Severity describes the gate, not a claim that a nonexistent board has failed.

| ID | Severity | Finding / action | Confidence and evidence |
|---|---|---|---|
| A01 | BLOCKER: original retrofit | Missing Altium schematic/PCB/libraries and replacement schematic; obtain before changing original design | Deterministic: only four input PNG files found |
| A02 | BLOCKER: integration | Original isolation purpose and sample-ground paths unknown; preserve isolated architecture until resolved | Datasheet-backed function of ADuM5401; inference about this product |
| A03 | BLOCKER: fabrication | No CAD, ERC/DRC, footprint audit or fabrication package exists | Deterministic phase boundary |
| A04 | WARNING | REF3220 slow-ramp enable constraint; use U5 and verify brownout/ramp behavior | Datasheet-backed, REF32xx Rev D §6.1.1 |
| A05 | WARNING | REF3220 has ±0.2% initial limit; 0.01% is typical, not maximum | Datasheet-backed, electrical table; calibration required |
| A06 | WARNING | Probe connector exact MPN/mechanics and input protection unselected | Inference: cannot sign off layout/field ESD without them |
| A07 | WARNING | Humidity/flux leakage may dominate the electronics budget | Calculated 100 fA target; not measured |
| A08 | WARNING | Actual sample temperature unavailable | Deterministic missing requirement; external thermometer in prototype |
| A09 | WARNING | LMP91200MT/NOPB listed obsolete, MTX/NOPB active in supplied addendum | Manufacturer lifecycle evidence; choose active tape variant and confirm stock later |
| A10 | WARNING | Interface can back-power unpowered module/host | Engineering inference; use common power sequencing or isolate appropriately |
| A11 | WARNING | 50 ×35 mm board assumes a compatible insulated BNC | Planning assumption; footprint/mechanical review before outline freeze |

No defect in the client's actual PCB can be asserted from these screenshots.

## Missing inputs and when they become blocking

The prototype architecture can proceed without another questionnaire. The following gate the **original retrofit**, not this phase:

1. Original Altium schematic/PCB/project and libraries, or complete exported connectivity plus stackup/placement/outline sufficient for a controlled migration.
2. Promised LMP91200 replacement schematic and its intended probe connector.
3. Available rail values/noise/current margins; original isolation boundary and its intended function.
4. Probe model, source impedance, cable/shell connection, sample grounding, other immersed sensors and USB/charger use.
5. Available MCU GPIOs/I²C addresses and firmware ownership.
6. Mechanical region permitted for edits, enclosure/connector dimensions and manufacturing constraints.
7. Product accuracy, temperature/humidity, calibration, EMC/ESD and ingress requirements.

If these cannot be obtained, the next work should remain a documented demonstrator. A new whole-device design would require an explicitly new system scope.

## Verification basis and tool coverage

Primary datasheets were read directly and archived with source URLs/hashes. The signal-chain numbers are analytical calculations. No symbol, footprint, net or PCB copper has yet been cross-verified because none exists. No bench result or simulation pass is claimed.

| Check/tool | Phase 1 status |
|---|---|
| Screenshot inspection | All four images read visually |
| Datasheet/manual pin-plan check | Core five ICs examined; implementation must repeat against actual CAD |
| Structured kicad-happy datasheet cache | Not generated; direct PDFs are evidence, not a scored extraction cache |
| `analyze_schematic.py` | Not applicable yet: no schematic |
| `analyze_pcb.py --full` | Not applicable yet: no PCB |
| `cross_analysis.py` | Not applicable: neither required analyzer input exists |
| `analyze_emc.py` | Not applicable: no schematic/PCB pair; interference risk reviewed qualitatively |
| `analyze_thermal.py` | Not applicable: no layout; LDO power allocation only |
| SPICE / `simulate_subcircuits.py` | Not run: no schematic/models; ngspice, ltspice and xyce not found on PATH during phase 1 |
| `analyze_gerbers.py` | Not applicable: no fabrication files |
| Distributor lifecycle audit | Not run: no final schematic/BOM; manufacturer orderable records checked selectively |
| Native KiCad ERC/DRC | Not run: no CAD; KiCad CLI v10.0.7 available |
| KiCadRoutingTools | Repository/API inspected only; no board routed |
| Prior review/run delta | No previous design review or analysis run found in the original workspace |
| False-positive triage | No analyzer findings exist; no findings dismissed or suppressed |

**Trust summary:** manufacturer-backed component facts; reproducible analytical calculations; inferred architectural decisions; unverified implementation and product requirements. This is an architecture review, not a complete schematic/layout or ready-to-fabricate review.
