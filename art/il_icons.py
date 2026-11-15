"""Ironfist Legacy icon set: the Red Clause ink glyphs plus new dwarven / Cinder-Tusk glyphs (256 px)."""
import math, os
from chibi import render, INK, DEFS
import icons as base
from icons import G, glyph, S

OUT = "/home/claude/il/module/assets/icons"


@glyph
def fist(c="#efe2c0"):
    return (f'<rect x="120" y="30" width="16" height="200" fill="#5a5660" {S(6)}/><path d="M112 228 L128 252 L144 228 Z" fill="#5a5660" {S(5)}/>'
            f'<path d="M70 100 h116 v66 q0 36 -44 36 h-28 q-44 0 -44 -36 Z" fill="{c}" {S(8)}/>'
            + "".join(f'<path d="M{70+k*29} 100 v-24 q14 -14 29 0 v24" fill="{c}" {S(7)}/>' for k in range(4))
            + f'<path d="M70 136 q-30 -6 -28 24 q4 24 34 20" fill="{c}" {S(7)}/>')


@glyph
def rivetshield(c="#5a5660"):
    return (f'<path d="M48 40 H208 V140 Q208 210 128 236 Q48 210 48 140 Z" fill="{c}" {S(10)}/>'
            f'<path d="M64 56 H192 V138 Q192 192 128 214 Q64 192 64 138 Z" fill="none" stroke="#b8862e" stroke-width="7"/>'
            f'<circle cx="98" cy="96" r="16" fill="#c8963a" {S(6)}/><circle cx="160" cy="92" r="12" fill="#9aa0aa" {S(6)}/>'
            f'<path d="M90 160 l30 22 M170 120 l-20 30" stroke="{INK}" stroke-width="6"/>')


@glyph
def rivet(c="#c8963a"):
    return (f'<circle cx="128" cy="128" r="88" fill="{c}" {S(10)}/><circle cx="128" cy="128" r="56" fill="none" stroke="#6a4410" stroke-width="8"/>'
            f'<circle cx="104" cy="104" r="20" fill="#fff" opacity="0.4"/><path d="M60 196 L196 60" stroke="#6a4410" stroke-width="5" opacity="0.6"/>')


@glyph
def valve(c="#c0283a"):
    return (f'<circle cx="128" cy="128" r="92" fill="none" stroke="{INK}" stroke-width="30"/><circle cx="128" cy="128" r="92" fill="none" stroke="{c}" stroke-width="16"/>'
            + "".join(f'<line x1="128" y1="128" x2="{128+math.cos(a)*92:.0f}" y2="{128+math.sin(a)*92:.0f}" stroke="{INK}" stroke-width="22"/><line x1="128" y1="128" x2="{128+math.cos(a)*92:.0f}" y2="{128+math.sin(a)*92:.0f}" stroke="{c}" stroke-width="10"/>' for a in [i*math.pi/3 for i in range(6)])
            + f'<circle cx="128" cy="128" r="26" fill="#b8862e" {S(8)}/>')


@glyph
def gauge(c="#efe2c0"):
    return (f'<circle cx="128" cy="128" r="100" fill="#3a3640" {S(10)}/><circle cx="128" cy="128" r="80" fill="{c}" {S(6)}/>'
            + "".join(f'<line x1="{128+math.cos(a)*62:.0f}" y1="{128+math.sin(a)*62:.0f}" x2="{128+math.cos(a)*76:.0f}" y2="{128+math.sin(a)*76:.0f}" stroke="{INK}" stroke-width="{7 if k%3==0 else 4}"/>' for k, a in enumerate([-math.pi*1.2+i*math.pi*1.4/9 for i in range(10)]))
            + f'<path d="M{128+math.cos(-0.5)*70:.0f} {128+math.sin(-0.5)*70:.0f} A70 70 0 0 1 {128+math.cos(0.2)*70:.0f} {128+math.sin(0.2)*70:.0f}" stroke="#c0283a" stroke-width="12" fill="none"/>'
            f'<path d="M128 128 L190 100" stroke="{INK}" stroke-width="10" stroke-linecap="round"/><circle cx="128" cy="128" r="14" fill="#b8862e" {S(5)}/>')


