# Tool provenance and reproduction

The authoritative artifacts are the reviewed native KiCad files, not the construction helpers. Open hardware/Soil_pH_AFE/Soil_pH_AFE.kicad_pro in KiCad 10 with standard 3D libraries installed. All symbols/footprints needed for editing/manufacture are project-local; only standard 3D model paths use KICAD10_3DMODEL_DIR. Custom BNC VRML is local and illustrative.

- KiCad CLI 10.0.7: native ERC, schematic-parity DRC, netlist, Gerber/drill/placement/PDF/3D exports.
- kicad-happy revision `6a91aaaea124152b2923326c1cf77278e0999cd4`: schematic, full PCB, cross-domain, EMC, thermal, Gerber and lifecycle review. https://github.com/aklofas/kicad-happy
- KiCadRoutingTools revision `fd59a050e258581d5938c4d9456bbfeb13240e67`: selected noncritical nets and buffered analog routes; critical input/guard copper preserved. https://github.com/drandyhaas/KiCadRoutingTools
- Gerbonara: independent parsing and top/bottom copper/drill rendering. CairoSVG rasterizes its SVGs; some ImageMagick SVG renderers mishandle clearances.
- Arduino-ESP32 3.3.12 / generic ESP32-S3: successful compile recorded in analysis/firmware_build.log. Firmware is supplied as source, not a board-independent flash image.

## Repeat release checks

Python 3.11 dependencies: `sexpdata shapely gerbonara cairosvg`. With KiCad CLI on PATH or KICAD_CLI set:

```sh
python3 scripts/export_release.py
python3 scripts/validate_release.py
python3 docs/architecture/calculations.py
```

Export aborts on native ERC/DRC violations. The audit uses the native netlist and the archived critical-placement baseline under analysis/stages. Review every change rather than blindly trusting green checks; PCB parity and geometry do not prove correct physical pin assignment or analog performance.

Full final analyzer JSONs are in analysis/final; generic findings are triaged in design_review.md. The earlier timestamped analyzer cache reused an old PCB analysis even after its source-hash metadata changed. Final analysis therefore used fresh explicit output paths. A generic diff reported no change despite rerouting; that result is not trusted. The independent geometry audit and native reports establish the final state; prior routing logs remain historical records of intermediate attempts.

Construction helpers under scripts/development are archived, machine-specific implementation history. They can overwrite final libraries/CAD and do not reproduce the final manual routing edits. Do not run them on the released native project. The final export/audit scripts are the supported review path.

The repository omits local runtime environments, raw client screenshots, third-party datasheet PDFs/text, prebuilt binaries and intermediate routing stages (except the geometry baseline needed for audit). Manufacturer URLs, hashes and partial pin extraction records are retained. Retrieve PDFs from the source register for a new datasheet review; partial extraction is not a complete behavioral model.

Run `python3 scripts/package_release.py` after review to regenerate the fabrication ZIP and controlled-file hashes.
