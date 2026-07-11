# Retro SFX generator (sfxr-style) for Mars Miner 2D.
# 8-bit-flavored synth: square/saw/noise + envelopes, freq slides, arpeggios,
# simple one-pole lowpass. Writes 16-bit mono WAVs to assets/sfx/.
#
# Usage: python gen_sfx.py            -> all sounds
#        python gen_sfx.py ore_pickup -> just one (fast iteration)
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "assets" / "sfx"


def t(dur):
    return np.arange(int(SR * dur)) / SR


def square(freq, dur, duty=0.5):
    """freq may be scalar or per-sample array."""
    ph = np.cumsum(np.full(int(SR * dur), freq) / SR) if np.isscalar(freq) else np.cumsum(freq / SR)
    return np.where((ph % 1.0) < duty, 1.0, -1.0)


def saw(freq, dur):
    ph = np.cumsum(np.full(int(SR * dur), freq) / SR) if np.isscalar(freq) else np.cumsum(freq / SR)
    return 2.0 * (ph % 1.0) - 1.0


def sine(freq, dur):
    ph = np.cumsum(np.full(int(SR * dur), freq) / SR) if np.isscalar(freq) else np.cumsum(freq / SR)
    return np.sin(2 * np.pi * ph)


def noise(dur):
    return np.random.default_rng(4).uniform(-1, 1, int(SR * dur))


def env(n, attack=0.005, decay=0.2, sustain_level=0.0):
    """attack/decay in seconds; simple AD with optional tail level."""
    a = int(SR * attack)
    d = int(SR * decay)
    e = np.ones(n) * sustain_level
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a)
    dd = min(d, n - a)
    if dd > 0:
        e[a:a + dd] = np.linspace(1, sustain_level, dd)
    return e


def lowpass(x, cutoff):
    """one-pole; cutoff scalar or per-sample array (Hz)."""
    c = np.full(len(x), cutoff) if np.isscalar(cutoff) else cutoff
    alpha = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha[i] * (x[i] - acc)
        y[i] = acc
    return y


def slide(f0, f1, dur, curve=1.0):
    """frequency ramp f0 -> f1 (per-sample array)."""
    n = int(SR * dur)
    return f0 + (f1 - f0) * np.linspace(0, 1, n) ** curve


def save(name, x, gain=0.8):
    OUT.mkdir(parents=True, exist_ok=True)
    x = np.clip(x * gain / (np.max(np.abs(x)) + 1e-9), -1, 1)
    data = (x * 32767).astype(np.int16)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("wrote", name, f"({len(x)/SR:.2f}s)")


# === sounds ===

def dig_pop():
    """block breaks: short noise burst, pitch-down thump underneath"""
    d = 0.14
    n = noise(d) * env(len(t(d)), 0.001, 0.12)
    th = square(slide(220, 70, d), d) * env(len(t(d)), 0.001, 0.1)
    return lowpass(n * 0.7 + th * 0.6, 2600)


def ore_pickup():
    """coin-ish two-step up blip"""
    a = square(660, 0.06) * env(int(SR * 0.06), 0.001, 0.05)
    b = square(990, 0.12) * env(int(SR * 0.12), 0.001, 0.11)
    return np.concatenate([a, b]) * 0.9


def money_tick():
    """tiny high blip for the counting HUD"""
    d = 0.045
    return square(1320, d, duty=0.3) * env(int(SR * d), 0.001, 0.04)


def cargo_full_punch():
    """low square punch + noise slap (matches the clean slam)"""
    d = 0.3
    p = square(slide(160, 55, d), d) * env(int(SR * d), 0.001, 0.26)
    sl = noise(d) * env(int(SR * d), 0.001, 0.05)
    return lowpass(p * 0.9 + sl * 0.5, 1800)


def zone_sweep():
    """announcement: dark rising sweep with vibrato tail"""
    d = 0.7
    f = slide(140, 480, d, curve=0.7)
    vib = 1 + 0.02 * np.sin(2 * np.pi * 9 * t(d))
    x = saw(f * vib, d) * env(int(SR * d), 0.03, 0.55)
    return lowpass(x, slide(900, 3200, d))


def artifact_chime():
    """mysterious up-arpeggio (minor add9)"""
    notes = [523, 622, 784, 1047]  # C5 Eb5 G5 C6
    seg = []
    for i, f in enumerate(notes):
        dd = 0.09 if i < 3 else 0.42
        x = square(f, dd, duty=0.35) * env(int(SR * dd), 0.002, dd * 0.9)
        seg.append(x)
    return lowpass(np.concatenate(seg), 5200) * 0.8


def explosion():
    """boom: noise with falling lowpass + sub thump"""
    d = 0.85
    n = noise(d) * env(int(SR * d), 0.002, 0.7)
    x = lowpass(n, slide(3400, 220, d, curve=0.6))
    sub = sine(slide(90, 38, d), d) * env(int(SR * d), 0.002, 0.5)
    return x * 0.85 + sub * 0.7


def ui_blip():
    d = 0.05
    return square(880, d, duty=0.25) * env(int(SR * d), 0.001, 0.045)


def drill_clink():
    """metallic tink on undiggable rock: two detuned high partials, fast decay"""
    d = 0.16
    x = sine(2350, d) * 0.6 + sine(3571, d) * 0.35 + noise(d) * 0.12
    return x * env(int(SR * d), 0.0005, 0.14)


def hurt_thud():
    """fall damage: dull low thud"""
    d = 0.22
    x = sine(slide(140, 48, d), d) * env(int(SR * d), 0.001, 0.2)
    n = lowpass(noise(d), 500) * env(int(SR * d), 0.001, 0.06)
    return x * 0.9 + n * 0.6


def fuel_warning():
    """two-tone alarm blip (subtle, not shrill)"""
    a = square(520, 0.09, duty=0.4) * env(int(SR * 0.09), 0.002, 0.08)
    gap = np.zeros(int(SR * 0.05))
    b = square(392, 0.12, duty=0.4) * env(int(SR * 0.12), 0.002, 0.11)
    return lowpass(np.concatenate([a, gap, b]), 2400) * 0.7


def identify_reveal():
    """sparkle: fast up-arp into shimmer"""
    notes = [784, 988, 1175, 1568]
    seg = [square(f, 0.055, duty=0.3) * env(int(SR * 0.055), 0.001, 0.05) for f in notes]
    tail_d = 0.5
    tail = sine(slide(1568, 1560, tail_d), tail_d) * env(int(SR * tail_d), 0.005, 0.45) * 0.5
    vib = 1 + 0.15 * np.sin(2 * np.pi * 6 * t(tail_d))
    return np.concatenate(seg + [tail * vib]) * 0.8


SOUNDS = {
    "dig_pop": dig_pop,
    "ore_pickup": ore_pickup,
    "money_tick": money_tick,
    "cargo_full_punch": cargo_full_punch,
    "zone_sweep": zone_sweep,
    "artifact_chime": artifact_chime,
    "explosion": explosion,
    "ui_blip": ui_blip,
    "drill_clink": drill_clink,
    "hurt_thud": hurt_thud,
    "fuel_warning": fuel_warning,
    "identify_reveal": identify_reveal,
}


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for name, fn in SOUNDS.items():
        if only and name != only:
            continue
        save(name, fn())
