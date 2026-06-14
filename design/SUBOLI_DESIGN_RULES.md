# SUBOLI Control Unit — PCB Design Rulebook

**Repo-authored, verified design rules. Read this before any layout, routing,
review, or manufacturing-export work on the SUBOLI control-unit board.**

This is the single source of truth for both Codex instances (MacBook/KiCad and
iMac/Blender) and any human working the board. It encodes the frozen design
knowledge of the SUBOLI vibroacoustic control unit and the workflow for taking
its KiCad project from schematic to a fab/assembly quote. It has two jobs and
one hard boundary.

**Job 1 — Review** placement and routing against the locked audio-layout rules.
**Job 2 — Export** the manufacturing package (Gerbers + drill + centroid + BOM)
in the form an assembly house ingests.
**Boundary — This skill does not route traces.** No autorouter produces a
correct analog/Class-D board here; routing is done by a human in the KiCad GUI.
The skill makes that human far less likely to err. If asked to “route the
board,” explain the boundary and offer to (a) review what’s been routed, or
(b) produce a routing checklist for the GUI session — never fabricate tracks.

## What this board is

A single-supply +19V vibroacoustic control unit. Two signal paths share one
enclosure: a tactile path (MA12070 Class-D module driving two 4Ω bass shakers)
and a headphone path (OPA1622 on the main board). The MA12070 is an OFF-BOARD
stacked module — the main PCB connects to it only through two connectors
(J5 power, J6 audio); the module’s speaker outputs wire directly to the panel
connector, NOT through this PCB. Full net-level detail and the component table
live in `design-spec.md` — read it before any review or export.

## Before doing anything

1. Identify the working KiCad project. For this project it is the
   `suboli-control-unit` GitHub repo, `kicad/suboli_control.kicad_*`. If review
   is of a specific commit, clone/pull that commit first.
1. Read `design-spec.md` — the locked nets, values, footprints, and
   the star-ground topology. This is the single source of truth; the generator
   script in the repo is ARCHIVED and must be ignored.
1. Determine which phase the request is: **review placement**, **review
   routing**, or **export for quote**. Each has its own checklist below.

## Job 1a — Placement review

Read the .kicad_pcb, extract every footprint’s (x,y,layer,rotation), and check
against `layout-rules.md`. Report pass/fail per rule with the actual
measured value as evidence — never a bare “looks fine.” The rules that matter
most, in priority order:

1. **Star-ground point.** All GND_STAR returns (C1, C2, TVS1, LED1, J5 ground,
   and the NT1 net-tie) must converge at one physical point — C1’s ground pad.
   Measure the spread; flag anything returning elsewhere.
1. **NT1 is the only GND_SIG↔GND_STAR bridge.** Confirm NT1 sits at the star
   point and that no other copper joins the two ground domains.
1. **OPA1622 isolation.** The headphone input network (C9/C10, R2/R3, the gain
   resistors, A2 inputs) must be ≥15 mm from the MA12070 module connectors
   (J5/J6) and from the high-current output wiring. Measure the nearest spacing.
1. **Power chain compactness.** J1→SW1→F1→D1→TVS1→C1 should be a short, ordered
   run; flag a path that wanders across the board.
1. **C1 clearance.** C1 is Ø16×20mm — the tallest part. Confirm it is placed to
   lie horizontal or that the enclosure has the height. Flag if it collides with
   the stacked-module standoff zone.
1. **Decoupling proximity.** C5/C7 within ~5mm of A2 pin 8; U1 (TLE2426) within
   ~10mm of A2; C2 near the MA12070 supply feed (J5).

## Job 1b — Routing review

After the human routes, verify against `layout-rules.md` §routing:

- Track widths by net class (power/output ≥2.0mm, signal 0.3mm, etc. — table in
  the reference). Extract actual widths and compare.
- Two ground pours (GND_STAR and GND_SIG) joined only through NT1; no signal
  trace crosses the pour boundary.
- Output and power loops kept small. Flag long parallel runs of sensitive
  signal next to switching/output copper.
- Run `kicad-cli pcb drc` and report the result verbatim. Never suppress.

## Job 2 — Manufacturing export for quote

Use `design/scripts/export_manufacturing.sh` (wraps kicad-cli; KiBot optional). It
produces, into an `mfg/` output dir: Gerbers, Excellon drill, the centroid/
placement (CPL) file, and a BOM. Then verify the package is complete with
`design/scripts/check_quote_ready.py`, which asserts every file a quote needs exists
and that the BOM has Manufacturer/MPN columns populated. Read
`manufacturing.md` for the exact Eurocircuits and JLCPCB upload
specifics (what they read, where bare-board vs assembly upload differ, and the
gotchas like the off-board module not being an assembly line item).

A quote is “ready” only when ALL of these exist and pass the checker:

- Board outline present on Edge.Cuts (non-empty)
- Gerbers for all copper + mask + silk layers, plus drill file
- Centroid/CPL with one row per board-assembled part (NOT the off-board module)
- BOM with Reference, Value, Footprint, Qty, Manufacturer, MPN
- DRC clean (or every violation explained)

If any are missing, say exactly which and why — most commonly the board isn’t
routed yet, in which case the honest answer is “no quote possible until layout
is done,” not a partial export.

## Reusing the design knowledge

For a future SUBOLI variant (Pro, batch 2, full-body mat), the locked constants
in `design-spec.md` — supply rail, star-ground discipline, OPA1622
supply rules, the off-board-module pattern, trace-width table — carry forward.
Update the reference, keep the rules. The same review/export jobs apply.

## Tone when reporting

Match the project’s established review style: lead with the verdict (APPROVED /
FIX REQUIRED), give per-item evidence with measured numbers, own any error in
the rules themselves rather than blaming the executor, and never reverse a
correct earlier decision under pressure. Past assistance is not authorization
to skip a check.
