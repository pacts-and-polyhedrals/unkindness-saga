"""Ironfist Legacy cast: grotesque-chibi gothic portraits (front) and true overhead tokens.

Same engine and treatment as the Hag Host / Red Clause art (chibi.py). New pieces here:
dwarven beards with bronze clasps, orc tusks, goblin ears, Ironfist heraldry, and the
held items this cast needs (shield, hammer, cleaver, ladle, wrench, ledger, lantern, spear).
"""
import math, os, sys
from chibi import *

F = dict
CAST = {}
OUT = "/home/claude/saga/il/module/assets"

# palettes ------------------------------------------------------------------
DWARF = F(skin="#d9a07e", skin_dk="#a86a4e", ears="round", nose="bulb", eye=0.9)
DWARF_DK = F(skin="#a8704e", skin_dk="#764632", ears="round", nose="bulb", eye=0.9)
ORC = F(skin="#7e9a5a", skin_dk="#4e6a34", ears="pointed", nose="bulb", iris="#e8c35a", eye=0.8)
ORC_GREY = F(skin="#8a9a8a", skin_dk="#566656", ears="pointed", nose="bulb", iris="#ff9a3a", eye=0.8)
GOBLIN = F(skin="#9ab84a", skin_dk="#5e7a24", ears="pointed", nose="hook", iris="#ffd27a", slit=True, eye=1.15)
IRONFIST_RED = "#7a1a18"
BRONZE = "#a86f32"
BG_FAMILY, BG_COUNCIL, BG_VANGUARD, BG_CINDER, BG_ENGINE, BG_COMMON = "#6a4a1a", "#4a3a20", "#6a0c12", "#3a5014", "#3a2a50", "#3a3a40"


def C(key, portrait, token, bgc):
    CAST[key] = (portrait, token, bgc)


# --------------------------------------------------------------------------- heraldry + items
def fist_emblem(x=500, y=820, s=1.0, c="#efe2c0"):
    """The Ironfist sigil: a white fist gripping an iron nail."""
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<rect x="-8" y="-95" width="16" height="190" fill="url(#iron)" {S(5)}/><path d="M-14 95 L0 130 L14 95 Z" fill="url(#iron)" {S(5)}/>'
            f'<path d="M-52 -40 h104 v62 q0 34 -40 34 h-24 q-40 0 -40 -34 Z" fill="{c}" {S(7)}/>'
            + "".join(f'<path d="M{-52+k*26} -40 v-22 q13 -12 26 0 v22" fill="{c}" {S(6)}/>' for k in range(4))
            + f'<path d="M-52 -8 q-26 -6 -24 22 q4 22 30 18" fill="{c}" {S(6)}/></g>')


def tusk_emblem(x=500, y=820, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><circle r="60" fill="#3a2a14" {S(7)}/>'
            f'<path d="M-30 30 Q-44 -20 -10 -50 Q-22 0 -6 30 Z M30 30 Q44 -20 10 -50 Q22 0 6 30 Z" fill="#efe2c0" {S(5)}/>'
            f'<circle r="14" fill="#ff7a1a" {S(4)}/></g>')


def tusks(head=1.0, hy=430, big=False):
    hh = 210 * head
    my = hy + hh * 0.66
    L = 70 if big else 52
    return "".join(f'<path d="M{500+s*70} {my+18} Q{500+s*92} {my-L*0.6} {500+s*80} {my-L} Q{500+s*62} {my-L*0.4} {500+s*48} {my+20} Z" fill="#f4ecd0" {S(7)}/>' for s in (-1, 1))


def beard_clasps(head=1.0, hy=430, n=2, c="url(#brass)"):
    hh = 210 * head
    y0 = hy + hh * 1.25
    return "".join(f'<rect x="{500+dx-26}" y="{y0+k*58}" width="52" height="34" rx="8" fill="{c}" {S(6)}/>' for k in range(n) for dx in (-70, 70))


def braid(x, y, length=260, c="#8a8a90"):
    return "".join(f'<ellipse cx="{x}" cy="{y+i*42}" rx="26" ry="28" fill="{c}" {S(6)}/>' for i in range(int(length / 42)))


def i_shield(two_rivets=False, c="#5a5660", x=270, y=780, rot=-8):
    rv = (f'<circle cx="-40" cy="-30" r="16" fill="#b88a3a" {S(5)}/><circle cx="34" cy="-36" r="12" fill="#8a8f99" {S(5)}/>'
          if two_rivets else "")
    return (f'<g transform="translate({x},{y}) rotate({rot})"><path d="M-150 -170 H150 V40 Q150 170 0 220 Q-150 170 -150 40 Z" fill="{c}" {S(12)}/>'
            f'<path d="M-120 -140 H120 V40 Q120 140 0 182 Q-120 140 -120 40 Z" fill="none" stroke="#b8862e" stroke-width="10"/>'
            f'<path d="M-150 -170 H150 V40 Q150 170 0 220 Z" fill="url(#hatch)" opacity="0.35"/>'
            f'{fist_emblem(0, 10, 0.9)}{rv}'
            f'<path d="M-100 60 l40 30 M90 -100 l-30 50" stroke="{INK}" stroke-width="6"/></g>')


def i_hammer(x=760, y=760, rot=18, head="url(#iron)"):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-16" y="-80" width="32" height="300" rx="10" fill="#5a3416" {S(8)}/>'
            f'<rect x="-90" y="-170" width="180" height="100" rx="14" fill="{head}" {S(10)}/><rect x="-90" y="-130" width="180" height="20" fill="url(#brass)" {S(5)}/></g>')


def i_cleaver(x=760, y=740, rot=20):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-16" y="40" width="32" height="200" rx="10" fill="#3a2414" {S(8)}/>'
            f'<path d="M-30 50 L-30 -240 Q60 -260 120 -200 L120 -20 Q60 30 -30 50 Z" fill="url(#iron)" {S(10)}/>'
            f'<path d="M110 -190 L110 -30" stroke="#c8ccd6" stroke-width="10"/><circle cx="20" cy="-180" r="16" fill="#120909"/>'
            f'<path d="M0 -120 l60 20 M10 -60 l50 10" stroke="#7a1a18" stroke-width="8"/></g>')


def i_axe(x=760, y=760, rot=16):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-15" y="-160" width="30" height="380" rx="10" fill="#4a2c14" {S(8)}/>'
            f'<path d="M15 -150 Q160 -190 170 -60 Q120 -90 15 -60 Z" fill="url(#iron)" {S(9)}/>'
            f'<path d="M-15 -150 Q-120 -170 -130 -80 Q-90 -100 -15 -70 Z" fill="url(#iron)" {S(8)}/></g>')


