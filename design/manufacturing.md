# SUBOLI — Manufacturing & Quote Workflow

How to take the routed board to a fab/assembly quote. Covers Eurocircuits
(primary — has a Hungary plant at Eger, accepts native KiCad, free DFM
analysis) and JLCPCB (cost fallback).

## The package a quote needs

|Artifact                             |Bare-board quote                            |Assembly quote|
|-------------------------------------|--------------------------------------------|--------------|
|Board outline (Edge.Cuts)            |required                                    |required      |
|Gerbers (Cu/mask/silk) + drill       |required                                    |required      |
|Native .kicad_pcb                    |accepted by Eurocircuits in place of Gerbers|accepted      |
|BOM (Ref,Value,Footprint,Qty,Mfr,MPN)|—                                           |required      |
|Centroid / CPL (placement XY+rot)    |—                                           |required      |

## Critical: the off-board module is NOT an assembly line item

The MA12070 module and the OPA1622 DIP-8 module are sub-assemblies, not catalog
parts. No assembly house stocks them. They must be EXCLUDED from the assembly
BOM/CPL and hand-installed. The same is true of all panel/wired parts (pots,
switch, mini-XLR, DC jack). So the assembly scope is only: board-level passives,
diodes, the DIP-8 socket (not the module), LEDs, connectors, NT1. Mark the rest
“do not place / consigned.”

## Generating the package

Run `scripts/export_manufacturing.sh <kicad_pcb_path> <out_dir>`. It uses
kicad-cli:

- `kicad-cli pcb export gerbers` and `... drill` → Gerber + Excellon
- `kicad-cli pcb export pos` → centroid (CPL), CSV, mm, both sides
- `kicad-cli sch export bom` (or KiBot) → BOM with Mfr/MPN columns

KiBot (optional, INTI-CMNB/KiBot) can produce a single fab+assembly package
from one YAML config and is worth it for repeatable batches. For a one-off
quote, raw kicad-cli is enough.

Then run `scripts/check_quote_ready.py <out_dir> <kicad_pcb_path>` — it fails
loudly if the board outline is empty, any layer/drill/CPL is missing, or the
BOM lacks Manufacturer/MPN. A passing check means the package is uploadable.

## Eurocircuits specifics

- Upload native .kicad_pcb to PCB Visualizer; it auto-sets parameters and runs
  DFM. Resolve its flags before ordering.
- For assembly, it extracts BOM + placement from the KiCad data; verify the
  extracted list excludes the off-board module and panel parts.
- No tooling charge, no MOQ. Eger plant = short ship to Budapest.
- Two routes: **turnkey** (they source parts — fast, but they re-pick from
  their distributor lines, so your specific HESTORE parts may be substituted by
  equivalents; fine for passives, a spec conversation for the LP30-300 fuse and
  exact film caps) vs **consigned** (you ship parts — keeps exact parts, adds a
  shipping leg + handling lead time).

## JLCPCB fallback

Cheaper, but assembly uses their LCSC parts library — expect more substitution
and their CPL/BOM format quirks. Use their own BOM/CPL templates if going there.

## Decision note for a beginner builder

If the human is not confident soldering and lacks temp-controlled tools, prefer
turnkey assembly for the passive layer and hand-finish only the modules + panel
wiring (big, forgiving through-hole). Get the real quote number before
committing — setup cost and lead time may change the call. This board is 100%
through-hole, so DIY assembly is also feasible (a calm evening with an iron),
but the deadline risk of a first-timer’s cold joints is real.
