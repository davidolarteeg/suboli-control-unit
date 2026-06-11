#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import uuid
from pathlib import Path

PROJECT = "suboli_control"
ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / f"{PROJECT}.kicad_sch"
PCB = ROOT / f"{PROJECT}.kicad_pcb"
PRO = ROOT / f"{PROJECT}.kicad_pro"
SYM = ROOT / f"{PROJECT}.kicad_sym"
SYMTABLE = ROOT / "sym-lib-table"

ROOT_UUID = uuid.uuid5(uuid.NAMESPACE_URL, "suboli-control-root")


def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"suboli-control:{name}"))


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def eff(size: float = 1.27, hide: bool = False, justify: str | None = None) -> str:
    parts = [f'(font (size {size:.2f} {size:.2f}))']
    if justify:
        parts.append(f"(justify {justify})")
    if hide:
        parts.append("(hide yes)")
    return "(effects " + " ".join(parts) + ")"


def snap(value: float) -> float:
    return round(value / 2.54) * 2.54


class SymbolDef:
    def __init__(self, name: str, ref: str, value: str, pins: list[tuple[str, str, float]], in_bom: bool = True, on_board: bool = True, pin_type: str = "passive"):
        self.name = name
        self.ref = ref
        self.value = value
        self.pins = pins
        self.in_bom = in_bom
        self.on_board = on_board
        self.pin_type = pin_type

    @property
    def height(self) -> float:
        y_vals = [p[2] for p in self.pins]
        return max(7.62, max(y_vals) - min(y_vals) + 5.08)

    @property
    def y_min(self) -> float:
        return min(p[2] for p in self.pins)

    @property
    def y_max(self) -> float:
        return max(p[2] for p in self.pins)

    def pin_xy(self, pin: str) -> tuple[float, float]:
        for number, _name, y in self.pins:
            if number == pin:
                return (-10.16, y)
        raise KeyError(pin)

    def sexpr(self, cache_library: bool = True) -> str:
        top = self.y_min - 2.54
        bottom = self.y_max + 2.54
        title_y = top - 3.81
        value_y = bottom + 3.81
        lib_name = f"{PROJECT}:{self.name}" if cache_library else self.name
        lines = [
            f'  (symbol "{lib_name}"',
            "    (pin_names (offset 1.016))",
            "    (exclude_from_sim no)",
            f"    (in_bom {'yes' if self.in_bom else 'no'})",
            f"    (on_board {'yes' if self.on_board else 'no'})",
            f'    (property "Reference" "{esc(self.ref)}" (at 0 {title_y:.2f} 0) {eff()})',
            f'    (property "Value" "{esc(self.value)}" (at 0 {value_y:.2f} 0) {eff()})',
            f'    (property "Footprint" "" (at 0 0 0) {eff(hide=True)})',
            f'    (property "Datasheet" "~" (at 0 0 0) {eff(hide=True)})',
            f'    (property "Description" "{esc(self.value)}" (at 0 0 0) {eff(hide=True)})',
            f'    (symbol "{self.name}_0_1"',
            f"      (rectangle (start -6.35 {top:.2f}) (end 8.89 {bottom:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))",
            f'      (text "{esc(self.value[:28])}" (at 1.27 {(top + bottom) / 2:.2f} 0) {eff(1.00)})',
            "    )",
            f'    (symbol "{self.name}_1_1"',
        ]
        for number, name, y in self.pins:
            lines.extend(
                [
                    f"      (pin {self.pin_type} line (at -10.16 {y:.2f} 0) (length 3.81)",
                    f'        (name "{esc(name)}" {eff(1.00)})',
                    f'        (number "{esc(number)}" {eff(1.00)})',
                    "      )",
                ]
            )
        lines.extend(["    )", "    (embedded_fonts no)", "  )"])
        return "\n".join(lines)


def pins(names: list[str]) -> list[tuple[str, str, float]]:
    return [(str(i + 1), name, i * 2.54) for i, name in enumerate(names)]