def i_ladle(x=740, y=760, rot=20):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-12" y="-220" width="24" height="320" rx="10" fill="#8a6a3a" {S(7)}/>'
            f'<ellipse cx="0" cy="110" rx="70" ry="52" fill="url(#iron)" {S(9)}/><ellipse cx="0" cy="100" rx="48" ry="26" fill="#d8a050" {S(5)}/></g>')


def i_wrench(x=760, y=760, rot=24, c="url(#iron)"):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-20" y="-150" width="40" height="320" rx="14" fill="{c}" {S(8)}/>'
            f'<path d="M-70 -150 Q-80 -250 0 -260 Q80 -250 70 -150 L30 -150 L30 -210 L-30 -210 L-30 -150 Z" fill="{c}" {S(9)}/></g>')


def i_ledger(x=720, y=780, rot=12):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-120" y="-150" width="240" height="300" rx="10" fill="#5e2a14" {S(10)}/>'
            f'<rect x="-100" y="-130" width="200" height="260" fill="#efe2c0" {S(6)}/>'
            + "".join(f'<line x1="-80" y1="{-100+k*34}" x2="80" y2="{-100+k*34}" stroke="#7a5a3a" stroke-width="5"/>' for k in range(7))
            + f'<rect x="-120" y="-150" width="40" height="300" fill="url(#brass)" {S(6)}/></g>')


def i_lantern(x=740, y=760, c="#ffb35a"):
    return (f'<g transform="translate({x},{y})"><circle r="120" fill="{c}" filter="url(#glw2)" opacity="0.6"/>'
            f'<rect x="-60" y="-80" width="120" height="160" rx="16" fill="{c}" {S(9)}/><rect x="-70" y="-100" width="140" height="30" fill="url(#iron)" {S(7)}/>'
            f'<rect x="-70" y="72" width="140" height="30" fill="url(#iron)" {S(7)}/><path d="M-30 -100 Q0 -170 30 -100" fill="none" {S(9)}/></g>')


def i_spear(x=780, y=560, c="#dfe6ef"):
    return (f'<g transform="translate({x},{y})"><rect x="-12" y="-120" width="24" height="560" fill="#5a3416" {S(7)}/>'
            f'<path d="M0 -300 L40 -120 L-40 -120 Z" fill="{c}" {S(8)}/><rect x="-46" y="-130" width="92" height="22" fill="url(#brass)" {S(5)}/></g>')


def i_bomb(x=740, y=790):
    return (f'<g transform="translate({x},{y})"><circle r="96" fill="#2a2630" {S(10)}/><circle cx="-30" cy="-30" r="22" fill="#fff" opacity="0.25"/>'
            f'<rect x="-24" y="-130" width="48" height="40" fill="url(#brass)" {S(6)}/><path d="M0 -130 q30 -60 70 -50" fill="none" stroke="#3a2a14" stroke-width="10"/>'
            f'<circle cx="70" cy="-180" r="30" fill="#ffd27a" filter="url(#glw)"/><circle cx="70" cy="-180" r="14" fill="#fff4c0"/></g>')


def i_quill_scroll(x=730, y=790):
    return (f'<g transform="translate({x},{y}) rotate(-8)"><rect x="-130" y="-90" width="260" height="180" rx="16" fill="#efe2c0" {S(9)}/>'
            + "".join(f'<line x1="-100" y1="{-55+k*30}" x2="100" y2="{-55+k*30}" stroke="#7a5a3a" stroke-width="5"/>' for k in range(4))
            + f'<circle cx="80" cy="60" r="28" fill="#8e1424" {S(6)}/><path d="M-60 -60 Q20 -250 140 -300 Q60 -180 -40 -50 Z" fill="#f4f0e6" {S(7)}/></g>')


def i_censer(x=740, y=760):
    return (f'<g transform="translate({x},{y})"><path d="M0 -260 V-80" stroke="{INK}" stroke-width="8"/><circle cy="-30" r="70" fill="url(#brass)" {S(9)}/>'
            f'<circle cy="-30" r="100" fill="#ffd27a" filter="url(#glw2)" opacity="0.35"/><path d="M-30 -110 q-20 -60 10 -100 M20 -110 q30 -50 0 -90" stroke="#cfc8d8" stroke-width="10" fill="none" opacity="0.7"/></g>')


def i_pick(x=760, y=760, rot=18):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-14" y="-140" width="28" height="360" rx="10" fill="#5a3416" {S(8)}/>'
            f'<path d="M-170 -120 Q0 -200 170 -120 Q0 -165 -170 -120 Z" fill="url(#iron)" {S(9)}/></g>')


def goggles(head=1.0, c="#7ad0ff", hy=430, up=True):
    hh, hw = 210 * head, 225 * head
    gy = hy - hh * (0.75 if up else 0.05)
    return (f'<path d="M{500-hw*1.0} {gy} Q500 {gy-30} {500+hw*1.0} {gy}" stroke="#3a2a14" stroke-width="26" fill="none"/>'
            + "".join(f'<circle cx="{500+s*hw*0.42}" cy="{gy}" r="{62*head}" fill="{c}" fill-opacity="0.75" stroke="{INK}" stroke-width="12"/><circle cx="{500+s*hw*0.42}" cy="{gy}" r="{62*head}" fill="none" stroke="url(#brass)" stroke-width="8"/><circle cx="{500+s*hw*0.42-18}" cy="{gy-16}" r="12" fill="#fff" opacity="0.8"/>' for s in (-1, 1)))


def soot(head=1.0, hy=430):
    hh, hw = 210 * head, 225 * head
    return (f'<ellipse cx="{500-hw*0.5}" cy="{hy+hh*0.45}" rx="60" ry="26" fill="#2a2420" opacity="0.45"/>'
            f'<ellipse cx="{500+hw*0.3}" cy="{hy-hh*0.55}" rx="44" ry="18" fill="#2a2420" opacity="0.4"/>')


def sash(c="#a86f32"):
    return (f'<path d="M290 690 L720 1000 L640 1000 L230 730 Z" fill="{INK}"/><path d="M300 700 L700 1000 L650 1000 L250 730 Z" fill="{c}"/>'
            f'<circle cx="470" cy="830" r="30" fill="url(#brass)" {S(6)}/>')


def pauldrons(c="url(#iron)", bw=300):
    return "".join(f'<path d="M{500+s*bw*0.35} 690 Q{500+s*bw*1.15} 640 {500+s*bw*1.05} 820 Q{500+s*bw*0.7} 760 {500+s*bw*0.35} 760 Z" fill="{c}" {S(11)}/>'
                   f'<path d="M{500+s*bw*0.5} 700 Q{500+s*bw*1.0} 680 {500+s*bw*0.98} 780" stroke="#c8ccd6" stroke-width="7" fill="none" opacity="0.6"/>' for s in (-1, 1))


