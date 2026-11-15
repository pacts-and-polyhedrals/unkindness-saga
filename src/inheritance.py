"""Shadows Beyond Barovia — the Inheritance of the Mists.

Carries the end-state of the Ravenloft finale (The Cat and the Unkindness) into Ironfist Legacy:
Dark Power Attention, dispositions and final choices, the brides, Finn, Tatyana, Strahd's courtesy,
the Wish, Arl, the prophecies and the Black Road. Adds light rules, per-session Shadow beats keyed to
existing scenes, Dark Gifts that offer shortcuts to routes the adventure already has, and hooks that
lead forward without taking the arc away from Baldrik, Hadrik, Korga and the players.

Single source of truth: the same data builds the journals, items, tables, macros and
module/data/inheritance.json (read by the Inheritance window in main.mjs).
"""
import json, os
from lib5e import *
import items_spells as IS
import misc as MI

HERE = os.path.dirname(__file__)
OUT_JSON = os.path.join(HERE, "..", "module", "data", "inheritance.json")
IMGP = f"modules/{MOD}/assets/shadows/"

POWERS = {
    "orcus": {
        "name": "Orcus", "title": "The Harvest Denied", "img": "orcus", "icon": "sh-orcus", "color": "#1c4a2a",
        "wants": "The ending Barovia denied him: deaths that stay deaths. In Kharad-Varr he notices one thing above all — "
                 "<strong>Last Bastion is a mass death with a schedule.</strong> He did not plan it and cannot cause it. He waits for it the way a farmer waits for rain.",
        "why": "The Unkindness are grave-thieves: soul coins, Legna's return, Exethanter's phylactery, and Thorgrinn, a soul in iron who keeps choosing life. "
               "Every rescue in this arc is a harvest refused.",
        "signs": ["Lantern flames lean towards whoever is closest to dying.", "Thorgrinn's soul coin is cold to the touch for a breath, then warm again.",
                  "Somebody counts under their breath and stops when looked at.", "A pickaxe rings like a funeral bell.",
                  "Green corpse-light in standing water, gone when anyone kneels to look.", "Ash on a windowsill in the shape of a horned hoof.",
                  "Every bird in the Fifth Finger's yard faces the same way: down the mountain.", "A soldier's death-register entry rewrites itself in a hand nobody owns."],
        "rule": ("The Grave-Thief's Toll",
                 "While Orcus is <strong>Reaching</strong> or higher, once per session when a non-player creature dies in the party's presence, Orcus can be heard counting. "
                 "If the party could have prevented that death and chose speed, comfort or advantage instead, Orcus Attention +1.",
                 "While Orcus is <strong>Claiming</strong> or higher, once per session the GM may raise one ordinary dead enemy as a <em>husk</em> at the start of the next round "
                 "(use the original stat block at half hit points, no reactions; radiant damage or a consecrated corpse prevents it). Never raise a named NPC this way.",
                 "Rescuing people the scheme meant to kill — without a Dark Gift — is the most direct way to starve him (see Attention)."),
        "modes": {"vengeful": "Banished at Ravenloft. He hunts: husks and omens cluster around whoever struck the final blow; offers come only as sneers.",
                  "indebted/curious": "Spared. He watches with something like professional interest and offers fair-seeming trades. He keeps his word — exactly.",
                  "claimant": "Bargained with, or Thorgrinn walked the Black Road. He considers something already his and arrives to inspect it.",
                  "unset": "No final choice was recorded. Treat as indebted/curious."},
    },
    "vampyr": {
        "name": "Vampyr", "title": "The First Thirst", "img": "vampyr", "icon": "sh-vampyr", "color": "#5c0f14",
        "wants": "Covenants. Vampyr is the thirst that binds: it feeds on owed protection. Kharad-Varr runs on exactly that — "
                 "<strong>rank sold as safety, commissions that own the commissioned, households classified as support zones.</strong> "
                 "Vampyr did not build the Ironfist system. It finds it delicious.",
        "why": "Thorgrinn smashed its prison and refused the succession. Damien became a vampire to save everyone and escaped it. Finn and Tatyana were taken from it. "
               "The 'metal dwarf' who has no blood still has something it wants to drink.",
        "signs": ["Wine on the high table looks black to anyone carrying a Blood-Debt.", "A signature's ink smells of iron.",
                  "Someone thanks a PC too warmly for a favour that was never done.", "A rivet on the two-rivet shield weeps one red drop and dries.",
                  "A Cinder-Tusk healer's poultice turns dark when it touches a dwarven wound.", "Every lamp in a corridor goes out except the one behind the party.",
                  "A child in Lowhearth draws a sun that is black at the centre.", "Damien wakes thirsty, and the thirst passes before breakfast."],
        "rule": ("Blood-Debt",
                 "While Vampyr is <strong>Reaching</strong> or higher, when a PC accepts protection, payment, rank or a commission under coercion — or signs in blood — Vampyr may lay a "
                 "<strong>Blood-Debt</strong> on them (record it on the Inheritance window; give the item). A creature with a Blood-Debt has disadvantage on saving throws against being "
                 "charmed by anyone it owes, and Vampyr can see through any wound it takes.",
                 "A Blood-Debt ends when it is repaid or released <em>publicly and freely</em>: returning the payment in front of witnesses, refusing the commission at the public roll (5.2), "
                 "or the creditor releasing it. Freely given gifts — Heddra's food, the shield offered without terms — can never become debts.",
                 "Publicly cancelling a debt someone else holds (Dagnner's company, a Lowhearth household's ration debt) is the most direct way to starve it."),
        "modes": {"vengeful": "Banished. It wants the party bound and drained. It lays debts aggressively and turns rescued creditors against them.",
                  "obsessed": "Allowed to withdraw. It is fixated on one PC (default: Thorgrinn; Damien if he bargained) and courts them with gifts that are never free.",
                  "possessive claimant": "Bargained with. It holds a mark on someone and calls it in at the worst moment: a debt due during Last Bastion.",
                  "claimant": "Bargained with. As possessive claimant.",
                  "unset": "No final choice was recorded. Treat as obsessed (Thorgrinn)."},
    },
    "vecna": {
        "name": "Vecna", "title": "The Unwritten Page", "img": "vecna", "icon": "sh-vecna", "color": "#3b1d5a",
        "wants": "Secrets, and who is allowed to write the record. Kharad-Varr's whole war is fought over documents: sealed orders, a signed classification, "
                 "a compact with two copies, <strong>a record nobody gets to edit</strong> (8.4). Vecna finds this the most interesting thing in the mountain.",
        "why": "The Tome of Strahd, the repeated loops, a destroyed lich, Vesper's second vision, any lesser bargain — and if he granted the Wish, a price he is owed.",
        "signs": ["A sentence in a PC's journal that they did not write.", "An eye-shaped water stain on a sealed dispatch.",
                  "A clerk forgets a word mid-sentence and cannot find it again.", "Ink dries before the pen lifts.",
                  "Vesper's divination returns one extra answer to a question nobody asked.", "A locked cabinet in the archive is found open, nothing missing, one page warm.",
                  "A whisper finishes someone's lie for them, more convincingly.", "Every candle in the archive gutters at the same moment, as if something blinked."],
        "rule": ("The Redacted Line",
                 "While Vecna is <strong>Reaching</strong> or higher, whenever the party examines a sealed, redacted or destroyed document, Vecna may offer to supply the missing line. "
                 "What he supplies is true. It is <strong>knowledge, not evidence</strong>: it tells them where to look and who to ask, but it does not authenticate anything before the Stone Council.",
                 "Accepting gives the party the route to one revelation (R1–R5) immediately; the asker gives Vecna a true secret and Vecna Attention +1.",
                 "Putting secrets on the public record — evidence laid before the council or the public roll — is the most direct way to starve him."),
        "modes": {"distant": "He departed Barovia first and simply watches. Use only signs and one whisper per chapter.",
                  "curious": "Something in the finale fascinated him. One offer per chapter, always fair, always priced.",
                  "claimant": "He granted the Borrowed Ending, or holds a lesser deal. The price is live: see the Borrowed Ending item.",
                  "unset": "Treat as distant."},
    },
}

