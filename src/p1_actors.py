"""Part I (The Cat and the Unkindness): full dnd5e stat blocks for the 23 Ravenloft-finale actors.

Part I's source data only carried each creature's actions as notes, so on the sheet every NPC showed a
single flavour feature. This file turns every action, bonus action, reaction, legendary action and
trait into a real embedded item with working activities (attack rolls, saves with DCs, damage parts,
healing, recharge, per-encounter uses, legendary-action costs), adds the missing saves, skills,
senses, resistances, immunities and languages, and writes them into data/ravenloft/actors.json.
The numbers are the module's own (to-hit, damage, DCs); the vague notes are replaced by rules text.
"""
import json, hashlib, re, os
from lib5e import *
from bestiary import per_enc, per_day

ROOT = "/home/claude/saga/il"
DATA = f"{ROOT}/module/data/ravenloft/actors.json"
BONUS = lambda c="": activation("bonus", 1, c)
REACT = lambda c="": activation("reaction", 1, c)
LEG = lambda n=1: activation("legendary", n)
SPECIAL = activation("special", None)


def Pp(*ps):
    return "".join(f"<p>{x}</p>" for x in ps)


def parts_of(spec, types):
    """'2d8+6+3d8', 'piercing/necrotic' -> [2d8+6 piercing, 3d8 necrotic]."""
    ts = types.split("/") if types else ["bludgeoning"]
    out, cur = [], None
    for tok in re.findall(r"[+-]?\s*\d+d\d+|[+-]?\s*\d+", spec.replace(" ", "")):
        if "d" in tok:
            n, d = tok.lstrip("+").split("d")
            cur = [int(n), int(d), 0]
            out.append(cur)
        elif cur is not None:
            cur[2] += int(tok)
    res = []
    for i, (n, d, b) in enumerate(out):
        res.append(dmg(n, d, str(b) if b else "", [ts[min(i, len(ts) - 1)]]))
    return res


def dmg_text(spec, types):
    ps = parts_of(spec, types)
    bits = []
    for p in ps:
        avg = int(p["number"] * (p["denomination"] + 1) / 2 + (int(p["bonus"]) if p["bonus"] else 0))
        f = f"{p['number']}d{p['denomination']}" + (f" + {p['bonus']}" if p["bonus"] else "")
        bits.append(f"{avg} ({f}) {p['types'][0]}")
    return " plus ".join(bits)


class S:
    def __init__(self, sid):
        self.sid, self.items, self.n = sid, [], 0

    def _k(self, name):
        self.n += 1
        return f"p1-{self.sid}-{self.n}-{slug(name)}"

    def _add(self, k, name, desc, ic, acts=(), uses_=None):
        it = feat(k, name, desc, img=icon(ic), activities=list(acts), uses_=uses_, sort=self.n * 1000)
        it["flags"] = {MOD: {"sourceId": f"{self.sid}.item.{self.n}", "managed": True}}
        self.items.append(it)
        return self

    def multi(self, text):
        k = self._k("multiattack")
        return self._add(k, "Multiattack", Pp(text), "ab-multi", [utility(k, 0)])

    def atk(self, name, hit, spec, types, *, reach=5, rng=None, desc="", act=None, cost=None, recharge_=None, per=None,
            ic="ab-blade", kind=None):
        k = self._k(name)
        kind = kind or ("ranged" if rng else "melee")
        cons = consume_legact(cost) if cost else (consume_item_uses() if (recharge_ or per) else None)
        u = uses(1, [recharge(recharge_)]) if recharge_ else (per_enc(per) if per else None)
        a = attack(k, 0, to_hit=hit, kind=kind, parts=parts_of(spec, types), reach=reach, range_=rng,
                   act=act or (LEG(cost) if cost else None), consumption=cons)
        where = f"range {rng} ft." if rng else f"reach {reach} ft."
        head = f"<em>{'Ranged' if kind == 'ranged' else 'Melee'} Weapon Attack:</em> +{hit} to hit, {where}, one target. <em>Hit:</em> {dmg_text(spec, types)} damage."
        tag = f" <strong>Costs {cost} legendary action{'s' if cost > 1 else ''}.</strong>" if cost else ""
        rch = f" <strong>Recharge {recharge_}–6.</strong>" if recharge_ else ""
        return self._add(k, name, Pp(head + (" " + desc if desc else "") + tag + rch), ic, [a], u)

    def sv(self, name, abil, dc, desc, *, spec=None, types=None, act=None, cost=None, recharge_=None, per=None,
           half=True, tmpl=None, count=None, ic="ab-burst"):
        k = self._k(name)
        cons = consume_legact(cost) if cost else (consume_item_uses() if (recharge_ or per) else None)
        u = uses(1, [recharge(recharge_)]) if recharge_ else (per_enc(per) if per else None)
        tg = target("", "creature", tmpl[0], tmpl[1], tmpl[2] if len(tmpl) > 2 else "") if tmpl else target(count or 1, "creature")
        a = save(k, 0, ability=abil, dc=dc, parts=parts_of(spec, types) if spec else [], on_save="half" if (spec and half) else "none",
                 act=act or (LEG(cost) if cost else None), consumption=cons, tgt=tg)
        txt = f"<em>DC {dc} {ABIL[abil]} saving throw.</em> " + desc
        if spec:
            txt += f" <em>Damage:</em> {dmg_text(spec, types)}" + (" (half on a success)." if half else " (none on a success).")
        tag = f" <strong>Costs {cost} legendary action{'s' if cost > 1 else ''}.</strong>" if cost else ""
        rch = f" <strong>Recharge {recharge_}–6.</strong>" if recharge_ else ""
        pe = f" <strong>{per}/encounter.</strong>" if per else ""
        return self._add(k, name, Pp(txt + tag + rch + pe), ic, [a], u)

    def util(self, name, desc, *, act=None, cost=None, per=None, recharge_=None, ic="ab-slip"):
        k = self._k(name)
        cons = consume_legact(cost) if cost else (consume_item_uses() if (recharge_ or per) else None)
        u = uses(1, [recharge(recharge_)]) if recharge_ else (per_enc(per) if per else None)
        tag = f" <strong>Costs {cost} legendary action{'s' if cost > 1 else ''}.</strong>" if cost else ""
        pe = f" <strong>{per}/encounter.</strong>" if per else ""
        rch = f" <strong>Recharge {recharge_}–6.</strong>" if recharge_ else ""
        return self._add(k, name, Pp(desc + tag + pe + rch), ic, [utility(k, 0, act=act or (LEG(cost) if cost else ACT()), consumption=cons)], u)

    def heal(self, name, desc, formula, *, temp=False, act=None, per=None, count=1, ic="ab-heal"):
        k = self._k(name)
        cons = consume_item_uses() if per else None
        u = per_enc(per) if per else None
        a = heal_act(k, 0, formula_part=dmg_formula(formula), act=act or ACT(), tgt=target(count, "creature"), temp=temp, consumption=cons)
        pe = f" <strong>{per}/encounter.</strong>" if per else ""
        return self._add(k, name, Pp(desc + pe), ic, [a], u)

    def trait(self, name, desc, ic="ab-shield"):
        return self._add(self._k(name), name, Pp(desc) if not desc.startswith("<") else desc, ic)

    def legres(self, n, note=""):
        k = self._k("legres")
        return self._add(k, f"Legendary Resistance ({n})", Pp("If this creature fails a saving throw, it can choose to succeed instead." + (" " + note if note else "")),
                         "ab-legendary", [utility(k, 0, act=SPECIAL, consumption=consume_legres())])

    def legact_header(self, n, who):
        return self.trait("Legendary Actions", f"{who} can take {n} legendary actions, choosing from the options marked <em>Legendary</em>. Only one option can be used at a time and only at the end of another creature's turn. Spent legendary actions are regained at the start of its turn.", "ab-legendary")


