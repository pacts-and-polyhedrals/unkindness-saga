"""Playlists: track keys (files in assets/audio/music|sfx) and display titles."""
PLAYLISTS = {
    "Ironfist Legacy — Ambience": ["beyond-the-last-mist", "lowhearth-hearth", "the-deep-roads", "sluice-works", "cinder-warrens", "treaty-stair", "heartworks-pulse"],
    "Ironfist Legacy — Scenes & Themes": ["the-shield-between-us", "hammerhall-feast", "two-mismatched-rivets", "the-stone-council", "hearthwatch-night", "the-next-morning"],
    "Ironfist Legacy — Battle": ["battle-at-the-ninth-sluice", "the-war-inside-the-mountain", "korgas-last-argument", "last-bastion"],
    "Ironfist Legacy — Sound Effects": ["war-horn", "hammer-strike", "alarm-bell", "steam-vent", "lift-chain", "great-door", "evidence-sting", "pressure-rupture"],
}
SFX = set(PLAYLISTS["Ironfist Legacy — Sound Effects"])
TRACK_TITLES = {
    "beyond-the-last-mist": "Beyond the Last Mist", "lowhearth-hearth": "Lowhearth Hearth", "the-deep-roads": "The Deep Roads",
    "sluice-works": "Sluice Works", "cinder-warrens": "The Cinder Warrens", "treaty-stair": "The Treaty Stair",
    "heartworks-pulse": "Heartworks Pulse", "the-shield-between-us": "The Shield Between Us (Main Theme)",
    "hammerhall-feast": "Hammerhall Feast", "two-mismatched-rivets": "Two Mismatched Rivets (Brothers)",
    "the-stone-council": "The Stone Council", "hearthwatch-night": "Hearthwatch Night", "the-next-morning": "The Next Morning",
    "battle-at-the-ninth-sluice": "Battle at the Ninth Sluice", "the-war-inside-the-mountain": "The War Inside the Mountain",
    "korgas-last-argument": "Korga's Last Argument", "last-bastion": "Last Bastion",
    "war-horn": "War Horn", "hammer-strike": "Hammer Strikes", "alarm-bell": "Alarm Bell", "steam-vent": "Steam Vent",
    "lift-chain": "Lift Chain & Drop", "great-door": "Great Door Boom", "evidence-sting": "Evidence Sting", "pressure-rupture": "Pressure Rupture",
}