def kerchief(head=1.0, hy=430, c="#8a3a2a"):
    hh, hw = 210 * head, 225 * head
    return (f'<path d="M{500-hw*1.05} {hy-hh*0.2} C{500-hw*1.0} {hy-hh*1.35} {500+hw*1.0} {hy-hh*1.35} {500+hw*1.05} {hy-hh*0.2} Q500 {hy-hh*0.7} {500-hw*1.05} {hy-hh*0.2} Z" fill="{c}" {S(11)}/>'
            + "".join(f'<circle cx="{500+dx}" cy="{hy-hh*0.85+dy}" r="10" fill="#efe2c0" opacity="0.8"/>' for dx, dy in ((-120, 10), (-40, -40), (60, -30), (140, 20), (0, 30))))


def crest_helm(head=1.0, hy=430, c="url(#iron)", crest="#7a1a18"):
    hh, hw = 210 * head, 225 * head
    return (f'<path d="M{500-hw*1.1} {hy-hh*0.05} C{500-hw*1.15} {hy-hh*1.45} {500+hw*1.15} {hy-hh*1.45} {500+hw*1.1} {hy-hh*0.05} L{500+hw*0.9} {hy-hh*0.35} L{500-hw*0.9} {hy-hh*0.35} Z" fill="{c}" {S(12)}/>'
            f'<path d="M{500-hw*0.95} {hy-hh*0.42} H{500+hw*0.95}" stroke="url(#brass)" stroke-width="22"/>'
            f'<path d="M500 {hy-hh*1.25} Q{500-hw*0.2} {hy-hh*1.9} {500+hw*0.9} {hy-hh*1.75} Q{500+hw*0.5} {hy-hh*1.45} {500+hw*0.15} {hy-hh*1.2} Z" fill="{crest}" {S(9)}/>'
            f'<rect x="488" y="{hy-hh*1.1}" width="24" height="{hh*0.7}" fill="url(#brass)" {S(5)}/>')


def mech_overlay():
    return ""


# ===========================================================================
#  THE IRONFIST FAMILY
# ===========================================================================
C("baldrik",
  F(**DWARF, coat="#3a2426", coat_dk="#1a0c0c", armor="#5a5660", beard="full", beard_c="#8a8a90", mouth_in_beard=True,
    mouth="none", brow="angry", brow_c="#5a5a60", scar=True, iris="#6a8aaa", body_w=330, head=1.02, hat="helm",
    hat_c="#4a4650", seed=21, emblem=fist_emblem(500, 860, 0.8),
    item=i_shield(True, x=250, y=800) + i_hammer(780, 760),
    over=pauldrons(bw=330) + beard_clasps(1.02, n=2) + braid(400, 760, 170, "#8a8a90") + braid(600, 760, 170, "#8a8a90")),
  F(shoulders=330, coat="#3a2426", trim=BRONZE, cap="helm", cap_c="#5a5660", head=165, beard=True, beard_c="#8a8a90",
    hand="#d9a07e", skin="#d9a07e", item=ot_item("maul", 1),
    over=f'<g transform="translate(220,600) scale(0.55)">{i_shield(True, x=0, y=0, rot=0)}</g>'), BG_VANGUARD)

C("heddra",
  F(**DWARF, coat="#6a4a2a", trim="#c8b48a", belt="#3a2414", hair="#c8c8c8", hair_style="bun", brow="kind",
    mouth="smile", blush=True, head=1.05, body_w=320, warts=[(0.45, 0.35)], seed=22,
    item=i_ladle(760, 760), over=kerchief(1.05, c="#8a3a2a")),
  F(shoulders=310, coat="#6a4a2a", trim="#c8b48a", cap="hair", cap_c="#c8c8c8", bun=True, head=150, hand="#d9a07e",
    skin="#d9a07e", item=ot_item("basket", 1)), BG_FAMILY)

C("runa",
  F(**DWARF, coat="#3a3a40", hair="#8a3a1a", hair_style="messy", brow="worried", mouth="frown", head=1.0, body_w=280,
    seed=23, gloves="#3a2a1a", item=i_wrench(770, 760),
    over=goggles(1.0) + soot(1.0) + sash("#a86f32") + braid(330, 520, 300, "#8a3a1a")),
  F(shoulders=270, coat="#3a3a40", trim="#a86f32", cap="hair", cap_c="#8a3a1a", head=145, hand="#3a2a1a",
    skin="#d9a07e", over='<circle cx="460" cy="430" r="40" fill="#7ad0ff" stroke="#120909" stroke-width="10"/><circle cx="540" cy="430" r="40" fill="#7ad0ff" stroke="#120909" stroke-width="10"/>'),
  BG_FAMILY)

# ===========================================================================
#  THE IRONFIST AUTHORITIES
# ===========================================================================
C("hadrik",
  F(**DWARF, coat="#1a1418", trim="#c8a050", armor="#2f2c34", beard="huge", beard_c="#2a2420", mouth_in_beard=True,
    mouth="none", brow="angry", iris="#8a6a3a", body_w=350, head=1.0, seed=24, emblem=fist_emblem(500, 870, 0.75),
    item=f'<g transform="translate(770,700) rotate(14)"><rect x="-14" y="-260" width="28" height="420" fill="#d8dee8" {S(7)}/><rect x="-70" y="150" width="140" height="26" rx="8" fill="url(#brass)" {S(6)}/><rect x="-16" y="170" width="32" height="90" fill="#3a1414" {S(6)}/></g>',
    over=crest_helm(1.0, c="url(#iron)", crest="#c8a050") + pauldrons("url(#brass)", 350) + beard_clasps(1.0, n=3)),
  F(shoulders=350, coat="#1a1418", trim="#c8a050", cap="helm", cap_c="#2f2c34", head=165, beard=True, beard_c="#2a2420",
    hand="#d9a07e", skin="#d9a07e", cape="#5a0c10", item=ot_item("sword", 1)), BG_COUNCIL)

C("brynja",
  F(**DWARF_DK, coat="#2c3a4a", armor="#4a5260", hair="#e8d8a0", hair_style="long", brow="angry", mouth="frown",
    scar=True, body_w=330, head=1.0, seed=25, emblem=fist_emblem(500, 870, 0.75), hat="helm", hat_c="#4a5260",
    item=i_shield(False, c="#2c3a4a", x=250, y=800) + i_spear(800, 560),
    over=pauldrons(bw=330) + braid(330, 560, 280, "#e8d8a0") + braid(670, 560, 280, "#e8d8a0")),
  F(shoulders=320, coat="#2c3a4a", trim="#c8ccd6", cap="helm", cap_c="#4a5260", head=155, hand="#a8704e",
    skin="#a8704e", item=ot_item("spear", 1)), BG_COUNCIL)