SYMBOLS: dict[str, SymbolDef] = {
    "A1_MA12070_MODULE": SymbolDef(
        "A1_MA12070_MODULE",
        "A",
        "MA12070 stereo module socket",
        pins(["PVDD", "GND", "IN0A", "IN0B", "IN1A", "IN1B", "OUT0A", "OUT0B", "OUT1A", "OUT1B", "EN/MUTE"]),
    ),
    "A2_OPA1622_DIP8": SymbolDef(
        "A2_OPA1622_DIP8",
        "A",
        "OPA1622 dual op-amp DIP-8 adapter",
        [
            ("1", "OUT_L", 0.00),
            ("2", "IN_L-", 2.54),
            ("3", "IN_L+", 5.08),
            ("4", "V-", 7.62),
            ("5", "IN_R+", 10.16),
            ("6", "IN_R-", 12.70),
            ("7", "OUT_R", 15.24),
            ("8", "V+", 17.78),
        ],
    ),
    "TLE2426_3PIN": SymbolDef("TLE2426_3PIN", "U", "TLE2426 rail splitter", pins(["IN", "COM", "OUT"])),
    "CONN_2": SymbolDef("CONN_2", "J", "2-pin panel header", pins(["1", "2"])),
    "CONN_3_TRS": SymbolDef("CONN_3_TRS", "J", "TRS panel header", pins(["Tip", "Ring", "Sleeve"])),
    "CONN_4": SymbolDef("CONN_4", "J", "4-pin panel header", pins(["1", "2", "3", "4"])),
    "SW_DPST_HEADER": SymbolDef("SW_DPST_HEADER", "SW", "DPST panel switch header", pins(["A_IN", "A_OUT", "B_IN", "B_OUT"])),
    "POT_DUAL_HEADER": SymbolDef("POT_DUAL_HEADER", "P", "Dual-gang pot panel header", pins(["L_TOP", "L_WIPER", "L_BOTTOM", "R_TOP", "R_WIPER", "R_BOTTOM"])),
    "R_2PIN": SymbolDef("R_2PIN", "R", "Resistor", pins(["1", "2"])),
    "C_2PIN": SymbolDef("C_2PIN", "C", "Capacitor", pins(["1", "2"])),
    "CP_2PIN": SymbolDef("CP_2PIN", "C", "Polarized capacitor", pins(["+", "-"])),
    "D_2PIN": SymbolDef("D_2PIN", "D", "Diode", pins(["A", "K"])),
    "LED_2PIN": SymbolDef("LED_2PIN", "LED", "LED", pins(["A", "K"])),
    "FUSE_2PIN": SymbolDef("FUSE_2PIN", "F", "Fuse/PPTC", pins(["1", "2"])),
    "FERRITE_2PIN": SymbolDef("FERRITE_2PIN", "FB", "Ferrite bead", pins(["1", "2"])),
    "NET_TIE_2": SymbolDef("NET_TIE_2", "NT", "Single star ground net tie", pins(["GND_SIG", "GND_STAR"])),
    "PWR_FLAG_LOCAL": SymbolDef("PWR_FLAG_LOCAL", "#FLG", "PWR_FLAG", pins(["1"]), in_bom=False, on_board=False, pin_type="power_out"),
}


