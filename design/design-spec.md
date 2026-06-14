# SUBOLI Control Unit — Locked Design Spec

**Baseline commit family: R4/R5 (`suboli-control-unit` repo). KiCad 10.**
The repo’s `generate_suboli_schematic_ARCHIVED.py` is STALE — ignore it. The
`.kicad_sch` is the single source of truth.

## System

Single +19V DC rail (Delight 55365 PSU, 5.5×2.5mm barrel, center-positive).
Two paths in one enclosure:

- **Tactile**: MA12070 Class-D module (off-board, stacked) → 2× Xcite XBS25-4
  bass shakers (4Ω, ~40Hz Fs) via panel connector.
- **Headphone**: OPA1622 (DIP-8 socket on main board), single-supply off the
  +19V_HP branch with a TLE2426 virtual ground.

## Power & protection chain (physical order)

`J1 (DC in)` → `SW1` (switches the rail) → `F1` (PPTC 3A) → `D1` (SB560 Schottky,
reverse-polarity) → `TVS1` (P6KE24A, 20.5V standoff / ~33V clamp — safely under
MA12070 39V abs max) + `C1` (1000µF/35V bulk) → `+19V`.
A ferrite `FB1` splits `+19V` → `+19V_HP` for the headphone branch.

**OPA1622 supply note (verified):** OPA1622 operates ±2V to ±18V. The single
+19V_HP with a TLE2426 mid-rail reference gives the op-amp a within-spec supply.
No additional regulator. Do not “add a regulator to be safe” — it’s unnecessary
and was explicitly designed out.

## Net list (post-R4, MA12070 off-board)

Power: `/+19V_RAW /GND_RAW /+19V_F /+19V_SW /+19V /+19V_HP`
Module interface (the ONLY board↔module nets): `J5.1→+19V, J5.2→GND_STAR`
(power); `J6.1→TACT_INL, J6.2→GND_SIG, J6.3→TACT_INR` (audio).
Input/control: `/IN_L /IN_R /TACT_INL /TACT_INR /HP_INL /HP_INR`
Headphone internal: `/HP_L_SER /HP_R_SER /HP_OUT_L /HP_OUT_R` plus the
A2 bias/feedback nets and `/VGND`.
Grounds: `/GND_STAR` (power/high-current domain), `/GND_SIG` (analog domain),
joined ONLY at `NT1`.
Glow: `/+19V → R10 → GLOW_A → RV3 → GLOW_B → LED2 → GLOW_MID → LED3 → GND_STAR`.

**Deleted at R4:** symbol A1 (MA12070 now off-board), J3 (Speakon — replaced by
direct module→panel wiring), nets OUTL±/OUTR±. The panel connector is a
mechanical choice (mini-XLR 4-pole chosen over Speakon) and is NOT on this PCB.

## Component table (refs, values, footprints)

|Ref        |Value                      |Footprint                                                           |
|-----------|---------------------------|--------------------------------------------------------------------|
|J1         |DC barrel/term in          |Connector_Phoenix_MSTB:…MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal  |
|J5         |Module power               |same 2-pin MSTBA                                                    |
|SW1        |Power switch               |…MSTBA_2,5_4-G-5,08_1x04_P5.08mm_Horizontal                         |
|J2, J4     |Audio in / HP out          |Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical                 |
|J6         |Module audio               |JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical                               |
|RV1, RV2   |Dual-gang 10k log          |JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical                               |
|A2         |OPA1622                    |Package_DIP:DIP-8_W7.62mm_Socket                                    |
|U1         |TLE2426ILP                 |Package_TO_SOT_THT:TO-92_Inline                                     |
|D1         |SB560                      |Diode_THT:D_DO-201AD_P15.24mm_Horizontal                            |
|TVS1       |P6KE24A                    |Diode_THT:D_DO-15_P10.16mm_Horizontal                               |
|F1         |LP30-300 PPTC              |suboli_control:PPTC_LP30-300_P7.60mm (custom)                       |
|FB1        |Axial ferrite 1µH/2A       |Inductor_THT:L_Axial_L12.0mm_D5.0mm_P15.24mm_Horizontal_Fastron_MISC|
|C1         |1000µF/35V Ø16             |Capacitor_THT:CP_Radial_D16.0mm_P7.50mm                             |
|C3         |1000µF/25V                 |Capacitor_THT:CP_Radial_D10.0mm_P5.00mm                             |
|C11, C12   |470µF/25V HP-out coupling  |CP_Radial_D10.0mm_P5.00mm                                           |
|C5, C6     |10µF/25V                   |CP_Radial_D5.0mm_P2.00mm                                            |
|C9, C10    |1µF/63V film input coupling|Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm                          |
|C2,C4,C7,C8|100nF                      |Capacitor_THT:C_Disc_D7.5mm_W4.4mm_P5.00mm                          |
|R1–R10     |metal film 0.6W            |Resistor_THT:R_Axial_DIN0207_…_P10.16mm_Horizontal                  |
|RV3        |10k multiturn trimmer      |Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical               |
|LED1       |green 5mm (signal/power)   |LED_THT:LED_D5.0mm                                                  |
|LED2, LED3 |warm white 5mm (glow)      |LED_THT:LED_D5.0mm                                                  |
|NT1        |net tie                    |NetTie:NetTie-2_SMD_Pad0.5mm                                        |

**Resistor values:** R2/R3=100k, R4–R7=10k (OPA1622 gain ×2 network),
R1=8.2k (LED1), R8/R9=10Ω (HP output series), R10=1.2k (glow limit).
OPA1622 stage: gain ×2 (10k/10k), 1µF film input coupling, 10Ω series +
AC-coupled (470µF) outputs, TLE2426 VGND reference.

## Custom symbol library convention

The project’s custom symbols use pin **1 = anode/A, 2 = cathode/K** for
diodes and LEDs (opposite of KiCad stock). Verify polarized-part orientation
against THIS convention, not the stock one.

## Known electrical caveats to check on hardware

- OPA1622 DIP-8 adapter must tie the DFN’s EN pin high and handle its GND pin.
- Custom library pins are typed “passive” → ERC cannot catch power/conflict
  errors. A clean ERC is low-information until pin types are real. For
  production, assign proper pin electrical types.