C("odran",
  F(**DWARF, coat="#5a4214", trim="#e8c35a", beard="short", beard_c="#c8a070", mouth="smile", spectacles=True,
    brow="kind", body_w=360, head=1.05, hat="tophat", seed=26, item=i_ledger(740, 780),
    warts=[(-0.5, 0.2)], over=beard_clasps(1.05, n=1)),
  F(shoulders=360, coat="#5a4214", trim="#e8c35a", cap="tophat", head=160, beard=True, beard_c="#c8a070",
    hand="#d9a07e", skin="#d9a07e", item=ot_item("clipboard", 1)), BG_COUNCIL)

C("dagnner",
  F(**DWARF_DK, coat="#3a1414", armor="#3a3640", hair="#2a1a14", hair_style="fringe", brow="angry", mouth="frown",
    scar=True, body_w=310, seed=27, emblem=fist_emblem(500, 870, 0.7), item=i_quill_scroll(760, 800),
    warts=[(0.55, -0.1)], over=pauldrons("url(#iron)", 310) + braid(310, 520, 250, "#2a1a14")),
  F(shoulders=300, coat="#3a1414", trim="#7a1a18", cap="hair", cap_c="#2a1a14", head=150, hand="#a8704e",
    skin="#a8704e", item=ot_item("clipboard", 1)), BG_VANGUARD)

C("edda",
  F(**DWARF, coat="#4a3a2a", armor="#5a5660", hair="#a85a2a", hair_style="long", brow="worried", mouth="smile",
    body_w=300, seed=28, hat="cap", hat_c="#5a5660", badge=True, item=i_spear(790, 560), emblem=fist_emblem(500, 870, 0.7)),
  F(shoulders=290, coat="#4a3a2a", trim=BRONZE, cap="helm", cap_c="#5a5660", head=150, hand="#d9a07e",
    skin="#d9a07e", item=ot_item("spear", 1)), BG_COUNCIL)

C("yrsa",
  F(**DWARF_DK, coat="#efe2c0", trim="#a86f32", hat="veil", hat_c="#5a4a6a", sun=True, brow="kind", mouth="smile",
    body_w=290, seed=29, item=i_censer(760, 760), warts=[(-0.4, 0.4), (0.5, 0.1)]),
  F(shoulders=280, coat="#efe2c0", trim="#a86f32", cap="veil", cap_c="#5a4a6a", head=150, hand="#a8704e",
    skin="#a8704e", item=ot_item("lantern", 1)), BG_COMMON)

C("tovik",
  F(**DWARF, coat="#5a4a3a", beard="full", beard_c="#6a3a1a", mouth_in_beard=True, mouth="none", brow="worried",
    hat="cap", hat_c="#8a6a2a", body_w=320, seed=30, item=i_pick(780, 760), over=soot(1.0)),
  F(shoulders=310, coat="#5a4a3a", cap="cap", cap_c="#8a6a2a", head=150, beard=True, beard_c="#6a3a1a",
    hand="#d9a07e", skin="#d9a07e", item=ot_item("maul", 1)), BG_COMMON)

C("venn",
  F(**DWARF, coat="#2a2a3a", trim="#8a8f99", beard="short", beard_c="#9a9a9a", spectacles=True, mouth="o",
    brow="worried", head=1.1, body_w=250, seed=31, item=i_quill_scroll(740, 800), hair="#9a9a9a", hair_style="fringe"),
  F(shoulders=240, coat="#2a2a3a", trim="#8a8f99", cap="hair", cap_c="#9a9a9a", head=150, beard=True,
    beard_c="#9a9a9a", hand="#d9a07e", skin="#d9a07e", item=ot_item("clipboard", 1)), BG_COUNCIL)

# ===========================================================================
#  THE CINDER-TUSK CLAN
# ===========================================================================
C("korga",
  F(**ORC, coat="#3a2414", armor="#4a3a2a", hair="#1a1414", hair_style="messy", brow="angry", mouth="frown",
    scar=True, body_w=380, head=1.0, seed=32, eye_glow="#ff7a1a", warts=[(0.6, -0.3), (-0.55, 0.45)],
    emblem=tusk_emblem(500, 860, 0.9), item=i_cleaver(790, 740),
    over=tusks(1.0, big=True) + pauldrons("#5a3a1a", 380)
    + '<path d="M300 700 L360 640 L380 720 Z M700 700 L640 640 L620 720 Z" fill="#efe2c0" stroke="#120909" stroke-width="7"/>'),
  F(shoulders=380, coat="#3a2414", trim="#ff7a1a", cap="hair", cap_c="#1a1414", head=170, hand="#7e9a5a",
    skin="#7e9a5a", skin_dk="#4e6a34", ears="pointed", item=ot_item("maul", 1),
    over='<path d="M430 640 q-20 40 -6 70 M570 640 q20 40 6 70" stroke="#f4ecd0" stroke-width="22" stroke-linecap="round" fill="none"/>'),
  BG_CINDER)

C("urzha",
  F(**ORC_GREY, coat="#5a3a5a", trim="#e8c35a", hood="#3a2a3a", brow="kind", mouth="frown", body_w=300, seed=33,
    warts=[(-0.5, -0.3)], item=i_lantern(760, 780, "#7ad0ff"),
    over=tusks(1.0) + '<path d="M260 700 Q500 820 740 700 L760 760 Q500 880 240 760 Z" fill="#8a5a2a" stroke="#120909" stroke-width="8"/>'),
  F(shoulders=290, coat="#5a3a5a", trim="#e8c35a", cap="hood", cap_c="#3a2a3a", head=150, hand="#8a9a8a",
    skin="#8a9a8a", item=ot_item("lantern", 1)), BG_CINDER)

C("skrik",
  F(**GOBLIN, coat="#4a3a24", trim="#a86f32", mouth="grin", brow="worried", head=1.15, body_w=230, seed=34,
    gloves="#3a2a1a", item=i_wrench(770, 760, c="url(#brass)"), over=goggles(1.15, "#ffd27a") + soot(1.15),
    warts=[(0.5, 0.3), (-0.3, -0.4)]),
  F(shoulders=210, coat="#4a3a24", trim="#a86f32", cap="hair", cap_c="#3a2a14", head=150, ears="pointed",
    hand="#3a2a1a", skin="#9ab84a", item=ot_item("clipboard", 1),
    over='<circle cx="460" cy="430" r="36" fill="#ffd27a" stroke="#120909" stroke-width="10"/><circle cx="540" cy="430" r="36" fill="#ffd27a" stroke="#120909" stroke-width="10"/>'),
  BG_CINDER)