class Component:
    def __init__(self, ref: str, value: str, sym: str, x: float, y: float, nets: dict[str, str], dnp: bool = False, fields: dict[str, str] | None = None):
        self.ref = ref
        self.value = value
        self.sym = sym
        self.x = snap(x)
        self.y = snap(y)
        self.nets = nets
        self.dnp = dnp
        self.fields = fields or {}
        self.uuid = uid(f"sym:{ref}")

    def pin_abs(self, pin: str) -> tuple[float, float]:
        sx, sy = SYMBOLS[self.sym].pin_xy(pin)
        return self.x + sx, self.y - sy

    def sexpr(self) -> str:
        sd = SYMBOLS[self.sym]
        lines = [
            "  (symbol",
            f'    (lib_id "{PROJECT}:{sd.name}")',
            f"    (at {self.x:.2f} {self.y:.2f} 0)",
            "    (unit 1)",
            "    (exclude_from_sim no)",
            f"    (in_bom {'no' if self.ref.startswith('#') else 'yes'})",
            f"    (on_board {'no' if self.ref.startswith('#') else 'yes'})",
            f"    (dnp {'yes' if self.dnp else 'no'})",
            f'    (uuid "{self.uuid}")',
            f'    (property "Reference" "{esc(self.ref)}" (at {self.x:.2f} {self.y - sd.height - 4.0:.2f} 0) {eff()})',
            f'    (property "Value" "{esc(self.value)}" (at {self.x:.2f} {self.y + 4.0:.2f} 0) {eff()})',
            f'    (property "Footprint" "" (at {self.x:.2f} {self.y:.2f} 0) {eff(hide=True)})',
            f'    (property "Datasheet" "~" (at {self.x:.2f} {self.y:.2f} 0) {eff(hide=True)})',
        ]
        for idx, (key, value) in enumerate(self.fields.items(), start=1):
            lines.append(f'    (property "{esc(key)}" "{esc(value)}" (at {self.x:.2f} {self.y + 4.0 + idx*3.0:.2f} 0) {eff(0.90)})')
        for number, _name, _y in sd.pins:
            lines.append(f'    (pin "{esc(number)}" (uuid "{uid(f"pin:{self.ref}:{number}")}"))')
        lines.extend(
            [
                "    (instances",
                f'      (project "{PROJECT}"',
                f'        (path "/{ROOT_UUID}"',
                f'          (reference "{esc(self.ref)}")',
                "          (unit 1)",
                "        )",
                "      )",
                "    )",
                "  )",
            ]
        )
        return "\n".join(lines)