THRESHOLDS = [(0, "Watching", "Signs only (roll the omens table when a scene needs atmosphere). No offers."),
              (3, "Reaching", "One Shadow beat per session from the session guide. One Dark Gift may be offered per chapter. The power's signature rule is active."),
              (6, "Claiming", "Use the Shadow beat in every session. Offers can arrive in combat. The power's second signature clause is active. It names a price out loud before Last Bastion."),
              (9, "Arriving", "An echo of the power is physically present at the climax (8.3) — a voice, a shape in the steam, a hand on the regulator. It never replaces Korga, Hadrik or the Bastion Engine as the opponent. It sets the terms of the epilogue.")]

ATTENTION_UP = [("Accept a Dark Gift", "+1 to +3 (listed on the gift)"), ("Use the active benefit of a Mark", "+1"),
                ("Orcus: let a preventable death happen for speed or advantage", "+1"), ("Vampyr: sign or accept a binding obligation under coercion", "+1"),
                ("Vecna: keep a damaging secret from people it harms", "+1"), ("Seal a treaty or oath in blood", "+1 Vampyr")]
ATTENTION_DOWN = [("Refuse a Dark Gift when it would have cost the party something real to refuse", "−1 (once per power per chapter)"),
                  ("Orcus: evacuate Lowhearth or save the doomed without dark aid", "−1; full Last Bastion success −2"),
                  ("Vampyr: publicly release or repay a debt (yours or another's)", "−1"), ("Vecna: put authenticated evidence on the public record", "−1 (once per chapter)"),
                  ("A fulfilled prophecy invoked against its power", "−1")]

# --------------------------------------------------------------------------- Dark Gifts
GIFTS = {
    "orcus": [
        ("count", "The Count of the Dying", "Orcus speaks the number of the dead if Last Bastion runs — then, slowly, the names. Lowhearth's names.",
         "Reveals <strong>R3</strong> as knowledge: the party knows Lowhearth floods and where to find proof (Runa's bypass sheets, the Heartworks plates). It is not evidence.",
         "+2 Orcus. The asker gains the Death-Mark of the Black Road."),
        ("denied", "Death, Denied", "One person who died in this arc rises at dawn, whole, with a cold soul.",
         "Returns one dead NPC to life without components (a worker, Tovik, a soldier — even Baldrik).",
         "+3 Orcus. The returned person carries the Death-Mark. Orcus takes 'a death of equal weight' later: one Last Bastion pressure stage starts one step worse."),
        ("rider", "The Rider's Night (Thorgrinn only)", "For one night the iron remembers flesh: warmth, taste, the weight of a cup.",
         "Thorgrinn experiences full bodily sensation for one night (Hearthwatch or the Night Before the Horns). No mechanical change to his body.",
         "+3 Orcus; disposition becomes claimant. His soul coin glows green whenever Orcus is near, for the rest of the campaign."),
    ],
    "vampyr": [
        ("owed", "What Is Owed", "Vampyr shows the web of debts in the mountain as threads of red light.",
         "Reveals who owes whom: points straight to <strong>E2</strong> (foundry requisitions) and to Dagnner's duplicate of <strong>E3</strong>.",
         "+2 Vampyr. The asker takes a Blood-Debt."),
        ("bond", "The Bond That Holds", "A chosen NPC's loyalty is made certain.",
         "One NPC (Dagnner, Ketta, a unit of Vanguard soldiers) becomes reliably loyal to one PC for the arc, no check required.",
         "+3 Vampyr. The NPC is blood-bound: their will erodes while Vampyr is Claiming. If discovered, Civilian Accord −1. Directly opposes Bunch's prophecy."),
        ("thirst", "Thirst of Iron", "A weapon learns to drink.",
         "One weapon deals +1d6 necrotic damage and its wielder regains hit points equal to the necrotic dealt, once per turn, until the end of the arc.",
         "+2 Vampyr. The wielder takes a Blood-Debt; Vampyr sees through every wound the weapon makes."),
    ],
    "vecna": [
        ("redacted", "The Redacted Line", "Vecna recites the contents of a sealed or destroyed page.",
         "Gives the full text of one sealed document before it is found (Hadrik's <strong>E5</strong>, Baldrik's <strong>E3</strong>, Odran's ledgers). The paper itself must still be found.",
         "+2 Vecna. The asker gives one true secret, written into Vecna's ledger."),
        ("noedit", "A Record Nobody Can Edit", "Vecna makes one document permanent.",
         "One authenticated document cannot be destroyed, altered or forged for the rest of the campaign (fits 8.4).",
         "+2 Vecna. The holder gains the Whispered Eye: Vecna may look through their senses for one minute at a moment of the GM's choosing."),
        ("step", "The Unwritten Step", "The walls of the mountain become a sentence Vecna can skip.",
         "Once, the party moves between two places they have seen in Kharad-Varr, ignoring doors, wards, guards and distance (e.g. straight into the Heartworks).",
         "+1 Vecna. Each traveller tells Vecna one true secret they have never knowingly given him."),
    ],
}