@glyph
def runestone(c="#7ac0e0", ch="ᚱ"):
    return (f'<path d="M70 40 L186 40 L214 120 L186 226 L70 226 L42 120 Z" fill="#5a5660" {S(10)}/>'
            f'<path d="M70 40 L186 40 L214 120 L186 226 Z" fill="url(#hatch)" opacity="0.3"/>'
            f'<circle cx="128" cy="134" r="70" fill="{c}" opacity="0.25"/>'
            f'<text x="128" y="172" font-family="Cinzel" font-weight="900" font-size="104" text-anchor="middle" fill="{c}" stroke="{INK}" stroke-width="4">{ch}</text>')


@glyph
def hammer(c="#9aa0aa"):
    return (f'<rect x="116" y="90" width="26" height="150" rx="8" fill="#5a3416" {S(7)}/>'
            f'<rect x="56" y="30" width="146" height="74" rx="12" fill="{c}" {S(9)}/><rect x="56" y="58" width="146" height="16" fill="#b8862e" {S(4)}/>')


@glyph
def anvil(c="#5a5660"):
    return (f'<path d="M30 80 H190 Q240 80 230 110 Q190 110 170 130 L170 160 H90 L90 130 Q50 120 30 80 Z" fill="{c}" {S(9)}/>'
            f'<path d="M80 160 H180 L200 220 H60 Z" fill="#3a3640" {S(9)}/><path d="M70 40 l20 30 M120 30 l0 36 M170 40 l-20 30" stroke="#ff9a3a" stroke-width="8"/>')


@glyph
def cleaver(c="#9aa0aa"):
    return (f'<path d="M60 40 L200 40 Q220 120 190 160 L100 160 L60 40 Z" fill="{c}" {S(9)}/><circle cx="170" cy="72" r="12" fill="{INK}"/>'
            f'<rect x="70" y="150" width="40" height="90" rx="10" fill="#3a2414" {S(7)}/><path d="M80 60 L190 60" stroke="#fff" stroke-width="6" opacity="0.5"/>')


@glyph
def axe(c="#9aa0aa"):
    return (f'<rect x="118" y="30" width="22" height="210" rx="8" fill="#4a2c14" {S(7)}/>'
            f'<path d="M140 40 Q240 30 236 130 Q200 100 140 110 Z" fill="{c}" {S(8)}/><path d="M118 40 Q30 40 26 120 Q60 100 118 104 Z" fill="{c}" {S(8)}/>')


@glyph
def tusk(c="#f4ecd0"):
    return (f'<path d="M70 220 Q40 120 110 40 Q90 130 110 220 Z" fill="{c}" {S(8)}/><path d="M186 220 Q216 120 146 40 Q166 130 146 220 Z" fill="{c}" {S(8)}/>'
            f'<circle cx="128" cy="180" r="24" fill="#ff7a1a" {S(6)}/>')


@glyph
def drop(c="#5ab0e0"):
    return (f'<path d="M128 26 C128 26 50 120 50 160 A78 78 0 0 0 206 160 C206 120 128 26 128 26 Z" fill="{c}" {S(9)}/>'
            f'<path d="M90 150 Q92 120 110 100" stroke="#fff" stroke-width="10" fill="none" opacity="0.6"/>')


@glyph
def mushroom(c="#9adf5a"):
    return (f'<path d="M110 130 L100 230 L156 230 L146 130 Z" fill="#e8dcc0" {S(8)}/><path d="M30 140 Q40 40 128 36 Q216 40 226 140 Z" fill="{c}" {S(9)}/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#efe2c0" {S(4)}/>' for x, y, r in ((80, 100, 14), (130, 70, 18), (180, 104, 12))))


@glyph
def lift(c="#b8862e"):
    return (f'<line x1="128" y1="10" x2="128" y2="70" stroke="{INK}" stroke-width="10"/><rect x="50" y="70" width="156" height="160" fill="none" {S(10)}/>'
            + "".join(f'<line x1="{50+k*31}" y1="70" x2="{50+k*31}" y2="230" stroke="{c}" stroke-width="7"/>' for k in range(6))
            + f'<rect x="50" y="70" width="156" height="22" fill="{c}" {S(6)}/><rect x="50" y="208" width="156" height="22" fill="{c}" {S(6)}/>')


