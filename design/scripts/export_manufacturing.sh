#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
PCB="$ROOT/kicad/suboli_control.kicad_pcb"
OUT="$ROOT/manufacturing"

if [[ "${SUBOLI_EXPORT_APPROVED:-}" != "YES" ]]; then
  echo "Refusing manufacturing export: set SUBOLI_EXPORT_APPROVED=YES after human approval." >&2
  exit 2
fi

if grep -q "schematic phase only" "$PCB"; then
  echo "Refusing manufacturing export: PCB still contains schematic-phase placeholder note." >&2
  exit 2
fi

mkdir -p "$OUT/gerbers" "$OUT/drill" "$OUT/pos"

"$KICAD_CLI" pcb export gerbers --output "$OUT/gerbers" "$PCB"
"$KICAD_CLI" pcb export drill --output "$OUT/drill" "$PCB"
"$KICAD_CLI" pcb export pos --output "$OUT/pos/suboli_control.pos" "$PCB"

echo "Manufacturing export complete: $OUT"