ACT = activation
ABIL = {"str": "Strength", "dex": "Dexterity", "con": "Constitution", "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma"}
VEIL = ("Ordinary sunlight and the <em>daylight</em> spell do not trigger this creature's sunlight weaknesses. "
        "<strong>Artifact-grade sunlight</strong> (the Sunsword, the Holy Symbol of Ravenkind's sunlight) suppresses the Veil: while in it, "
        "the creature takes 15 radiant damage at the start of each of its turns, has disadvantage on attack rolls and ability checks, and its Regeneration does not work.")
VAMP_WEAK = ("<em>Forbiddance.</em> It can't enter a residence without an invitation from one of the occupants. "
             "<em>Harmed by Running Water.</em> It takes 20 acid damage if it ends its turn in running water. "
             "<em>Stake to the Heart.</em> If a piercing weapon made of wood is driven into its heart while it is incapacitated in its resting place, it is paralyzed until the stake is removed.")
VAMP_RES = dict(dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", ci=[], senses={"darkvision": 120})


def bride_common(s, regen=10):
    s.trait("Veil of the Black Sun", VEIL, "ab-lantern")
    s.trait("Regeneration", f"It regains {regen} hit points at the start of its turn if it has at least 1 hit point and isn't in artifact sunlight or running water. "
            "If it takes radiant damage from an artifact, this trait doesn't function at the start of its next turn.", "ab-heal")
    s.trait("Spider Climb", "It can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check.", "ab-slip")
    s.trait("Vampire Weaknesses", VAMP_WEAK, "ab-will")


DEFS = {}


def define(sid, *, system=None, token_size=None, disposition=-1):
    def deco(fn):
        DEFS[sid] = (fn, system or {}, token_size, disposition)
        return fn
    return deco


def sysp(saves=(), skills=None, senses=None, dr=(), di=(), dv=(), ci=(), dr_custom="", di_custom="", langs=(), lang_custom="",
         legact=0, legres=0, alignment="", fly=None, hover=None, cr=None):
    s = {"attributes": {"senses": {"darkvision": 0, "blindsight": 0, "tremorsense": 0, "truesight": 0, "units": "ft", "special": ""}},
         "traits": {"dr": {"value": list(dr), "custom": dr_custom}, "di": {"value": list(di), "custom": di_custom},
                    "dv": {"value": list(dv), "custom": ""}, "ci": {"value": list(ci), "custom": ""},
                    "languages": {"value": list(langs), "custom": lang_custom}},
         "resources": {"legact": {"value": legact, "max": legact}, "legres": {"value": legres, "max": legres}},
         "abilities": {a: {"proficient": 1} for a in saves},
         "skills": {k: {"value": v, "ability": SKILL_ABIL[k]} for k, v in (skills or {}).items()}}
    for k, v in (senses or {}).items():
        s["attributes"]["senses"][k] = v
    if alignment:
        s["details"] = {"alignment": alignment}
    if fly is not None:
        s["attributes"]["movement"] = {"fly": fly, "hover": bool(hover)}
    return s


VAMP_LANGS = ("common", "elvish", "abyssal")


# ---------------------------------------------------------------- the brides, Finn, Tatyana
@define("cu.actor.anastrasya", system=sysp(saves=("dex", "wis", "cha"), skills={"prf": 2, "per": 1, "ste": 1, "prc": 1}, senses={"darkvision": 120},
                                           dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", langs=("common", "elvish"), alignment="lawful evil"))
def _(s):
    s.multi("Anastrasya makes two Crimson Rapier attacks. She can replace one of them with Courtly Gaze.")
    s.atk("Crimson Rapier", 9, "1d8+5+3d6", "piercing/necrotic", desc="While Anastrasya has fewer than 55 hit points (Bloodied Courtier), the rapier deals an extra 3 (1d6) necrotic damage.", ic="ab-blade")
    s.sv("Compelled Waltz", "wis", 17, "One creature Anastrasya can see within 30 feet. On a failure, Anastrasya moves the target up to its speed along a route she chooses; this movement doesn't provoke opportunity attacks. She can then make one Crimson Rapier attack against it.", recharge_=5, ic="ab-will")
    s.sv("Courtly Gaze", "wis", 17, "One creature within 30 feet that can see her. On a failure, the target can't willingly target Anastrasya with attacks or harmful spells until the start of her next turn.", act=BONUS(), ic="ab-will")
    s.util("Partner's Step", "When an enemy enters a space within 5 feet of Anastrasya, she moves up to 15 feet without provoking opportunity attacks.", act=REACT("An enemy moves within 5 feet"), ic="ab-slip")
    s.trait("Bloodied Courtier", "While she has fewer than 55 hit points, her Crimson Rapier deals an extra 1d6 necrotic damage (included in the attack's text).", "ab-roar")
    bride_common(s)


@define("cu.actor.volenta", system=sysp(saves=("str", "con", "wis", "cha"), skills={"ath": 9, "itm": 9, "prc": 7}, senses={"darkvision": 120},
                                        dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", ci=["frightened"], langs=("common", "elvish", "abyssal"), alignment="lawful evil"))
def _(s):
    s.multi("Volenta makes two Black Oath Blade attacks. If Sanguine Smite is available, he can use it on one hit.")
    s.atk("Black Oath Blade", 10, "1d10+6+2d8", "slashing/necrotic", desc="The necrotic damage is his broken oath feeding each strike.", ic="ab-cleaver")
    s.atk("Sanguine Smite", 10, "2d6+6+5d8", "slashing/necrotic", desc="Use in place of one Black Oath Blade attack. If the target is frightened, charmed, or more than 10 feet from all of its allies, it also can't regain hit points until the start of Volenta's next turn.", recharge_=5, ic="ab-bolt")
    s.sv("Dreadful Aspect", "wis", 18, "Each creature of Volenta's choice within 30 feet that can see him. On a failure, a creature is frightened of him for 1 minute; it repeats the save at the end of each of its turns. A creature holding an artifact of light has advantage on the save.", per=1, tmpl=("radius", 30), ic="ab-roar")
    s.sv("Months, Not Minutes", "wis", 18, "One creature within 30 feet. On a failure, the target is also frightened of Volenta until the end of its next turn.", spec="3d8", types="psychic", ic="ab-will")
    s.util("Unholy Intercession", "When Anastrasya or another allied vampire within 30 feet is hit by an attack, Volenta moves up to half his speed toward the attacker without provoking opportunity attacks. If he ends within 5 feet of the attacker, he makes one Black Oath Blade attack against it.", act=REACT("An allied vampire within 30 feet is hit"), ic="ab-shield")
    s.trait("Broken Vow Aura", "A hostile creature that starts its turn within 10 feet of Volenta must succeed on a DC 18 Wisdom saving throw or be unable to take reactions until the start of its next turn.", "ab-will")
    s.trait("Aura of Hate", "His corrupted oath is already in his damage: do not add a further Charisma bonus to his weapon damage.", "ab-roar")
    bride_common(s, regen=15)


@define("cu.actor.ludmilla", system=sysp(saves=("dex", "int", "wis"), skills={"arc": 11, "his": 9, "prc": 7}, senses={"darkvision": 120},
                                         dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", langs=("common", "elvish", "draconic", "infernal"), alignment="neutral evil"))
def _(s):
    s.multi("Ludmilla casts Blood Lance twice, or Blood Lance and Grave Sigil.")
    s.atk("Blood Lance", 9, "4d10", "necrotic", rng=120, kind="ranged", desc="A spear of congealed blood.", ic="ab-spear")
    s.sv("Grave Sigil", "dex", 17, "Ludmilla marks a visible 10-foot square within 90 feet. It erupts at the start of her next turn; each creature in it saves.", spec="5d8", types="necrotic", tmpl=("cube", 10), ic="ab-burst")
    s.sv("Black Sun Pulse", "con", 17, "All non-artifact light within 60 feet of Ludmilla goes out. Each creature of her choice within 60 feet saves; on a failure it is also blinded until the start of its next turn.", spec="3d8", types="necrotic", recharge_=5, tmpl=("radius", 60), ic="ab-vent")
    s.util("Counterspell Reserve", "When she sees a creature within 60 feet cast a spell, Ludmilla interrupts it as the <em>counterspell</em> spell (3rd level; she makes an ability check with +5 for higher-level spells). Save it for a meaningful spell, not routine healing.", act=REACT("A creature within 60 feet casts a spell"), per=2, ic="ab-scroll")
    s.util("Nightglass Step", "Ludmilla teleports from one area of dim light or darkness to another she can see within 40 feet.", act=BONUS(), ic="ab-slip")
    s.trait("Nightglass Pylons", "While at least two Nightglass Pylons remain active, Ludmilla has resistance to radiant damage that isn't produced by an artifact. The pylons never stop the Sunsword or the Holy Symbol.", "ab-construct")
    bride_common(s)


@define("cu.actor.finn", system=sysp(saves=("dex", "con", "wis"), skills={"acr": 9, "ste": 9, "slt": 9, "dec": 8, "prc": 6}, senses={"darkvision": 120},
                                     dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", langs=("common", "elvish"), alignment="chaotic evil"))
def _(s):
    s.multi("Finn makes three Blade or Claw attacks. He can replace one of them with a Bite.")
    s.atk("Blade / Claw", 9, "1d8+5+2d6", "piercing/necrotic", ic="ab-blade")
    s.atk("Bite", 9, "1d6+5+3d8", "piercing/necrotic", desc="Finn regains hit points equal to half the necrotic damage dealt.", ic="ab-tusk")
    s.trait("Quick Hand", "Once per turn, Finn deals an extra 10 (3d6) damage to a creature he hits if he has advantage on the attack or another hostile creature is within 5 feet of the target.", "ab-blade")
    s.util("Sanguine Moon Step", "Finn teleports up to 30 feet through red mist to an unoccupied space he can see.", act=BONUS(), ic="ab-slip")
    s.util("Not Yet", "When Finn would be reduced to 0 hit points, he drops to 1 hit point instead.", act=REACT("Reduced to 0 hit points"), per=1, ic="ab-will")
    s.trait("Three Chains of Claim", "Finn can be saved by breaking three chains: the <em>Sanguine Moon</em>, the <em>Rejected Self</em> and the <em>Master's Gift</em>. Breaking one takes an action and a meaningful DC 16 Persuasion, Insight or Religion check tied to that chain (the Finale Dashboard tracks them). With all three broken he stops fighting.", "ab-chain")
    bride_common(s)


@define("cu.actor.tatyana", system=sysp(saves=("dex", "wis", "cha"), skills={"ins": 6, "per": 8, "prc": 6}, senses={"darkvision": 120},
                                        dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", langs=("common",), alignment="neutral good"), disposition=0)
def _(s):
    s.multi("Tatyana makes two Claw attacks.")
    s.atk("Claw", 7, "1d8+4+2d6", "slashing/necrotic", ic="ab-blade")
    s.util("No", "<strong>Phase III only, and only if the party treated her as a person rather than a prize.</strong> When Strahd's Phase III profile drops to about half its hit points, Tatyana strips one of his remaining Legendary Resistances (spend it from his pool) and shouts where the coffin is.", act=REACT("Strahd Phase III is at half hit points"), per=1, ic="ab-will")
    s.trait("Agency, Not Objective", "Tatyana is not another bride encounter. If the party has treated her as an object to recover, she does not use <em>No</em>; she defends herself and flees.", "ab-will")
    s.trait("Veil of the Black Sun", VEIL, "ab-lantern")


@define("cu.actor.abbot", system=sysp(saves=("wis", "cha"), skills={"ins": 9, "rel": 7, "per": 8}, senses={"darkvision": 120},
                                      dr=["radiant"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", ci=["charmed", "exhaustion", "frightened"],
                                      langs=("common", "celestial"), alignment="lawful evil"), disposition=0)
def _(s):
    s.multi("The Abbot makes two Radiant Strike attacks.")
    s.atk("Radiant Strike", 9, "2d8+5+2d8", "bludgeoning/radiant", ic="ab-hammer")
    s.heal("One Healing Miracle", "<strong>Only if persuaded to abandon the altar.</strong> Each member of the Unkindness regains 20 hit points and may end one disease, curse or condition affecting them. The Abbot then withdraws.", "20", per=1, count="", ic="ab-heal")
    s.heal("Bless Finn", "If the party fails the social confrontation but does not attack him, the Abbot gives Finn 30 temporary hit points before withdrawing.", "30", temp=True, per=1, ic="ab-heal")
    s.trait("Angelic Weapons", "His weapon attacks are magical and already include his radiant damage.", "ab-lantern")
    s.trait("Magic Resistance", "The Abbot has advantage on saving throws against spells and other magical effects.", "ab-shield")
    s.trait("Fallen Certainty", "He believes this wedding is a sacrament. Arguments that the bride never consented, or that Finn is being stolen from himself, can end the fight (DC 17 Persuasion or Religion, three successes before three failures).", "ab-will")


# ---------------------------------------------------------------- Strahd's three phases
STRAHD_SYS = dict(saves=("dex", "wis", "cha"), skills={"arc": 11, "itm": 12, "per": 12, "prc": 10, "ste": 11}, senses={"darkvision": 120},
                  dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", ci=["charmed"],
                  langs=("common", "abyssal", "draconic", "elvish", "giant", "infernal"), legact=3, legres=4, alignment="lawful evil")


def strahd_common(s, regen_text):
    s.legres(4, "Strahd's four Legendary Resistances are shared across all three phases. At each phase change he regains one spent use, to a maximum of four.")
    s.trait("Veil of the Black Sun", VEIL, "ab-lantern")
    s.trait("Regeneration", regen_text, "ab-heal")
    s.trait("Castle Step", "While not in artifact sunlight, Strahd can move through walls, floors and ceilings of Castle Ravenloft as if they were difficult terrain. If he ends his movement inside solid matter, he is forced to the nearest unoccupied space and takes 10 (3d6) force damage.", "ab-slip")
    s.trait("Vampire Weaknesses", VAMP_WEAK, "ab-will")


@define("cu.actor.strahd1", system=sysp(**STRAHD_SYS))
def _(s):
    s.multi("Strahd makes two Crimson Blade attacks, or one Crimson Blade and one Blood Grasp. He can replace one attack with a Bite against a grappled, willing or incapacitated target.")
    s.atk("Crimson Blade", 11, "2d8+6+3d8", "piercing/necrotic", ic="ab-blade")
    s.atk("Blood Grasp", 11, "2d10+6", "bludgeoning", desc="The target is grappled (escape DC 18).", ic="ab-fist")
    s.atk("Bite", 11, "1d6+6+4d8", "piercing/necrotic", desc="Only against a grappled, willing or incapacitated target. Strahd regains hit points equal to half the necrotic damage.", ic="ab-tusk")
    s.sv("Master's Command", "wis", 18, "One humanoid within 30 feet that can see him. On a failure it is charmed until the end of its next turn, and Strahd chooses its movement or one weapon attack it makes.", recharge_=5, ic="ab-will")
    s.util("Ebon Step", "Strahd teleports from one shadow to another he can see within 30 feet.", act=BONUS(), ic="ab-slip")
    s.util("Mocking Reversal", "When an attack misses Strahd, he moves up to 20 feet without provoking opportunity attacks.", act=REACT("An attack misses him"), ic="ab-parry")
    s.legact_header(3, "Strahd")
    s.util("Step (Legendary)", "Strahd moves up to half his speed without provoking opportunity attacks.", cost=1, ic="ab-slip")
    s.atk("Crimson Blade (Legendary)", 11, "2d8+6+3d8", "piercing/necrotic", cost=1, ic="ab-blade")
    s.sv("Shadow Hand (Legendary)", "str", 18, "One creature within 30 feet. On a failure, its own shadow pulls it 20 feet toward Strahd and knocks it prone.", cost=2, ic="ab-chain")
    s.atk("Bite (Legendary)", 11, "1d6+6+4d8", "piercing/necrotic", cost=2, desc="Grappled, willing or incapacitated target only; he regains half the necrotic damage.", ic="ab-tusk")
    strahd_common(s, "Strahd regains 20 hit points at the start of his turn if he has at least 1 hit point and isn't in artifact sunlight or running water. Artifact sunlight or artifact radiant damage stops it until the start of his following turn.")


@define("cu.actor.strahd2", system=sysp(**STRAHD_SYS))
def _(s):
    s.multi("Strahd makes two Crimson Blade attacks, or uses Blood Lightning or Shadow Crush and makes one Crimson Blade attack.")
    s.atk("Crimson Blade", 11, "2d8+6+3d8", "piercing/necrotic", ic="ab-blade")
    s.sv("Blood Lightning", "dex", 18, "A 60-foot line, 5 feet wide.", spec="5d10+3d8", types="lightning/necrotic", tmpl=("line", 60, 5), ic="ab-bolt")
    s.sv("Shadow Crush", "str", 18, "One creature within 60 feet. On a failure it is also restrained by its own shadow (escape DC 18).", spec="4d10", types="bludgeoning", ic="ab-chain")
    s.util("Heartstep", "Strahd teleports to a space next to any surviving Heart Chain.", act=BONUS(), ic="ab-slip")
    s.legact_header(3, "Strahd")
    s.util("Move (Legendary)", "Strahd moves up to half his speed.", cost=1, ic="ab-slip")
    s.sv("Blood Bolt (Legendary)", "dex", 18, "One creature within 60 feet.", spec="3d10", types="necrotic", cost=1, ic="ab-bolt")
    s.sv("Break the Floor (Legendary)", "dex", 18, "A 10-foot square within 60 feet collapses. On a failure a creature there falls 20 feet (2d6 bludgeoning) and lands prone.", spec="2d6", types="bludgeoning", cost=2, tmpl=("cube", 10), ic="ab-pick")
    s.util("Heartstep (Legendary)", "Strahd teleports next to a surviving Heart Chain.", cost=2, ic="ab-slip")
    s.trait("Eternal Night", "The chamber is supernatural darkness: non-artifact light can't illuminate it. Artifact sunlight cuts visible corridors through it and suppresses Castle Step in those corridors.", "ab-vent")
    strahd_common(s, "Strahd regains 20 hit points at the start of his turn (10 once the Blood Chain is destroyed) if he has at least 1 hit point and isn't in artifact sunlight or running water.")


@define("cu.actor.strahd3", system=sysp(**STRAHD_SYS))
def _(s):
    s.multi("Strahd makes three Rend attacks. He can replace one with a Bite.")
    s.atk("Rend", 11, "2d8+6+2d8", "slashing/necrotic", ic="ab-cleaver")
    s.atk("Bite", 11, "1d8+6+4d8", "piercing/necrotic", desc="Strahd regains hit points equal to half the necrotic damage.", ic="ab-tusk")
    s.sv("The Devil's Roar", "wis", 18, "Each creature of his choice within 60 feet that can hear him. On a failure a creature is also frightened until the end of its next turn; on a success it takes half damage and isn't frightened.", spec="4d8", types="psychic", recharge_=5, tmpl=("radius", 60), ic="ab-roar")
    s.trait("Predator's Pounce", "If Strahd moves at least 20 feet straight toward a creature and then hits it with Rend, it must succeed on a DC 18 Strength saving throw or fall prone. He can then Bite it as a bonus action.", "ab-press")
    s.legact_header(3, "Strahd")
    s.util("Rush (Legendary)", "Strahd moves up to half his speed.", cost=1, ic="ab-slip")
    s.atk("Rend (Legendary)", 11, "2d8+6+2d8", "slashing/necrotic", cost=1, ic="ab-cleaver")
    s.sv("Grave Burst (Legendary)", "dex", 18, "A crypt within 30 feet explodes; each creature within 10 feet of it saves. On a failure it is also knocked prone.", spec="4d8", types="piercing", cost=2, tmpl=("radius", 10), ic="ab-bomb")
    s.atk("Drink the Last Breath (Legendary)", 11, "1d8+6+4d8", "piercing/necrotic", cost=3, desc="Can target a creature at 0 hit points within reach (each hit counts as a failed death save; a critical as two). This is the first phase in which Strahd attacks the fallen.", ic="ab-tusk")
    strahd_common(s, "Strahd regains 10 hit points at the start of his turn only if the Blood Chain survived Phase II; if it was destroyed he doesn't regenerate. Artifact sunlight suppresses it either way.")


# ---------------------------------------------------------------- objects of the finale
OBJ = dict(di=["poison", "psychic"], ci=["blinded", "charmed", "deafened", "exhaustion", "frightened", "paralyzed", "petrified", "poisoned", "prone", "stunned", "unconscious"])


@define("cu.actor.pylon", system=sysp(**OBJ, dv=["radiant"]))
def _(s):
    s.sv("Black Sun Flare", "con", 13, "When the pylon takes damage, it flares: each creature within 10 feet of it saves. On a failure it is blinded until the end of its next turn.", act=REACT("The pylon takes damage"), per=1, tmpl=("radius", 10), ic="ab-vent")
    s.trait("Black Sun Conduit", "While at least two pylons remain, Ludmilla resists radiant damage that isn't produced by an artifact.", "ab-construct")
    s.trait("Object", "The pylon doesn't move or act except as described. It is destroyed at 0 hit points; it can't be healed.", "ab-construct")


def chain(sid, effect_text):
    @define(sid, system=sysp(**OBJ, dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks"))
    def _(s):
        s.sv("Backlash", "con", 15, "When the chain is damaged, its links lash out at the attacker if it is within 10 feet.", spec="2d8", types="necrotic", act=REACT("The chain takes damage from a creature within 10 feet"), ic="ab-chain")
        s.util("Sever the Chain", effect_text, act=SPECIAL, ic="ab-chain")
        s.trait("Object", "The Heart Chain is anchored to Strahd's heart. It is destroyed at 0 hit points and can't be healed. Strahd feels it break.", "ab-construct")
    return _


chain("cu.actor.chain.blood", "When destroyed, it deals 20 force or radiant damage to Strahd and reduces his Phase II Regeneration from 20 to 10. In Phase III he has no regeneration from this chain.")
chain("cu.actor.chain.stone", "When destroyed, it deals 20 force or radiant damage to Strahd, and he loses Castle Step for the rest of the fight.")
chain("cu.actor.chain.dominion", "When destroyed, it deals 20 force or radiant damage to Strahd, and he has one fewer legendary action each round for the rest of the fight.")


@define("cu.actor.coffin", system=sysp(**OBJ, dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks"))
def _(s):
    s.trait("Final Anchor", "Artifact sunlight touching the coffin suppresses all vampire Regeneration in the room. If the coffin is destroyed before Strahd reforms there, his mist is forced to flee the castle, and his next appearance starts without Regeneration.", "ab-construct")
    s.util("The Lid Opens", "If Strahd's mist reaches the coffin, he rests here and starts regaining hit points: 1 hit point after 1 hour, then the normal amount each turn. Destroying the coffin or putting artifact sunlight on it stops this.", act=SPECIAL, ic="ab-will")
    s.trait("Object", "The coffin is destroyed at 0 hit points and can't be healed.", "ab-construct")


# ---------------------------------------------------------------- the Dark Powers
DP = dict(di=["poison"], ci=["charmed", "exhaustion", "frightened", "poisoned"])


@define("cu.actor.orcus", system=sysp(saves=("str", "con", "wis", "cha"), skills={"arc": 12, "itm": 14, "prc": 12, "rel": 12}, senses={"truesight": 120},
                                      di=["necrotic", "poison"], dr=["cold", "fire", "lightning"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks",
                                      ci=["charmed", "exhaustion", "frightened", "poisoned"], langs=("abyssal", "common"), lang_custom="telepathy 120 ft.", legres=2, legact=3, alignment="chaotic evil"), token_size=3)
def _(s):
    s.multi("Orcus makes two Skull-Mace attacks, or uses Soul Hook and makes one Skull-Mace attack.")
    s.atk("Skull-Mace of the Manifestation", 11, "2d8+7+3d8", "bludgeoning/necrotic", reach=10, desc="Once per turn, against a fiend, one hit deals an extra 9 (2d8) force damage. This is why Arl treats Orcus as the immediate enemy.", ic="ab-hammer")
    s.sv("Word of Unmaking", "con", 18, "A 60-foot cone. A creature that fails can't regain hit points until the start of Orcus's next turn.", spec="6d8", types="necrotic", recharge_=5, tmpl=("cone", 60), ic="ab-roar")
    s.sv("Soul Hook", "cha", 18, "One creature within 60 feet that has been resurrected, bears a soul coin, or returned from death (Thorgrinn, Damien, any revived hero). On a failure it is also restrained, chained to the grave, until it or an ally uses an action to make a DC 18 Charisma (Religion) check to break the hook.", spec="2d8", types="psychic", ic="ab-chain")
    s.util("Call the Recently Dead", "Orcus chooses a corpse, destroyed undead or grave within 60 feet. Until the end of his next turn it is a deathless obstacle (a 10-foot cube of difficult terrain) or a 20-foot-radius necrotic hazard: a creature that starts its turn in it takes 10 (3d6) necrotic damage.", ic="ab-vent")
    s.util("Horned Advance", "Orcus moves up to half his speed toward Strahd, Vampyr or Arl without provoking opportunity attacks.", act=BONUS(), ic="ab-press")
    s.legact_header(3, "Orcus")
    s.util("Lumber (Legendary)", "Orcus moves up to half his speed without provoking opportunity attacks.", cost=1, ic="ab-press")
    s.atk("Skull-Mace (Legendary)", 11, "2d8+7+3d8", "bludgeoning/necrotic", reach=10, cost=2, ic="ab-hammer")
    s.sv("Grave Pulse (Legendary)", "con", 18, "Each living creature of Orcus's choice within 20 feet saves.", spec="3d8", types="necrotic", cost=2, tmpl=("radius", 20), ic="ab-vent")
    s.legres(2, "Two uses for the entire Ravenloft finale.")
    s.trait("Magic Resistance", "Orcus has advantage on saving throws against spells and other magical effects.", "ab-shield")
    s.trait("Dark Power Reconstitution — Wish Required", "Until the Edict of Finality exists (made by the party's Wish), reducing this manifestation to 0 hit points does not defeat Orcus. At the end of the next round he reforms at 115 hit points from the nearest surviving Grave Horn. Each destroyed Grave Horn removes one reconstitution.", "ab-will")
    s.trait("Edict of Finality", "Once the Wish has made the Edict active, Orcus can't reconstitute in Barovia, destroyed Grave Horns stay destroyed, and reaching 0 hit points ends the manifestation for good.", "ab-scroll")
    s.trait("Death Lord's Priority", "Orcus wants Strahd permanently dead so he can seize the soul and Barovia's death-energy. He attacks Arl when Arl interferes, then the Unkindness.", "ab-command")


@define("cu.actor.vampyr", system=sysp(saves=("dex", "con", "wis", "cha"), skills={"dec": 14, "ins": 11, "per": 14, "prc": 11}, senses={"truesight": 120},
                                       di=["necrotic", "poison"], dr=["cold"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", dv=["radiant"],
                                       ci=["charmed", "exhaustion", "frightened", "poisoned"], langs=("common", "abyssal", "elvish"), lang_custom="telepathy 120 ft.", legres=2, legact=3, alignment="neutral evil"), token_size=3)
def _(s):
    s.multi("Vampyr makes two Bloodlash attacks and uses First Thirst.")
    s.atk("Bloodlash", 10, "4d8+6", "necrotic", reach=15, desc="Vampyr can pull the target up to 15 feet toward a blood pool, Strahd, or one of its Covenant Hooks.", ic="ab-chain")
    s.sv("First Thirst", "con", 18, "One creature within 30 feet. Vampyr drinks blood, life-force or soul resonance; constructs and soul-coin vessels are not exempt. It regains hit points equal to half the necrotic damage dealt.", spec="5d8", types="necrotic", ic="ab-tusk")
    s.sv("Night Without Stars", "wis", 18, "The battlefield becomes supernatural night until initiative count 10 of the next round; non-artifact light fails, and artifact sunlight remains as a narrow cutting beam. Each creature of Vampyr's choice within 120 feet saves.", spec="3d8", types="psychic", recharge_=5, tmpl=("radius", 120), ic="ab-vent")
    s.util("Covenant Hook", "Vampyr attaches a blood tether to Strahd, Finn, Tatyana, Damien or another creature entangled with vampirism within 60 feet (track it on the Finale Dashboard). Three active Hooks on Strahd when he reaches 0 hit points let Vampyr claim him instead of letting him die.", ic="ab-chain")
    s.util("Red Mist Step", "Vampyr teleports up to 40 feet between blood, mist, a vampire, or a Ravenloft shadow.", act=BONUS(), ic="ab-slip")
    s.legact_header(3, "Vampyr")
    s.util("Drift (Legendary)", "Vampyr moves up to half its speed as red mist without provoking opportunity attacks.", cost=1, ic="ab-slip")
    s.atk("Bloodlash (Legendary)", 10, "4d8+6", "necrotic", reach=15, cost=1, ic="ab-chain")
    s.sv("Sip (Legendary)", "con", 18, "One creature within 30 feet that is bleeding or below half its hit points. Vampyr regains hit points equal to the necrotic damage dealt.", spec="3d8", types="necrotic", cost=2, ic="ab-tusk")
    s.legres(2, "Two uses for the entire Ravenloft finale.")
    s.trait("Artifact Sunlight Vulnerability", "Artifact sunlight suppresses Red Mist Step and Covenant Hook until the start of Vampyr's next turn. Vampyr takes 20 radiant damage when it starts its turn in artifact sunlight.", "ab-lantern")
    s.trait("Dark Power Reconstitution — Wish Required", "Until the Edict of Finality exists, reducing this manifestation to 0 hit points does not defeat Vampyr. At the end of the next round it reforms at 103 hit points from the nearest surviving Blood Heart.", "ab-will")
    s.trait("Edict of Finality", "Once the Wish has made the Edict active, Vampyr can't re-form in dying Barovia, destroyed Blood Hearts stay destroyed, and Strahd can't be claimed through the covenant.", "ab-scroll")
    s.trait("Vindictive First Thirst", "Vampyr remembers Thorgrinn shattering its Amber prison and calls him 'metal dwarf'. It wants the covenant and the humiliation answered more than it wants Strahd dead.", "ab-roar")


@define("cu.actor.anchor.orcus", system=sysp(**OBJ, dr=["necrotic"]))
def _(s):
    s.sv("Grave Toll", "con", 14, "At the start of each round, the horn sounds: each living creature within 20 feet saves.", spec="2d8", types="necrotic", act=SPECIAL, recharge_=5, tmpl=("radius", 20), ic="ab-roar")
    s.trait("Dark Power Anchor", "Destroying a Grave Horn removes one Orcus Intervention from the GM pool and reduces Orcus Pressure by 1. Three destroyed anchors force the manifestation into disarray (it loses its next Word of Unmaking recharge).", "ab-construct")
    s.trait("Object", "The horn doesn't move. It is destroyed at 0 hit points and can't be healed.", "ab-construct")


@define("cu.actor.anchor.vampyr", system=sysp(**OBJ, dv=["radiant"]))
def _(s):
    s.heal("Blood Pulse", "At the start of each round, the heart beats: Vampyr or Strahd (whichever is closer, within 120 feet) regains hit points.", "2d8+4", act=SPECIAL, ic="ab-heal")
    s.trait("Dark Power Anchor", "Destroying a Blood Heart severs one active Covenant Hook or reduces Vampyr Claim by 1. Artifact sunlight deals double damage to it.", "ab-construct")
    s.trait("Object", "The heart doesn't move. It is destroyed at 0 hit points and can't be healed.", "ab-construct")


# ---------------------------------------------------------------- Vallaki and allies
@define("cu.actor.vallaki-vampyr-cult", system=sysp(saves=("con", "cha"), skills={"dec": 6, "rel": 3, "prc": 4}, senses={"darkvision": 60}, dr=["necrotic"], langs=("common",), alignment="chaotic evil"))
def _(s):
    s.multi("The zealot makes two Blood Knife attacks, or one Blood Knife attack and uses Open the Vein.")
    s.atk("Blood Knife", 7, "1d6+4+2d6", "piercing/necrotic", desc="A ritual blade fed by willing or stolen blood.", ic="ab-blade")
    s.sv("Open the Vein", "con", 15, "One creature within 30 feet bleeds mystically.", spec="4d8", types="necrotic", ic="ab-tusk")
    s.util("Martyr of Wachter", "When first reduced below half its hit points, the zealot moves up to its speed toward an ally, hostage or blood sigil without provoking opportunity attacks.", act=REACT("First reduced below half hit points"), per=1, ic="ab-slip")
    s.trait("Blood Answered", "The cult is no longer symbolic: <em>detect magic</em> shows an active external vampiric resonance tied to offered blood. A zealot reduced to 0 hit points within 10 feet of a blood sigil rises at the end of the round with 10 hit points, once.", "ab-will")


@define("cu.actor.vallaki-orcus-cult", system=sysp(saves=("con", "wis"), skills={"itm": 5, "rel": 4, "prc": 5}, senses={"darkvision": 60}, dr=["necrotic"], langs=("common", "abyssal"), alignment="chaotic evil"))
def _(s):
    s.multi("The apostle makes two Bone Maul attacks, or one Bone Maul attack and rings the Grave Bell.")
    s.atk("Bone Maul", 7, "2d6+4+2d6", "bludgeoning/necrotic", desc="A maul built around relic-bone and grave iron.", ic="ab-hammer")
    s.sv("Grave Bell", "wis", 15, "Each creature of the apostle's choice within 20 feet hears a bell from beneath the earth. On a failure a creature is also frightened until the end of its next turn.", spec="3d8", types="necrotic", tmpl=("radius", 20), ic="ab-roar")
    s.util("Stand, Witness", "A corpse within 30 feet rises as a zombie (use the SRD zombie) under the apostle's command, or as an inert omen that grants the apostle advantage on its next attack. No spell is cast: something answers.", per=1, ic="ab-will")
    s.trait("Death Answered", "The cult's rites now get an active necromantic response. While a corpse is within 30 feet, the apostle has advantage on saving throws against being frightened and on death saving throws.", "ab-will")


@define("cu.actor.arl", system=sysp(saves=("dex", "con", "wis"), skills={"arc": 10, "dec": 12, "ins": 10, "itm": 12, "prc": 10}, senses={"truesight": 120, "darkvision": 120},
                                    di=["fire", "poison"], dr=["cold"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks that aren't Silvered", ci=["poisoned"],
                                    langs=("infernal", "common"), lang_custom="telepathy 120 ft.", alignment="lawful evil", fly=60), token_size=2, disposition=1)
def _(s):
    s.multi("Arl makes two Infernal Glaive attacks.")
    s.atk("Infernal Glaive", 11, "2d10+7+3d8", "slashing/fire", reach=10, desc="Against Orcus or an undead manifestation, one hit each turn deals an extra 9 (2d8) force damage.", ic="ab-spear")
    s.sv("Hellchain", "str", 18, "One target within 30 feet is bound by an infernal chain. On a failure it is also restrained until the end of Arl's next turn. Against Orcus, a failed save also stops Horned Advance until the end of Arl's next turn.", spec="3d8", types="fire/force", recharge_=5, ic="ab-chain")
    s.sv("Ordered Inferno", "dex", 18, "A 30-foot cone or a 20-foot-radius burst within 60 feet. Arl can exclude any members of the Unkindness: the contract requires mutual non-harm.", spec="6d8", types="fire", tmpl=("cone", 30), ic="ab-bomb")
    s.util("Break the Corrupt Gate", "Arl destroys a mundane or lesser magical barrier, or holds one Dark Power front for one pressure check.", per=1, ic="ab-pick")
    s.trait("Fear Aura", "Any creature hostile to Arl (never the Unkindness) that starts its turn within 20 feet of him must succeed on a DC 21 Wisdom saving throw or be frightened until the start of its next turn.", "ab-roar")
    s.trait("Magic Resistance", "Arl has advantage on saving throws against spells and other magical effects.", "ab-shield")
    s.trait("Infernal Contract — Mutual Non-Harm", "Arl and the Unkindness can't intentionally harm one another while the Ravenloft contract is in force. It binds both sides.", "ab-scroll")
    s.trait("Recognition, Not Future Service", "The party refused to owe a future favour. Arl is paid in truthful written recognition that his help materially aided Strahd's defeat. No souls and no service are owed.", "ab-scroll")
    s.trait("Priority: Orcus", "Once Orcus manifests, Arl treats him as the most offensive corruption on the field and focuses him unless the players direct otherwise.", "ab-command")


@define("cu.actor.van-richten", system=sysp(saves=("con", "int", "wis"), skills={"arc": 11, "his": 11, "ins": 11, "inv": 11, "med": 11, "rel": 11, "prc": 8}, langs=("common", "abyssal", "elvish", "infernal"), alignment="lawful good"), disposition=1)
def _(s):
    s.atk("Hunter's Shot", 8, "2d8+4+2d6", "piercing/radiant", rng=80, kind="ranged", desc="A prepared anti-undead shot. Van Richten isn't meant to join the castle assault; this profile is for Vallaki violence reaching his workshop.", ic="ab-bolt")
    s.atk("Silvered Rapier", 6, "1d8+3", "piercing", desc="Counts as silvered and magical.", ic="ab-blade")
    s.util("Monster Hunter's Diagnosis", "Van Richten names one visible undead or fiend's weakness, anchor, regeneration condition, or escape method that has already been shown in play. The next attack against it by an ally who heard him has advantage.", ic="ab-scroll")
    s.heal("Emergency Field Medicine", "One creature within 5 feet is stabilized and regains hit points from prepared reagents.", "3d8+5", per=1, ic="ab-medic")
    s.trait("The Locks Are Open", "Van Richten knows the Amber Temple's broken prisons changed Barovia's magic: cult symbols are now being answered by something outside them.", "ab-scroll")
    s.trait("Not Omniscient", "He can infer anchors, inheritance and Wish-scale magic, but can't prove the rules until Orcus or Vampyr shows them by reconstituting.", "ab-will")


@define("cu.actor.saraphene", system=sysp(saves=("dex", "wis", "cha"), skills={"acr": 9, "dec": 8, "ins": 6, "ste": 9}, senses={"darkvision": 120},
                                          dr=["necrotic"], dr_custom="Bludgeoning, Piercing, and Slashing from Nonmagical Attacks", langs=("common", "elvish"), alignment="neutral evil"), disposition=0)
def _(s):
    s.multi("Saraphene makes two Shadow Blade attacks.")
    s.atk("Shadow Blade", 9, "1d8+5+3d6", "piercing/necrotic", desc="She has asked not to fight the Unkindness.", ic="ab-blade")
    s.util("Fey Step (Shadow)", "Saraphene teleports up to 30 feet to an unoccupied space she can see; until the start of her next turn she is heavily obscured by shadow.", act=BONUS(), per=1, ic="ab-slip")
    s.util("Mist Escape", "Saraphene turns to mist and withdraws from the scene, unless artifact sunlight is on her.", per=1, ic="ab-vent")
    s.util("Court Gossip", "If she reappears, she reveals one current argument, patrol change, or bride's fear inside Ravenloft instead of fighting.", act=SPECIAL, ic="ab-ledger")
    s.trait("Survival First", "Saraphene hates Strahd and wants to survive. She isn't good and never claimed to be.", "ab-will")
    s.trait("Shadowfell Origin", "Shadar-kai before her turning; she has served Strahd for about eighty years.", "ab-will")
    bride_common(s)


CR_FIX = {  # objects and allies whose listed CR overstated what they can do (DMG method)
    "cu.actor.pylon": 0.5, "cu.actor.chain.blood": 1, "cu.actor.chain.stone": 1, "cu.actor.chain.dominion": 1,
    "cu.actor.coffin": 0, "cu.actor.anchor.orcus": 2, "cu.actor.anchor.vampyr": 1, "cu.actor.van-richten": 5, "cu.actor.arl": 15}


def build():
    import spellbooks as SB
    d = json.load(open(DATA))
    n_items = 0
    for a in d["actors"]:
        sid = a["sourceId"]
        if sid not in DEFS:
            raise SystemExit(f"no stat block for {sid}")
        fn, sp, tsize, disp = DEFS[sid]
        s = S(sid)
        fn(s)
        if sid in SB.SPELLBOOKS:
            bk = SB.SPELLBOOKS[sid]
            s.trait("Spellcasting", bk["note"] + " The spells are on the Spells tab (added at setup from the dnd5e compendiums).", "ab-scroll")
            sp["attributes"] = {**sp.get("attributes", {}), "spellcasting": bk["ability"]}
            sp["details"] = {**sp.get("details", {}), "spellLevel": bk["level"]}
        _sz = {"large": "lg", "medium": "med", "small": "sm"}.get(a["system"].get("traits", {}).get("size"), a["system"].get("traits", {}).get("size"))
        _sys = {"attributes": {"hp": dict(a["system"]["attributes"]["hp"])}, "abilities": a["system"]["abilities"], "traits": {"size": _sz or "med"}}
        hp_formula(_sys)
        sp["attributes"] = {**sp.get("attributes", {}), "hp": {**a["system"]["attributes"]["hp"], **_sys["attributes"]["hp"]}}
        if sid in CR_FIX:
            sp["details"] = {**sp.get("details", {}), "cr": CR_FIX[sid]}
        a["items"] = s.items
        n_items += len(s.items)
        # deep-merge the system additions
        def merge(dst, src):
            for k, v in src.items():
                if isinstance(v, dict) and isinstance(dst.get(k), dict):
                    merge(dst[k], v)
                else:
                    dst[k] = v
        merge(a["system"], sp)
        if a["system"]["traits"].get("size") == "large":
            a["system"]["traits"]["size"] = "lg"
        a["prototypeToken"] = {"width": tsize or {"med": 1, "sm": 1, "large": 2, "lg": 2, "huge": 3}.get(a["system"]["traits"].get("size"), 1),
                               "height": tsize or {"med": 1, "sm": 1, "large": 2, "lg": 2, "huge": 3}.get(a["system"]["traits"].get("size"), 1),
                               "disposition": disp, "displayName": 20, "displayBars": 20, "bar1": {"attribute": "attributes.hp"}}
        a.pop("features", None)
        body = json.dumps({k: v for k, v in a.items() if k != "sourceHash"}, sort_keys=True)
        a["sourceHash"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    json.dump(d, open(DATA, "w"), ensure_ascii=False, indent=1)
    return len(d["actors"]), n_items


if __name__ == "__main__":
    print(build())
