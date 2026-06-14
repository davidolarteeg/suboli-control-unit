#!/usr/bin/env bash
# SUBOLI manufacturing export — wraps kicad-cli to produce a fab+assembly package.
# Usage: export_manufacturing.sh <path/to/board.kicad_pcb> <output_dir>
# Produces in <output_dir>: gerbers/, drill, centroid CPL, and (if a .kicad_sch
# sibling exists) a BOM. Does NOT route or place anything.
set -euo pipefail

PCB="${1:?need path to .kicad_pcb}"
OUT="${2:?need output dir}"

# Locate kicad-cli: prefer PATH, fall back to the macOS app bundle path used in
# this project. Override with KICAD_CLI env var if needed.
CLI="${KICAD_CLI:-}"
if [ -z "$CLI" ]; then
  if command -v kicad-cli >/dev/null 2>&1; then
    CLI="kicad-cli"
  elif [ -x "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" ]; then
    CLI="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
  else
    echo "ERROR: kicad-cli not found. Set KICAD_CLI=/path/to/kicad-cli" >&2
    exit 1
  fi
fi

mkdir -p "$OUT/gerbers"

echo "== Gerbers =="
"$CLI" pcb export gerbers --output "$OUT/gerbers" "$PCB"

echo "== Drill (Excellon) =="
"$CLI" pcb export drill --output "$OUT/gerbers/" "$PCB"

echo "== Centroid / placement (CPL) =="
# CSV, millimeters, both sides — the common assembly-house format.
"$CLI" pcb export pos --output "$OUT/centroid.csv" --units mm --format csv --side both "$PCB" \
  || echo "WARN: pos export failed (older kicad-cli?) — try without --side." >&2

# BOM from the schematic sibling if present.
SCH="${PCB%.kicad_pcb}.kicad_sch"
if [ -f "$SCH" ]; then
  echo "== BOM =="
  "$CLI" sch export bom \
    --fields "Reference,Value,Footprint,Manufacturer,MPN,Supplier_PN,\${QUANTITY}" \
    --output "$OUT/bom.csv" "$SCH" \
    || "$CLI" sch export bom --output "$OUT/bom.csv" "$SCH"
else
  echo "WARN: no sibling .kicad_sch next to the board; BOM not generated here." >&2
fi

echo "Done. Package in: $OUT"
echo "Next: run check_quote_ready.py to verify completeness before uploading."
