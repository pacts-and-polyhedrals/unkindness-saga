"""Original procedurally synthesized music and sound effects for Ironfist Legacy.

Everything here is generated from oscillators, filtered noise and a plucked-string model, so the
module ships with its own royalty-free soundtrack. Loops crossfade their tail into their head so
they repeat seamlessly in a Foundry playlist.
"""
import json, math, os, subprocess, sys, tempfile
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

SR = 44100
OUT = "/home/claude/il/module/assets/audio"
RNG = np.random.default_rng(7)

# D dorian-ish modal palette (Hz) — dwarven, a little sombre
NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"])}


def hz(name, octave=4):
    return NOTE[name] * 2 ** (octave - 4)


def t(sec):
    return np.arange(int(sec * SR)) / SR


def lp(x, f, order=2):
    return sosfilt(butter(order, f / (SR / 2), "low", output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f / (SR / 2), "high", output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)


def env(n, a=0.01, r=0.3, sus=None):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    if sus is None:
        e[na:] = np.exp(-np.arange(n - na) / (r * SR))
    else:
        nr = int(r * SR)
        if nr < n - na:
            e[n - nr:] = np.linspace(1, 0, nr)
    return e


def saw(f, tt):
    return 2 * ((f * tt) % 1) - 1


def drone(notes, sec, bright=600, detune=0.004, amp=0.18, lfo=0.07):
    tt = t(sec)
    x = np.zeros_like(tt)
    for f in notes:
        for d in (-detune, 0, detune):
            x += saw(f * (1 + d), tt) * (0.6 if d else 1)
    x = lp(x, bright, 2)
    x *= 1 + 0.25 * np.sin(2 * np.pi * lfo * tt)
    return x / np.max(np.abs(x) + 1e-9) * amp


def pad(chords, sec_each, amp=0.14, bright=1200, vowel=(700, 1100)):
    out = []
    for ch in chords:
        tt = t(sec_each)
        x = sum(saw(f * (1 + d), tt) for f in ch for d in (-0.003, 0.003))
        x = lp(x, bright) + 0.5 * bp(x, vowel[0] * 0.8, vowel[1])
        e = np.minimum(1, np.minimum(tt / 1.5, (sec_each - tt) / 1.5))
        out.append(x * e)
    x = np.concatenate(out)
    return x / (np.max(np.abs(x)) + 1e-9) * amp


_PL = {}


def pluck(f, sec=1.6, decay=0.996, bright=0.5, amp=0.5):
    """Karplus-Strong string as a feedback comb filter (vectorised)."""
    key = (round(f, 2), sec, decay, bright)
    if key not in _PL:
        n = int(sec * SR)
        P = max(2, int(SR / f))
        exc = np.zeros(n)
        exc[:P] = lp(RNG.uniform(-1, 1, P), 2000 + 6000 * bright, 1)
        a = np.zeros(P + 2)
        a[0] = 1
        a[P] = -decay * 0.5
        a[P + 1] = -decay * 0.5
        y = lfilter([1], a, exc)
        _PL[key] = y / (np.max(np.abs(y)) + 1e-9) * env(n, 0.002, sec / 2.5)
    return _PL[key] * amp


def thump(sec=0.6, f0=90, f1=40, amp=0.9):
    tt = t(sec)
    f = f1 + (f0 - f1) * np.exp(-tt * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-tt * 7)
    x += lp(RNG.normal(0, 1, len(tt)), 300) * np.exp(-tt * 40) * 0.3
    return x * amp


def clank(sec=1.2, f=880, amp=0.5):
    tt = t(sec)
    x = sum(np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * (3 + m * 2)) / m for m in (1, 2.76, 5.4, 8.9))
    x += hp(RNG.normal(0, 1, len(tt)), 2000) * np.exp(-tt * 60) * 0.6
    return x * amp


def hand_drum(sec=0.35, f=180, amp=0.5):
    tt = t(sec)
    return (np.sin(2 * np.pi * f * tt * (1 + 0.3 * np.exp(-tt * 30))) * np.exp(-tt * 14)
            + bp(RNG.normal(0, 1, len(tt)), 400, 2500) * np.exp(-tt * 35) * 0.5) * amp


