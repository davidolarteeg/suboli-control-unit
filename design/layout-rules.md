# SUBOLI Layout Rules

## Placement

- Place `J1`, `SW1`, `J2`, `J4`, `RV1`, and `RV2` to match the panel harness
  exit directions before routing.
- Place `J5` and `J6` near the stacked MA12070 module standoff location.
- Keep `U1`, `C5`, `C6`, `C7`, and `C8` close to the OPA1622 adapter `A2`.
- Keep `C1` and `C2` close to the post-protection `+19V` entry point.
- Keep `R10`, `RV3`, `LED2`, and `LED3` away from audio input traces.

## Power Routing

- Route `+19V_RAW`, `+19V_SW`, `+19V`, and `GND_STAR` as power paths with
  width appropriate for the load and connector ratings.
- Keep the high-current MA12070 power feed from `J5` away from low-level audio.
- Do not route speaker outputs on this board; they leave the MA12070 module
  directly to the Speakon connector.

## Signal Routing

- Route `IN_L`, `IN_R`, `TACT_INL`, `TACT_INR`, `HP_INL`, `HP_INR`,
  `HP_OUT_L`, and `HP_OUT_R` as short, quiet audio paths.
- Avoid parallel runs between power switching/current paths and audio input
  paths.
- Keep the headphone amplifier feedback loops compact around `A2`.

## Grounding

- `GND_SIG` and `GND_STAR` may meet only at `NT1`.
- Do not add a copper pour that shorts `GND_SIG` to `GND_STAR`.
- If zones are added, review each zone net assignment before filling.

## Glow Circuit

- The glow circuit is power-rail driven and switched by `SW1`.
- Keep the glow series chain `+19V -> R10 -> RV3 -> LED2 -> LED3 -> GND_STAR`
  separate from audio nets.