# --------------------------------------------------------------------------- Session beats (keyed to existing scenes)
BEATS = {
    1: {"orcus": ("s11", "At the edge of the last mist a second road runs beside the stone one — black, smooth, unmarked by hammers — for a hundred yards, then ends at a cairn of rusted soul coins. If Thorgrinn accepted the Black Road, it does not end: it runs on towards the hold.",
                  "Edda's death register (1.2) lists Thorgrinn as dead. A voice only Thorgrinn hears: \"The register is correct.\" → Correcting the register and Hearthwatch (3.5b)."),
        "vampyr": ("s14", "At the feast, the commission Hadrik offers has a signature line marked to be signed 'in the old way'. Nobody at the table can say what that means. Anyone with a Blood-Debt sees the wine as black.",
                   "Damien recognises obligation language when he reads it → inspecting and negotiating the commission (1.4) rather than accepting it."),
        "vecna": ("s12", "The courier's message to Kharad-Varr contains one sentence nobody told Edda: a detail from inside the Barovian loop.",
                  "Who reads couriers' dispatches before the generals do? → Venn Slate, the records clerk, and the military archive (3.2–3.4).")},
    2: {"orcus": ("s16", "The wounded courier is dying on the floor of the side chamber. Orcus offers, conversationally, to count how many in the broken lift still breathe.",
                  "Accepting tells them seven are alive — and starts a quiet clock. → Urgency for 2.1 and 2.3 without any new enemy."),
        "vampyr": ("s15", "When Thorgrinn touches the two-rivet shield, one rivet weeps a single red drop (only if Vampyr is obsessed with him). It cannot hold the shield: it was given freely.",
                   "Baldrik says he 'paid for Heddra's roof'. The debt framing is Vampyr's language in Baldrik's mouth. → Pulling at it leads toward his admission (Baldrik event 1)."),
        "vecna": ("s21", "One wounded soldier remembers everything about the raid except the order he was given. There is a clean blank where it should be. Vecna offers to fill it.",
                  "The order was the 'support households' clause. → Tovik's dated gauge sheet (E1) and the first hint of R2.")},
    3: {"orcus": ("s23", "In Lift Shaft IX the dead workers' tools hang where they fell. If Orcus is Claiming, the first ordinary enemy killed here rises as a husk.",
                  "Naming the dead (Tovik knows them) gives them to Hearthwatch instead of to Orcus. → 3.5b, and Skrik later owning the sabotage."),
        "vampyr": ("s24", "Blood from the fight runs into the poisoned channel and turns black. If Vampyr is Claiming, one 20-foot stretch becomes a Blood Tide zone (difficult terrain; DC 16 Con on entry or 2d8 necrotic).",
                   "Why is the water already poisoned? → The dead fungal samples and flow markers of R1."),
        "vecna": ("s25", "Urzha's dated well records are missing one torn page. Vecna offers it.",
                  "Refusing and asking Urzha instead earns her respect. → R1 through people rather than shadows; the Urzha–Skrik partnership.")},
    4: {"orcus": ("s33", "Runa's calculations include a casualty estimate she could not bring herself to write down. Orcus says the number out loud, in her voice.",
                  "Runa breaks and shows her bypass sheets. → R3 early, through family rather than through the Gift."),
        "vampyr": ("s26", "Baldrik's signature on the classification smells of iron. If Vampyr is a claimant, it glows faintly to anyone carrying a Blood-Debt.",
                   "→ Confronting Baldrik with the signature: his admission (event 1) on the party's terms, not Vampyr's."),
        "vecna": ("s32", "'Three routes to the same lie' gains a fourth that only Vecna can see. This is the natural place to offer the Redacted Line.",
                  "→ E2 and E3; and the cost of knowing first.")},
    5: {"orcus": ("s35b", "At Hearthwatch, after the last name, Orcus keeps reading. The names he reads are not yet dead: Lowhearth families. Only those at Reaching or higher hear it. If Thorgrinn walked the Black Road, his lantern drifts upstream against the current, like the lantern from below.",
                  "This is the strongest R3 omen in the arc. → Evacuation planning; Heddra's kitchen as the centre of it."),
        "vampyr": ("s35", "At Heddra's table there is one extra place set, and nobody remembers setting it. Vampyr has laid it for whoever it wants back (Finn, Tatyana, Damien's old self).",
                   "Heddra's hospitality is freely given; Vampyr cannot sit. Saying so aloud ends the omen. → The family conversation 3.5 is built for."),
        "vecna": ("s36", "The Cinder-Tusk invitation arrives under seal. Before anyone breaks it, a PC with the Whispered Eye already knows what it says.",
                  "Do they pretend not to know when Urzha's courier asks? → Trust with the clan, and Chapter 4.")},
    6: {"orcus": ("s44", "On the 90-foot Pump Bridge, anyone who falls is caught one foot above the 200-foot drop by something cold. They live. They carry the Death-Mark (Orcus +1).",
                  "→ Makes the bridge fight deadly-feeling without being deadlier; the caught PC owes nothing — but Orcus noticed."),
        "vampyr": ("s43", "Korga demands the terms be sealed in blood. If they are, Vampyr Attention +1 and every signatory takes a Blood-Debt to the clan.",
                   "Offer an object instead: the matched compact copies (E4). → 'A treaty is an object, not a feeling' (4.6)."),
        "vecna": ("s42", "The raid was meant to retrieve the clan's copy of the compact. Vecna knows where the dwarven copy is filed, and under what false title.",
                  "→ E4 authentication without the archive break-in.")},
    7: {"orcus": ("s45", "The 'familiar sentence' is the ritual execution Baldrik once wanted to carry out on desperate thieves. Orcus approves of it, warmly.",
                  "→ Baldrik refusing an unlawful order in front of his soldiers (event 2) now means refusing Orcus's applause too."),
        "vampyr": ("s51", "The commission's final clause holds the commissioned's 'body and service' at the council's disposal. Vampyr reads that as ownership — the Sanguine Moon chain all over again. If Finn was freed, he is the one who says it.",
                   "→ Refusing the commission at the public roll, which also breaks any Blood-Debt from 1.4."),
        "vecna": ("s52", "At the public roll Vecna offers to make one name vanish from the record, or appear on it.",
                  "→ Honest registration, or a lie that will be found in 8.4.")},
    8: {"orcus": ("s55", "In the pump galleries' steam, a horned shape stands where the pressure gauges are. Last Bastion is his harvest bell. If Orcus is Claiming, this is where he offers the Count of the Dying.",
                  "→ R3, the controlled inspection, and the turn of the whole arc."),
        "vampyr": ("s53", "Vampyr makes its offer to Baldrik, not to the party: protection for his rank and his family, for a debt. The PCs can see the mark settle on him if they look.",
                   "→ Baldrik submitting evidence and himself to judgement (event 3) is how he breaks it."),
        "vecna": ("s54", "Vecna whispers each general's secret to whoever carries the Whispered Eye: Odran's hidden liability, Brynja's doubt, Hadrik's sealed order.",
                  "→ The Stone Council hearing, with the knowledge to aim it.")},
    9: {"orcus": ("s64", "At the Vanguard Redoubt the dead the Vanguard made of its own suspected deserters are buried under the parade ground. Their ghosts point at their graves.",
                  "→ Evidence of Vanguard brutality that moves Dagnner — she knew two of them."),
        "vampyr": ("s62", "The displaced households owe Korga for protection, exactly as Lowhearth owes Hadrik. Vampyr does not care which side wins; it is fed either way.",
                   "→ Urzha's rejected limited settlement (R4) and a settlement that frees both peoples from protection-debt."),
        "vecna": ("s61", "On the war table's map one route is missing: the narrow service passage to the Heartworks. Vecna offers the Unwritten Step.",
                  "→ Skrik can supply the same route honestly.")},
    10: {"orcus": ("s72", "As orders are written that send soldiers to hold fronts, a voice counts the ones who will not return.",
                   "→ Choosing which front the party takes (7.1) with full knowledge of what it costs elsewhere."),
         "vampyr": ("s65", "Baldrik's 'order he cannot postpone' arrives sealed in red wax that is still warm.",
                    "→ The moment for Baldrik to refuse (event 2) if he has not."),
         "vecna": ("s71", "Vecna offers to tell them which of the three fronts truly matters.",
                   "Accepting reveals the next Siege Dispatch before it is drawn (+1 Vecna). → The war council of 7.1."),
         "all": ("s67", "During the long rest before the horns, each present power visits its marked PC in a dream. This is the last offer before the war. Refusing here at real cost reduces that power's Attention by 1.",
                 "Run it as one short beat per marked PC, then ring the war horns at dawn.")},
    11: {"orcus": ("s73", "On the chosen front, if Orcus is Claiming, fallen raiders rise as husks at the start of round 3. Radiant damage, fire or Legna's ravens deny them.",
                   "→ The Upper Gate or Lower Bridge countdown, with something worse than losing ground at stake."),
         "vampyr": ("s75", "Korga falls. Vampyr speaks through his blood: \"Give him to me and the war ends tonight.\" A vampiric Korga is exactly the ninth-session villain this arc refuses to create.",
                    "Refusing (Vampyr −1) and ending the war by terms is the arc's answer. Bunch's prophecy speaks here if fulfilled."),
         "vecna": ("s76", "The pressure gauge's needle settles on a number that is also a sentence, if you know how to read it.",
                   "→ The Heartworks timeline; what the party knows Hadrik knew.")},
    12: {"orcus": ("s83", "If Orcus is Arriving, his echo stands at the regulator. Each failed Last Bastion stage gives Orcus +1. If the party wins cleanly, he sets down the scythe: \"No harvest. Again.\" (Orcus −2.)",
                   "→ The epilogue: whether Orcus leaves as an enemy, a rival or an admirer."),
         "vampyr": ("s85", "If Baldrik carries a Blood-Debt, it is still on him at the family conversation. A freely chosen act between the brothers — not forgiveness, just a choice — cancels it.",
                    "→ 'Brothers, not a verdict'. The shield offered without terms."),
         "vecna": ("s84", "'The record nobody gets to edit.' Vecna offers to edit it. Only he could.",
                   "Refusing: Vecna −2, and he is genuinely impressed. Accepting: the record says what they want, and Vecna owns the difference."),
         "all": ("s86", "The next morning each present power leaves a calling card where the PCs will find it. See 'Calling Cards'.",
                 "→ What Hunts Them Next: the campaign after this one.")},
}