C("brakk",
  F(**ORC, coat="#2a2a2a", armor="#3a3640", hat="bandana", hat_c="#7a1a18", brow="angry", mouth="frown", body_w=350,
    seed=35, warts=[(0.5, 0.2)], scar=True, emblem=tusk_emblem(500, 860, 0.75), item=i_axe(780, 760),
    over=tusks(1.0) + pauldrons("url(#iron)", 350)),
  F(shoulders=350, coat="#2a2a2a", trim="#7a1a18", cap="cap", cap_c="#7a1a18", head=160, hand="#7e9a5a",
    skin="#7e9a5a", ears="pointed", item=ot_item("sword", 1)), BG_CINDER)

C("ketta",
  F(**GOBLIN, coat="#3a4a2a", hair="#c84a1a", hair_style="messy", mouth="grin", brow="angry", head=1.15, body_w=220,
    seed=36, item=i_bomb(750, 790), over=soot(1.15) + goggles(1.15, "#ff9a3a")),
  F(shoulders=200, coat="#3a4a2a", trim="#c84a1a", cap="hair", cap_c="#c84a1a", head=145, ears="pointed",
    hand="#9ab84a", skin="#9ab84a",
    item='<g transform="translate(790,640)"><circle r="70" fill="#2a2630" stroke="#120909" stroke-width="9"/><circle cx="40" cy="-60" r="26" fill="#ffd27a"/></g>'),
  BG_CINDER)

# ===========================================================================
#  OPPOSITION AND EXTRAS
# ===========================================================================
C("ironfist-trooper",
  F(**DWARF, coat="#3a3036", armor="#5a5660", beard="full", beard_c="#5a3a1a", mouth_in_beard=True, mouth="none",
    hat="helm", hat_c="#5a5660", brow="angry", body_w=300, seed=37, emblem=fist_emblem(500, 870, 0.7),
    item=i_spear(800, 560) + i_shield(False, x=250, y=820)),
  F(shoulders=300, coat="#3a3036", trim=BRONZE, cap="helm", cap_c="#5a5660", head=150, beard=True,
    beard_c="#5a3a1a", hand="#d9a07e", skin="#d9a07e", item=ot_item("spear", 1)), BG_COUNCIL)

C("shield-warden",
  F(**DWARF_DK, coat="#2a2a30", armor="#6a6670", beard="huge", beard_c="#3a2a1a", mouth_in_beard=True, mouth="none",
    brow="angry", body_w=360, seed=38, emblem=fist_emblem(500, 870, 0.7),
    item=i_shield(False, c="#3a3a44", x=270, y=780, rot=0) + i_hammer(790, 760),
    over=crest_helm(1.0, c="url(#iron)", crest="#5a5660") + pauldrons(bw=360)),
  F(shoulders=360, coat="#2a2a30", trim="#c8ccd6", cap="helm", cap_c="#6a6670", head=160, beard=True,
    beard_c="#3a2a1a", hand="#a8704e", skin="#a8704e", item=ot_item("maul", 1),
    over='<path d="M150 380 H350 V560 Q350 660 250 690 Q150 660 150 560 Z" fill="#3a3a44" stroke="#120909" stroke-width="14"/>'),
  BG_COUNCIL)

C("vanguard-officer",
  F(**DWARF, coat="#4a0c10", armor="#2f2c34", beard="full", beard_c="#1a1414", mouth_in_beard=True, mouth="none",
    brow="angry", body_w=320, seed=39, emblem=fist_emblem(500, 870, 0.7, "#e8c35a"), item=i_hammer(780, 760),
    over=crest_helm(1.0, c="url(#iron)", crest="#7a1a18") + pauldrons(bw=320)),
  F(shoulders=320, coat="#4a0c10", trim="#e8c35a", cap="helm", cap_c="#2f2c34", head=155, beard=True,
    beard_c="#1a1414", hand="#d9a07e", skin="#d9a07e", cape="#2a0608", item=ot_item("maul", 1)), BG_VANGUARD)

C("shock-trooper",
  F(**ORC, coat="#3a2a1a", armor="#4a3a30", brow="angry", mouth="frown", body_w=360, seed=40, hat="helm",
    hat_c="#3a3640", warts=[(-0.5, 0.3)], emblem=tusk_emblem(500, 860, 0.75), item=i_axe(780, 760),
    over=tusks(1.0, big=True) + pauldrons("#5a3a1a", 360)),
  F(shoulders=360, coat="#3a2a1a", trim="#ff7a1a", cap="helm", cap_c="#3a3640", head=160, hand="#7e9a5a",
    skin="#7e9a5a", ears="pointed", item=ot_item("maul", 1)), BG_CINDER)

C("goblin-sapper",
  F(**GOBLIN, coat="#2a3a2a", hat="bandana", hat_c="#5a3a14", mouth="grin", brow="angry", head=1.1, body_w=210,
    seed=41, item=i_bomb(760, 800), over=goggles(1.1, "#9adf5a")),
  F(shoulders=190, coat="#2a3a2a", trim="#a86f32", cap="cap", cap_c="#5a3a14", head=140, ears="pointed",
    hand="#9ab84a", skin="#9ab84a",
    item='<g transform="translate(780,650)"><circle r="60" fill="#2a2630" stroke="#120909" stroke-width="9"/></g>'), BG_CINDER)

C("lowhearth-worker",
  F(**DWARF, coat="#5a5040", beard="short", beard_c="#8a5a2a", mouth="smile", brow="worried", hat="cap",
    hat_c="#4a4a3a", body_w=290, seed=42, item=i_pick(770, 780), over=soot(1.0)),
  F(shoulders=280, coat="#5a5040", cap="cap", cap_c="#4a4a3a", head=145, beard=True, beard_c="#8a5a2a",
    hand="#d9a07e", skin="#d9a07e", item=ot_item("maul", 1)), BG_COMMON)

C("cinder-civilian",
  F(**ORC_GREY, coat="#6a4a3a", hood="#4a3a2a", mouth="smile", brow="worried", body_w=280, seed=43,
    item=i_lantern(750, 790, "#9adf5a"), over=tusks(1.0)),
  F(shoulders=270, coat="#6a4a3a", cap="hood", cap_c="#4a3a2a", head=145, hand="#8a9a8a", skin="#8a9a8a",
    item=ot_item("basket", 1)), BG_CINDER)

