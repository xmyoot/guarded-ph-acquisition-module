# Phase 2 implementation handoff

**Stop condition in this phase:** architecture and board plan only. The user requested a pause before implementation with GPT-6.1 Sol. Do not start CAD, routing, firmware or manufacturing exports merely because these instructions exist.

On continuation, implement the proposed bench module unless the user supplies original CAD and directs a retrofit. Resolve any scope change explicitly. The prototype is not a complete soil-testing product.

## Ordered work and acceptance gates

1. **Freeze build inputs.** Read this package, select the insulated BNC and keyed interface connector from manufacturer drawings, and confirm whether the build is a nonisolated bench module or an isolated retrofit. For retrofit, recover original CAD, supply/isolation and mechanical constraints first. Preserve a copy/checksum of original files.
2. **Create KiCad sources.** Use a clean local project with source schematic, PCB, project rules and project-local libraries for any missing/custom assets. Prefer one readable schematic sheet for the core; name power, guard, analog and interface nets explicitly.
3. **Complete exact component selection.** Candidate core MPNs: LMP91200MTX/NOPB, ADS112C04IPWR, REF3220AIDBVT, **TPS7A2033PDBVR**, TPS3839K33DBZT. The LDO is the five-pin DBV variant; do not substitute the four-pin DQN pin map. Select capacitors by effective capacitance; resistor/connector/MPN completion is required before fabrication.
4. **Pin and topology review.** Compare every CAD pin and footprint pad to its actual package drawing. Inspect no-connects, reference force/sense returns, REF ENABLE/ADC RESET, ADC addresses, power-off paths, differential inputs and probe-shell bias. Check component fields and count against raw CAD.
5. **Schematic validation.** Run native ERC and kicad-happy schematic analysis. Fix errors; justify warnings individually. Archive reports. Populate datasheet extraction cache using the local datasheets skill before making analyzer-backed component claims.
6. **Place and manually route the critical cell.** Apply `02_board_plan.md`; freeze connector/outline only after mechanical checks. Lock sensitive copper and add router protection entries.
7. **Route ordinary nets using KiCadRoutingTools.** Begin with an explicit noncritical allowlist and a preserved input copy. Record command, version, input/output hashes, allowed nets and changes. Follow with native zone refill, connectivity and DRC.
8. **Complete full review.** Run schematic, PCB `--full`, cross, EMC and thermal analysis; SPICE if a supported simulator is available. Include lifecycle audit, exact MPN pin checks and critical raw-file checks. Separately inspect guard loops, all-layer keepouts, mask apertures, reference return paths and BNC/chassis isolation.
9. **Review artifacts visually.** Render schematic pages, both copper faces, mask/paste layers, 3D assembly and Gerbers/drills. Resolve legibility, solder-mask errors, component collisions, connector orientation and silkscreen conflicts. Exported pictures alone do not prove connectivity.
10. **Prepare a prototype fabrication package.** Generate Gerbers, plated/nonplated drill files, board/assembly drawings, exact BOM, placement file, schematic PDF and source archive. Analyze Gerbers and compare to the reviewed PCB. Use a release manifest and content hashes. Label the package prototype/unvalidated until bench tests pass.
11. **Implement minimal bring-up firmware.** Use external ESP32-S3, deterministic register init/readback, raw data logging, fault flags and calibration storage. Confirm firmware compilation and electrical protocol behavior. Avoid an unnecessary cloud application or motor-control redesign.
12. **Execute bring-up on physical hardware when available.** Record measured data using `05_validation_plan.md`; report unexecuted tests honestly. Manufacturing-file completion cannot establish physical accuracy.

## Tool locations and provenance

| Tool | Local location / revision |
|---|---|
| KiCad CLI | `/Users/hector/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` · observed version 10.0.7 |
| kicad-happy | `/Users/hector/Documents/KiCAD_Projects/ESP32_C6_EPaperDisplayDriver/tools/kicad-happy` · git `6a91aaaea124152b2923326c1cf77278e0999cd4` |
| KiCadRoutingTools | `/Users/hector/Documents/KiCAD_Projects/ESP32_C6_EPaperDisplayDriver/tools/KiCadRoutingTools` · git `fd59a050e258581d5938c4d9456bbfeb13240e67` |

Read each tool's current local instructions when implementation begins. The tool repositories belong to a neighboring project; use them as tools without modifying that project's board or history. Availability of a repository is not proof that all runtime dependencies or router binaries have been exercised.

Read kicad-happy `skills/kicad/SKILL.md`, `references/report-generation.md`, and `skills/datasheets/SKILL.md`. Its review contract requires explicit disclosures of every omitted analyzer and evidence for elevated findings. Keep generated analyses in timestamped `analysis/` runs and retain both raw output and human review.

## Deliverable matrix

| Eventual artifact | Current state | Phase 2 completion evidence |
|---|---|---|
| Requirements and architecture | Proposed and documented | Accepted scope and closed architecture gates |
| Native KiCad schematic/project | Not started | Opens cleanly, ERC report, reviewed pin mapping |
| PCB layout | Not started | Correct outline/placement, DRC/connectivity, manual guard audit |
| BOM | Preliminary candidates only | Exact MPNs, quantities, footprints, population and sourcing status |
| Fabrication/assembly files | Not started | Independent visual checks, analysis and matching release hashes |
| Bring-up firmware | Contract only | Build log and protocol/bench evidence |
| Calibrated electrical performance | Not measured | Raw data, calibration record, acceptance table |
| Complete soil-device integration | Not designed | Original host/motor/supply requirements and integrated tests |
| Updated Altium project from screenshot | Not created | Separate agreed Altium delivery workflow if still required |

## Gates that must not be waived silently

Missing connector drawing, footprint mismatch, unidentified power source, unknown isolation bypass, floating sense pin, unfinished input guard, unresolved ERC/DRC error, hidden unrouted net, stale fabrication output, or missing exact part selection prevents a fabrication-ready claim.

Open accuracy, humidity and field-protection tests prevent a production-ready claim even after a prototype may be manufactured. Do not turn proposed thresholds into a “pass” without measurements.