CALLING_CARDS = {
    "orcus": "A soul coin left on Heddra's step, warm, stamped with a horned skull: an invitation to an audience in the Abyss, or a declaration of war, depending on disposition.",
    "vampyr": "A red-sealed letter in Finn's handwriting (or Tatyana's, or Damien's own) that none of them wrote, naming a city and a date.",
    "vecna": "A page from the Tome of Strahd that was not in the Tome, describing tomorrow.",
}

COMBINED = [
    ("orcus+vampyr", "The Undeath Schism", "Harvest and Thirst both want Thorgrinn's soul coin: Orcus as a death denied, Vampyr as a covenant refused.",
     "When both are Reaching or higher, their omens interfere. Once per chapter the party can play one against the other: a Gift from one may be refused by invoking the other's claim (no Attention cost, but both +1 at the next threshold check).",
     "Their quarrel gives the party leverage, not safety: the first power to reach Arriving tries to destroy the other's mark on its PC."),
    ("orcus+vecna", "The Ledger of the Dead", "Vecna wants the names Orcus collects. The Hearthwatch register and the corrected death register are their battlefield.",
     "Any document listing the dead (the death register, Hearthwatch names, the missing shift's roster) counts as both 'sealed' for Vecna and 'a harvest' for Orcus. Destroying or falsifying one feeds both (+1 each).",
     "A fair record of the dead, publicly kept, starves both."),
    ("vampyr+vecna", "Blood Remembers", "Vampyr's covenants are written; Vecna reads everything written.",
     "A signed Blood-Debt is also a secret Vecna can read: a PC with both marks gives Vecna one free look through their senses per chapter.",
     "The public roll (5.2) and the council record (8.4) can release debts and secrets together."),
    ("all", "The Council of Broken Gods", "All three were freed or angered by the Unkindness. None of them caused this war.",
     "If all three are Reaching or higher, they negotiate with each other through the PCs, offering joint Gifts (combine any two, total Attention cost split as the players choose).",
     "In 8.6 the three calling cards arrive together, and the next campaign is a war over the Unkindness rather than with it."),
]