def horn(f, sec=3.0, amp=0.35):
    tt = t(sec)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * tt) * np.minimum(1, tt)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    x = sum(np.sin(ph * k) / k ** 0.9 for k in range(1, 9))
    x = lp(x, 900 + 1400 * np.minimum(1, tt / 0.6).mean())
    return x * env(len(tt), 0.35, 0.8, sus=True) * amp


def noise_bed(sec, lo, hi, amp=0.1, lfo=0.1):
    tt = t(sec)
    x = bp(RNG.normal(0, 1, len(tt)), lo, hi)
    x *= 0.7 + 0.3 * np.sin(2 * np.pi * lfo * tt + RNG.uniform(0, 6))
    return x / (np.max(np.abs(x)) + 1e-9) * amp


def place(buf, snd, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    n = min(len(snd), len(buf) - i)
    buf[i:i + n] += snd[:n] * gain


def melody(buf, seq, start, beat, octave=4, amp=0.35, decay=0.996, bright=0.5, sec=1.8):
    tcur = start
    for item in seq:
        name, beats = item
        if name != "-":
            nm, oc = (name[:-1], int(name[-1])) if name[-1].isdigit() else (name, octave)
            place(buf, pluck(hz(nm, oc), sec, decay, bright, amp), tcur)
        tcur += beats * beat
    return tcur


def stereo(x, width=0.012):
    d = int(width * SR)
    L = x
    R = np.concatenate([np.zeros(d), x[:-d]]) if d else x
    return np.stack([L, R], 1)


def reverb(x, mix=0.25):
    """Cheap cave reverb: a few feedback combs + allpass smear."""
    y = np.zeros_like(x)
    for dl, g in ((1557, 0.82), (1617, 0.8), (1491, 0.79), (1422, 0.78), (1277, 0.77), (1356, 0.76)):
        a = np.zeros(dl + 1)
        a[0] = 1
        a[dl] = -g
        y += lfilter([1], a, x)
    y = lp(y / 6, 5000)
    return x * (1 - mix) + y * mix


def finish(x, name, sub="music", loop=True, fade=4.0, rev=0.25):
    if rev:
        x = reverb(x, rev)
    if loop:
        n = int(fade * SR)
        head, tail = x[:n], x[-n:]
        w = np.linspace(0, 1, n)
        x = x[:-n].copy()
        x[:n] = head * w + tail * (1 - w)
    else:
        n = int(0.05 * SR)
        x[-n:] *= np.linspace(1, 0, n)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = stereo(x)
    pcm = (st * 32767).astype(np.int16)
    os.makedirs(f"{OUT}/{sub}", exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as f:
        f.write(pcm.tobytes())
        raw = f.name
    dst = f"{OUT}/{sub}/{name}.ogg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", raw,
                    "-c:a", "libvorbis", "-q:a", "3", dst], check=True)
    os.unlink(raw)
    return dst


TRACKS = {}


def track(fn):
    TRACKS[fn.__name__.replace("_", "-")] = fn
    return fn


THEME = [("D4", 1), ("F4", 1), ("A4", 2), ("G4", 1), ("F4", 1), ("E4", 2), ("D4", 1), ("C4", 1), ("D4", 2), ("A3", 2),
         ("D4", 1), ("F4", 1), ("A4", 1), ("C5", 1), ("Bb4", 2), ("A4", 2), ("G4", 1), ("E4", 1), ("D4", 4)]


# ---------------------------------------------------------------- ambience
@track
def beyond_the_last_mist():
    S = 96
    x = drone([hz("D", 2), hz("A", 2)], S, 400, amp=0.12, lfo=0.03)
    x += noise_bed(S, 200, 1400, 0.12, 0.05)  # wind
    for k in range(int(S / 3.2)):
        at = 2 + k * 3.2
        place(x, clank(0.8, 1200 + (k % 3) * 80, 0.08), at)
        place(x, clank(0.8, 1100, 0.05), at + 0.8)
    for i, at in enumerate((10, 40, 70)):
        melody(x, THEME[:8], at, 0.9, amp=0.18, bright=0.3)
    return finish(x, "beyond-the-last-mist", rev=0.35)