@glyph
def horn(c="#e8dcc0"):
    return (f'<path d="M30 180 Q60 60 200 40 L220 70 Q110 100 90 200 Z" fill="{c}" {S(9)}/><ellipse cx="210" cy="56" rx="22" ry="30" fill="#3a2414" {S(6)}/>'
            f'<path d="M60 150 L80 160 M80 110 L100 124 M110 80 L126 96" stroke="#b8862e" stroke-width="10"/>')


@glyph
def banner(c="#7a1a18"):
    return (f'<rect x="60" y="20" width="12" height="220" fill="#5a3416" {S(5)}/><path d="M72 30 H210 V170 L141 140 L72 170 Z" fill="{c}" {S(8)}/>'
            + fist("#efe2c0").replace('<rect x="120"', '<rect transform="translate(70,30) scale(0.45)" x="120"').replace('<path d="M112', '<path transform="translate(70,30) scale(0.45)" d="M112').replace('<path d="M70 100 h', '<path transform="translate(70,30) scale(0.45)" d="M70 100 h').replace('<path d="M70 136', '<path transform="translate(70,30) scale(0.45)" d="M70 136'))


@glyph
def steam(c="#cfd6e0"):
    return (f'<rect x="60" y="180" width="136" height="50" rx="8" fill="#5a5660" {S(8)}/>'
            + "".join(f'<path d="M{x} 170 q-30 -40 0 -80 q30 -40 0 -80" fill="none" stroke="{INK}" stroke-width="26" stroke-linecap="round"/><path d="M{x} 170 q-30 -40 0 -80 q30 -40 0 -80" fill="none" stroke="{c}" stroke-width="14" stroke-linecap="round"/>' for x in (90, 128, 166)))


@glyph
def piston(c="#9aa0aa"):
    return (f'<rect x="80" y="20" width="96" height="120" rx="10" fill="#3a3640" {S(9)}/><rect x="110" y="130" width="36" height="70" fill="{c}" {S(7)}/>'
            f'<rect x="60" y="196" width="136" height="44" rx="10" fill="{c}" {S(9)}/><path d="M40 230 l-20 10 M216 230 l20 10" stroke="#ff9a3a" stroke-width="8"/>')


@glyph
def wrench(c="#9aa0aa"):
    return (f'<g transform="rotate(40 128 128)"><rect x="112" y="80" width="32" height="160" rx="10" fill="{c}" {S(8)}/>'
            f'<path d="M80 80 Q70 10 128 6 Q186 10 176 80 L148 80 L148 36 L108 36 L108 80 Z" fill="{c}" {S(8)}/></g>')


@glyph
def bomb(c="#2a2630"):
    return (f'<circle cx="118" cy="148" r="82" fill="{c}" {S(9)}/><circle cx="92" cy="122" r="18" fill="#fff" opacity="0.3"/>'
            f'<rect x="160" y="54" width="36" height="36" fill="#b8862e" {S(6)}/><path d="M178 54 q20 -40 50 -30" fill="none" stroke="#3a2a14" stroke-width="8"/>'
            f'<circle cx="230" cy="24" r="20" fill="#ffd27a" filter="url(#glw)"/>')


@glyph
def map_(c="#efe2c0"):
    return (f'<path d="M30 60 L90 40 L166 60 L226 40 L226 200 L166 220 L90 200 L30 220 Z" fill="{c}" {S(9)}/>'
            f'<path d="M90 40 V200 M166 60 V220" stroke="{INK}" stroke-width="5" opacity="0.6"/>'
            f'<path d="M50 180 Q90 120 130 150 T210 80" stroke="#c0283a" stroke-width="8" fill="none" stroke-dasharray="14 10"/><path d="M196 70 l20 20 M216 70 l-20 20" stroke="#c0283a" stroke-width="9"/>')


G["map"] = map_


@glyph
def manual(c="#3a2a1a"):
    return (f'<rect x="50" y="36" width="156" height="190" rx="8" fill="{c}" {S(9)}/><rect x="62" y="36" width="20" height="190" fill="#120909"/>'
            + gauge("#efe2c0").replace('<circle cx="128" cy="128" r="100"', '<circle transform="translate(55,45) scale(0.6)" cx="128" cy="128" r="100"')
            .replace('<circle cx="128" cy="128" r="80"', '<circle transform="translate(55,45) scale(0.6)" cx="128" cy="128" r="80"'))