# --------------------------------------------------------------------------- Outcomes from the Ravenloft finale (cond = JS expression on the imported state `s`)
OUTCOMES = [
    ("strahd-dead", "Strahd died permanently", "s.strahd==='dead'",
     "No Strahd echo. The mists that brought them stay gone; Vistani routes into Ironfist country now run in daylight.",
     "Baldrik's Vistani contact (Mirela) can carry letters back to whoever survived Barovia's end."),
    ("courtesy", "Accepted Strahd's Courtesy (the short rest)", "s.restAccepted===true",
     "<strong>Guest-Right Remembered.</strong> Once in the arc, when a host offers the party hospitality under false pretences (Hadrik's feast counts), a PC may sense it: they learn whether the host intends harm tonight.",
     "Strahd's last letter, delivered by a raven a year late, thanking them for 'the hour'."),
    ("courtesy-refused", "Refused Strahd's Courtesy", "s.restAccepted===false",
     "<strong>No Hour Given.</strong> Once in the arc, the party may refuse an enforced delay (a hearing adjourned, a summons, a wait for permission) and act first; the refusal is legally defensible.",
     "None needed: this is a reputation the Ironfists understand."),
    ("tatyana", "Honoured Tatyana's agency", "s.tatyanaAgencyHonoured===true",
     "<strong>Her Own Name</strong> (item). Once in the arc, a PC may reroll a failed save against being charmed, commanded or claimed, and say whose choice it is.",
     "A letter, signed only 'I.', from somewhere far from Barovia."),
    ("tatyana-not", "Tatyana's choice was taken", "s.tatyanaAgencyHonoured===false",
     "No mechanical penalty. Vampyr omens use her voice at least once.",
     "Somewhere she is still deciding what she owes them."),
    ("finn-freed", "Finn was freed (all three Chains broken)", "s.finnFreed===true",
     "Finn can be present in Kharad-Varr (via Baldrik's Vistani route, arriving at Session 3). He is a halfling vampire who chooses not to feed on the unwilling. Vampyr wants him back: while he is present, Vampyr's beats prefer him.",
     "Finn's three chains echo the commission's three clauses (5.1). He recognises them before anyone else."),
    ("finn-lost", "Finn was destroyed or remains claimed", "s.finnFreed===false",
     "No Finn. If he was destroyed, Orcus omens use his voice. If he remains claimed (mist), Vampyr does.",
     "'Don't make this weird' written in frost on a window."),
    ("brides-saved", "Spared or saved a bride", "s.bridesSaved>0",
     "Each bride saved is a creature who owes them nothing and knows it. Volenta, if saved, may write offering service as an oathbreaker seeking a new oath (Legna's material).",
     "Ludmilla's Black Sun notes are wanted by Vecna; Anastrasya's mist is wanted by Vampyr."),
    ("brides-destroyed", "Destroyed all three brides", "s.bridesDestroyed>=3",
     "<strong>Three Ashes.</strong> Vampyr cannot lay a Blood-Debt on a PC who struck a bride's final blow unless that PC accepts a Gift first.",
     "Nobody in Kharad-Varr believes this story until Dagnner does."),
    ("wish-djinn", "The Wish came from Damien's djinn", "s.wishSource==='djinn'",
     "<strong>The Djinn's Witness</strong> (item). The debt is settled. Once, the djinn appears to witness a contract and swear to its terms — a perfect authentication before the Stone Council.",
     "The djinn writes once, to complain."),
    ("wish-vecna", "The Wish came through Vecna (the Borrowed Ending)", "s.wishSource==='vecna'",
     "<strong>The Borrowed Ending</strong> (item) is live: the agreed price stands (Damien's memory, Vesper's Whispered Eye, Bunch's secret, Legna's first true name, or Thorgrinn's coin inscriptions). Vecna begins at least at Reaching.",
     "Every Vecna beat in this arc is also a reminder of the price."),
    ("arl", "Arl the pit fiend fought for them under contract", "s.arlFreed===true",
     "<strong>Arl's Acknowledgement</strong> (item). The contract is closed; the recognition clause stands. An infernal auditor may ask, once, whether Arl aided them. Answering truthfully costs nothing — and is a perfect example of a fair contract to set beside Hadrik's commission.",
     "If someone asks why a pit fiend's contract was fairer than their own general's, let it land."),
    ("black-road", "Thorgrinn walked the Black Road", "s.blackRoad==='accepted'",
     "Orcus is a claimant on Thorgrinn specifically and starts at least at Reaching. The Black Road beat in Session 1 continues to the hold.",
     "Orcus's offer of restoration to flesh is not trustworthy, and Sister Yrsa will say so."),
    ("black-road-refused", "Thorgrinn refused the Black Road", "s.blackRoad==='refused'",
     "<strong>The Road Back.</strong> The keepsake box is the surviving connection. Once in the arc, Thorgrinn has advantage on a check or save made to protect family or to refuse a claim on his body.",
     "Baldrik carries the star-shaped key."),
    ("vallaki-mercy", "Showed mercy before victory in Vallaki", "s.mercyBeforeVictory===true",
     "Counts towards a Merciful reputation.", "—"),
]

PROPHECIES = {
    "damien": ("p-healer", "The Saving Hand", "Once in the arc, when a creature would die, Damien can spend his reaction to leave it at 1 hit point. If doing so denies a Dark Power a death or a claim, that power −1."),
    "vesper": ("p-diviner", "Who Wrote This?", "Once in the arc, Vesper may ask which of three apparently certain things is an authored lie. The GM answers truthfully, and names who authored it — one forged or misleading document is exposed (it does not authenticate the true one)."),
    "bunch": ("p-traitor", "The Arithmetic Refused", "Once in the arc, when someone is told that one must suffer so others can live, Bunch can hand the choice to someone it belongs to. That NPC immediately acts on their own free choice (Ketta, Dagnner, Skrik, Korga's lieutenant)."),
    "legna": ("p-raven", "The Smallest Sign", "Once in the arc, in darkness, chaos or a dead end, Legna sees a black feather travelling against the wind: it reveals one hidden route, secret door or concealed object in the current scene."),
    "thorgrinn": ("p-horseman", "The Road Back", "If Thorgrinn refused the Black Road: once in the arc, advantage on a check or save to protect family or refuse a claim on his body, and the keepsake box opens."),
}

KEEPSAKE = ("The Keepsake Box",
            "Baldrik's family-crested keepsake box with the star-shaped lock reached Thorgrinn in Barovia, unopened. Baldrik carries the star-shaped key and has not mentioned it.",
            ["<strong>Baldrik's unsent letter</strong>, written the night he saw Thorgrinn's body — the most direct route to his admission (event 1).",
             "<strong>The paired Neverwinter patrol badges</strong>, one bent where Thorgrinn's shield once took a blow meant for Baldrik.",
             "<strong>A draft confession</strong> — Baldrik's own copy of the classification, annotated 'this is wrong' in his hand and never filed. Not E3, but it makes E3 impossible for him to deny."],
            "Choose one before Session 1, or let Jp's open of the box decide. It opens when Baldrik hands over the key, when Thorgrinn's prophecy triggers, or when Thorgrinn breaks it — each says something different.")

