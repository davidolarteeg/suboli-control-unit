# design/ — SUBOLI PCB Design Rulebook

The locked, verified design rules and manufacturing tooling for the SUBOLI
control-unit board. This folder is the single source of truth shared across all
machines and agents (MacBook/KiCad, iMac/Blender, and human work).

**Read `SUBOLI_DESIGN_RULES.md` first.** It is the entry point and points to the
rest.

## Contents

|File                             |What it is                                                                                                                                           |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
|`SUBOLI_DESIGN_RULES.md`         |Entry point: the two jobs (review, export), the no-autoroute boundary, and how to use the rest.                                                      |
|`design-spec.md`                 |Locked design: nets, component values, footprints, star-ground topology, OPA1622 supply rule, off-board-module pattern, custom-symbol pin convention.|
|`layout-rules.md`                |Audio-layout rules with the *why* for each: zones, star ground, OPA1622 isolation, trace widths, ground pours, mechanical, pre-Gerber gate.          |
|`manufacturing.md`               |Fab/assembly quote workflow: what files a quote needs, Eurocircuits/JLCPCB specifics, the off-board-module exclusion, turnkey vs consigned.          |
|`scripts/export_manufacturing.sh`|Wraps kicad-cli to produce Gerbers + drill + centroid + BOM. Run after the board is routed.                                                          |
|`scripts/check_quote_ready.py`   |Verifies the export package is complete and the board is actually laid out before uploading for a quote.                                             |

## Boundary

Nothing here routes a board. The KiCad MCP exposes no placement/routing tools and
Freerouting is not installed; routing is a human GUI task. Codex CAN write
footprint placement and board outline as raw S-expressions into the .kicad_pcb,
and CAN run kicad-cli exports. These rules guide placement, review the result,
and drive the manufacturing export — they never fabricate tracks.

## Scope of authority

If anything elsewhere (including an agent’s reconstruction from memory)
contradicts these files, these files win. They were built and verified against
the actual schematic, supplier listings, and KiCad libraries.
