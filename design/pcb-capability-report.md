# PCB Capability Report

Generated: 2026-06-13T15:30:54Z

| Capability | Result |
|---|---|
| MCP tool that places a footprint on the PCB at given XY? | no; none exposed |
| MCP tool that draws a board outline on Edge.Cuts? | no; none exposed |
| MCP tool that routes a track / creates copper segments? | no; none exposed |
| MCP tool that creates/fills a copper zone? | no; none exposed |
| Is Freerouting installed and callable? | no |
| Can raw S-expressions be written into `.kicad_pcb` by file edit? | yes |

## KiCad PCB Export Subcommands

`kicad-cli pcb export --help` reports these manufacturing export subcommands:

- `gerbers`
- `drill`
- `pos`

The local KiCad MCP server exposes schematic and PCB read/check tools in this
session, but no PCB mutation tools.