@glyph
def badge2(c="#c8963a"):
    return (f'<path d="M128 26 L222 70 V134 Q222 196 128 232 Q34 196 34 134 V70 Z" fill="{c}" {S(10)}/>'
            + fist("#efe2c0").replace('<rect x="120"', '<g transform="translate(64,62) scale(0.5)"><rect x="120"', 1) + '</g>')


@glyph
def compact(c="#e8b496"):
    return (base.scroll("#efe2c0")
            + f'<path d="M30 200 L90 160 L130 176 L110 196 L150 196 L180 176 L226 200 L180 236 L80 236 Z" fill="{c}" {S(7)}/>'
            f'<path d="M30 200 L90 160 L130 176 L110 196 L150 196 L180 176 L226 200 L180 236 L80 236 Z" fill="#9ab84a" opacity="0.45"/>')


@glyph
def filter_(c="#c87a4a"):
    return (f'<path d="M50 60 H206 L170 200 H86 Z" fill="{c}" {S(9)}/><ellipse cx="128" cy="60" rx="78" ry="20" fill="#8a4a2a" {S(7)}/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{INK}"/>' for x in (100, 128, 156) for y in (110, 150))
            + f'<path d="M128 200 v30" stroke="#5ab0e0" stroke-width="12"/>')


G["filter"] = filter_


@glyph
def lantern(c="#ffb35a"):
    return (f'<circle cx="128" cy="140" r="90" fill="{c}" opacity="0.25"/><rect x="88" y="80" width="80" height="120" rx="12" fill="{c}" {S(8)}/>'
            f'<rect x="80" y="64" width="96" height="22" fill="#5a5660" {S(6)}/><rect x="80" y="196" width="96" height="22" fill="#5a5660" {S(6)}/>'
            f'<path d="M104 64 Q128 10 152 64" fill="none" {S(8)}/>')


@glyph
def pick(c="#9aa0aa"):
    return (f'<rect x="116" y="60" width="24" height="180" rx="8" fill="#5a3416" {S(7)}/>'
            f'<path d="M20 90 Q128 20 236 90 Q128 54 20 90 Z" fill="{c}" {S(8)}/>')


@glyph
def kitchen(c="#d8a050"):
    return (f'<path d="M40 110 H216 L196 210 Q128 236 60 210 Z" fill="#3a3640" {S(9)}/><ellipse cx="128" cy="110" rx="88" ry="22" fill="{c}" {S(7)}/>'
            + "".join(f'<path d="M{x} 90 q-16 -30 0 -60" fill="none" stroke="#cfd6e0" stroke-width="9" opacity="0.8"/>' for x in (100, 128, 156)))


@glyph
def cog(c="#b8862e"):
    return base.gear(c)


@glyph
def chainbreak(c="#9a96a2"):
    return (f'<path d="M40 128 h50" stroke="{INK}" stroke-width="30" stroke-linecap="round"/><path d="M40 128 h50" stroke="{c}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M166 128 h50" stroke="{INK}" stroke-width="30" stroke-linecap="round"/><path d="M166 128 h50" stroke="{c}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M110 90 l10 30 l-14 14 l20 34 M146 90 l-10 30 l14 14 l-20 34" stroke="#ffd27a" stroke-width="8" fill="none"/>')


@glyph
def roar(c="#ff7a1a"):
    return (f'<path d="M40 128 Q40 60 110 60 L110 196 Q40 196 40 128 Z" fill="#7e9a5a" {S(8)}/>'
            + "".join(f'<path d="M{130+k*30} {128-40-k*16} Q{150+k*34} 128 {130+k*30} {128+40+k*16}" fill="none" stroke="{c}" stroke-width="10"/>' for k in range(3)))


