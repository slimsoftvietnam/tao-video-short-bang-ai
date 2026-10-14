# Synthesise the sound palette.
#
# Written as raw samples rather than ffmpeg `aevalsrc` expressions on purpose: those
# need every comma inside the expression escaped, which has silently produced wrong
# sounds before. Plain arithmetic into a WAV has no quoting layer to get wrong, and it
# is fully deterministic — the same run always produces byte-identical files.
#
# The palette is deliberately small. The brief bans overusing whoosh/flash/glitch, and a
# video that pings on every element becomes a slot machine. Eight sounds, each with one
# job, and most of them are barely above the music bed.
import io
import math
import os
import struct
import wave

SR = 48000
OUT = "assets/audio"
os.makedirs(OUT, exist_ok=True)


def write(name, samples, peak=0.9):
    """Normalise to `peak`, apply a 3ms fade at both ends so nothing clicks, write."""
    n = len(samples)
    fade = int(0.003 * SR)
    for i in range(min(fade, n // 2)):
        k = i / fade
        samples[i] *= k
        samples[n - 1 - i] *= k
    m = max(abs(x) for x in samples) or 1.0
    g = peak / m
    with wave.open(os.path.join(OUT, name), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x * g)) * 32767))
                               for x in samples))
    print("  %-18s %5.2fs" % (name, n / SR))


def env(t, tau):
    return math.exp(-t / tau)


# A fixed LCG. Noise has to be deterministic here — these files are committed and a
# re-run must not produce a different swipe.
_seed = 0x2545F491


def noise():
    global _seed
    _seed = (1103515245 * _seed + 12345) & 0x7FFFFFFF
    return (_seed / 0x3FFFFFFF) - 1.0


def sines(dur, parts, tau):
    """parts: list of (freq, amplitude). One shared exponential decay."""
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        v = sum(a * math.sin(2 * math.pi * f * t) for f, a in parts)
        out.append(v * env(t, tau))
    return out


# ── the opening bloom: the only long sound in the video ────────────────────
def bloom(dur=1.8):
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        # a slow rise then a long tail — the shape of the glow coming up out of black
        a = (t / 0.9) if t < 0.9 else env(t - 0.9, 0.55)
        f = 55 + 55 * (t / dur)
        v = (math.sin(2 * math.pi * f * t) * 0.75 +
             math.sin(2 * math.pi * f * 2 * t) * 0.22 +
             math.sin(2 * math.pi * f * 3.01 * t) * 0.08)
        out.append(v * a)
    return out


# ── a rising generate tone ─────────────────────────────────────────────────
def gen(dur=0.75):
    n = int(dur * SR)
    out = []
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = 300 + 620 * (t / dur) ** 1.4
        ph += 2 * math.pi * f / SR
        a = min(t / 0.06, 1.0) * (1.0 if t < dur - 0.18 else (dur - t) / 0.18)
        out.append((math.sin(ph) * 0.8 + math.sin(ph * 2) * 0.15) * a)
    return out


# ── a short downward swipe for a strike-through ────────────────────────────
def swipe(dur=0.3):
    n = int(dur * SR)
    out = []
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = 520 - 380 * (t / dur)
        ph += 2 * math.pi * f / SR
        out.append((math.sin(ph) * 0.55 + noise() * 0.30) * env(t, 0.085))
    return out


# ── two-note confirm ───────────────────────────────────────────────────────
def chime(dur, f1, f2, tau, gap=0.10):
    n = int(dur * SR)
    g = int(gap * SR)
    out = []
    for i in range(n):
        t = i / SR
        v = math.sin(2 * math.pi * f1 * t) * env(t, tau)
        if i >= g:
            t2 = (i - g) / SR
            v += math.sin(2 * math.pi * f2 * t2) * env(t2, tau) * 0.85
        out.append(v * 0.6)
    return out


write("sfx-bloom.wav", bloom(), 0.85)
write("sfx-gen.wav", gen(), 0.55)
write("sfx-swipe.wav", swipe(), 0.7)
write("sfx-done.wav", chime(0.55, 880, 1318.5, 0.13), 0.6)
write("sfx-select.wav", chime(0.85, 523.25, 783.99, 0.30, 0.06), 0.7)
# tick: a chip or a label arriving. Quiet and very short — this one plays most often.
write("sfx-tick.wav", sines(0.10, [(1760, 0.7), (2640, 0.2)], 0.022), 0.5)
# pop: a card or poster materialising, a little rounder than the tick
write("sfx-pop.wav", sines(0.16, [(784, 0.7), (1174, 0.3)], 0.042), 0.55)
# click: the cursor. Dry and small.
write("sfx-click.wav", sines(0.06, [(2400, 0.6), (1100, 0.4)], 0.010), 0.6)