REPUTATION = [
    ("Merciful", "4+ acts of mercy (spared powers, saved brides, Finn freed, Tatyana honoured, mercy in Vallaki, a Saving Hand)",
     "Civilian Accord starts at 1. Urzha and Sister Yrsa have heard the stories through the Vistani. Hadrik expects to be able to shame them."),
    ("Balanced", "2–3 acts of mercy", "No change. The stories contradict each other."),
    ("Ruthless", "0–1 acts of mercy, several destroyed foes", "Defence Readiness starts at 3 and Hadrik starts Supportive: soldiers want heroes like that. Civilian Accord cannot rise above 3 until a public act of mercy in Kharad-Varr."),
]

OMEN_TABLES = {
    "orcus": "Orcus — Omens in the Hold", "vampyr": "Vampyr — Omens in the Hold", "vecna": "Vecna — Omens in the Hold",
}
MIST_ECHOES = ["A raven sits on the rafters of Hammerhall during the feast and does not leave until Legna looks at it.",
               "Thorgrinn's soul coin hums the Vistani song for three notes.", "A thin mist pools at the bottom of Lift Shaft IX and smells of Barovian pine.",
               "A Lowhearth child asks Bunch whether the vampire was afraid at the end.", "Wolves howl on the mountain road. They are ordinary wolves. Nobody believes it.",
               "Damien's shadow is a half-second late, then catches up.", "Vesper's holy symbol frosts over when she passes the archive.",
               "Someone has left nine flasks of holy water at the shrine with no note.", "A Vistani wagon passes the Fifth Finger at dusk and does not stop.",
               "Every bell in the hold rings once at the hour Strahd died.", "A clerk writes 'Barovia' in a ledger and cannot explain why.",
               "The Sunsword's light briefly turns the colour of dawn over a land that no longer exists."]

# --------------------------------------------------------------------------- build helpers
def icon_(k): return f"modules/{MOD}/assets/icons/{k}.webp"


def _items():
    def box(*ps): return IS.box(IS.P(*ps))
    F = "Shadows Beyond Barovia"
    IS.add(F, item("sh-mark-orcus", "Death-Mark of the Black Road", "loot", box(
        "<strong>Mark of Orcus.</strong> Orcus knows where you are when you are dying.",
        "While marked: the first time each day you drop to 0 hit points, you may let Orcus hold you — you stay at 1 hit point instead (Orcus Attention +1). Refusing costs nothing.",
        "<strong>Ends:</strong> when you save someone Orcus was owed, without dark aid, in front of witnesses."), img=icon_("sh-grave-horn")))
    IS.add(F, item("sh-mark-vampyr", "Blood-Debt of the First Thirst", "loot", box(
        "<strong>Mark of Vampyr.</strong> You owe, and it knows to whom.",
        "While marked: disadvantage on saving throws against being charmed by anyone you owe; Vampyr can see through any wound you take. Once per long rest you may draw on the debt: regain 2d10 hit points (Vampyr Attention +1).",
        "<strong>Ends:</strong> repaid or released publicly and freely (see the Blood-Debt rule)."), img=icon_("sh-blood-heart")))
    IS.add(F, item("sh-mark-vecna", "The Whispered Eye", "loot", box(
        "<strong>Mark of Vecna.</strong> Something reads over your shoulder.",
        "While marked: once per chapter you may ask the GM one question about a written document you can see; the answer is true (Vecna Attention +1). Vecna may look through your senses for one minute at a moment of the GM's choosing — never during real-world private player material.",
        "<strong>Ends:</strong> when you put the thing you most wanted kept secret on the public record."), img=icon_("sh-vecna")))
    IS.add(F, item("sh-tatyana", "Her Own Name", "loot", box(
        "You let her choose. Once in this arc, reroll a failed saving throw against being charmed, commanded or claimed, and say aloud whose choice it is."), img=icon_("sh-tatyana")))
    IS.add(F, item("sh-djinn", "The Djinn's Witness", "loot", box(
        "The last Wish is spent; the debt is settled. Once, Damien may call the djinn to witness a contract or testimony. It swears to the terms, and the Stone Council treats the document as authenticated."), img=icon_("sh-djinn")))
    IS.add(F, item("sh-borrowed", "The Borrowed Ending", "loot", box(
        "Vecna granted the Wish. Record the agreed price here: <em>Damien — a memory; Vesper — the Whispered Eye; Bunch — a secret; Legna — his first true name; Thorgrinn — the inscriptions of his soul coin.</em>",
        "The price is live, finite and recoverable through play. It is never 'anything later'."), img=icon_("sh-edict")))
    IS.add(F, item("sh-arl", "Arl's Acknowledgement", "loot", box(
        "The infernal contract is closed: mutual non-harm ended with the assault, Arl's aid recognised in writing.",
        "If competent infernal authority asks whether Arl aided you, answer truthfully. Nothing more is owed. Show it to Hadrik when he says a fair contract with power is impossible."), img=icon_("sh-contract")))
    IS.add(F, item("sh-keepsake", KEEPSAKE[0], "loot", box(KEEPSAKE[1], "<strong>Possible contents (GM chooses one):</strong>", *KEEPSAKE[2], KEEPSAKE[3]), img=icon_("sh-keepsake")))
    for pc, (ic, nm, txt) in PROPHECIES.items():
        IS.add(F, item(f"sh-prophecy-{pc}", f"Prophecy Fulfilled — {nm}", "loot", box(
            f"<strong>{pc.title()}'s card from Madam Eva's final reading.</strong> Only if the prophecy was fulfilled at Ravenloft.", txt), img=icon_("sh-" + ic)))


def _tables():
    F = "Shadows Beyond Barovia"
    for k, name in OMEN_TABLES.items():
        MI.table(f"omens-{k}", name, POWERS[k]["signs"], f"Signs of {POWERS[k]['name']}'s attention in Kharad-Varr. Use at Watching or higher.", POWERS[k]["icon"], F)
    MI.table("mist-echoes", "Echoes of Barovia", MIST_ECHOES, "Small, harmless reminders that they came from somewhere else. One per session at most.", "sh-invitation", F)
    MI.table("dark-gifts", "Dark Gifts (any present power)",
             [f"{POWERS[p]['name']}: {g[1]}" for p in GIFTS for g in GIFTS[p]], "When you need an offer on the spot. Reroll if that power is below Reaching.", "sh-broken-gods", F)


