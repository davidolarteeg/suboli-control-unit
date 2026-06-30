# SUBOLI — Control Unit Procurement & Inventory

> Status snapshot for build verification. Generated from the supply tracker.
> **Logged spend:** €407.87 + 80 154 Ft · **53 line items**

This file records what has been **procured and is physically in hand** vs ordered/to-source,
so the circuit can be cross-checked against the frozen BOM (`mfg/bom.csv`, `reports/bom.csv`).

## ⚑ Engineering checks required (BOM vs procurement)

The HESTORE order was reconciled line-by-line against invoice **HS/26/044668 (26 584 Ft)** and
all 32 invoice lines were physically received. The following BOM references were **NOT** found on
that invoice or in any received bag — please verify against the schematic:

| BOM ref | Part | PN (BOM) | Finding |
|---|---|---|---|
| C5, C6 | 10 µF decoupling (A2 V+, VGND) | 100.004.04 | **Required in final BOM and not ordered / not received.** Source qty 2. |
| J1 | DC barrel jack header | 100.425.38 | Not on invoice. Likely covered: DC **panel** jack came from SoundImports; 2P/4P terminal blocks present. |
| LED1 | Dedicated power LED | 100.201.14 | Not on invoice. Likely covered by orange LEDs (100.298.75 ×3). |

**Part-number corrections applied** (old tracker/BOM had wrong codes):
- Dual-log pots are **100.383.27** (POS1615-A10K ×2) — *not* 100.415.52 (that code is the 6-pin XH header).
- Warm-white LED is **100.202.93** (×5) — *not* 100.392.63.

## ✅ In hand

### Eurocircuits

| Ref | Component | PN | Qty |
|---|---|---|---|
| PCB | Bare control board (125×95×1.6mm, frozen) | — | 1 |

### SoundImports

| Ref | Component | PN | Qty |
|---|---|---|---|
| SI-ORD | SoundImports order — shakers, OFC wire, 3.5mm & DC panel jacks | — | 1 |
| SHK | Xcite XBS25-4 bass shaker (4Ω, cushion) | XBS25-4 | 4 |
| WIRE | OFC speaker wire 2×2.5mm² (cushion run) | ICC-25MM | 7 |
| HJACK | 3.5mm headphone jack (panel mount) | — | 1 |
| DCJACK | DC barrel jack 5.5×2.5mm (panel mount) | 25MM-DC-JACK | 1 |

### eMAG

| Ref | Component | PN | Qty |
|---|---|---|---|
| PSU | Delight 55366 PSU · 19V / 4.74A / 90W | 55366 | 3 |

### HQ Elektronika

| Ref | Component | PN | Qty |
|---|---|---|---|
| TVS1 | P6KE24A TRANSIL TVS · 24V / 600W (1ms) | P6KE24A | 5 |
| WINT | Mini hook-up wire (internal connections) | — | 1 |

### HESTORE

| Ref | Component | PN | Qty |
|---|---|---|---|
| ORDER | HESTORE order — passives, headers & connectors (bulk) | — | 1 |
| BA | 1000µF / 35V bulk cap (C1) | 100.432.81 | 1 |
| CU | 1000µF / 25V electrolytic (C3) | 100.310.10 | 1 |
| DE | 470µF / 25V Low-ESR cap | 100.285.01 | 3 |
| NV | 1µF / 63V film cap | 100.008.95 | 2 |
| KF | 100nF / 50V X7R cap | 100.448.15 | 6 |
| XA | 100K 1% resistor | 100.205.64 | 2 |
| CH | 10K 1% resistor | 100.205.41 | 4 |
| MU | 10R 1% resistor | 100.204.73 | 2 |
| KE | 1.2K 1% resistor | 100.205.19 | 1 |
| AB | 8.2K 1% resistor | 100.205.39 | 1 |
| SF | 3296W-10K trimmer | 100.412.47 | 1 |
| RA | POS1615-A10K dual-log 10K pot | 100.383.27 | 2 |
| AE | LED 5mm warm white 1500-2000mcd | 100.202.93 | 5 |
| LS | LED 5mm orange OSOR5161A-NO | 100.298.75 | 3 |
| AD | SB560 Schottky diode 60V / 5A | 100.492.21 | 1 |
| KD | 4602-RC choke 1µH / 2A | 100.358.61 | 1 |
| MB | LP30-300 resettable fuse 3A / 30V | 100.238.56 | 1 |
| LV | TLE2426ILP rail-splitter IC | 100.346.37 | 2 |
| ST | ECPF08 precision IC socket | 100.231.43 | 1 |
| SS | B3B-XH-A header · XH 3P THT | 100.415.50 | 3 |
| LB | B6B-XH-A header · XH 6P THT | 100.415.52 | 2 |
| CO | XHP-3-CABLE · assembled 3P cable 20cm | 100.416.04 | 2 |
| OL | XHP-6-CABLE · assembled 6P cable 20cm | 100.416.07 | 2 |
| NU | KFG-2EDGK-5.08-2P terminal block | 100.425.63 | 1 |
| RR | KFG-2EDGK-5.08-4P terminal block | 100.425.66 | 2 |
| MH | White heat-shrink 18/9mm (5 m) | 100.226.71 | 1 |
| ON | White heat-shrink 2.5/1.25mm (5 m) | 100.226.76 | 1 |
| OP | White heat-shrink 4/2mm (3 m) | 100.226.81 | 1 |
| PL | LIYV 1×0.14 black hook-up wire (5 m) | 100.448.88 | 1 |
| NT | SN99C 0.5mm solder wire (0.1 kg) | 100.426.68 | 1 |
| AA | MF-X3210I Stannol flux pen 10ml | 100.469.38 | 1 |
| SU | ZD-180-1 desolder braid | 100.360.46 | 1 |

### 3D Printing (TBC)

| Ref | Component | PN | Qty |
|---|---|---|---|
| FIL | Transparent PETG filament · 1 kg spool | Sunlu? | 2 |

## 🚚 Ordered — incoming

| Ref | Component | Supplier | Carrier · Method | ETA | Note |
|---|---|---|---|---|---|
| AMP | MA12070 Class-D module (60×80×33mm) | Audiophonics | Courier TBC · Home | 8 Jul | Audiophonics — both invoices ship together · still processing |
| A2 | OPA1622 dual op-amp on DIP-8 adapter | Audiophonics | Courier TBC · Home | 8 Jul | Audiophonics — ships with MA12070 · still processing |
| XLR | Mini-XLR 4-pin terminations (F104 chassis + male plug) | Elimex | GLS · Pickup | TBC | Confirm Elimex payment |
| HS | Black heat-shrink assortment kit | Elimex |  | — | In Elimex order |
| CAB4 | Sommer Cable SC-CICADA 4 · 5 m (cushion cable) | FlyMusic (RO) | DPD · Home | 9 Jul | 5 m · mates with mini-XLR · from Romania |

## 🔻 To source

| Ref | Component | Note |
|---|---|---|
| FOAM-B | EVA puzzle foam — cushion base | Source supplier + price |
| FOAM-S | Soft seating foam — comfort layer | Find supplier |
| FABRIC | Pillow cover fabric | Source fabric |
| MFG | Pillow manufacturing / sewing | Find manufacturer |

## ⏸ Deferred

- FAB · Vintage fabric audio cable — Needs specialty source

---
_Machine-readable copy: `procurement/inventory.csv`. Interactive: `procurement/supply-tracker.html`. BOM cross-check: `procurement/BOM_RECONCILIATION.md`._