C("ironfist-courier",
  F(**DWARF, coat="#5a2a14", trim="#e8c35a", hair="#3a2414", hair_style="messy", mouth="o", brow="worried",
    tears=False, body_w=260, seed=44, item=i_quill_scroll(750, 800),
    over='<path d="M400 640 l-40 120 M600 640 l40 120" stroke="#7a1a18" stroke-width="10"/>'),
  F(shoulders=250, coat="#5a2a14", trim="#e8c35a", cap="hair", cap_c="#3a2414", head=145, hand="#d9a07e",
    skin="#d9a07e", item=ot_item("clipboard", 1)), BG_COMMON)


# ---------------------------------------------------------------------------- machines
def bastion_engine_p():
    s = [f'<path d="M140 1000 L180 600 Q500 460 820 600 L860 1000 Z" fill="url(#iron)" {S(14)}/>',
         f'<path d="M180 600 Q500 460 820 600" stroke="url(#brass)" stroke-width="26" fill="none"/>']
    for x in (230, 770):
        s.append(f'<g transform="translate({x},640)"><rect x="-70" y="-30" width="140" height="300" rx="20" fill="#3a3640" {S(10)}/>'
                 f'<rect x="-50" y="240" width="100" height="120" rx="10" fill="url(#brass)" {S(9)}/></g>')
    s.append(f'<circle cx="500" cy="420" r="230" fill="url(#iron)" {S(14)}/>')
    s.append(f'<circle cx="500" cy="420" r="170" fill="#efe2c0" {S(9)}/>')
    for k in range(12):
        a = -math.pi * 0.85 + k * math.pi * 0.7 / 11
        s.append(f'<line x1="{500+math.cos(a)*130:.0f}" y1="{420+math.sin(a)*130:.0f}" x2="{500+math.cos(a)*160:.0f}" y2="{420+math.sin(a)*160:.0f}" stroke="{INK}" stroke-width="{10 if k%3==0 else 5}"/>')
    s.append(f'<path d="M{500+math.cos(-0.3)*140:.0f} {420+math.sin(-0.3)*140:.0f} A140 140 0 0 1 {500+math.cos(0.2)*140:.0f} {420+math.sin(0.2)*140:.0f}" stroke="#c0283a" stroke-width="22" fill="none"/>')
    s.append(f'<path d="M500 420 L620 360" stroke="{INK}" stroke-width="18" stroke-linecap="round"/><circle cx="500" cy="420" r="26" fill="url(#brass)" {S(7)}/>')
    s.append(f'<circle cx="500" cy="420" r="260" fill="#ff7a1a" filter="url(#glw2)" opacity="0.25"/>')
    for x in (300, 700):
        s.append(f'<path d="M{x} 200 q-30 -80 20 -150 q40 60 -20 150" fill="#cfd6e0" opacity="0.6"/>')
    s.append(f'<rect x="380" y="760" width="240" height="120" rx="16" fill="#2a2630" {S(9)}/>'
             + "".join(f'<rect x="{400+k*56}" y="780" width="36" height="80" rx="6" fill="#ff7a1a" opacity="0.85" {S(4)}/>' for k in range(4)))
    s.append(fist_emblem(500, 945, 0.45))
    return "".join(s)


def ram_p():
    s = [f'<path d="M80 900 L160 520 L840 520 L920 900 Z" fill="#5a3a1a" {S(14)}/>',
         f'<path d="M160 520 L500 300 L840 520 Z" fill="#7a1a18" {S(12)}/>']
    for k in range(5):
        s.append(f'<path d="M{200+k*150} 520 L{180+k*160} 900" stroke="{INK}" stroke-width="6" opacity="0.5"/>')
    s.append(f'<rect x="300" y="600" width="400" height="120" rx="40" fill="#4a3a2a" {S(12)}/>'
             f'<path d="M700 580 L860 560 Q900 660 860 760 L700 740 Z" fill="url(#iron)" {S(12)}/>'
             f'<path d="M860 600 q30 60 0 120" stroke="#c8ccd6" stroke-width="8" fill="none"/>')
    for x in (230, 770):
        s.append(f'<circle cx="{x}" cy="900" r="90" fill="#3a2414" {S(12)}/><circle cx="{x}" cy="900" r="30" fill="url(#iron)" {S(7)}/>')
    s.append(tusk_emblem(500, 420, 0.8))
    return "".join(s)


def bastion_token():
    return (f'<circle cx="500" cy="520" r="440" fill="#000" opacity="0.35" filter="url(#glw)"/>'
            f'<rect x="120" y="120" width="760" height="760" rx="90" fill="url(#iron)" {S(16)}/>'
            + "".join(f'<rect x="{x-70}" y="{y-70}" width="140" height="140" rx="20" fill="#3a3640" {S(10)}/><circle cx="{x}" cy="{y}" r="44" fill="url(#brass)" {S(8)}/>' for x, y in ((210, 210), (790, 210), (210, 790), (790, 790)))
            + f'<circle cx="500" cy="500" r="230" fill="#efe2c0" {S(12)}/><circle cx="500" cy="500" r="250" fill="#ff7a1a" filter="url(#glw2)" opacity="0.3"/>'
            + f'<path d="M500 500 L640 420" stroke="{INK}" stroke-width="22" stroke-linecap="round"/><circle cx="500" cy="500" r="34" fill="url(#brass)" {S(8)}/>'
            + f'<path d="M500 280 A220 220 0 0 1 700 420" stroke="#c0283a" stroke-width="30" fill="none"/>')


def ram_token():
    return (f'<ellipse cx="500" cy="520" rx="440" ry="300" fill="#000" opacity="0.35" filter="url(#glw)"/>'
            f'<rect x="140" y="260" width="720" height="480" rx="40" fill="#5a3a1a" {S(16)}/>'
            f'<path d="M140 500 L860 500" stroke="#3a2414" stroke-width="20"/>'
            + "".join(f'<line x1="{140+k*120}" y1="260" x2="{140+k*120}" y2="740" stroke="{INK}" stroke-width="6" opacity="0.5"/>' for k in range(7))
            + f'<path d="M860 380 L980 420 L980 580 L860 620 Z" fill="url(#iron)" {S(14)}/>'
            + "".join(f'<rect x="{x-50}" y="{y-30}" width="100" height="60" rx="14" fill="#2a1a10" {S(8)}/>' for x, y in ((240, 230), (760, 230), (240, 770), (760, 770)))
            + tusk_emblem(500, 500, 1.2))