def _macros():
    F = "Shadows Beyond Barovia"
    MI.macro("inheritance", "Inheritance of the Mists", "api.inheritance.open();", "sh-broken-gods", F)
    MI.macro("shadow-beat", "Shadow Beat (this session)", "api.inheritance.beat();", "sh-invitation", F)
    MI.macro("dark-gift", "Offer a Dark Gift", "api.inheritance.gift();", "sh-edict", F)
    MI.macro("shadow-attention", "Adjust Shadow Attention", "api.inheritance.adjust();", "sh-vecna", F)
    MI.macro("shadow-import", "Import the Ravenloft Ending", "api.inheritance.importFinale();", "sh-orcus", F)


def export_json():
    data = {"powers": {k: {kk: v[kk] for kk in ("name", "title", "icon", "color", "modes")} | {"rule": v["rule"][0]} for k, v in POWERS.items()},
            "thresholds": THRESHOLDS,
            "gifts": {k: [{"key": g[0], "name": g[1], "offer": g[2], "effect": g[3], "price": g[4]} for g in v] for k, v in GIFTS.items()},
            "beats": {str(n): {p: {"scene": b[0], "beat": b[1], "hook": b[2]} for p, b in d.items()} for n, d in BEATS.items()},
            "outcomes": [{"key": o[0], "label": o[1], "cond": o[2], "effect": o[3], "hook": o[4]} for o in OUTCOMES],
            "combined": [{"key": c[0], "name": c[1], "premise": c[2], "rule": c[3], "turn": c[4]} for c in COMBINED],
            "calling": CALLING_CARDS, "reputation": REPUTATION}
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(data, open(OUT_JSON, "w"), ensure_ascii=False)


_items(); _tables(); _macros(); export_json()


