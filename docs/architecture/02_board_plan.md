# Board planning and routing contract

Status: proposed geometry and constraints, not a PCB layout. The dimensions below apply only to the bench module. Original-board retrofit placement remains unknown.

## Mechanical and layer proposal

Start from a **50 × 35 mm, two-layer, 1.6 mm FR-4 board**, with top-side component assembly and a right-angle insulated BNC facing the left edge. This deliberately leaves room for cleaning and probe access. Confirm the selected BNC courtyard, connector insertion loads and mounting before freezing the outline; permit a documented size change if required.

Use 1 oz copper, ENIG finish, 0.20 mm baseline trace/space, 0.30 mm finished via drill with 0.60 mm pads, ≥0.30 mm copper-to-edge, and 0603 or larger passives. These are conservative project proposals, not a fabrication vendor's accepted rules. Package fanout may require local exceptions documented against the selected fabricator. ENIG is not itself a guarantee of insulation resistance.

Two layers are adequate for the small core with no switching converter or RF transmitter onboard. A full product retrofit should retain the original stackup unless engineering evidence supports changing it. If the original board is four or more layers, keep buried planes away from the guarded input cell; extending a solid ground plane directly beneath PH_IN would defeat the intended isolation geometry.

```text
Proposed top view — connector facing outward, not to scale
                  50 mm
  ┌──────────────────────────────────────────────────┐
  │ BNC  [guarded high-Z cell]  U1  RC  U2      J2   │
  │  ←  center → PH_IN (short)     ADC/ref test pads │
  │      shell → PH_VCM          U3 reference        │ 35 mm
  │                              U5       U4 / 5 V  │
  │     clear for cleaning       power / bus edge   │
  └──────────────────────────────────────────────────┘
```

Aim for connector signal pad to U1 input under 10 mm, with U1 guard pins oriented toward the connector. Keep ADC input resistors and differential capacitor next to ADC pins, reference adjacent to its load, and power/interface hardware on the opposite edge. The BNC shell is an active VCM node; select an insulated bulkhead/board arrangement and ensure enclosure hardware cannot ground it.

Mounting holes are optional pending mechanics. If used, keep them outside the analog cell and avoid unintended shell/chassis grounding. Define them as mechanical holes, not assumed ground fasteners.

## High-impedance cell

Use one dedicated `PH_GUARD` net from both U1 guard pins, forming continuous exposed guard loops on **both copper sides** around the PH_IN conductor and connector signal termination. Connect top and bottom guard loops with guard vias; these vias are allowed even though PH_IN itself should have none. The input pin's guard must continue through its immediate escape geometry, not stop at a decorative ring around the connector.

Remove solder mask from the input/guard area on both sides as specified in the LMP91200 layout guidance. Create explicit mask apertures and review plotted mask files. Remove solder paste from exposed guard-only copper; exposed guard is not an assembly pad. No silkscreen, glue, label adhesive or unqualified coating belongs in the cell. Clean the assembly thoroughly, dry it and verify leakage. [LMP91200 p.17, §10](06_sources.md)

Starting layout constraints:

| Region/net | Constraint |
|---|---|
| PH_IN | Top layer only; no vias; no stubs/test-point branch; shortest direct route; no autorouting |
| PH_GUARD | Top/bottom loops and selected stitching; manual continuity check |
| Guard trace | Proposed 0.5 mm width and about 0.5 mm spacing to PH_IN, adjusted at fine-pitch pads |
| Outside guarded cell | Keep unrelated copper at least 1 mm beyond guard when practical |
| Under cell | No ground/power/digital copper on either layer; guard copper only where planned |
| Probe reference route | PH_VCM goes to connector shell without crossing the input cell |
| Supply decoupling | Ground returns local to IC; avoid routing through the cell |

These dimensions are engineering starting points. Electrical leakage and stable guard operation are the acceptance criteria, not a ring-width rule. Avoid a very large guard plane: its capacitance can burden the buffer, and DRC cannot prove stability.

The guard is not a shield ground. Do not attach a two-conductor probe's shell to GUARD, join GUARD to GND/VCM, or place a ground pour inside the loop. A grounded enclosure shield, if later used, requires its own documented connection.

## Ground, reference and interference

Use one contiguous local ground domain beneath the low-impedance circuitry, interrupted only by the explicit high-impedance keepout. Do not split ADC analog and digital grounds with a slot or long single trace. Place digital activity so its return current stays near the interface edge and away from the connector/U1.

Route REF3220 force output to the ADC reference load; return its sense connection from that load. Use a quiet ground sense return beside it. Branch the LMP reference from the same reference node. Keep these traces away from I²C and power connector transients. Do not route supply or I²C through the analog filter's reference return.

In a future original-board retrofit, place the cell as far as practicable from motor output traces, switching inductors and the radio antenna. An arbitrary distance in millimeters cannot certify rejection; use placement, return-path inspection and the interference tests in the validation plan. Do not put a new guard plane or ground copper into an ESP32 module antenna keepout.

## KiCadRoutingTools use

Route the guarded cell, VCM path, analog differential path, reference force/sense and critical decoupling manually first. Lock that copper in KiCad. Add protected-net entries for all these nets in the future `.kicad_pro`, using the router's supported `kicad_routing_tools.protected_nets` map.

Illustrative configuration (to be created during implementation, not already applied):

```json
{
  "kicad_routing_tools": {
    "protected_nets": {
      "PH_IN": "High impedance electrode path",
      "PH_GUARD": "Driven guard geometry",
      "PH_VCM": "Electrode reference drive",
      "PH_VOUT": "Analog buffer output",
      "PH_VOCM": "Differential reference buffer output",
      "ADC_P": "Matched analog filter",
      "ADC_N": "Matched analog filter",
      "REF_2V048": "Precision reference force/sense"
    }
  }
}
```

Add any separately named sense segments to the protection map. Use explicit allowed nets for ordinary I²C/control routing. **Exact net targeting can override protected-net filtering**, so never put a sensitive net in the router command's explicit allowlist. Locked tracks/vias provide a second protection layer. Plane changes and refill still require inspection.

Perform a geometry/net comparison before and after automation. Reject moved, severed or crossed guards; new PH_IN vias; copper added under the cell; and changed reference routes. Refill zones and run native KiCad DRC after routing. A router completion message is not routing acceptance.

## Testability and manufacturing plan

Provide labeled ground clips and low-impedance test points for +5V_IN, +3V3_A, REF_2V048, PH_VCM, PH_VOUT, PH_VOCM, AFE_READY, SDA, SCL and DRDY. Avoid oversized pads on filtered ADC nodes and never use a normal oscilloscope probe directly on PH_IN.

Keep connector mounting details, guard mask windows and cleaning instructions on fabrication/assembly drawings. Use an approved cleaning process and compatible solvent; capture before/after high-resistance tests. No conformal coating should be assumed benign without a coated-coupon comparison.

Before fabrication: final connector drawing and footprint review; exact MPN/pad audit; measured 3D clearances; copper/mask/paste/outline/drill visual review; and a controlled release manifest. No files in this phase are suitable for board manufacture.
