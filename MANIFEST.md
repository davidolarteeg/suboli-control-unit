# SUBOLI Control Unit Review Package Manifest

## Export Metadata

| Item | Value |
|---|---|
| KiCad version used | 10.0.3 |
| Export date/time | 2026-06-11T12:03:41Z |
| Git commit hash of upload | See Git history / final review-package status. A commit cannot contain its own hash because the hash is computed from the committed file contents. |
| Source project | `suboli_control` |
| Packaging scope | KiCad project plus generated ERC, netlist, BOM, and schematic renders |

## File Tree

```text
suboli-control-unit/
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
│   ├── sym-lib-table
│   └── tools/
│       └── generate_suboli_schematic.py
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
| `/` | One-sheet SUBOLI carrier/motherboard schematic: power/protection, MA12070 module socket, OPA1622 headphone stage, panel header interfaces, star-ground net tie, and notes. |

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
ERC report (2026-06-11T14:03:04, Encoding UTF8)
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
| Footprints | Not assigned. All schematic `Footprint` fields are blank. |
| MA12070 module footprint | Deferred. A1 is a module/socket symbol only; no footprint was improvised. |
| A1 EN/MUTE | Left no-connect pending exact MA12070 module pad map/control behavior. |
| Placeholder component values | `R2`/`R3` are `47-100 k`; `C11`/`C12` are `220-470 uF / 25 V`; `TVS1` is DNP. |
| Nonstandard references | Requested designators such as `J_DC`, `J_IN`, `J_HP`, `J_SPK`, `P_TACT`, `P_HP`, and `U_vg` are preserved in the schematic. KiCad appends `?` to some of these in the generated BOM because they are not standard annotation formats. |
| GitHub upload | Uploaded by Git over SSH after the repository was created externally. |

## Checkpoints

| Checkpoint | Status | Evidence |
|---|---|---|
| 1. MA12070 module footprint deferred, not improvised | DONE | `A1` has an empty `Footprint` field; schematic note states EN/MUTE and module pad map are pending. |
| 2. PWR_FLAG symbols present on power nets | DONE | `#FLG1` `+19V_RAW`, `#FLG2` `+19V`, `#FLG3` `GND_STAR`, `#FLG4` `+19V_HP`, `#FLG5` `GND_SIG`, `#FLG6` `VGND`. |
| 3. ERC warnings reported, not suppressed | DONE | ERC was exported with `--severity-all`; report shows `0 Errors 0 Warnings` and includes exclusions. |
| 4. OPA1622 stage component values match confirmed design | DONE | Actual values: `R4`/`R5` = 10 k left gain network; `R6`/`R7` = 10 k right gain network; `R2`/`R3` = 47-100 k input bias to `VGND`; `U_vg` = TLE2426 rail splitter, no resistor divider; `C5`/`C7` decouple `+19V_HP` to `GND_STAR`; `C6`/`C8` decouple `VGND` to `GND_SIG`; A2 output coupling `C11`/`C12` = 220-470 uF / 25 V; output series `R8`/`R9` = 10 ohm. |
