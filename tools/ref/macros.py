"""Script macros calling the module API."""
from lib5e import *

MACROS = []


def macro(key, name, call, img, folder):
    mid = fid("macro:" + key)
    cmd = (f'const api = game.modules.get("{MOD}")?.api;\n'
           f'if (!api) return ui.notifications.warn("Enable The Night of the Red Clause first.");\n'
           f'{call}')
    MACROS.append({"_id": mid, "name": name, "type": "script", "scope": "global", "img": icon(img), "command": cmd,
                   "folder": folder, "sort": len(MACROS) * 100, "ownership": {"default": 0},
                   "flags": {MOD: {"key": key}}, "_key": f"!macros!{mid}", "_stats": STATS})


GM = "GM Setup"
TB = "At the Table"
CT = "The High Court"
macro("setup", "Red Clause Manager", "api.openManager();", "mc-setup", GM)
macro("nightfall", "Nightfall (toggle day / night)", "api.nightfall();", "mc-night", TB)
macro("handout", "Show Handout", "api.showHandout();", "mc-handout", TB)
macro("fine", "Issue a Festive Fine", "api.issueFine();", "mc-fine", TB)
macro("gift", "Hand Out a Gift", "api.giveGift();", "mc-gift", TB)
macro("challenge", "Skill Challenge", "api.skillChallenge();", "mc-challenge", TB)
macro("save", "Request Group Save", "api.requestSave();", "mc-save", TB)
macro("bells", "The Midnight Docket", "api.docket.open(true);", "mc-bells", CT)
macro("exhibit", "Present an Exhibit", "api.presentExhibit();", "mc-exhibit", CT)
macro("writ", "Break a Writ", "const n = await foundry.applications.api.DialogV2.wait({window:{title:'Which Writ?'}, content:'<p>Choose the Writ.</p>', buttons:[{action:'1',label:'Writ I'},{action:'2',label:'Writ II'},{action:'3',label:'Writ III'}]});\nif (n) api.breakWrit(Number(n));", "mc-writ", CT)
macro("phase2", "The Smile Disappears (Phase II)", "api.phase2();", "mc-phase", CT)