# --------------------------------------------------------------------------- journals (called from journals.build_docs)
def build(J):
    P, RA, BOX, UL, TABLE, BANNER, SECRET, IMG = J.P, J.RA, J.BOX, J.UL, J.TABLE, J.BANNER, J.SECRET, J.IMG
    L_page, L_macro, L_item, L_table = J.L_page, J.L_macro, J.L_item, J.L_table
    title = lambda s: J.TITLES.get(s, s)
    sc = lambda s: L_page("ch" + s[1], s, f"{s[1]}.{s[2:]} {title(s)}")
    pw = lambda k: L_page("shadows", k, POWERS[k]["name"])

    start = (BANNER("Shadows Beyond Barovia", "The Inheritance of the Mists", "Carrying the Ravenloft ending into Kharad-Varr")
             + IMG(IMGP + "broken-gods.webp", "il-hero")
             + P("The Unkindness did not leave Barovia clean. At Ravenloft they faced three released Dark Powers — <strong>Orcus</strong>, <strong>Vampyr</strong> and, from very far away, <strong>Vecna</strong> — "
                 "and every choice there (banish, spare, bargain; who was saved; who granted the Wish) left a mark. This section carries those marks into the Ironfist arc.")
             + BOX("Module law for the Shadows",
                   UL("<strong>The Dark Powers did not cause this war.</strong> The diversion, Last Bastion and Korga's escalation are entirely mortal (Section 1). Nothing here changes that.",
                      "They are <strong>opportunists</strong>: they watch, tempt and complicate. A Dark Gift is always a shortcut to something the adventure already lets the party achieve honestly.",
                      "They never replace Hadrik, Korga or the Bastion Engine as the opponent, and the arc still closes at 8.6 without a compulsory ninth-session villain.",
                      "Every price is stated before acceptance. No vague 'you owe me later'.",
                      "Thorgrinn's body is his. No power can switch it off, extract him or override his consent — Orcus can only <em>offer</em>."))
             + BOX("How to run it in four steps",
                   "1. Run " + L_macro("shadow-import", "Import the Ravenloft Ending") + " once (it reads the Part I finale state: the Finale Dashboard). Or enter the results by hand in " + L_macro("inheritance", "Inheritance of the Mists") + ".",
                   "2. Read which powers are <em>present</em> (Attention 3+) and their mode. Apply the " + L_page("outcomes", "outcomes", "outcome rules") + " that the window highlights, and the reputation start to the Stone Ledger.",
                   "3. Each session, open the session guide: its <em>Shadows</em> box links the beat for each present power. " + L_macro("shadow-beat", "Shadow Beat") + " posts them to GM chat.",
                   "4. Adjust Attention as the party accepts or refuses. Thresholds change what the powers can do."))
    attention = (BANNER("Shadows Beyond Barovia", "Attention & Thresholds")
                 + P("Each power keeps the Attention score it ended Ravenloft with. Attention is <strong>interest</strong>, not approval: a vengeful Orcus at 7 is as present as a curious one.")
                 + TABLE(["Attention", "Stage", "What the power can do"], [[f"{t[0]}+", t[1], t[2]] for t in THRESHOLDS])
                 + BOX("Present, primary and combined",
                       "A power is <strong>present</strong> at 3+. The highest present power is <strong>primary</strong>; any power within 1 of it is <strong>co-primary</strong> and runs a "
                       + L_page("shadows", "combined", "combined arc") + ". Ties are good. Below 3, a power is only Watching — signs, never offers.")
                 + "<h3>What raises Attention</h3>" + TABLE(["Act", "Change"], [list(r) for r in ATTENTION_UP])
                 + "<h3>What lowers it</h3>" + TABLE(["Act", "Change"], [list(r) for r in ATTENTION_DOWN])
                 + P("Attention never drops below 0. A power at 0 after Arriving is not gone — it has simply lost interest in <em>this</em> story."))
    gifts_page = BANNER("Shadows Beyond Barovia", "Dark Gifts", "Shortcuts with a stated price") + P(
        "Offer at most one Gift per present power per chapter (Claiming powers may offer in combat). Each Gift reaches something the adventure already lets the party reach honestly — that is the point of the temptation.")
    for k, gl in GIFTS.items():
        gifts_page += f"<h3>{POWERS[k]['name']} — {POWERS[k]['title']}</h3>" + TABLE(["Gift", "What it gives", "Price"], [[f"<strong>{g[1]}</strong><br><em>{g[2]}</em>", g[3], g[4]] for g in gl])
    marks = (BANNER("Shadows Beyond Barovia", "Marks") + P("Marks are items. Give them to the character sheet when a price says so; the Inheritance window keeps a list.")
             + UL(L_item("sh-mark-orcus", "Death-Mark of the Black Road") + " — Orcus.", L_item("sh-mark-vampyr", "Blood-Debt of the First Thirst") + " — Vampyr.",
                  L_item("sh-mark-vecna", "The Whispered Eye") + " — Vecna.")
             + P("Every mark lists how it ends. Ending a mark is always something the players can do in the story, never a roll."))
    J.journal("shadows-start", "06 — Shadows Beyond Barovia: Start Here", "Shadows Beyond Barovia",
              [("start", "The Inheritance of the Mists", start), ("attention", "Attention & Thresholds", attention), ("gifts", "Dark Gifts", gifts_page), ("marks", "Marks", marks)], sort=600)

    pages = []
    for k, d in POWERS.items():
        r = d["rule"]
        h = (BANNER(d["title"], d["name"]) + IMG(IMGP + d["img"] + ".webp")
             + BOX("What it wants in Kharad-Varr", d["wants"]) + BOX("Why it watches the Unkindness", d["why"])
             + f"<h3>Signature rule — {r[0]}</h3>" + P(*r[1:])
             + "<h3>Mode (from the Ravenloft final choice)</h3>" + TABLE(["Disposition", "How it behaves"], [[m, t] for m, t in d["modes"].items()])
             + "<h3>Signs</h3>" + P(L_table(f"omens-{k}", OMEN_TABLES[k]) + " — roll or choose.") + UL(*d["signs"])
             + "<h3>Its beats this arc</h3>" + UL(*[f"Session {n}: {sc(b[k][0])} — {b[k][1][:110]}…" for n, b in BEATS.items() if k in b]))
        pages.append((k, f"{d['name']} — {d['title']}", h))
    comb = BANNER("Shadows Beyond Barovia", "When Shadows Share a Hunt") + P("Use when two or more powers are co-primary.")
    for c in COMBINED:
        comb += BOX(f"{c[1]} ({c[0].replace('+', ' + ')})", f"<strong>Premise.</strong> {c[2]}", f"<strong>Rule.</strong> {c[3]}", f"<strong>Turn.</strong> {c[4]}")
    pages.append(("combined", "Combined Arcs", comb))
    cards = BANNER("Shadows Beyond Barovia", "Calling Cards (8.6)") + P("The next morning, each present power leaves one. This is the bridge to whatever the Unkindness do after Kharad-Varr.") + UL(
        *[f"<strong>{POWERS[k]['name']}:</strong> {t}" for k, t in CALLING_CARDS.items()])
    pages.append(("calling", "Calling Cards", cards))
    J.journal("shadows", "07 — The Three Shadows", "Shadows Beyond Barovia", pages, sort=700)

    out = (BANNER("Shadows Beyond Barovia", "What Ravenloft Left Behind", "Specific rules for how the finale actually ended")
           + P("Apply every row that matches. The Inheritance window ticks the matching rows automatically after import.")
           + TABLE(["If at Ravenloft…", "In this arc", "Hook"], [[f"<strong>{o[1]}</strong>", o[3], o[4]] for o in OUTCOMES]))
    rep = (BANNER("Shadows Beyond Barovia", "Reputation from the Mists") + P(
        "Stories of the Unkindness reach Kharad-Varr through Baldrik's Vistani route before the party does (1.2 already has the courier). Count acts of mercy at Ravenloft and in Vallaki:")
           + TABLE(["Reputation", "When", "Starting effect"], [list(r) for r in REPUTATION])
           + P("These are starting adjustments, applied once from the Inheritance window. They change where the tracks begin, never what counts later."))
    proph = BANNER("Shadows Beyond Barovia", "Five Prophecies, Fulfilled") + P("Madam Eva's final reading paid out at Ravenloft. A fulfilled card carries one more use into this arc.") + TABLE(
        ["PC", "Card", "Use in Kharad-Varr"], [[pc.title(), L_item(f"sh-prophecy-{pc}", v[1]), v[2]] for pc, v in PROPHECIES.items()])
    keep = (BANNER("Shadows Beyond Barovia", KEEPSAKE[0]) + IMG(IMGP + "keepsake.webp") + P(KEEPSAKE[1]) + "<h3>What is inside</h3>" + UL(*KEEPSAKE[2]) + P(KEEPSAKE[3])
            + SECRET("Why it matters", "The box is the thread that pulled Thorgrinn out of the collapsing mists towards Ironfist country. It is not magic. It is the one thing Baldrik gave freely, which is why no Dark Power can use it."))
    J.journal("outcomes", "08 — What Ravenloft Left Behind", "Shadows Beyond Barovia",
              [("outcomes", "Outcome Rules", out), ("reputation", "Reputation from the Mists", rep), ("prophecies", "Prophecies Fulfilled", proph), ("keepsake", "The Keepsake Box", keep)], sort=800)

    sp = []
    for n, d in BEATS.items():
        S = next(s for s in J.SC.SESSIONS if s["n"] == n)
        h = BANNER(f"Session {n} · {J.SC.DATES[n-1]}", S["title"], "Shadow beats — use only for present powers")
        for p in ("orcus", "vampyr", "vecna", "all"):
            if p not in d: continue
            s, beat, hook = d[p]
            nm = "Every present power" if p == "all" else POWERS[p]["name"]
            h += BOX(f"{nm} — {sc(s)}", beat, f"<strong>Hook:</strong> {hook}", cls="il-box il-shadow-" + p)
        sp.append((f"b{n}", f"Session {n} — {S['title']}", h))
    J.journal("shadow-beats", "09 — Shadow Beats by Session", "Shadows Beyond Barovia", sp, sort=900)


def session_box(J, n):
    d = BEATS.get(n, {})
    items = [f"{POWERS[p]['name'] if p != 'all' else 'All present powers'}: {J.L_page('ch' + d[p][0][1], d[p][0], d[p][0][1] + '.' + d[p][0][2:])}" for p in d]
    return J.BOX("Shadows Beyond Barovia", "Only for powers that are present (Attention 3+). " + J.L_page("shadow-beats", f"b{n}", "This session's beats") + " · "
                 + J.L_macro("shadow-beat", "Shadow Beat macro"), J.UL(*items), cls="il-box il-shadows")


def before_box(J):
    return J.BOX("Coming from Part I: The Cat and the Unkindness",
                 "The finale ends on <em>The First Sound Is an Anvil</em>: three strikes, a pause, two strikes; real weather; a stone road; a white banner with a fist gripping an iron nail. 1.1 picks up on exactly that road.",
                 "As the mists lost their borders, Thorgrinn's " + J.L_item("sh-keepsake", "keepsake box") + " grew heavy and smelled of coal smoke: Baldrik's Vistani route and the box he left are why the mists put them <em>here</em>.",
                 "Run " + J.L_macro("shadow-import", "Import the Ravenloft Ending") + " before Session 1. It reads Part I's Dark Power Attention, final choices, brides, Finn, Tatyana, the Wish, Arl, the prophecies and the Black Road, and sets up " + J.L_page("shadows-start", "start", "the Inheritance of the Mists") + ".")
