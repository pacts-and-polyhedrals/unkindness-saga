"""Every creature and NPC in The Shield Between Us as a dnd5e NPC actor with working activities.

Combat numbers follow Appendix A of the adventure plan where a profile exists (troopers, wardens,
shock troopers, sappers, tunnel captains, Baldrik, Hadrik, Korga and the Bastion Engine). The other
cast members keep the v0.1 module's numbers, with their damage types corrected.
"""
from lib5e import *

ACT = activation
BONUS = lambda c="": activation("bonus", 1, c)
REACT = lambda c="": activation("reaction", 1, c)
LEG = lambda n=1: activation("legendary", n)
SPECIAL = activation("special", None)

FOLDERS = {}


def P(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


def parse_dice(s):
    """'2d8+5' -> (2, 8, '5')."""
    import re
    m = re.match(r"(\d+)d(\d+)\s*([+-]\s*\d+)?", s.replace(" ", ""))
    return int(m.group(1)), int(m.group(2)), (m.group(3) or "").replace("+", "")


class B:
    """Small builder for one actor's embedded items."""

    def __init__(self, key):
        self.key, self.items, self.n = key, [], 0

    def _k(self, name):
        self.n += 1
        return f"{self.key}-{self.n}-{slug(name)}"

    def multi(self, text):
        k = self._k("multiattack")
        self.items.append(feat(k, "Multiattack", P(text), img=icon("ab-multi"), activities=[utility(k, 0)]))
        return self

    def attack(self, name, to_hit, dice, dtype, *, reach=5, range_=None, extra=None, ic="ab-blade", desc="", kind="melee",
               act=None, consumption=None, uses_=None):
        k = self._k(name)
        n, d, b = parse_dice(dice)
        parts = [dmg(n, d, b, [dtype])]
        if extra:
            en, ed, eb = parse_dice(extra[0])
            parts.append(dmg(en, ed, eb, [extra[1]]))
        rng_txt = f"reach {reach} ft." if not range_ else f"range {range_} ft."
        dmg_txt = f"{dice} {dtype}" + (f" plus {extra[0]} {extra[1]}" if extra else "")
        body = P(f"<em>{'Melee' if kind == 'melee' else 'Ranged'} Weapon Attack:</em> +{to_hit} to hit, {rng_txt}, one target. "
                 f"<em>Hit:</em> {dmg_txt} damage." + (f" {desc}" if desc else ""))
        a = attack(k, 0, to_hit=to_hit, kind=kind, parts=parts, reach=reach, range_=range_, act=act, consumption=consumption)
        self.items.append(feat(k, name, body, img=icon(ic), activities=[a], uses_=uses_))
        return self

    def save(self, name, ability, dc, desc, *, dice=None, dtype=None, ic="ab-burst", act=None, uses_=None, on_save="half",
             tgt=None, consumption=None, effects=None):
        k = self._k(name)
        parts = []
        if dice:
            n, d, b = parse_dice(dice)
            parts = [dmg(n, d, b, [dtype])]
        a = save(k, 0, ability=ability, dc=dc, parts=parts, on_save=on_save if dice else "none", act=act, tgt=tgt,
                 consumption=consumption, effects=effects)
        self.items.append(feat(k, name, P(desc), img=icon(ic), activities=[a], uses_=uses_, effects=effects and [] or None))
        return self

    def feature(self, name, desc, *, ic="ab-fist", act=None, uses_=None, consumption=None, heal=None, temp=False):
        k = self._k(name)
        if heal:
            acts_ = [heal_act(k, 0, formula_part=dmg_formula(heal), act=act or ACT(), tgt=target(1, "creature"), temp=temp,
                              consumption=consumption)]
        elif act:
            acts_ = [utility(k, 0, act=act, consumption=consumption)]
        else:
            acts_ = []
        self.items.append(feat(k, name, P(desc) if not desc.startswith("<") else desc, img=icon(ic), activities=acts_, uses_=uses_))
        return self

    def legres(self, n):
        k = self._k("legres")
        self.items.append(feat(k, f"Legendary Resistance ({n}/Day)", P("If this creature fails a saving throw, it can choose to succeed instead."),
                               img=icon("ab-legendary"), activities=[utility(k, 0, act=SPECIAL, consumption=consume_legres())]))
        return self


def per_enc(n=1):
    return uses(n, [{"period": "sr", "type": "recoverAll", "formula": ""}])


def per_day(n=1):
    return uses(n, ["day"])


def creature(folder, key, name, *, cr, ac, hp, abilities, b, ctype="humanoid", subtype="dwarf", size="med", speed=25,
             saves=(), skills=None, langs=("common",), lang_custom="", senses=None, bio="", legact=0, legres=0,
             disposition=0, di=(), ci=(), dr=(), tsize=None, alignment=""):
    a = npc(key, name, img=portrait(key), token=tok(key), size=size, ctype=ctype, subtype=subtype, cr=cr, ac=ac,
            ac_calc="flat", hp=hp, speed=speed, abilities=abilities, saves=saves, skills=skills, langs=langs,
            lang_custom=lang_custom, senses=senses or {"darkvision": 60}, bio=bio, items=b.items, legact=legact,
            legres=legres, disposition=disposition, di=di, ci=ci, dr=dr, tsize=tsize, alignment=alignment,
            flags={MOD: {"key": key}})
    FOLDERS.setdefault(folder, []).append(a)
    return a


def bio(role, want, line, extra=""):
    return (f'<div class="il-dossier"><p><strong>Role.</strong> {role}</p><p><strong>Wants.</strong> {want}</p>'
            f'<blockquote class="il-line">“{line}”</blockquote>{P(extra) if extra else ""}</div>')


FAM, AUTH, CINDER, OPP, CIV = "The Ironfist Family", "Ironfist Authorities", "The Cinder-Tusk Clan", "Opposition & Encounter Profiles", "Civilians & Messengers"
DW = ("common", "dwarvish")
OR = ("common", "orc", "goblin")

# =========================================================================== the family
creature(FAM, "baldrik", "Baldrik Ironfist", cr=9, ac=20, hp=170, abilities=(20, 12, 18, 10, 14, 14), saves=("str", "con", "wis"),
         skills={"ath": 1, "prc": 1}, langs=DW, disposition=0,
         b=B("baldrik").multi("Baldrik makes two Warhammer attacks.")
         .attack("Warhammer", 9, "2d8+5", "bludgeoning", ic="ab-hammer")
         .feature("Hold With Me", "Bonus Action. One willing ally within 10 feet gains advantage on its next attack roll before the start of Baldrik's next turn.", ic="ab-rally", act=BONUS())
         .feature("The Old Shield", "Reaction. When an adjacent willing ally takes damage, Baldrik reduces it by 2d8 + 4. The two-rivet shield takes the blow. Protecting someone is a visible choice; no feature forces Thorgrinn to trust him or stay close.", ic="ab-shield", act=REACT("An adjacent willing ally takes damage"))
         .feature("Second Wind", "Bonus Action, once per encounter. Baldrik regains 25 hit points.", ic="ab-heal", act=BONUS(), heal="25", uses_=per_enc(1), consumption=consume_item_uses())
         .feature("Vanguard Captain", "Baldrik coordinates disciplined Ironfist soldiers. He has no supernatural authority over civilians or player characters. He surrenders, retreats or accepts disarmament according to his current convictions.", ic="ab-command"),
         bio=bio("Vanguard captain; Thorgrinn's brother. A scar crosses his eyebrow; bronze clasps hold his iron-grey beard; the repaired two-rivet shield never leaves him.",
                 "His brother alive, respected and close — but he confuses protection with deciding for him. He knows he signed an unjust report; he does not yet know Last Bastion will drown Lowhearth.",
                 "I saw you dead. I had not decided what to say at your grave."))

creature(FAM, "heddra", "Aunt Heddra Ironfist", cr=1, ac=13, hp=42, abilities=(13, 10, 16, 12, 15, 14), langs=DW, disposition=1,
         b=B("heddra").attack("Handaxe", 4, "1d6+2", "slashing", ic="ab-axe")
         .feature("Household Authority", "Among Lowhearth households, Heddra can usually secure a hearing, shelter, food or a messenger without a roll unless doing so creates serious danger.", ic="ab-kitchen")
         .feature("Kitchen Remedy", "Action. One creature Heddra can touch regains 2d4 + 3 hit points from broth, bandage and scolding.", ic="ab-heal", act=ACT(), heal="2d4+3", uses_=per_day(2), consumption=consume_item_uses())
         .feature("Get Behind Me", "Reaction when a creature within 5 feet of Heddra is attacked: she imposes disadvantage on that attack roll (she must be able to see the attacker).", ic="ab-shield", act=REACT("An ally within 5 feet is attacked")),
         bio=bio("Lower-tier household steward; keeps the communal kitchen and the family accounts. No military rank.",
                 "The family reunited without surrendering its conscience. She took Baldrik's money for repairs and food and hates that it let her avoid asking how it was earned.",
                 "I am glad you came home. That does not mean I am glad about everything we did while you were gone."))

creature(FAM, "runa", "Runa Ironfist", cr=5, ac=16, hp=88, abilities=(12, 14, 16, 18, 14, 12), skills={"arc": 1, "inv": 2},
         langs=DW, disposition=1,
         b=B("runa").attack("Runic Hammer", 7, "1d8+4", "bludgeoning", extra=("1d6", "force"), ic="ab-hammer")
         .attack("Rune Bolt", 8, "2d8+4", "force", range_="60", kind="ranged", ic="ab-gauge")
         .feature("Pressure Ward", "Reaction. Reduce damage to an adjacent creature or mechanism by 1d10 + 4.", ic="ab-shield", act=REACT())
         .feature("Master Engineer", "Advantage on checks concerning pumps, pressure networks, dwarven engineering and runic mechanisms. She examines Thorgrinn only by invitation.", ic="ab-tools"),
         bio=bio("Heddra's adult daughter, a junior military engineer. Precise speech; soot-stained sleeves beneath a newly issued rank sash.",
                 "The mechanism repaired and her work recognised. She designed a valve; Hadrik bypassed its safeguards; she hid her calculations to protect the family's advancement.",
                 "I did not build a weapon. I built a valve. Then somebody decided the difference was paperwork."))

# =========================================================================== authorities
creature(AUTH, "hadrik", "Marshal-General Hadrik Varr", cr=10, ac=20, hp=180, abilities=(18, 12, 18, 16, 14, 18),
         saves=("con", "wis", "cha"), skills={"ins": 1, "per": 1}, langs=DW, legact=2, disposition=0,
         b=B("hadrik").multi("Hadrik makes three Command-Blade attacks.")
         .attack("Command-Blade", 9, "2d8+4", "slashing", ic="ab-parry")
         .feature("Redeploy", "Bonus Action. Two willing allies within 30 feet can each use their reaction to move 15 feet.", ic="ab-press", act=BONUS())
         .feature("Parry", "Reaction. Hadrik adds 3 to his AC against one melee attack he can see.", ic="ab-parry", act=REACT("Hit by a melee attack he can see"))
         .feature("Reposition (Legendary, 1)", "Hadrik moves up to 15 feet, provoking opportunity attacks normally.", ic="ab-press", act=LEG(1), consumption=consume_legact(1))
         .attack("Strike (Legendary, 2)", 9, "2d8+4", "slashing", ic="ab-parry", act=LEG(2), consumption=consume_legact(2), desc="Costs 2 legendary actions.")
         .feature("Politics, Not Immunity", "Hadrik uses cover, allies and negotiation. At 35 hit points without loyal support he offers surrender, evidence or resignation. His political threats cannot magically control a player character, and a body is not military property.", ic="ab-command"),
         bio=bio("One of three council generals; commands offensive operations. Controlled, generous in public, genuinely convinced coercion preserves civilization.",
                 "Emergency command over all three portfolios, the Cinder-Tusk expelled, and Thorgrinn's reputation attached to the operation. He knows the civilian cost of Last Bastion.",
                 "You understand the cost of hesitation better than most. That is why your people need you beside us."))

creature(AUTH, "brynja", "General Brynja Flintward", cr=9, ac=21, hp=165, abilities=(20, 10, 18, 12, 16, 14), saves=("str", "con"),
         langs=DW, disposition=0,
         b=B("brynja").multi("Brynja makes two Warhammer attacks.")
         .attack("Warhammer", 9, "1d10+5", "bludgeoning", ic="ab-hammer")
         .feature("Defensive Order", "Bonus Action. Up to four allies within 30 feet gain +1 AC until the start of Brynja's next turn while they stay within 5 feet of cover or an ally.", ic="ab-command", act=BONUS())
         .feature("Hold the Line", "Reaction. When an ally within 10 feet would be pushed, knocked prone or moved, Brynja grants advantage on the save or check and may move 5 feet toward them.", ic="ab-shield", act=REACT()),
         bio=bio("Garrison commander. Practical defender with little patience for aristocratic display, still shaped by the caste system.",
                 "A hold that survives and soldiers who obey lawful orders. She needs credible engineering evidence before stopping an active operation.",
                 "Show me the failure point. Then show me who will hold the gate while we change the plan."))

creature(AUTH, "odran", "General Odran Brassmantle", cr=6, ac=17, hp=96, abilities=(12, 14, 16, 16, 16, 18), skills={"ins": 1, "per": 1},
         langs=DW, disposition=0,
         b=B("odran").multi("Odran makes two Cane-Sword attacks.")
         .attack("Cane-Sword", 7, "1d8+3", "piercing", ic="ab-blade")
         .feature("Terms of Engagement", "Once per encounter, Odran forces a one-round pause in hostilities among creatures willing to hear terms. Not mind control: it fails against creatures determined to keep fighting.", ic="ab-ledger", act=ACT(), uses_=per_enc(1), consumption=consume_item_uses()),
         bio=bio("Contracts and provisioning commander. An accountant-soldier who measures promises in wagons and winter rations; not Hadrik's co-conspirator.",
                 "External contracts kept and a defensible settlement. Evidence of concealed liability, lost water and a workable replacement supply plan moves him. A bribe without a plan does not.",
                 "You may be right. Explain how everyone eats after you prove it."))

creature(AUTH, "dagnner", "Sergeant Dagnner", cr=7, ac=19, hp=118, abilities=(18, 12, 16, 12, 14, 13), langs=DW, disposition=0,
         b=B("dagnner").multi("Dagnner makes two Military Hammer attacks.")
         .attack("Military Hammer", 8, "1d8+5", "bludgeoning", ic="ab-hammer")
         .feature("Form Shield Wall", "Bonus Action. Two adjacent allied soldiers gain +2 AC until one moves away or until Dagnner's next turn.", ic="ab-shield", act=BONUS())
         .feature("Interpose", "Reaction. Reduce damage to an adjacent ally by 1d10 + 3.", ic="ab-shield", act=REACT()),
         bio=bio("The severe Vanguard sergeant who examined the party's damage in Barovia and later considered their bounty. Supervises escorts and requisitions; keeps copies of cargo receipts and sealed orders.",
                 "A functioning company and its pay. A protected pension for her troops and proof she'll otherwise be scapegoated may buy cooperation. Her testimony needs corroboration.",
                 "You call it greed. My soldiers call it getting home with wages."))

creature(AUTH, "edda", "Edda, Warden of the Fifth Finger", cr=5, ac=18, hp=92, abilities=(16, 12, 16, 13, 15, 14), langs=DW, disposition=1,
         b=B("edda").multi("Edda makes two Spear attacks.")
         .attack("Spear", 7, "1d8+4", "piercing", ic="ab-spear", desc="Range 20/60 ft. when thrown.")
         .feature("Gate Discipline", "Allied guards within 15 feet have advantage on checks to resist being deceived or rushed through a controlled checkpoint.", ic="ab-fist"),
         bio=bio("Warden of the road fortress three miles from the mist. One job: the gate. One habit: she taps the register twice before she writes in it.",
                 "To correct the death register properly — with witnesses — and to get the stranded supply crew moving.",
                 "Your company was the Neverwinter auxiliary. I remember the patrol pair. I remember the funeral notice too."))

creature(AUTH, "venn", "Venn Stoneclerk", cr=0.25, ac=12, hp=26, abilities=(9, 12, 12, 16, 14, 13), skills={"inv": 1, "his": 1},
         langs=DW, disposition=1,
         b=B("venn").attack("Dagger", 3, "1d4+1", "piercing", ic="ab-blade")
         .feature("Archive Memory", "Advantage on checks to locate an indexed military record or identify a suspicious alteration in a registry. He can testify that he filed E3.", ic="ab-scroll")
         .feature("Cite the Regulation", "Action. Venn quotes the standing order that applies. One officer or guard who can hear him must succeed on a DC 13 Wisdom saving throw or stop and verify the order before acting, losing its next action.", ic="ab-ledger", act=ACT()),
         bio=bio("Records clerk of the military archive. Habit: reads every document twice, aloud, under his breath.",
                 "Not to be the clerk who gets blamed. Protection as a witness makes him brave.",
                 "Archive transfer is due tomorrow. I am only mentioning it."))

# =========================================================================== civilians & messengers
creature(CIV, "yrsa", "Sister Yrsa Coalbraid", cr=6, ac=18, hp=90, abilities=(14, 10, 16, 13, 18, 15), skills={"med": 2, "rel": 1},
         langs=DW, disposition=1,
         b=B("yrsa").multi("Yrsa makes two Forge-Mace attacks.")
         .attack("Forge-Mace", 7, "1d8+4", "bludgeoning", ic="ab-hammer")
         .feature("Coalbraid Benediction", "Action, 3/Day. An adjacent creature regains 2d8 + 4 hit points, or is stabilised and stops being frightened.", ic="ab-medic", heal="2d8 + 4", uses_=per_day(3), consumption=consume_item_uses())
         .feature("Witness of Stone", "Advantage on checks to authenticate oaths, burial records and religious or memorial inscriptions.", ic="ab-scroll"),
         bio=bio("Shrine keeper and veteran medic in Lowhearth. Recognises continuity of personhood through relationships, testimony and the person's own account.",
                 "Care for every wounded body on both sides, and an ethical — consent-based — inquiry if Thorgrinn ever wants one. She cannot promise a return to flesh.",
                 "A body can need work without its inhabitant needing permission to exist."))

creature(CIV, "tovik", "Tovik Deepgauge", cr=2, ac=15, hp=52, abilities=(14, 12, 15, 16, 14, 11), langs=DW, disposition=1,
         b=B("tovik").attack("Work Hammer", 5, "1d6+2", "bludgeoning", ic="ab-pick")
         .feature("Read the Pressure", "Tovik can identify dangerous changes in a visible pump or gauge without a roll; complex sabotage still requires investigation. He carries the dated gauge sheet that begins E1.", ic="ab-gauge")
         .feature("Crew, On Me", "Bonus Action. Up to three Lowhearth workers who can hear Tovik move up to half their speed without provoking opportunity attacks.", ic="ab-rally", act=BONUS())
         .feature("Shore It Up", "Action. Tovik braces a failing pump, door or tunnel section within 5 feet: it can't collapse or burst until the start of his next turn, and a work challenge he takes part in gains 1 progress (once per challenge).", ic="ab-tools", act=ACT()),
         bio=bio("Adult mine foreman at the Ninth Sluice. Habit: counts his crew by name, every time.",
                 "His missing shift brought home, and the complaints about dying wells — filed as 'enemy propaganda' — finally read.",
                 "We filed the complaints. They called them propaganda."))

creature(CIV, "lowhearth-worker", "Lowhearth Worker", cr=0.125, ac=11, hp=11, abilities=(13, 10, 13, 10, 11, 10), langs=DW, disposition=1,
         b=B("lowhearth-worker").attack("Pick", 3, "1d6+1", "piercing", ic="ab-pick")
         .feature("Shift Roster", "Name every worker. The rescue is about people, not tokens. Sample names: Hild, Borri, Masa, Grenn, Tuvi, Oskar, Yeln, Daga.", ic="ab-scroll"),
         bio=bio("Labourers, cooks, porters and pump crews of Lowhearth.", "Water, wages, and to be counted.", "Two lifts down and nobody up top remembers our names."))

creature(CIV, "cinder-civilian", "Cinder-Tusk Household Member", cr=0.125, ac=11, hp=11, ctype="humanoid", subtype="orc", speed=30,
         abilities=(12, 11, 13, 10, 12, 10), langs=OR, disposition=0,
         b=B("cinder-civilian").attack("Knife", 3, "1d4+1", "piercing", ic="ab-blade")
         .feature("Household", "Orc and goblin families of the Warrens. Neither ancestry predicts loyalty. Sample names: Gashra, Tiv, Morg, Ezzi, Ulka, Snark, Hura, Pell.", ic="ab-lantern"),
         bio=bio("Displaced households of the Cinder Warrens.", "Clean wells, safe homes and the return of prisoners.", "Korga does not speak for my kitchen."))

creature(CIV, "ironfist-courier", "Ironfist Courier", cr=0.125, ac=12, hp=9, abilities=(10, 14, 10, 11, 12, 11), langs=DW, disposition=1,
         b=B("ironfist-courier").attack("Shortsword", 4, "1d6+2", "piercing", ic="ab-blade")
         .feature("Fast Legs", "Couriers reach Kharad-Varr before a party that sleeps at the Fifth Finger. Bonus Action: Dash or Disengage.", ic="ab-slip", act=BONUS()),
         bio=bio("Messengers who run the nine miles of military road.", "To deliver the dispatch and get paid.", "Sealed orders for the captain. Don't ask me what's in them."))

# =========================================================================== Cinder-Tusk
creature(CINDER, "korga", "Korga Emberjaw", cr=11, ac=18, hp=220, ctype="humanoid", subtype="orc", speed=30,
         abilities=(22, 14, 20, 12, 14, 16), saves=("str", "con", "wis"), skills={"ath": 1, "prc": 1}, langs=OR, legact=2,
         disposition=-1,
         b=B("korga").multi("Korga makes three Ember Cleaver attacks.")
         .attack("Ember Cleaver", 10, "2d10+6", "slashing", ic="ab-cleaver")
         .save("Breaking Roar", "wis", 17, "Recharge 5–6. Each enemy in a 15-foot cone that can hear Korga must succeed on a DC 17 Wisdom saving throw or be frightened of him until the end of his next turn.",
               ic="ab-roar", uses_=uses(1, [recharge(5)]), consumption=consume_item_uses(), tgt=target("", "enemy", "cone", 15))
         .feature("Brace", "Reaction. Korga reduces one instance of damage by 1d10 + 5.", ic="ab-brace", act=REACT())
         .feature("Unbroken Will (2/Encounter)", "When Korga fails a saving throw, he can succeed instead by taking 20 damage that can't be reduced. Describe the visible cost so the players know their effect mattered.", ic="ab-will", act=SPECIAL, uses_=per_enc(2), consumption=consume_item_uses())
         .feature("Reposition (Legendary, 1)", "Korga moves up to 15 feet, provoking opportunity attacks normally.", ic="ab-press", act=LEG(1), consumption=consume_legact(1))
         .attack("Cleave (Legendary, 2)", 10, "2d10+6", "slashing", ic="ab-cleaver", act=LEG(2), consumption=consume_legact(2), desc="Costs 2 legendary actions.")
         .feature("Last Argument", "Korga fights to preserve his command and extract concessions. At half hit points he seeks a better position; at 40 hit points with no supporters and a viable surrender offer, he can yield.", ic="ab-tusk"),
         bio=bio("Orc war-chief of the Cinder-Tusk. An effective tunnel commander who treats the diversion as proof coexistence is impossible — and who has turned defence into conquest.",
                 "The upper reservoir, the foundry gates and political dominance. Respects enforceable power and concrete terms, not one charming speech.",
                 "When they took our water it was policy. When we take their gates it is savagery. Explain the difference without lying to me."))

creature(CINDER, "urzha", "Urzha Deepwell", cr=5, ac=17, hp=100, ctype="humanoid", subtype="orc", speed=30, abilities=(17, 12, 18, 14, 17, 16),
         skills={"per": 1, "ins": 1}, langs=OR, disposition=0,
         b=B("urzha").multi("Urzha makes two Longspear attacks.")
         .attack("Longspear", 7, "1d10+4", "piercing", reach=10, ic="ab-spear")
         .feature("Hold the Truce", "Allies who can hear Urzha have advantage on the first check to avoid escalating a negotiation into violence, provided she is actively arguing for restraint.", ic="it-compact"),
         bio=bio("Orc civilian speaker; former caravan negotiator, responsible for the displaced households.",
                 "Water, secure homes, the return of prisoners and accountability on both sides. She will not accept peace bought with a massacre of her own people.",
                 "You can stop a war without telling me the dead were a misunderstanding."))

creature(CINDER, "skrik", "Skrik Coilhand", cr=5, ac=16, hp=78, ctype="humanoid", subtype="goblin", size="sm", speed=30,
         abilities=(10, 18, 14, 18, 14, 13), skills={"inv": 1, "arc": 1}, langs=OR, disposition=0,
         b=B("skrik").multi("Skrik makes two Coilknife attacks or one Pressure Bolt.")
         .attack("Coilknife", 7, "1d6+4", "piercing", ic="ab-blade")
         .attack("Pressure Bolt", 8, "2d8+4", "force", range_="60", kind="ranged", ic="ab-gauge")
         .feature("Remote Bleed Valve", "Once per short rest, Skrik manipulates a visible pressure mechanism within 30 feet as though adjacent, if he has studied its controls.", ic="ab-tools", act=ACT(), uses_=per_enc(1), consumption=consume_item_uses())
         .save("Flash Charge", "dex", 16, "Each creature in a 10-foot-radius sphere centred within 30 feet takes 4d6 thunder damage on a failed DC 16 Dexterity save, or half as much on a success.",
               dice="4d6", dtype="thunder", ic="ab-bomb", uses_=per_enc(1), consumption=consume_item_uses(), tgt=target("", "creature", "sphere", 10)),
         bio=bio("Goblin engineer who runs the clan's pumps. Organised sabotage and rescue work both; owns the lift sabotage that injured dwarven workers.",
                 "Mutual access to the regulators and binding limits on unilateral diversion. He needs Runa's upper-system calculations; she needs his lower maps.",
                 "Your map ends where our homes begin. That is the first mistake."))

creature(CINDER, "brakk", "Brakk Ash-Tusk (Tunnel Captain)", cr=7, ac=18, hp=125, ctype="humanoid", subtype="orc", speed=30,
         abilities=(18, 14, 16, 12, 14, 14), saves=("str", "con", "wis"), skills={"prc": 1}, langs=OR, disposition=-1,
         b=B("brakk").multi("The captain makes three blade attacks.")
         .attack("Tunnel Blade", 8, "2d6+4", "slashing", ic="ab-axe")
         .feature("Rally (1/Encounter)", "Bonus Action. Up to two allies within 30 feet gain 10 temporary hit points and can each use their reaction to move 10 feet.", ic="ab-rally", act=BONUS(), uses_=per_enc(1), consumption=consume_item_uses())
         .feature("Punish an Opening", "Reaction. After an adjacent enemy misses the captain with a melee attack, the captain makes one Tunnel Blade attack against it.", ic="ab-blade", act=REACT("An adjacent enemy misses with a melee attack"))
         .feature("Morale", "Keeps a route to retreat and tries to preserve specialists. Surrenders below 25 hit points without effective support if offered a credible way to survive. Use this profile for every tunnel captain and loyalist officer; rename the token.", ic="ab-tusk"),
         bio=bio("Korga's tunnel captain. Struck a surrendered guard at the Ninth Sluice — both of the wounded witnesses' accounts are true.",
                 "The regulator, the gates, and his war-chief's approval.", "Policy took our wells. Steel takes them back."))

creature(CINDER, "ketta", "Ketta Sparkfinger", cr=3, ac=16, hp=54, ctype="humanoid", subtype="goblin", size="sm", speed=30,
         abilities=(9, 18, 14, 16, 13, 12), skills={"ste": 1}, langs=OR, disposition=-1,
         b=B("ketta").multi("Ketta makes two Shortblade attacks or one Bolt attack.")
         .attack("Shortblade", 7, "1d6+4", "piercing", ic="ab-blade")
         .attack("Bolt", 7, "1d8+4", "piercing", range_="80/320", kind="ranged", ic="ab-bolt")
         .save("Thunder Charge", "dex", 16, "Recharge 5–6. Ketta throws a visible charge to a space within 30 feet. At the start of her next turn it bursts: each creature within 10 feet takes 3d6 thunder damage (DC 16 Dexterity half). Before then, an adjacent creature can use an action to throw it 20 feet or disable it with a DC 16 tools check.",
               dice="3d6", dtype="thunder", ic="ab-bomb", uses_=uses(1, [recharge(5)]), consumption=consume_item_uses(), tgt=target("", "creature", "sphere", 10)),
         bio=bio("Goblin sapper who can be captured or recruited. Habit: names every charge she builds.",
                 "To get home with all her fingers — and to know whether the bridge she was told to blow fed her own family.",
                 "Cut the blue one. No — the OTHER blue one."))

# =========================================================================== encounter profiles (Appendix A)
creature(OPP, "ironfist-trooper", "Ironfist Trooper", cr=2, ac=17, hp=32, abilities=(16, 10, 14, 10, 12, 10), saves=("str", "con"),
         skills={"prc": 1}, langs=DW, disposition=0,
         b=B("ironfist-trooper").multi("The trooper makes two Spear attacks.")
         .attack("Spear", 6, "1d8+3", "piercing", ic="ab-spear", desc="Range 20/60 ft. when thrown.")
         .feature("Cover a Comrade", "Reaction. Add 2 to the AC of one adjacent willing ally against one visible attack, possibly causing it to miss. Doesn't stack with another trooper's use against the same attack.", ic="ab-shield", act=REACT())
         .feature("Morale", "Holds an assigned lane; doesn't chase a lone PC away from the objective. Surrenders when isolated, lawfully relieved or clearly abandoned.", ic="ab-fist"),
         bio=bio("Ordinary Ironfist soldier.", "To hold the lane and get home.", "Orders say hold. We hold."))

creature(OPP, "shield-warden", "Ironfist Shield Warden", cr=5, ac=19, hp=85, abilities=(20, 10, 18, 10, 12, 12), saves=("str", "con", "wis"),
         skills={"prc": 1}, langs=DW, disposition=0,
         b=B("shield-warden").multi("The warden makes two Hammer attacks.")
         .attack("Hammer", 8, "1d8+7", "bludgeoning", ic="ab-hammer")
         .save("Shield Press", "str", 16, "Bonus Action, after hitting a creature with the Hammer this turn. The target must succeed on a DC 16 Strength saving throw or be pushed 5 feet or knocked prone (warden's choice).",
               ic="ab-shield", act=BONUS("After a Hammer hit"), tgt=target(1, "creature"))
         .feature("Interpose", "Reaction. Reduce damage to one adjacent willing ally by 1d10 + 3, provided the warden sees the attacker.", ic="ab-shield", act=REACT())
         .feature("Morale", "Protects doors, wounded soldiers and records. Two wardens don't fight to the death for a discredited officer when given lawful orders and safe surrender.", ic="ab-fist"),
         bio=bio("Heavy Ironfist guard of doors, archives and wounded.", "Lawful orders.", "Not one step closer to the cabinet."))

creature(OPP, "vanguard-officer", "Righteous Vanguard Officer", cr=5, ac=19, hp=85, abilities=(18, 12, 16, 12, 14, 14), saves=("str", "con", "wis"),
         langs=DW, disposition=-1,
         b=B("vanguard-officer").multi("The officer makes two Hammer attacks.")
         .attack("Hammer", 7, "1d8+5", "bludgeoning", ic="ab-hammer")
         .feature("Conflicting Orders", "The redoubt's duty officer holds the release key. He can surrender or bargain; authentic orders, Baldrik's authority, evidence of the purge or Dagnner's signal can make him an ally.", ic="it-key"),
         bio=bio("Duty officer of the Vanguard Redoubt; holds the Heartworks release key.", "To survive the order he can't verify.", "I have two orders on my desk and both have seals."))

creature(OPP, "shock-trooper", "Cinder-Tusk Shock Trooper", cr=5, ac=17, hp=78, ctype="humanoid", subtype="orc", speed=30,
         abilities=(20, 12, 16, 10, 12, 12), saves=("str", "con"), skills={"prc": 1}, langs=OR, disposition=-1,
         b=B("shock-trooper").multi("The trooper makes two Heavy Axe attacks.")
         .attack("Heavy Axe", 8, "2d8+5", "slashing", ic="ab-axe")
         .feature("Press the Line", "Bonus Action. Move up to 15 feet toward a visible hostile creature (provoking normally). If the trooper then hits that creature this turn, the first hit deals an extra 1d6 damage.", ic="ab-press", act=BONUS())
         .feature("Morale", "Clears a route for engineers. Retreats when the mission is impossible and a safe withdrawal exists. Can represent any trained heavy fighter — orc, dwarf or goblin.", ic="ab-tusk"),
         bio=bio("Heavy infantry of Korga's war.", "To open the route for the sappers.", "Shields up. Axes down. Move."))

creature(OPP, "goblin-sapper", "Goblin Sapper", cr=3, ac=16, hp=40, ctype="humanoid", subtype="goblin", size="sm", speed=30,
         abilities=(10, 18, 14, 16, 12, 10), saves=("dex", "int"), skills={"ste": 1}, langs=OR, disposition=-1,
         b=B("goblin-sapper").multi("The sapper makes two Shortblade attacks or one Bolt attack.")
         .attack("Shortblade", 7, "1d6+4", "piercing", ic="ab-blade")
         .attack("Bolt", 7, "1d8+4", "piercing", range_="80/320", kind="ranged", ic="ab-bolt")
         .feature("Slip Away", "Bonus Action. The sapper takes the Disengage or Hide action.", ic="ab-slip", act=BONUS())
         .save("Thunder Charge", "dex", 16, "Recharge 5–6. Throw a visible charge to a space within 30 feet; it bursts at the start of the sapper's next turn in a 10-foot radius for 3d6 thunder damage (DC 16 Dexterity half). An adjacent creature can use an action to throw it 20 feet or disable it (DC 16 tools).",
               dice="3d6", dtype="thunder", ic="ab-bomb", uses_=uses(1, [recharge(5)]), consumption=consume_item_uses(), tgt=target("", "creature", "sphere", 10)),
         bio=bio("Cinder-Tusk combat engineer.", "Controls first, fights second.", "Fuse is lit. Move or don't."))

creature(OPP, "battering-engine", "Cinder-Tusk Battering Engine", cr=0, ac=17, hp=80, ctype="construct", subtype="", size="lg",
         speed=15, abilities=(18, 6, 18, 1, 1, 1), langs=(), disposition=-1, di=("poison", "psychic"),
         ci=("charmed", "frightened", "poisoned", "unconscious", "exhaustion"), senses={},
         b=B("battering-engine").feature("Ram Impact", "On initiative 10 each round the crew drives the ram into the gate. Three successful impacts before the end of round 5 breach the Upper Gate.", ic="ab-piston", act=activation("special", None))
         .feature("Haul Chains", "Two exposed haul chains each take one action and a DC 16 Athletics, tools or Arcana check to disable; each removes one attack route. Teleporting or flying behind the engine is effective.", ic="ab-chain"),
         bio=bio("A roofed siege ram escorted up the ramp.", "To reach the Upper Gate.", "—"))

creature(OPP, "bastion-engine", "The Bastion Engine", cr=12, ac=19, hp=250, ctype="construct", subtype="", size="huge", speed=15,
         abilities=(22, 8, 20, 3, 10, 1), saves=("str", "con", "wis"), langs=(), legact=2, disposition=-1,
         di=("poison",), ci=("charmed", "frightened", "poisoned", "unconscious"), senses={"blindsight": 60},
         b=B("bastion-engine").multi("The Engine makes two Piston attacks.")
         .attack("Piston", 10, "3d8+7", "bludgeoning", reach=15, ic="ab-piston")
         .save("Pressure Burst", "dex", 17, "Recharge 5–6. A clearly visible 20-foot cone. Each creature in it takes 6d6 force damage on a failed DC 17 Dexterity saving throw, or half as much on a success.",
               dice="6d6", dtype="force", ic="ab-burst", uses_=uses(1, [recharge(5)]), consumption=consume_item_uses(), tgt=target("", "creature", "cone", 20))
         .save("Telegraphed Vent", "dex", 16, "Lair-style hazard. On initiative 20, mark one 20-by-10-foot strip as hissing. On initiative 20 next round it vents: 3d6 fire damage, DC 16 Dexterity half, then mark a different strip. Never mark every safe route. Stops when the Relief Channel is complete.",
               dice="3d6", dtype="fire", ic="ab-vent", act=activation("lair", 1, "Initiative count 20"), tgt=target("", "creature", "line", 20, 10))
         .feature("Crawl (Legendary, 1)", "The Engine moves 10 feet.", ic="ab-construct", act=LEG(1), consumption=consume_legact(1))
         .attack("Piston (Legendary, 2)", 10, "3d8+7", "bludgeoning", reach=15, ic="ab-piston", act=LEG(2), consumption=consume_legact(2), desc="Costs 2 legendary actions.")
         .feature("Locked Instruction", "A mindless maintenance guardian following locked military settings. It contains no captive soul — and nothing about it applies to Thorgrinn. Completing all three regulator stations ends its hostile state. Destroying it does not open the relief channel.", ic="ab-gauge")
         .feature("If Hadrik Also Fights", "Reduce the Engine to 190 hit points and remove its legendary actions; Hadrik uses his normal profile with no additional guards.", ic="ab-command"),
         bio=bio("The Heartworks' maintenance guardian.", "Hold the armed settings.", "—"))

creature(OPP, "pressure-vent", "Marked Vent Strip (Hazard Marker)", cr=0, ac=10, hp=1, ctype="construct", subtype="", size="med",
         speed=0, abilities=(1, 1, 1, 1, 1, 1), langs=(), disposition=-1, senses={},
         b=B("pressure-vent").save("Vent", "dex", 16, "Use this token to mark the hissing 20-by-10-foot strip. It vents on initiative 20 next round for 3d6 fire damage (DC 16 Dexterity half).",
                                  dice="3d6", dtype="fire", ic="ab-vent", tgt=target("", "creature", "line", 20, 10)),
         bio=bio("A token marker for the Bastion Engine's vent hazard.", "—", "—"))

ACTORS = [a for v in FOLDERS.values() for a in v]