def vent_token():
    return (f'<circle cx="500" cy="500" r="420" fill="#ff7a1a" filter="url(#glw2)" opacity="0.4"/>'
            f'<circle cx="500" cy="500" r="330" fill="url(#iron)" {S(14)}/>'
            + "".join(f'<rect x="200" y="{300+k*90}" width="600" height="40" rx="12" fill="#1a1416" {S(6)}/>' for k in range(5))
            + f'<circle cx="500" cy="500" r="360" fill="none" stroke="#ffb35a" stroke-width="14" stroke-dasharray="40 30"/>')


C("bastion-engine", bastion_engine_p(), "special:bastion", BG_ENGINE)
C("battering-engine", ram_p(), "special:ram", BG_CINDER)
C("pressure-vent", f'<g transform="translate(0,0)">{vent_token()}</g>', "special:vent", BG_ENGINE)

# =========================================================================== the Hold (venue keepers & side-quest cast)
BG_HOLD = "#4a2a1a"
C("grimma",
  F(**DWARF, coat="#6a3a1a", trim="#c8b48a", belt="#3a2414", hair="#a83a1a", hair_style="bun", brow="kind", mouth="grin",
    blush=True, head=1.05, body_w=340, seed=61, item=f'<g transform="translate(760,760) rotate(10)">{i_tankard()}</g>' if False else i_lantern(750, 770, "#ffd27a"),
    over=kerchief(1.05, c="#3a5a2a") + braid(340, 560, 210, "#a83a1a")),
  F(shoulders=330, coat="#6a3a1a", trim="#c8b48a", cap="hair", cap_c="#a83a1a", bun=True, head=150, hand="#d9a07e",
    skin="#d9a07e", item=ot_item("basket", 1)), BG_HOLD)
C("old-dagny",
  F(**DWARF_DK, coat="#3a3a5a", trim="#c8b48a", hair="#e8e8e8", hair_style="long", brow="kind", mouth="o", head=1.0,
    body_w=290, seed=62, warts=[(0.4, 0.3), (-0.5, 0.0)], item=i_lantern(760, 760), over=braid(330, 560, 260, "#e8e8e8")),
  F(shoulders=280, coat="#3a3a5a", trim="#c8b48a", cap="hair", cap_c="#e8e8e8", head=148, hand="#a8704e",
    skin="#a8704e", item=ot_item("lute", 1)), BG_COMMON)
C("sorvald",
  F(**DWARF, coat="#5a1418", trim="#e8c35a", beard="full", beard_c="#e8c070", mouth_in_beard=True, mouth="none",
    brow="kind", body_w=360, head=1.05, seed=63, spectacles=False, item=i_ledger(740, 780),
    over=beard_clasps(1.05, n=3, c="url(#brass)") + sash("#e8c35a")),
  F(shoulders=360, coat="#5a1418", trim="#e8c35a", cap="hair", cap_c="#e8c070", head=160, beard=True, beard_c="#e8c070",
    hand="#d9a07e", skin="#d9a07e", item=ot_item("clipboard", 1)), BG_COUNCIL)
C("eirik",
  F(**DWARF, coat="#2a2a3a", armor="#5a5660", beard="short", beard_c="#d8b060", brow="angry", mouth="grin", body_w=330,
    head=1.0, seed=64, hat="helm", hat_c="#5a5660", emblem=fist_emblem(500, 860, 0.75), item=i_hammer(780, 760),
    over=pauldrons("url(#brass)", 330) + beard_clasps(1.0, n=1)),
  F(shoulders=330, coat="#2a2a3a", trim="#c8a050", cap="helm", cap_c="#5a5660", head=160, beard=True, beard_c="#d8b060",
    hand="#d9a07e", skin="#d9a07e", item=ot_item("maul", 1)), BG_VANGUARD)
C("fenn",
  F(**DWARF_DK, coat="#efe2c0", trim="#8a5a2a", beard="huge", beard_c="#e0e0e0", mouth_in_beard=True, mouth="none",
    brow="worried", body_w=330, head=1.05, seed=65, item=i_wrench(770, 760, c="url(#brass)"),
    over=soot(1.05) + beard_clasps(1.05, n=2)),
  F(shoulders=320, coat="#efe2c0", trim="#8a5a2a", cap="hair", cap_c="#e0e0e0", head=155, beard=True, beard_c="#e0e0e0",
    hand="#a8704e", skin="#a8704e", item=ot_item("brass", 1)), BG_COMMON)
C("pip",
  F(**GOBLIN, coat="#5a4a2a", trim="#a86f32", mouth="o", brow="worried", head=1.25, body_w=190, seed=66,
    item=i_lantern(740, 780, "#ffd27a"), over=soot(1.25)),
  F(shoulders=180, coat="#5a4a2a", trim="#a86f32", cap="hair", cap_c="#3a2a14", head=140, ears="pointed",
    hand="#9ab84a", skin="#9ab84a", item=ot_item("lantern", 1)), BG_CINDER)
C("iskra",
  F(**DWARF, coat="#2a1a3a", trim="#e8c35a", hair="#1a1414", hair_style="long", brow="kind", mouth="smile", head=1.0,
    body_w=300, seed=67, hat="tophat", item=i_ledger(740, 780), warts=[(0.5, 0.25)],
    over=sash("#e8c35a") + braid(330, 560, 260, "#1a1414") + braid(670, 560, 260, "#1a1414")),
  F(shoulders=290, coat="#2a1a3a", trim="#e8c35a", cap="tophat", head=150, hand="#d9a07e", skin="#d9a07e",
    item=ot_item("clipboard", 1)), BG_COUNCIL)
C("brannoc",
  F(**DWARF_DK, coat="#3a2a1a", armor="#4a4650", beard="full", beard_c="#2a1a14", mouth_in_beard=True, mouth="none",
    brow="angry", body_w=370, head=1.05, seed=68, gloves="#2a1a10", item=i_hammer(780, 760),
    over=goggles(1.05) + soot(1.05) + beard_clasps(1.05, n=2)),
  F(shoulders=370, coat="#3a2a1a", trim=BRONZE, cap="hair", cap_c="#2a1a14", head=160, beard=True, beard_c="#2a1a14",
    hand="#2a1a10", skin="#a8704e", item=ot_item("maul", 1)), BG_FAMILY)
C("sigrun",
  F(**DWARF, coat="#3a2a5a", trim="#b88aff", hair="#e8d8f0", hair_style="messy", brow="worried", mouth="smile", head=1.0,
    body_w=280, seed=69, item=i_lantern(750, 770, "#b88aff"), spectacles=True),
  F(shoulders=270, coat="#3a2a5a", trim="#b88aff", cap="hair", cap_c="#e8d8f0", head=145, hand="#d9a07e",
    skin="#d9a07e", item=ot_item("lantern", 1, "#b88aff")), BG_ENGINE)