components: list[Component] = [
    Component("J_DC", "DC barrel jack panel header 5.5x2.5", "CONN_2", 28, 34, {"1": "+19V_RAW", "2": "GND_RAW"}, fields={"Pinout": "1=center, 2=sleeve"}),
    Component("SW1", "DPST power switch panel header", "SW_DPST_HEADER", 68, 36, {"1": "+19V_RAW", "2": "+19V_SW", "3": "GND_RAW", "4": "GND_STAR"}),
    Component("F1", "PPTC fuse ~3 A", "FUSE_2PIN", 106, 34, {"1": "+19V_SW", "2": "+19V_F"}),
    Component("D1", "SB560 Schottky reverse-polarity diode", "D_2PIN", 138, 34, {"1": "+19V_F", "2": "+19V"}),
    Component("TVS1", "SMBJ24A TVS", "D_2PIN", 138, 54, {"1": "+19V", "2": "GND_STAR"}, dnp=True),
    Component("C1", "1000 uF / 35 V bulk", "CP_2PIN", 170, 34, {"1": "+19V", "2": "GND_STAR"}),
    Component("C2", "100 nF main bypass", "C_2PIN", 170, 54, {"1": "+19V", "2": "GND_STAR"}),
    Component("R1", "8.2 k LED resistor", "R_2PIN", 204, 34, {"1": "+19V", "2": "PWR_LED_ANODE"}),
    Component("LED1", "Power LED", "LED_2PIN", 236, 34, {"1": "PWR_LED_ANODE", "2": "GND_STAR"}),
    Component("FB1", "Ferrite bead >=1 A", "FERRITE_2PIN", 204, 58, {"1": "+19V", "2": "+19V_HP"}),
    Component("J_IN", "3.5 mm TRS input panel header", "CONN_3_TRS", 30, 104, {"1": "IN_L", "2": "IN_R", "3": "GND_SIG"}, fields={"Pinout": "Tip=IN_L, Ring=IN_R, Sleeve=GND_SIG"}),
    Component("P_TACT", "Dual-gang 10 k log tactile volume panel header", "POT_DUAL_HEADER", 86, 104, {"1": "IN_L", "2": "TACT_INL", "3": "GND_SIG", "4": "IN_R", "5": "TACT_INR", "6": "GND_SIG"}, fields={"Wiring": "top=input, wiper=output, bottom=GND_SIG"}),
    Component("P_HP", "Dual-gang 10 k log headphone volume panel header", "POT_DUAL_HEADER", 86, 144, {"1": "IN_L", "2": "HP_INL", "3": "GND_SIG", "4": "IN_R", "5": "HP_INR", "6": "GND_SIG"}, fields={"Wiring": "top=input, wiper=output, bottom=GND_SIG"}),
    Component("A1", "MA12070 stereo Class-D module socket, 2xBTL", "A1_MA12070_MODULE", 178, 104, {"1": "+19V", "2": "GND_STAR", "3": "TACT_INL", "4": "GND_SIG", "5": "TACT_INR", "6": "GND_SIG", "7": "OUTL+", "8": "OUTL−", "9": "OUTR+", "10": "OUTR−"}, fields={"Pending": "EN/MUTE left NC until module pad map/behavior is supplied"}),
    Component("J_SPK", "4-pole Speakon/XLR panel header", "CONN_4", 292, 104, {"1": "OUTL+", "2": "OUTL−", "3": "OUTR+", "4": "OUTR−"}, fields={"Pinout": "1+=OUTL+, 1-=OUTL−, 2+=OUTR+, 2-=OUTR−"}),
    Component("C3", "1000 uF / 25 V HP branch bulk", "CP_2PIN", 236, 58, {"1": "+19V_HP", "2": "GND_SIG"}),
    Component("C4", "100 nF HP branch bypass", "C_2PIN", 268, 58, {"1": "+19V_HP", "2": "GND_SIG"}),
    Component("U_vg", "TLE2426 rail splitter", "TLE2426_3PIN", 236, 82, {"1": "+19V_HP", "2": "GND_SIG", "3": "VGND"}),
    Component("C5", "10 uF A2 V+ bulk decouple", "CP_2PIN", 198, 158, {"1": "+19V_HP", "2": "GND_STAR"}),
    Component("C6", "10 uF VGND decouple", "CP_2PIN", 198, 178, {"1": "VGND", "2": "GND_SIG"}),
    Component("C7", "100 nF A2 V+ bypass", "C_2PIN", 230, 158, {"1": "+19V_HP", "2": "GND_STAR"}),
    Component("C8", "100 nF VGND bypass", "C_2PIN", 230, 178, {"1": "VGND", "2": "GND_SIG"}),
    Component("C9", "1 uF film L input coupling", "C_2PIN", 150, 156, {"1": "HP_INL", "2": "A2_INL_BIAS"}),
    Component("C10", "1 uF film R input coupling", "C_2PIN", 150, 184, {"1": "HP_INR", "2": "A2_INR_BIAS"}),
    Component("R2", "47-100 k L input bias to VGND", "R_2PIN", 176, 156, {"1": "A2_INL_BIAS", "2": "VGND"}),
    Component("R3", "47-100 k R input bias to VGND", "R_2PIN", 176, 184, {"1": "A2_INR_BIAS", "2": "VGND"}),
    Component("A2", "OPA1622 dual op-amp on DIP-8 adapter", "A2_OPA1622_DIP8", 274, 168, {"1": "A2_OUT_L_RAW", "2": "A2_L_FB", "3": "A2_INL_BIAS", "4": "GND_STAR", "5": "A2_INR_BIAS", "6": "A2_R_FB", "7": "A2_OUT_R_RAW", "8": "+19V_HP"}),
    Component("R4", "10 k L feedback", "R_2PIN", 316, 148, {"1": "A2_OUT_L_RAW", "2": "A2_L_FB"}),
    Component("R5", "10 k L gain to VGND", "R_2PIN", 316, 162, {"1": "A2_L_FB", "2": "VGND"}),
    Component("R6", "10 k R feedback", "R_2PIN", 316, 182, {"1": "A2_OUT_R_RAW", "2": "A2_R_FB"}),
    Component("R7", "10 k R gain to VGND", "R_2PIN", 316, 196, {"1": "A2_R_FB", "2": "VGND"}),
    Component("R8", "10 ohm L output series", "R_2PIN", 350, 150, {"1": "A2_OUT_L_RAW", "2": "HP_L_SER"}),
    Component("R9", "10 ohm R output series", "R_2PIN", 350, 184, {"1": "A2_OUT_R_RAW", "2": "HP_R_SER"}),
    Component("C11", "220-470 uF / 25 V L output coupling", "CP_2PIN", 382, 150, {"1": "HP_L_SER", "2": "HP_OUT_L"}),
    Component("C12", "220-470 uF / 25 V R output coupling", "CP_2PIN", 382, 184, {"1": "HP_R_SER", "2": "HP_OUT_R"}),
    Component("J_HP", "3.5 mm TRS headphone panel header", "CONN_3_TRS", 414, 168, {"1": "HP_OUT_L", "2": "HP_OUT_R", "3": "GND_SIG"}, fields={"Pinout": "Tip=HP_OUT_L, Ring=HP_OUT_R, Sleeve=GND_SIG"}),
    Component("NT1", "Only GND_SIG to GND_STAR connection", "NET_TIE_2", 268, 36, {"1": "GND_SIG", "2": "GND_STAR"}, fields={"Purpose": "single physical star point"}),
    Component("#FLG1", "PWR_FLAG +19V_RAW", "PWR_FLAG_LOCAL", 28, 20, {"1": "+19V_RAW"}),
    Component("#FLG2", "PWR_FLAG +19V", "PWR_FLAG_LOCAL", 170, 20, {"1": "+19V"}),
    Component("#FLG3", "PWR_FLAG GND_STAR", "PWR_FLAG_LOCAL", 268, 20, {"1": "GND_STAR"}),
    Component("#FLG4", "PWR_FLAG +19V_HP", "PWR_FLAG_LOCAL", 236, 20, {"1": "+19V_HP"}),
    Component("#FLG5", "PWR_FLAG GND_SIG", "PWR_FLAG_LOCAL", 300, 20, {"1": "GND_SIG"}),
    Component("#FLG6", "PWR_FLAG VGND", "PWR_FLAG_LOCAL", 330, 20, {"1": "VGND"}),
]


