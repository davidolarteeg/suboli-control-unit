#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
SCH="$ROOT/kicad/suboli_control.kicad_sch"
PCB="$ROOT/kicad/suboli_control.kicad_pcb"
OUT="$ROOT/reports"

mkdir -p "$OUT"

"$KICAD_CLI" sch erc --output "$OUT/erc_report.txt" --severity-all "$SCH"
"$KICAD_CLI" pcb drc --output "$OUT/drc_report.txt" --severity-all "$PCB"

echo "Preflight complete:"
echo "  ERC: $OUT/erc_report.txt"
echo "  DRC: $OUT/drc_report.txt"
