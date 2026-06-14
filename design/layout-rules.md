# SUBOLI — Audio Layout Rules

These are the rules a SUBOLI board is reviewed against. They exist because this
is a mixed Class-D + sensitive-analog board where layout, not schematic,
determines whether it’s quiet. Each rule says what to check and why.

## Zones (floorplan)

Suggested outline ~110×80mm (shrunk from 140×90 after the MA12070 moved
off-board). Diagonal separation is the core idea: power/high-current at
rear, sensitive headphone analog at the opposite front corner.

- **Zone P (rear-left)** — power entry & protection: J1, SW1, F1, D1, TVS1,
  C1, C2, LED1, R1, and the STAR point. NT1 lives here.
- **Module stack (over Zone P)** — MA12070 on M3 standoffs ABOVE the board,
  fed by J5/J6. Never stack it over the headphone zone. Standoff ≥25mm or C1
  laid horizontal for clearance. The old 60×60 keepout is gone; only the J5/J6
  connector strip remains on-board.
- **Zone C (front-left)** — input & control: J2, RV1, RV2; glow parts R10, RV3,
  LED2, LED3 mid-board pointing at the lid.
- **Zone D (front-right, diagonal from the module)** — the sensitive zone:
  A2 (OPA1622), U1, C5–C8, C9/C10, R2–R9, C11/C12, J4. FB1 gates Zone P→D.

## Placement rules (priority order)

1. **Star ground.** GND_STAR returns converge at C1’s ground pad. The
   acceptable spread is tight — all of {C1, C2, TVS1, LED1 return, J5 ground,
   NT1} within a small radius of that pad. Why: a single low-impedance
   reference point keeps high shaker-current returns from modulating the analog
   ground.
1. **NT1 = sole ground bridge.** GND_STAR and GND_SIG meet at exactly one
   point, NT1, at the star. Why: two bridges = a ground loop = hum.
1. **OPA1622 isolation ≥15mm.** HP input network and A2 inputs kept ≥15mm from
   J5/J6 (module/switching side) and from any high-current run. Why: Class-D
   edges couple into high-impedance analog inputs.
1. **Power chain ordered & compact.** J1→SW1→F1→D1→TVS1→C1 in sequence,
   ≤~50mm. Why: protection only works if it’s in-line before the load; long
   loops radiate.
1. **C1 mechanical.** Ø16×20mm, tallest part — horizontal mount or confirmed
   enclosure height; must clear module standoffs.
1. **Decoupling proximity.** C5/C7 ≤5mm from A2 pin 8; U1 ≤10mm from A2;
   C2 near J5 supply feed. Why: decoupling works only when local.

## Routing rules

|Net class                        |Min width|Why                                      |
|---------------------------------|---------|-----------------------------------------|
|GND_STAR, +19V rail nets         |2.0mm    |shaker current peaks, low-Z return       |
|Module feed (J5 power)           |2.0mm    |same current path                        |
|+19V_HP, VGND                    |0.5mm    |<50mA                                    |
|Audio signal (all HP_*, bias, fb)|0.3mm    |low current; short matters more than wide|
|Glow (GLOW_*)                    |0.3mm    |DC only                                  |

- **Two ground pours**, GND_STAR under Zone P + module area, GND_SIG under
  Zones C/D, joined ONLY through NT1. No signal trace may cross the gap between
  pours — route between-zone signals over their own pour.
- Keep output/power loop area small; pair related currents.
- Keep sensitive analog away from the module feed and glow runs even though
  glow is DC (it shares the rail).

## Mechanical

- 4× M3 mounting holes, 5mm corner inset (place footprints directly in PCB
  editor; no schematic symbols).
- LED2/LED3 vertical at full lead length for the lid-glow orb; ~board center
  under the frosted top.
- Panel parts (pots, switch, jacks, mini-XLR, DC jack) are wired to board
  headers — they are not placed on the PCB.

## Pre-Gerber gate

1. Real parts measured: F1 pitch 7.6mm, C1 pitch 7.5mm/Ø16, C9/C10 box 5.0mm.
1. MA12070 module: J5/J6 interface verified against the physical module’s
   connector; module mounts on standoffs, outputs wire module→panel directly.
1. OPA1622 adapter: EN tied high, GND handled.
1. DRC clean; two-pour ground check done visually.
1. Upload native .kicad_pcb to the fab’s DFM analyzer; resolve findings BEFORE
   ordering.