@glyph
def hourglass(c="#ffd27a"):
    return (f'<rect x="60" y="24" width="136" height="22" rx="6" fill="#5a3416" {S(6)}/><rect x="60" y="210" width="136" height="22" rx="6" fill="#5a3416" {S(6)}/>'
            f'<path d="M76 46 H180 Q180 110 140 128 Q180 146 180 210 H76 Q76 146 116 128 Q76 110 76 46 Z" fill="#cfe8ff" fill-opacity="0.4" {S(7)}/>'
            f'<path d="M90 80 H166 Q150 112 128 122 Q106 112 90 80 Z M128 140 L128 190 M96 200 H160 Q150 180 128 176 Q106 180 96 200 Z" fill="{c}" stroke="{c}" stroke-width="3"/>')


@glyph
def cards(c="#7a1a18"):
    return (f'<rect x="40" y="60" width="110" height="160" rx="12" fill="#efe2c0" {S(7)} transform="rotate(-14 95 140)"/>'
            f'<rect x="106" y="40" width="110" height="160" rx="12" fill="{c}" {S(7)} transform="rotate(10 161 120)"/>'
            f'<circle cx="161" cy="120" r="30" fill="#b8862e" {S(5)}/>')


@glyph
def note(c="#ffd27a"):
    return (f'<path d="M90 190 V60 L200 36 V166" fill="none" stroke="{INK}" stroke-width="16"/><path d="M90 190 V60 L200 36 V166" fill="none" stroke="{c}" stroke-width="8"/>'
            f'<ellipse cx="70" cy="190" rx="30" ry="22" fill="{c}" {S(7)}/><ellipse cx="180" cy="166" rx="30" ry="22" fill="{c}" {S(7)}/>')


@glyph
def ev(c="#c09040", n="1"):
    return (base.scroll("#efe2c0")
            + f'<circle cx="190" cy="190" r="48" fill="#8e1424" {S(7)}/>'
            f'<text x="190" y="206" font-family="Cinzel" font-weight="900" font-size="44" text-anchor="middle" fill="{c}">E{n}</text>')


@glyph
def ore(c="#7ac0e0"):
    return (f'<path d="M40 170 L70 90 L140 60 L210 100 L220 180 L140 220 Z" fill="#4a4650" {S(9)}/>'
            f'<path d="M90 110 L130 90 L150 130 L110 150 Z M150 160 L190 140 L196 180 Z" fill="{c}" {S(6)}/><circle cx="128" cy="140" r="90" fill="{c}" opacity="0.12"/>')


@glyph
def chisel(c="#9aa0aa"):
    return (f'<g transform="rotate(35 128 128)"><rect x="112" y="20" width="32" height="110" rx="6" fill="#5a3416" {S(7)}/>'
            f'<path d="M108 128 H148 L148 200 L128 236 L108 200 Z" fill="{c}" {S(8)}/></g><circle cx="60" cy="200" r="14" fill="#7ac0e0" opacity="0.8"/>')


# ----------------------------------------------------------------------------- icon list
RUNES = {"varn": "ᚹ", "dor": "ᛞ", "keth": "ᚲ", "orun": "ᛟ", "thar": "ᚦ", "drath": "ᛞ", "iskar": "ᛁ", "vael": "ᚢ",
         "grum": "ᚷ", "ruun": "ᚱ", "mor": "ᛗ", "khal": "ᚺ"}
RUNE_C = {"varn": "#7ac0e0", "dor": "#ff9a3a", "keth": "#c8ccd6", "orun": "#d8b0ff", "thar": "#ffd27a", "drath": "#ff5a1a",
          "iskar": "#a8e8ff", "vael": "#9adf5a", "grum": "#c8a070", "ruun": "#ffb35a", "mor": "#e05a6a", "khal": "#e8c35a"}