@track
def lowhearth_hearth():
    S = 100
    x = drone([hz("D", 2), hz("A", 2), hz("F", 3)], S, 500, amp=0.12, lfo=0.05)
    crack = np.zeros(int(S * SR))
    for _ in range(420):
        place(crack, hp(RNG.normal(0, 1, 400), 2500) * np.exp(-np.arange(400) / 60), RNG.uniform(0, S), RNG.uniform(0.05, 0.25))
    x += crack * 0.4
    beat = 0.75
    tcur = 6
    while tcur < S - 16:
        tcur = melody(x, THEME, tcur, beat, amp=0.22, bright=0.35, decay=0.997) + 6
    return finish(x, "lowhearth-hearth", rev=0.3)


@track
def hammerhall_feast():
    S = 88
    x = drone([hz("D", 2), hz("A", 2)], S, 700, amp=0.1)
    beat = 0.5
    for i in range(int(S / beat)):
        at = i * beat
        if i % 4 == 0:
            place(x, thump(0.5, 110, 50, 0.6), at)
        if i % 4 == 2:
            place(x, hand_drum(0.3, 200, 0.35), at)
        if i % 8 == 7:
            place(x, clank(0.6, 1600, 0.12), at)
    up = [(n, b) for n, b in THEME]
    tcur = 4
    while tcur < S - 12:
        tcur = melody(x, up, tcur, beat, amp=0.32, bright=0.7, decay=0.995)
        tcur = melody(x, [(n[:-1] + str(int(n[-1]) + 1), b) for n, b in THEME[:10]], tcur, beat, amp=0.22, bright=0.8) + 2
    return finish(x, "hammerhall-feast", rev=0.3)


@track
def the_deep_roads():
    S = 100
    x = drone([hz("D", 1), hz("A", 1)], S, 220, amp=0.2, lfo=0.02)
    for _ in range(60):
        f = RNG.uniform(1800, 3400)
        place(x, np.sin(2 * np.pi * f * t(0.25)) * np.exp(-t(0.25) * 25) * 0.15, RNG.uniform(0, S))
    x += noise_bed(S, 60, 300, 0.06, 0.03)
    return finish(x, "the-deep-roads", rev=0.5)


@track
def sluice_works():
    S = 90
    x = noise_bed(S, 300, 3000, 0.16, 0.2)  # water
    x += drone([hz("D", 2), hz("Eb", 2)], S, 300, amp=0.1)
    for i in range(int(S / 1.5)):
        place(x, thump(0.4, 70, 35, 0.4), i * 1.5)
        place(x, clank(0.5, 700, 0.07), i * 1.5 + 0.75)
    for _ in range(14):
        at = RNG.uniform(0, S)
        place(x, noise_bed(2.5, 2000, 8000, 0.14) * env(int(2.5 * SR), 0.2, 1.0), at)  # steam
    return finish(x, "sluice-works", rev=0.3)


@track
def cinder_warrens():
    S = 92
    x = drone([hz("A", 1), hz("E", 2)], S, 350, amp=0.12)
    beat = 0.6
    pat = [1, 0, 0.5, 0, 1, 0.5, 0, 0.5]
    for i in range(int(S / beat)):
        g = pat[i % 8]
        if g:
            place(x, hand_drum(0.35, 150 if g == 1 else 240, 0.35 * g), i * beat)
    for _ in range(40):
        f = RNG.choice([hz("A", 5), hz("C", 6), hz("E", 6), hz("G", 5)])
        place(x, np.sin(2 * np.pi * f * t(2)) * env(int(2 * SR), 0.5, 0.6) * 0.04, RNG.uniform(0, S))
    return finish(x, "cinder-warrens", rev=0.4)


