#!/usr/bin/env python3
"""SUBOLI quote-readiness checker.

Verifies a manufacturing package is complete enough to upload for a fab/assembly
quote, and — crucially — that the board is actually laid out (not an empty
.kicad_pcb). Exits non-zero with a clear list if anything is missing.

Usage: check_quote_ready.py <output_dir> <path/to/board.kicad_pcb>
"""
import csv
import os
import re
import sys


def check_board_laid_out(pcb_path):
    """The most common failure: schematic done, board empty. Catch it first."""
    problems = []
    try:
        pcb = open(pcb_path).read()
    except OSError as e:
        return [f"cannot read board: {e}"]
    n_fp = len(re.findall(r"\(footprint\s+\"", pcb))
    n_seg = len(re.findall(r"\(segment\s", pcb))
    n_arc = len(re.findall(r"\(arc\s", pcb))
    # A real outline = a graphic item (line/rect/poly/arc) drawn ON Edge.Cuts.
    has_outline = bool(
        re.search(r"\(gr_(line|rect|poly|arc|curve)\b[\s\S]{0,400}?Edge\.Cuts", pcb)
    )
    if n_fp == 0:
        problems.append("no footprints placed on the board — layout not started")
    if n_seg + n_arc == 0:
        problems.append("no routed tracks — board is unrouted")
    if not has_outline:
        problems.append("no board outline on Edge.Cuts")
    return problems


def check_files(out_dir):
    problems = []
    gerber_dir = os.path.join(out_dir, "gerbers")
    if not os.path.isdir(gerber_dir) or not os.listdir(gerber_dir):
        problems.append("gerbers/ missing or empty")
    else:
        files = os.listdir(gerber_dir)
        has_drill = any(f.lower().endswith((".drl", ".xln")) for f in files)
        has_copper = any(re.search(r"(F_Cu|B_Cu|\.gtl|\.gbl)", f, re.I) for f in files)
        if not has_drill:
            problems.append("no drill file (.drl/.xln) in gerbers/")
        if not has_copper:
            problems.append("no copper gerber layers found")
    if not os.path.isfile(os.path.join(out_dir, "centroid.csv")):
        problems.append("centroid.csv (placement/CPL) missing — needed for assembly")
    return problems


def check_bom(out_dir):
    problems = []
    bom = os.path.join(out_dir, "bom.csv")
    if not os.path.isfile(bom):
        return ["bom.csv missing"]
    with open(bom, newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return ["bom.csv is empty"]
    header = [h.strip().lower() for h in rows[0]]
    for needed in ("manufacturer", "mpn"):
        if not any(needed in h for h in header):
            problems.append(f"BOM missing a '{needed}' column (assembly quote needs it)")
    # Warn if MPN column exists but is mostly empty.
    mpn_idx = next((i for i, h in enumerate(header) if "mpn" in h), None)
    if mpn_idx is not None and len(rows) > 1:
        filled = sum(1 for r in rows[1:] if len(r) > mpn_idx and r[mpn_idx].strip())
        if filled < (len(rows) - 1) * 0.5:
            problems.append(
                f"BOM MPN column mostly empty ({filled}/{len(rows)-1} rows) — "
                "turnkey quote can't price unlabelled parts"
            )
    return problems


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    out_dir, pcb = sys.argv[1], sys.argv[2]

    layout = check_board_laid_out(pcb)
    files = check_files(out_dir)
    bom = check_bom(out_dir)
    all_problems = layout + files + bom

    print("SUBOLI quote-readiness check")
    print("=" * 32)
    if layout:
        print("\nBOARD (blocking — fix before anything else):")
        for p in layout:
            print(f"  ✗ {p}")
    if files:
        print("\nMANUFACTURING FILES:")
        for p in files:
            print(f"  ✗ {p}")
    if bom:
        print("\nBOM:")
        for p in bom:
            print(f"  ✗ {p}")

    if not all_problems:
        print("\n✓ QUOTE READY — all artifacts present, board laid out, BOM labelled.")
        sys.exit(0)
    else:
        print(f"\n✗ NOT QUOTE READY — {len(all_problems)} issue(s) above.")
        if layout:
            print("  Root cause is most likely that PCB layout isn't done yet.")
        sys.exit(1)


if __name__ == "__main__":
    main()
