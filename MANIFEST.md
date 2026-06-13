# SUBOLI Control Unit Review Package Manifest

## Export Metadata

| Item | Value |
|---|---|
| KiCad version used | 10.0.3 |
| Export date/time | 2026-06-13T15:30:54Z |
| Git commit hash of upload | See Git history / final review-package status. A commit cannot contain its own hash because the hash is computed from the committed file contents. |
| Source project | `suboli_control` |
| Packaging scope | KiCad project plus generated ERC, netlist, BOM, and schematic renders |

ARCHIVED — stale since commit 166da31. The .kicad_sch is the sole source of truth.

design/ holds the locked SUBOLI PCB rules + manufacturing scripts — read before any layout or export work.

## File Tree

```text
suboli-control-unit/
├── design/
│   ├── SUBOLI_DESIGN_RULES.md
│   ├── design-spec.md
│   ├── layout-rules.md
│   ├── manufacturing.md
│   ├── pcb-capability-report.md
│   └── scripts/
│       ├── export_manufacturing.sh
│       └── preflight_layout.sh
├── MANIFEST.md
├── README.md
├── kicad/
│   ├── SCHEMATIC_PHASE_REPORT.md
│   ├── fp-lib-table
│   ├── suboli_control.kicad_pcb
│   ├── suboli_control.kicad_prl
│   ├── suboli_control.kicad_pro
│   ├── suboli_control.kicad_sch
│   ├── suboli_control.kicad_sym
│   ├── suboli_control.pretty/
│   │   └── PPTC_LP30-300_P7.60mm.kicad_mod
│   ├── sym-lib-table
│   └── tools/
│       └── generate_suboli_schematic_ARCHIVED.py
├── renders/
│   ├── schematic.pdf
│   └── schematic.svg
└── reports/
    ├── bom.csv
    ├── erc_report.txt
    └── netlist.net
```

Skipped because no PCB layout exists:

- `reports/drc_report.txt`
- `renders/board_3d.png`

## Schematic Sheets

| Sheet | Description |
|---|---|
| `/` | One-sheet SUBOLI carrier/motherboard schematic: power/protection, off-board MA12070 module power/signal interfaces, OPA1622 headphone stage, panel header interfaces, interior glow, star-ground net tie, and notes. |

MA12070 module is off-board, stacked on standoffs; speaker outputs wire module→Speakon directly; J5/J6 are the only board↔module interfaces. Deferred-footprint list is now EMPTY.

## Component / Footprint Table

| Reference(s) | Footprint | Verification |
|---|---|---|
| J1, J5 | `Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal` | Found |
| SW1 | `Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_4-G-5,08_1x04_P5.08mm_Horizontal` | Found |
| J2, J4, J6 | `Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical` | Found |
| RV1, RV2 | `Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical` | Found |
| A2 | `Package_DIP:DIP-8_W7.62mm_Socket` | Found |
| U1 | `Package_TO_SOT_THT:TO-92_Inline` | Found |
| D1 | `Diode_THT:D_DO-201AD_P15.24mm_Horizontal` | Found |
| TVS1 | `Diode_THT:D_DO-15_P10.16mm_Horizontal` | Found |
| F1 | `suboli_control:PPTC_LP30-300_P7.60mm` | Project-local custom footprint |
| FB1 | `Inductor_THT:L_Axial_L12.0mm_D5.0mm_P15.24mm_Horizontal_Fastron_MISC` | Found |
| C1 | `Capacitor_THT:CP_Radial_D16.0mm_P7.50mm` | Found |
| C3, C11, C12 | `Capacitor_THT:CP_Radial_D10.0mm_P5.00mm` | Found |
| C5, C6 | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` | Found |
| C9, C10 | `Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm` | Found |
| C2, C4, C7, C8 | `Capacitor_THT:C_Disc_D7.5mm_W4.4mm_P5.00mm` | Found |
| R1-R10 | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` | Found |
| RV3 | `Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical` | Found |
| LED1, LED2, LED3 | `LED_THT:LED_D5.0mm` | Found |
| NT1 | `NetTie:NetTie-2_SMD_Pad0.5mm` | Found |

## Value Changes

| Reference | New value |
|---|---|
| TVS1 | P6KE24A |
| U1 | TLE2426ILP |
| RV3 | 3296W-10K |

## ERC Summary

