# SUBOLI PCB Design Rules

This directory is the locked rulebook for SUBOLI PCB layout, fabrication export,
and manufacturing checks. Read these files before any layout or export work.

## Source of Truth

- `kicad/suboli_control.kicad_sch` is the electrical source of truth.
- `kicad/tools/generate_suboli_schematic_ARCHIVED.py` is archived and stale.
- Existing schematic values, nets, and footprints must not be changed during
  layout work unless an explicit schematic-change task requires it.

## Product Architecture

- The MA12070 module is off-board and stacked on standoffs.
- Speaker outputs wire directly from the MA12070 module to the Speakon output.
- `J5` and `J6` are the only PCB-to-MA12070-module interfaces.
- The OPA1622 headphone stage remains on the carrier through the DIP-8 socketed
  adapter interface.

## Layout Gate

Do not generate fabrication outputs until all items are true:

- All schematic-assigned footprints are present on the PCB.
- Board outline, connector positions, mounting holes, clearances, and enclosure
  fit have been mechanically reviewed.
- Power, signal, virtual-ground, and star-ground routing follows
  `layout-rules.md`.
- ERC runs with `--severity-all` and has 0 errors and 0 warnings.
- DRC runs on the PCB and has 0 errors and 0 warnings.
- A human approval note for manufacturing export is recorded.

## Export Gate

Gerber, drill, and position exports are manufacturing artifacts. Do not export
them from an unrouted or placeholder board.

Use `design/scripts/preflight_layout.sh` before layout review and
`design/scripts/export_manufacturing.sh` only after the export gate is approved.
