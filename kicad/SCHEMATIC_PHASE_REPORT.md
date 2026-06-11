# SUBOLI Control Unit - Schematic Phase Report

Generated: 2026-06-08

Scope: schematic phase only. No footprint finalization, PCB placement, routing, STEP export, or Gerber export was performed.

## Files Created / Updated

| File | Purpose |
|---|---|
| `suboli_control.kicad_pro` | KiCad project file |
| `suboli_control.kicad_sch` | One-sheet SUBOLI carrier/motherboard schematic |
| `suboli_control.kicad_sym` | Project-local custom/simple symbols |
| `sym-lib-table` | Project symbol library mapping |
| `suboli_control.kicad_pcb` | Empty schematic-phase PCB placeholder only |
| `suboli_control.net` | Exported KiCad netlist |
| `suboli_control_erc.rpt` | KiCad CLI ERC report |
| `exports/suboli_control.svg` | Schematic SVG preview |
| `tools/generate_suboli_schematic.py` | Reproducible schematic generator |

## Schematic Summary

- One root schematic sheet.
- 37 physical schematic components.
- 30 schematic nets reported by MCP schematic info.
- 31 nets in the exported KiCad netlist, including the intentionally unconnected A1 EN/MUTE pad net.
- A1 is represented as a purchased MA12070 module/socket, not an IC-level design.
- A2 is represented as an OPA1622 dual op-amp DIP-8 adapter/socket.
- Panel-mounted parts are represented as wired panel headers.
- `NT1` was added as a schematic net-tie/star-link so `GND_SIG` and `GND_STAR` remain distinct KiCad nets while documenting the only intended connection point.

## ERC

Command:

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --output suboli_control_erc.rpt suboli_control.kicad_sch
```

Result:

- Errors: 0
- Warnings: 0
- ERC messages: 0

Note: `kicad-cli sch export netlist` prints an annotation warning because the requested references such as `J_DC`, `J_IN`, `J_HP`, `J_SPK`, `P_TACT`, `P_HP`, and `U_vg` are nonstandard KiCad annotation formats. The references were preserved exactly as requested.

Tooling note: after regeneration, MCP `get_erc_violations` appeared to return a stale pre-fix warning list. The KiCad CLI ERC report and exported netlist were used as the authoritative check for this phase.

## Critical Net Checks

| Check | Result |
|---|---|
| `J_DC` center to `+19V_RAW` | PASS |
| `J_DC` sleeve to `GND_RAW` | PASS |
| `SW1` switches both raw positive and raw ground | PASS |
| `F1` in `+19V` line before `D1` | PASS |
| `D1` reverse-polarity Schottky from `+19V_F` to `+19V` | PASS |
| `FB1` isolates `+19V_HP` from `+19V` | PASS |
| `U_vg` creates `VGND` from `+19V_HP` / `GND_SIG` | PASS |
| `J_IN` Tip/Ring/Sleeve = `IN_L`/`IN_R`/`GND_SIG` | PASS |
| `P_TACT` creates `TACT_INL` and `TACT_INR` separately | PASS |
| `P_HP` creates `HP_INL` and `HP_INR` separately | PASS |
| A1 tactile input is single-ended via `IN0B`/`IN1B` to `GND_SIG` | PASS |
| `OUTL+` only A1.OUT0A to J_SPK pin 1+ | PASS |
| `OUTL−` only A1.OUT0B to J_SPK pin 1− | PASS |
| `OUTR+` only A1.OUT1A to J_SPK pin 2+ | PASS |
| `OUTR−` only A1.OUT1B to J_SPK pin 2− | PASS |
| `OUTL−` and `OUTR−` are not tied together | PASS |
| Tactile output remains stereo 2xBTL | PASS |
| No tactile output LC/low-pass filter exists | PASS |
| A2 headphone input is AC-coupled via C9/C10 and biased to `VGND` | PASS |
| A2 output is series-isolated and AC-coupled via R8/C11 and R9/C12 | PASS |
| `J_HP` sleeve connects to `GND_SIG` | PASS |
| `GND_SIG` meets `GND_STAR` only through `NT1` | PASS |

## Intentional Open Item

A1 `EN/MUTE` is intentionally left no-connect until the exact MA12070 module pad map and enable/mute behavior are supplied.

## PCB Status

The PCB file is an empty placeholder only:

- Board outline: none
- Footprints: 0
- Pads: 0
- Tracks: 0
- Vias: 0
- Copper zones: 0
- Gerbers: not generated
- STEP: not generated

## Stop Point

Proceed to the footprint phase only after receiving:

1. MA12070 module pad map / mechanical drawing / pin pitch.
2. Confirmation that the default PCB outline may be 100 x 80 mm, or replacement board dimensions.
3. Confirmation that the exact nonstandard references should remain as requested despite KiCad annotation warnings during netlist export.
4. Confirmation that `NT1` is acceptable as the explicit single star-ground net tie.
