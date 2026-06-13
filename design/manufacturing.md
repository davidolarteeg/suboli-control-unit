# SUBOLI Manufacturing Rules

## Required Checks Before Export

1. Schematic ERC with `--severity-all`: 0 errors, 0 warnings.
2. PCB DRC: 0 errors, 0 warnings.
3. Footprint validation against installed KiCad libraries.
4. Mechanical review of outline, connector orientation, mounting holes, and
   enclosure clearance.
5. Human approval recorded in the release notes or manifest.

## Export Artifacts

When approved, generate at minimum:

- Gerbers
- Excellon drill files
- Position file
- DRC report
- PCB PDF or SVG review plots
- Updated BOM with `Manufacturer`, `MPN`, and `Supplier_PN`

## KiCad CLI

Use the KiCad app-bundle CLI on this machine:

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
```

Known PCB export subcommands include `gerbers`, `drill`, and `pos`.

## No Placeholder Fabrication

Do not manufacture from a schematic-phase placeholder board, an unrouted board,
or a board with generic/unverified footprints.