def label_for(comp: Component, pin: str, net: str) -> str:
    x, y = comp.pin_abs(pin)
    lx = x - 10.16
    return "\n".join(
        [
            f'  (wire (pts (xy {x:.2f} {y:.2f}) (xy {lx:.2f} {y:.2f})) (stroke (width 0) (type default)) (uuid "{uid(f"wire:{comp.ref}:{pin}")}"))',
            f'  (label "{esc(net)}" (at {lx:.2f} {y:.2f} 0) {eff(0.90, justify="right")} (uuid "{uid(f"label:{comp.ref}:{pin}:{net}")}"))',
        ]
    )


def no_connect(comp: Component, pin: str) -> str:
    x, y = comp.pin_abs(pin)
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{uid(f"nc:{comp.ref}:{pin}")}"))'


def text_block(text: str, x: float, y: float, size: float = 1.15) -> str:
    return f'  (text "{esc(text)}" (at {x:.2f} {y:.2f} 0) {eff(size, justify="left")} (uuid "{uid(f"text:{text[:24]}:{x}:{y}")}"))'


def write_project_metadata() -> None:
    if not PRO.exists():
        return
    data = json.loads(PRO.read_text())
    data.setdefault("meta", {})
    data["meta"]["filename"] = f"{PROJECT}.kicad_pro"
    data.setdefault("text_variables", {})
    data["text_variables"]["PROJECT_NAME"] = "SUBOLI Control Unit"
    PRO.write_text(json.dumps(data, indent=2) + "\n")


def symbol_library() -> str:
    parts = [
        "(kicad_symbol_lib",
        "  (version 20250114)",
        '  (generator "codex-kicad-mcp-schematic-phase")',
        '  (generator_version "1")',
    ]
    for sym in SYMBOLS.values():
        parts.append(sym.sexpr(cache_library=False))
    parts.append(")")
    return "\n".join(parts) + "\n"


def sym_lib_table() -> str:
    return f"""(sym_lib_table
  (lib (name "{PROJECT}")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "SUBOLI project-local symbols"))
)
"""


