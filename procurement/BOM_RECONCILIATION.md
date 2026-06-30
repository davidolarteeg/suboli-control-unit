# SUBOLI Procurement vs Final BOM

Snapshot date: 2026-06-30

Sources:

- Final build BOM: `mfg/bom.csv`
- Physical/order inventory: `procurement/inventory.csv`
- Human-readable tracker: `procurement/INVENTORY.md`
- Interactive tracker: `procurement/supply-tracker.html`

This file reconciles the final board BOM against the current procurement
tracker. It does not change the KiCad design or manufacturing BOM.

## Summary

Most final BOM lines are covered by in-hand inventory. The current supply risk is
small and specific: two required 10 uF decoupling capacitors are missing, and a
few panel/LED references need an engineering substitution decision before build.

## Required Missing Items

| BOM ref | Final BOM item | Supplier PN | Required qty | Inventory status | Action |
|---|---|---:|---:|---|---|
| C5 | 10 uF A2 V+ bulk decouple | 100.004.04 | 1 | No match in inventory | Source |
| C6 | 10 uF VGND decouple | 100.004.04 | 1 | No match in inventory | Source |

Order qty 2 total of HESTORE `100.004.04` or an electrically/mechanically
equivalent 10 uF capacitor matching `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm`.

## Build Decision Items

| BOM ref | Final BOM item | BOM PN | Inventory evidence | Decision needed |
|---|---|---:|---|---|
| J1 | DC barrel jack panel header 5.5x2.5 | 100.425.38 | No direct PN match. DC panel jack is in hand from SoundImports; 2P terminal block `100.425.63` is in hand. | Confirm panel-jack-to-board wiring approach covers J1. |
| LED1 | Power LED | 100.201.14 | No direct PN match. Orange LEDs `100.298.75` qty 3 are in hand. | Confirm orange LED is acceptable for LED1 or source the BOM PN. |
| LED2, LED3 | Warm white 5 mm LEDs | 100.392.63 | Tracker says warm-white LED correction is `100.202.93` qty 5, in hand. | Update BOM later if correction is accepted. |
| A2 | OPA1622 dual op-amp on DIP-8 adapter | 100.231.43 | DIP-8 socket `100.231.43` is in hand; Audiophonics OPA1622 adapter `12489` is ordered. | Track as ordered until Audiophonics shipment arrives. |
| TVS1 | P6KE24A | blank in BOM | Inventory has `TVS1` / `P6KE24A` qty 5 in hand. | Optional: backfill supplier PN in BOM later. |
| NT1 | GND net tie | blank in BOM | No procured part needed. | No procurement action. |

## Covered BOM Lines

The following final BOM supplier PNs are covered by inventory quantities marked
`In hand`:

`100.432.81`, `100.448.15`, `100.310.10`, `100.008.95`, `100.285.01`,
`100.492.21`, `100.238.56`, `100.358.61`, `100.415.50`, `100.425.63`,
`100.205.39`, `100.205.64`, `100.205.41`, `100.204.73`, `100.205.19`,
`100.415.52`, `100.412.47`, `100.425.66`, and `100.346.37`.

## Non-board Items Still To Source

From `procurement/inventory.csv`:

| Ref | Item | Status |
|---|---|---|
| FOAM-B | EVA puzzle foam - cushion base | To source |
| FOAM-S | Soft seating foam - comfort layer | To source |
| FABRIC | Pillow cover fabric | To source |
| MFG | Pillow manufacturing / sewing | To source |
| FAB | Vintage fabric audio cable | Deferred |