Command:

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --output reports/erc_report.txt --severity-all kicad/suboli_control.kicad_sch
```

Result:

| Count | Value |
|---|---:|
| Errors | 0 |
| Warnings | 0 |

Verbatim warning/error list:

```text
No ERC warnings or errors reported.
```

Verbatim ERC report excerpt:

```text
ERC report (2026-06-13T17:30:22, Encoding UTF8)
Report includes: Errors, Warnings, Exclusions

***** Sheet /

 ** ERC messages: 0  Errors 0  Warnings 0

 ** Ignored checks:
    - Global label only appears once in the schematic
    - Four connection points are joined together
    - Assigned footprint doesn't match footprint filters
```

## Deviations / Incomplete Items

| Item | Status |
|---|---|
| PCB layout | Not present. `kicad/suboli_control.kicad_pcb` is a schematic-phase placeholder with 0 footprints, 0 pads, 0 tracks, 0 vias, and 0 copper zones. |
| DRC report | Skipped because no PCB layout exists. |
| 3D render | Skipped because no PCB layout exists. |
| Footprints | Assigned for all BOM references. Deferred-footprint list is EMPTY. |
| Stock footprint validation | All assigned stock footprint names were found in installed KiCad libraries after the R3.1 footprint-name corrections. |
| C1 footprint | Updated to `Capacitor_THT:CP_Radial_D16.0mm_P7.50mm` for the verified Ø16×20 mm, 7.5 mm pitch bulk capacitor. |
| BOM enrichment | `reports/bom.csv` includes `Manufacturer`, `MPN`, and `Supplier_PN`; unknown MPNs remain blank. Supplier_PN is filled for 39/41 BOM rows. |
| MA12070 module | Off-board, stacked on standoffs; speaker outputs wire module→Speakon directly; J5/J6 are the only board↔module interfaces. |
| TVS1 | Value updated to `P6KE24A`; Supplier_PN remains pending. |
| Interior glow | Added. glow circuit is power-rail driven, switched by SW1. |
| Generator script | ARCHIVED — stale since commit 166da31. The .kicad_sch is the sole source of truth. |
| GitHub upload | Uploaded by Git over SSH after the repository was created externally. |

## Checkpoints

| Checkpoint | Status | Evidence |
|---|---|---|
| 1. MA12070 module moved off-board | DONE | `A1`, `J3`, and `OUTL+`/`OUTL−`/`OUTR+`/`OUTR−` are removed; `J5` feeds `+19V`/`GND_STAR` and `J6` feeds `TACT_INL`/`GND_SIG`/`TACT_INR`. |
| 2. PWR_FLAG symbols present on power nets | DONE | `#FLG1` `+19V_RAW`, `#FLG2` `+19V`, `#FLG3` `GND_STAR`, `#FLG4` `+19V_HP`, `#FLG5` `GND_SIG`, `#FLG6` `VGND`. |
| 3. ERC warnings reported, not suppressed | DONE | ERC was exported with `--severity-all`; report shows `0 Errors 0 Warnings` and includes exclusions. |
| 4. OPA1622 stage component values match confirmed design | DONE | Actual values: `R4`/`R5` = 10 k left gain network; `R6`/`R7` = 10 k right gain network; `R2`/`R3` = 100k input bias to `VGND`; `U1` = TLE2426ILP, no resistor divider; `C5`/`C7` decouple `+19V_HP` to `GND_STAR`; `C6`/`C8` decouple `VGND` to `GND_SIG`; A2 output coupling `C11`/`C12` = 470uF/25V; output series `R8`/`R9` = 10 ohm. |
| 5. Footprint assignments verified against installed libraries | DONE | All assigned stock footprints were found in the installed KiCad libraries; the custom F1 footprint remains in the project-local `suboli_control` library. |
| 6. Supplier fields exported in BOM | DONE | `reports/bom.csv` includes `Supplier` and `Supplier_PN` columns; J5/J6 carry the requested HESTORE order codes. |
| 7. Generator script archived | DONE | `kicad/tools/generate_suboli_schematic_ARCHIVED.py` carries the archive header and the old generator path was removed. |
| 8. PCB capability report committed | DONE | `design/pcb-capability-report.md` records KiCad MCP PCB mutation limits, Freerouting status, raw S-expression edit capability, and `gerbers`/`drill`/`pos` export availability. |
| 9. Design rulebook committed | DONE | `design/` holds the locked SUBOLI PCB rules and manufacturing scripts. |