def schematic() -> str:
    parts = [
        "(kicad_sch",
        "  (version 20250114)",
        '  (generator "codex-kicad-mcp-schematic-phase")',
        '  (generator_version "1")',
        f'  (uuid "{ROOT_UUID}")',
        '  (paper "A3")',
        "  (title_block",
        '    (title "SUBOLI Control Unit Carrier / Motherboard")',
        '    (date "2026-06-08")',
        '    (rev "Schematic phase")',
        '    (company "SUBOLI")',
        "  )",
        "  (lib_symbols",
    ]
    for sym in SYMBOLS.values():
        parts.append(sym.sexpr(cache_library=True))
    parts.append("  )")
    parts.extend(
        [
            text_block("SUBOLI control unit - 2-layer carrier/motherboard schematic phase", 20, 14, 1.80),
            text_block("Panel-mounted parts are represented as wired panel headers. A1 is a purchased MA12070 module socket; A2 is an OPA1622 DIP-8 adapter/socket.", 20, 22, 1.10),
            text_block("Tactile = stereo 2xBTL. Never common OUT0B/OUT1B. No output LC filter.", 20, 206, 1.25),
            text_block("A1 EN/MUTE is intentionally left NC until the exact MA12070 module pad map and control behavior are supplied.", 20, 214, 1.05),
            text_block("Headphone output is AC-coupled: J_HP sleeve connects to GND_SIG, not VGND.", 20, 222, 1.05),
            text_block("NT1 is the only intended GND_SIG to GND_STAR connection. Keep Class-D return current out of the headphone/input area during layout.", 20, 230, 1.05),
            text_block("C5/C7 decouple A2 +19V_HP to GND_STAR. C6/C8 decouple VGND to GND_SIG for bias stability.", 20, 238, 1.05),
        ]
    )
    for comp in components:
        parts.append(comp.sexpr())
        for pin, net in comp.nets.items():
            parts.append(label_for(comp, pin, net))
    parts.append(no_connect(next(c for c in components if c.ref == "A1"), "11"))
    parts.extend(
        [
            "  (sheet_instances",
            '    (path "/"',
            '      (page "1")',
            "    )",
            "  )",
            "  (embedded_fonts no)",
            ")",
        ]
    )
    return "\n".join(parts) + "\n"


def pcb_placeholder() -> str:
    return f"""(kicad_pcb
  (version 20250114)
  (generator "codex-kicad-mcp-schematic-phase")
  (generator_version "1")
  (general
    (thickness 1.6)
    (legacy_teardrops no)
  )
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (2 "B.Cu" signal)
    (9 "F.Adhes" user "F.Adhesive")
    (11 "B.Adhes" user "B.Adhesive")
    (13 "F.Paste" user)
    (15 "B.Paste" user)
    (5 "F.SilkS" user "F.Silkscreen")
    (7 "B.SilkS" user "B.Silkscreen")
    (1 "F.Mask" user)
    (3 "B.Mask" user)
    (17 "Dwgs.User" user "User.Drawings")
    (19 "Cmts.User" user "User.Comments")
    (21 "Eco1.User" user "User.Eco1")
    (23 "Eco2.User" user "User.Eco2")
    (25 "Edge.Cuts" user)
    (27 "Margin" user)
    (31 "F.CrtYd" user "F.Courtyard")
    (29 "B.CrtYd" user "B.Courtyard")
    (35 "F.Fab" user)
    (33 "B.Fab" user)
  )
  (setup
    (stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "None")
      (dielectric_constraints no)
    )
    (pad_to_mask_clearance 0)
    (allow_soldermask_bridges_in_footprints no)
    (tenting front back)
  )
  (net 0 "")
  (gr_text "SUBOLI schematic phase only - no board outline, footprints, placement, routing, zones, STEP, or Gerbers yet"
    (at 10 10 0)
    (layer "Cmts.User")
    (uuid "{uid("pcb-placeholder-note")}")
    (effects (font (size 1.2 1.2) (thickness 0.15)) (justify left))
  )
  (embedded_fonts no)
)
"""


def main() -> None:
    (ROOT / "tools").mkdir(exist_ok=True)
    SCH.write_text(schematic())
    PCB.write_text(pcb_placeholder())
    SYM.write_text(symbol_library())
    SYMTABLE.write_text(sym_lib_table())
    write_project_metadata()


if __name__ == "__main__":
    main()