@track
def treaty_stair():
    S = 96
    x = pad([[hz("D", 3), hz("F", 3), hz("A", 3)], [hz("C", 3), hz("Eb", 3), hz("G", 3)], [hz("Bb", 2), hz("D", 3), hz("F", 3)], [hz("A", 2), hz("C#", 3), hz("E", 3)]] * 2, S / 8, 0.15)
    for k in range(10):
        place(x, hand_drum(0.4, 120, 0.25), 4 + k * 9.6)
    return finish(x, "treaty-stair", rev=0.45)


@track
def heartworks_pulse():
    S = 80
    x = drone([hz("D", 1), hz("Ab", 1)], S, 260, amp=0.18)
    for i in range(int(S / 0.8)):
        place(x, thump(0.35, 80, 40, 0.5), i * 0.8)
        if i % 2:
            place(x, clank(0.3, 2400, 0.05), i * 0.8 + 0.4)
    x += noise_bed(S, 3000, 9000, 0.05, 0.4)
    return finish(x, "heartworks-pulse", rev=0.25)


# ---------------------------------------------------------------- scenes / themes
@track
def the_shield_between_us():
    S = 100
    x = pad([[hz("D", 3), hz("A", 3), hz("F", 4)], [hz("Bb", 2), hz("F", 3), hz("D", 4)], [hz("C", 3), hz("G", 3), hz("E", 4)], [hz("A", 2), hz("E", 3), hz("C#", 4)]] * 2, S / 8, 0.13)
    tcur = 3
    while tcur < S - 16:
        tcur = melody(x, THEME, tcur, 0.7, amp=0.3, bright=0.45, decay=0.997, sec=2.2) + 2
    for i in range(0, int(S), 4):
        place(x, thump(0.7, 70, 40, 0.3), i)
    return finish(x, "the-shield-between-us", rev=0.35)


@track
def two_mismatched_rivets():
    S = 96
    x = pad([[hz("D", 3), hz("F", 3), hz("A", 3)], [hz("G", 2), hz("Bb", 2), hz("D", 3)], [hz("Bb", 2), hz("D", 3), hz("F", 3)], [hz("A", 2), hz("C#", 3), hz("E", 3)]] * 2, S / 8, 0.15, 900)
    slow = [("A4", 2), ("F4", 2), ("E4", 2), ("D4", 4), ("-", 2), ("F4", 2), ("G4", 2), ("A4", 2), ("E4", 4), ("-", 2)]
    tcur = 4
    while tcur < S - 20:
        tcur = melody(x, slow, tcur, 0.8, amp=0.3, bright=0.3, decay=0.998, sec=2.6) + 3
    return finish(x, "two-mismatched-rivets", rev=0.4)