ICONS = {
    # evidence and story items
    **{f"ev-e{n}": ("ev", "#e8c35a", bg, str(n)) for n, bg in zip(range(1, 8), ("#1a3a4a", "#4a3a14", "#4a0c10", "#2a4a14", "#3a0a1a", "#1a2a4a", "#3a2a14"))},
    "it-register": ("scroll", "#efe2c0", "#3a2a1a"), "it-commission": ("seal", "#c09040", "#4a0c10"),
    "it-shield": ("rivetshield", "#5a5660", "#4a0c10"), "it-rivet": ("rivet", "#c8963a", "#26262e"),
    "it-manual": ("manual", "#3a2a1a", "#3a2a50"), "it-key": ("key", "#e8c35a", "#3a2a50"),
    "it-compact": ("compact", "#e8b496", "#2a4a14"), "it-filter": ("filter", "#c87a4a", "#3a5014"),
    "it-ration": ("ledger", "#5e2a14", "#3a5014"), "it-gauge": ("gauge", "#efe2c0", "#1a3a4a"),
    "it-badge": ("badge2", "#c8963a", "#4a0c10"), "it-chisel": ("chisel", "#9aa0aa", "#26262e"),
    "it-map": ("map", "#efe2c0", "#3a2a1a"), "it-orders": ("seal", "#1a1418", "#3a5014"),
    "it-lantern": ("lantern", "#ffb35a", "#3a2a1a"), "it-mushroom": ("mushroom", "#9adf5a", "#26262e"),
    **{f"mat-{k}": ("ore", c, "#26262e") for k, c in (("deep-silver", "#dfe6ef"), ("emberglass", "#ff7a1a"), ("oathstone", "#ffd27a"),
                                                       ("sky-iron", "#7ac0e0"), ("hearthstone", "#d8a050"), ("ironbone", "#c8ccd6"))},
    **{f"rune-{k}": ("runestone", RUNE_C[k], "#1a1a26", ch) for k, ch in RUNES.items()},
    # abilities
    "ab-multi": ("slashes", "#c0283a", "#26262e"), "ab-spear": ("spear", "#dfe6ef", "#3a3036"),
    "ab-hammer": ("hammer", "#9aa0aa", "#3a3036"), "ab-axe": ("axe", "#9aa0aa", "#3a5014"),
    "ab-cleaver": ("cleaver", "#9aa0aa", "#3a5014"), "ab-blade": ("sword", "#e9eef6", "#26262e"),
    "ab-bolt": ("crossbow", "#7a4a22", "#3a5014"), "ab-shield": ("rivetshield", "#5a5660", "#26262e"),
    "ab-rally": ("horn", "#e8dcc0", "#4a0c10"), "ab-press": ("arrows", "#ff9a3a", "#3a5014"),
    "ab-bomb": ("bomb", "#2a2630", "#3a5014"), "ab-roar": ("roar", "#ff7a1a", "#3a5014"),
    "ab-brace": ("shield", "#7e9a5a", "#26262e"), "ab-legendary": ("crown", "#e8c35a", "#4a0c10"),
    "ab-will": ("tusk", "#f4ecd0", "#4a0c10"), "ab-piston": ("piston", "#9aa0aa", "#3a2a50"),
    "ab-burst": ("steam", "#cfd6e0", "#3a2a50"), "ab-vent": ("flame", "#ff7a1a", "#3a0a0a"),
    "ab-command": ("banner", "#7a1a18", "#26262e"), "ab-parry": ("sword", "#e8c35a", "#26262e"),
    "ab-medic": ("sun", "#ffd27a", "#3a2a1a"), "ab-ledger": ("ledger", "#5e2a14", "#4a3a14"),
    "ab-tools": ("wrench", "#9aa0aa", "#26262e"), "ab-slip": ("invisible", "#9fd0e0", "#3a5014"),
    "ab-kitchen": ("kitchen", "#d8a050", "#4a3a14"), "ab-fist": ("fist", "#efe2c0", "#4a0c10"),
    "ab-tusk": ("tusk", "#f4ecd0", "#3a5014"), "ab-gauge": ("gauge", "#efe2c0", "#3a2a50"),
    "ab-construct": ("cog", "#b8862e", "#3a2a50"), "ab-pick": ("pick", "#9aa0aa", "#26262e"),
    "ab-lantern": ("lantern", "#7ad0ff", "#3a5014"), "ab-scroll": ("scroll", "#efe2c0", "#26262e"),
    "ab-chain": ("chain", "#9a96a2", "#26262e"), "ab-heal": ("heart", "#c0283a", "#3a2a1a"),
    # spells (school colours)
    "sp-chisel-sign": ("chisel", "#9aa0aa", "#2a1a3a"), "sp-returning-hammer": ("hammer", "#ff9a3a", "#3a2a1a"),
    "sp-stoneward-script": ("runestone", "#7ac0e0", "#1a2a4a", "ᚹ"), "sp-echoes-masonry": ("runestone", "#d8b0ff", "#10303a", "ᛟ"),
    "sp-oath-rune": ("runestone", "#ffd27a", "#1a2a4a", "ᚦ"), "sp-seal-breach": ("rivetshield", "#5a5660", "#1a2a4a"),
    "sp-hammerfall": ("hammer", "#ff5a1a", "#3a0a0a"), "sp-shared-burden": ("chain", "#ffd27a", "#1a2a4a"),
    "sp-forgeward-bastion": ("anvil", "#5a5660", "#1a2a4a"), "sp-runegate": ("runestone", "#9adf5a", "#2a1a3a", "ᚢ"),
    "sp-ancestral-aegis": ("shield", "#ffd27a", "#1a2a4a"), "sp-carved-name": ("runestone", "#e05a6a", "#10303a", "ᛗ"),
    # macros, tables, cards, scenes, playlists
    "mc-ledger": ("ledger", "#5e2a14", "#4a3a14"), "mc-evidence": ("ev", "#e8c35a", "#4a0c10", "?"),
    "mc-defence": ("shield", "#7ac0e0", "#1a2a4a"), "mc-accord": ("compact", "#e8b496", "#2a4a14"),
    "mc-hearing": ("scales", "#e8c35a", "#4a3a14"), "mc-forge": ("anvil", "#5a5660", "#3a0a0a"),
    "mc-baldrik": ("rivetshield", "#5a5660", "#4a0c10"), "mc-council": ("banner", "#2c3a4a", "#26262e"),
    "mc-challenge": ("dice", "#2c4f8a", "#10203a"), "mc-countdown": ("hourglass", "#ffd27a", "#3a2a50"),
    "mc-handout": ("scroll", "#efe2c0", "#3a2a1a"), "mc-music": ("note", "#ffd27a", "#26262e"),
    "mc-cards": ("cards", "#7a1a18", "#26262e"), "mc-setup": ("cog", "#c09040", "#26262e"),
    "mc-save": ("shield", "#2c4f8a", "#10203a"), "mc-session": ("map", "#efe2c0", "#4a3a14"),
    "mc-pressure": ("gauge", "#efe2c0", "#3a0a0a"), "mc-fronts": ("horn", "#e8dcc0", "#3a0a0a"),
    "tb-dice": ("dice", "#7a1a18", "#26262e"), "note-pin": ("fist", "#efe2c0", "#4a0c10"),
    "il-title": ("fist", "#efe2c0", "#4a0c10"),
}