C("bera",
  F(**DWARF, coat="#3a5a2a", trim="#c8b48a", hair="#8a8a7a", hair_style="bun", brow="kind", mouth="smile", head=1.05,
    body_w=320, seed=70, warts=[(-0.4, 0.3), (0.45, 0.1)], item=i_censer(750, 760), over=kerchief(1.05, c="#5a7a3a")),
  F(shoulders=310, coat="#3a5a2a", trim="#c8b48a", cap="hair", cap_c="#8a8a7a", bun=True, head=150, hand="#d9a07e",
    skin="#d9a07e", item=ot_item("basket", 1)), BG_COMMON)
C("tikka",
  F(**GOBLIN, coat="#2a4a3a", trim="#9adf5a", mouth="grin", brow="kind", head=1.15, body_w=220, seed=71,
    gloves="#3a2a1a", item=i_pick(770, 770), warts=[(0.4, 0.3)]),
  F(shoulders=210, coat="#2a4a3a", trim="#9adf5a", cap="hair", cap_c="#2a3a14", head=150, ears="pointed",
    hand="#3a2a1a", skin="#9ab84a", item=ot_item("basket", 1)), BG_CINDER)
C("kharn",
  F(**DWARF_DK, coat="#2a2420", trim="#c8963a", beard="huge", beard_c="#f0f0f0", mouth_in_beard=True, mouth="none",
    brow="kind", body_w=300, head=1.05, seed=72, spectacles=True, item=i_quill_scroll(740, 790),
    over=beard_clasps(1.05, n=3, c="url(#brass)")),
  F(shoulders=290, coat="#2a2420", trim="#c8963a", cap="hair", cap_c="#f0f0f0", head=150, beard=True, beard_c="#f0f0f0",
    hand="#a8704e", skin="#a8704e", item=ot_item("staff", 1)), BG_COUNCIL)


def warden_p():
    s = [f'<circle cx="500" cy="520" r="330" fill="#c8963a" filter="url(#glw2)" opacity="0.25"/>',
         f'<path d="M300 920 L330 380 Q500 200 670 380 L700 920 Z" fill="#5a5660" {S(14)}/>',
         f'<rect x="360" y="440" width="280" height="90" rx="20" fill="#2a2630" {S(9)}/>',
         f'<rect x="390" y="465" width="80" height="40" fill="#ffcf6a"/><rect x="530" y="465" width="80" height="40" fill="#ffcf6a"/>']
    for k2, g in enumerate(("M-20 0 l20 -46 l20 46 m-40 -16 h40", "M-16 -46 v46 m0 -24 l28 -22 m-28 22 l28 22", "M0 -46 v46 m-20 -36 l20 12 l20 -12")):
        s.append(f'<path transform="translate({420+k2*80},{700})" d="{g}" fill="none" stroke="#ffcf6a" stroke-width="10" stroke-linecap="round"/>')
    return "".join(s)


def warden_token():
    return (f'<circle cx="500" cy="500" r="420" fill="#c8963a" filter="url(#glw2)" opacity="0.3"/>'
            f'<circle cx="500" cy="500" r="330" fill="#5a5660" {S(14)}/><circle cx="500" cy="500" r="200" fill="#3a3640" {S(10)}/>'
            + "".join(f'<path transform="translate(500,500) rotate({a})" d="M-20 -250 l20 -46 l20 46" fill="none" stroke="#ffcf6a" stroke-width="12"/>' for a in range(0, 360, 45))
            + f'<circle cx="500" cy="500" r="60" fill="#ffcf6a" {S(8)}/>')


def mephit_p():
    return (f'<circle cx="500" cy="520" r="360" fill="#ff7a1a" filter="url(#glw2)" opacity="0.35"/>'
            + "".join(f'<path d="M{500+dx} 600 q-60 -160 0 -320 q60 160 0 320" fill="#e8eef4" opacity="0.55"/>' for dx in (-140, 0, 140))
            + f'<circle cx="500" cy="520" r="150" fill="#ff9a3a" {S(10)}/><circle cx="450" cy="490" r="26" fill="#120909"/><circle cx="550" cy="490" r="26" fill="#120909"/>'
            + f'<path d="M440 580 q60 40 120 0" stroke="#120909" stroke-width="14" fill="none"/>'
            + f'<path d="M350 520 q-150 -100 -200 40 q120 -20 200 20 Z M650 520 q150 -100 200 40 q-120 -20 -200 20 Z" fill="#e8eef4" opacity="0.8" {S(6)}/>')


C("rune-warden", warden_p(), "special:warden", BG_COUNCIL)
C("scald-mephit", mephit_p(), "special:mephit", BG_ENGINE)

SPECIAL = {"bastion": bastion_token, "ram": ram_token, "vent": vent_token, "warden": warden_token, "mephit": lambda: mephit_p()}


def build(keys=None):
    os.makedirs(f"{OUT}/portraits", exist_ok=True)
    os.makedirs(f"{OUT}/tokens", exist_ok=True)
    for key, (por, tk, bgc) in CAST.items():
        if keys and key not in keys:
            continue
        inner = humanoid(por) if isinstance(por, dict) else por
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">{DEFS}'
               f'{bg(bgc, sum(map(ord, key)) & 255)}<g>{inner}</g>{frame()}</svg>')
        render(svg, f"{OUT}/portraits/{key}.webp", 768)
        tinner = token_overhead(tk) if isinstance(tk, dict) else SPECIAL[tk.split(":")[1]]()
        tsvg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">{DEFS}{tinner}</svg>'
        render(tsvg, f"{OUT}/tokens/{key}.webp", 400)


def sheet(kind="portraits", out="/home/claude/saga/il/art/preview/sheet.webp", cols=6):
    from PIL import Image
    keys = list(CAST)
    sz = 256
    rows = math.ceil(len(keys) / cols)
    im = Image.new("RGB", (cols * sz, rows * sz), "#222")
    for i, k in enumerate(keys):
        t = Image.open(f"{OUT}/{kind}/{k}.webp").convert("RGBA").resize((sz, sz))
        im.paste(t, ((i % cols) * sz, (i // cols) * sz), t)
    im.save(out, "WEBP", quality=80)


if __name__ == "__main__":
    build(sys.argv[1:] or None)
    sheet("portraits", "/home/claude/saga/il/art/preview/portraits.webp")
    sheet("tokens", "/home/claude/saga/il/art/preview/tokens.webp")
    print(len(CAST), "subjects")