@track
def the_stone_council():
    S = 90
    x = drone([hz("D", 2)], S, 400, amp=0.1)
    for i in range(int(S / 1.2)):
        f = [hz("D", 2), hz("D", 2), hz("F", 2), hz("C", 2)][(i // 8) % 4]
        place(x, lp(saw(f, t(1.0)) * env(int(SR), 0.05, 0.4), 700) * 0.3, i * 1.2)
    for k in range(9):
        place(x, clank(1.5, 520, 0.08), 5 + k * 10)
    return finish(x, "the-stone-council", rev=0.35)


@track
def hearthwatch_night():
    S = 96
    x = pad([[hz("D", 3), hz("F#", 3), hz("A", 3)], [hz("G", 2), hz("B", 2), hz("D", 3)], [hz("E", 3), hz("G", 3), hz("B", 3)], [hz("A", 2), hz("C#", 3), hz("E", 3)]] * 2, S / 8, 0.13)
    warm = [("D4", 1), ("F#4", 1), ("A4", 2), ("B4", 1), ("A4", 1), ("F#4", 2), ("G4", 1), ("F#4", 1), ("E4", 2), ("D4", 4)]
    tcur = 3
    while tcur < S - 14:
        tcur = melody(x, warm, tcur, 0.65, amp=0.3, bright=0.5) + 2
    for _ in range(30):
        place(x, clank(1.2, RNG.choice([1760, 2093, 2637]), 0.04), RNG.uniform(0, S))
    return finish(x, "hearthwatch-night", rev=0.4)


@track
def the_next_morning():
    S = 90
    x = pad([[hz("D", 3), hz("F#", 3), hz("A", 3)], [hz("A", 2), hz("E", 3), hz("C#", 4)], [hz("B", 2), hz("D", 3), hz("F#", 3)], [hz("G", 2), hz("D", 3), hz("B", 3)]] * 2, S / 8, 0.14, 1600)
    bright_theme = [(n.replace("F4", "F#4").replace("C4", "C#4").replace("Bb4", "B4"), b) for n, b in THEME]
    tcur = 2
    while tcur < S - 16:
        tcur = melody(x, bright_theme, tcur, 0.6, amp=0.3, bright=0.6) + 2
    x += noise_bed(S, 300, 2000, 0.03, 0.05)
    return finish(x, "the-next-morning", rev=0.3)


# ---------------------------------------------------------------- battle
def war_drums(x, S, beat, pattern, low=60, amp=0.8):
    for i in range(int(S / beat)):
        g = pattern[i % len(pattern)]
        if g:
            place(x, thump(0.5, 120 if g > 1 else 95, low, amp * min(1, g)), i * beat)
            if g > 1:
                place(x, hand_drum(0.3, 260, 0.3), i * beat)


@track
def battle_at_the_ninth_sluice():
    S = 80
    x = drone([hz("D", 2), hz("A", 2)], S, 900, amp=0.12)
    war_drums(x, S, 0.3, [2, 0, 1, 0, 1, 1, 0, 1])
    x += noise_bed(S, 400, 3000, 0.07, 0.3)
    tcur = 2
    riff = [("D4", 1), ("D4", 1), ("F4", 1), ("D4", 1), ("G4", 1), ("F4", 1), ("E4", 1), ("C4", 1)]
    while tcur < S - 6:
        tcur = melody(x, riff * 2, tcur, 0.3, amp=0.3, bright=0.8, decay=0.993, sec=0.8)
        tcur = melody(x, [(n[:-1] + "5", b) for n, b in riff], tcur, 0.3, amp=0.2, bright=0.8, decay=0.993, sec=0.8)
    return finish(x, "battle-at-the-ninth-sluice", rev=0.2)


@track
def the_war_inside_the_mountain():
    S = 84
    x = drone([hz("D", 1), hz("A", 1), hz("D", 2)], S, 700, amp=0.14)
    war_drums(x, S, 0.35, [2, 0, 0, 1, 2, 0, 1, 0])
    for k in range(int(S / 10.5)):
        place(x, horn(hz("D", 3), 3.5, 0.3), 1 + k * 10.5)
        place(x, horn(hz("A", 3), 3.0, 0.22), 1 + k * 10.5 + 4)
    return finish(x, "the-war-inside-the-mountain", rev=0.3)


@track
def korgas_last_argument():
    S = 84
    x = drone([hz("C", 1), hz("G", 1)], S, 500, amp=0.18)
    war_drums(x, S, 0.42, [2, 0, 2, 0, 1, 1, 2, 0], low=45, amp=1.0)
    for k in range(int(S / 8.4)):
        place(x, horn(hz("C", 2), 2.6, 0.32), k * 8.4)
        place(x, horn(hz("Eb", 2), 2.6, 0.25), k * 8.4 + 3.4)
    return finish(x, "korgas-last-argument", rev=0.25)


@track
def last_bastion():
    S = 80
    x = drone([hz("D", 1), hz("Ab", 1)], S, 600, amp=0.16)
    for i in range(int(S / 0.4)):
        place(x, thump(0.3, 90, 45, 0.55), i * 0.4)
        if i % 4 == 2:
            place(x, clank(0.4, 1900, 0.12), i * 0.4)
    for k in range(int(S / 5)):
        place(x, clank(2.0, 660, 0.2), k * 5)  # the warning bell
    riff = [("D4", 1), ("Eb4", 1), ("D4", 1), ("A3", 1)]
    tcur = 0
    while tcur < S - 3:
        tcur = melody(x, riff, tcur, 0.4, amp=0.22, bright=0.9, decay=0.99, sec=0.6)
    return finish(x, "last-bastion", rev=0.2)


# ---------------------------------------------------------------- sfx
SFX = {}


def sfx(fn):
    SFX[fn.__name__.replace("_", "-")] = fn
    return fn


@sfx
def war_horn():
    return finish(horn(hz("D", 3), 4.0, 0.6) + horn(hz("A", 3), 4.0, 0.3), "war-horn", "sfx", loop=False, rev=0.4)


@sfx
def hammer_strike():
    x = np.zeros(int(3 * SR))
    for k in range(3):
        place(x, clank(1.2, 1250, 0.7), k * 0.75)
    return finish(x, "hammer-strike", "sfx", loop=False, rev=0.3)


@sfx
def alarm_bell():
    x = np.zeros(int(6 * SR))
    for k in range(6):
        place(x, clank(2.0, 660, 0.8), k * 0.9)
    return finish(x, "alarm-bell", "sfx", loop=False, rev=0.4)


@sfx
def steam_vent():
    x = noise_bed(3.5, 1500, 9000, 0.9, 2) * env(int(3.5 * SR), 0.05, 1.2)
    return finish(x, "steam-vent", "sfx", loop=False, rev=0.2)


@sfx
def lift_chain():
    x = np.zeros(int(5 * SR))
    for k in range(40):
        place(x, clank(0.2, 2200 + RNG.uniform(-200, 200), 0.3), k * 0.11)
    place(x, thump(0.8, 70, 35, 0.9), 4.4)
    return finish(x, "lift-chain", "sfx", loop=False, rev=0.3)


@sfx
def great_door():
    x = thump(2.5, 60, 25, 1.0) + noise_bed(2.5, 40, 300, 0.4) * env(int(2.5 * SR), 0.01, 0.6)
    return finish(x, "great-door", "sfx", loop=False, rev=0.5)


@sfx
def evidence_sting():
    x = np.zeros(int(3 * SR))
    for i, n in enumerate(("D4", "F4", "A4", "D5")):
        place(x, pluck(hz(n[:-1], int(n[-1])), 2.5, 0.997, 0.6, 0.5), i * 0.12)
    return finish(x, "evidence-sting", "sfx", loop=False, rev=0.35)


@sfx
def pressure_rupture():
    x = thump(1.5, 50, 20, 1.0)
    x = np.concatenate([x, np.zeros(int(2.5 * SR))])
    x += noise_bed(4.0, 100, 4000, 0.7) * env(int(4 * SR), 0.02, 1.4)
    return finish(x, "pressure-rupture", "sfx", loop=False, rev=0.4)


PLAYLISTS = {
    "Ironfist Legacy — Ambience": ["beyond-the-last-mist", "lowhearth-hearth", "the-deep-roads", "sluice-works", "cinder-warrens", "treaty-stair", "heartworks-pulse"],
    "Ironfist Legacy — Scenes & Themes": ["the-shield-between-us", "hammerhall-feast", "two-mismatched-rivets", "the-stone-council", "hearthwatch-night", "the-next-morning"],
    "Ironfist Legacy — Battle": ["battle-at-the-ninth-sluice", "the-war-inside-the-mountain", "korgas-last-argument", "last-bastion"],
    "Ironfist Legacy — Sound Effects": ["war-horn", "hammer-strike", "alarm-bell", "steam-vent", "lift-chain", "great-door", "evidence-sting", "pressure-rupture"],
}

if __name__ == "__main__":
    which = sys.argv[1:]
    for k, fn in {**TRACKS, **SFX}.items():
        if which and k not in which:
            continue
        p = fn()
        print(k, os.path.getsize(p) // 1024, "KB", flush=True)