def build():
    os.makedirs(OUT, exist_ok=True)
    for name, spec in ICONS.items():
        g, col, bgc = spec[0], spec[1], spec[2]
        fn = G[g]
        if len(spec) > 3:
            if g in ("letter", "runestone", "scroll"):
                inner = fn(col, spec[3])
            elif g == "ev":
                inner = fn(col, spec[3])
        else:
            inner = fn(col)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">{DEFS}'
               f'<radialGradient id="ib"><stop offset="0" stop-color="{bgc}"/><stop offset="1" stop-color="#0a0405"/></radialGradient>'
               f'<rect x="4" y="4" width="248" height="248" rx="26" fill="url(#ib)" stroke="#120909" stroke-width="8"/>'
               f'<rect x="12" y="12" width="232" height="232" rx="20" fill="none" stroke="#a86f32" stroke-width="3" opacity="0.8"/>'
               f'<g transform="translate(128,128) scale(0.8) translate(-128,-128)">{inner}</g></svg>')
        render(svg, f"{OUT}/{name}.webp", 256)
    print(len(ICONS), "icons")


def sheet(out="/home/claude/il/art/preview/icons.webp", cols=12):
    from PIL import Image
    keys = list(ICONS)
    sz = 96
    rows = math.ceil(len(keys) / cols)
    im = Image.new("RGB", (cols * sz, rows * sz), "#222")
    for i, k in enumerate(keys):
        t = Image.open(f"{OUT}/{k}.webp").convert("RGBA").resize((sz, sz))
        im.paste(t, ((i % cols) * sz, (i // cols) * sz), t)
    im.save(out, "WEBP", quality=85)


if __name__ == "__main__":
    build()
    sheet()
