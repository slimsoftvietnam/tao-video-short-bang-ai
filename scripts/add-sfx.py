# Music bed + sound effects. Sole owner of the #music-bed and sx*** elements: it
# deletes what it previously wrote and regenerates, so it is safe to re-run.
#
# TIMES ARE REAL SECONDS — this composition is authored straight in recorded time.
#
# LEVELS come from the measured model, not from taste:
#     output dB = file mean dB + 20*log10(gain)
# Voice sits at -21.0 LUFS. Targets and file means (measured 2026-09-22):
#     thud     -22   file -11.7   gain 0.30
#     swoosh   -28   file -24.9   gain 0.70
#     pop      -29   file -21.0   gain 0.40  (0.26 inside a fast cascade)
#     laser    -26   active -21   gain 0.55  (the file's 0.05s lead-in is silence, so the
#                                            cue is written 0.05s before the moment)
#     riser    -24   peak  -8.5   gain 0.17  (the build sits UNDER the voice)
#     click    -30   file -25.7   gain 0.60  (the camera shutter, cut from "sound chụp ảnh nhanh")
#     bed      -33   file -19.8   gain 0.219 (Little Things Immaterial from 0:00, mean over the film's
#                                            105 s; 12 dB under the voice — between the house -31 and
#                                            the -35 the author asked for on the last video)

import io
import json
import re

P = "index.html"
_html = io.open(P, encoding="utf-8").read()


def _attr_of(el_id, attr):
    m = re.search(r'<\w+(?=[^>]*(?<![-\w])id="%s")[^>]*>' % re.escape(el_id), _html)
    assert m, "element not found: #" + el_id
    v = re.search(r'\b%s="([^"]*)"' % re.escape(attr), m.group(0))
    assert v, "#%s has no %s" % (el_id, attr)
    return float(v.group(1))


# Read, never retype.
DUR = _attr_of("root", "data-duration")
VO_END = _attr_of("vo", "data-duration")

G_THUD = 0.30
G_SWOOSH = 0.70
G_POP = 0.40
G_POP_SOFT = 0.26
G_LASER = 0.55
G_RISER = 0.17
G_BED = 0.219
G_CLICK = 0.60

DURATION = {"thud": 3.11, "swoosh": 1.12, "pop": 0.72, "laser": 0.37, "risercut3": 3.20, "click": 0.25}

# The author's rules, applied literally:
#   thud    once, at the start of the video
#   swoosh  every scene change — exactly the ledger's cut times
#   pop     only when an IMPORTANT icon appears ("hạn chế pop"), never within ~0.5s of a swoosh;
#           a mark that lands ON its word is led by 0.16 s (the file opens on 0.18 s of silence)
#   laser   a selection: a click on a control the picture shows (Download, a menu item, a send button)
#   click   the camera shutter (house: an important number) — "1 câu lệnh", "60M+", "125 credits"
#   riser   the hook's tension, cut by hand ("tự cắt ghép để thể hiện yếu tố kịch tính"): sfx-risercut3.mp3
#           is the riser's first 3.20 s, so a cue at t peaks at t + 3.20 — put that peak on the last word
#           of the hook's first sentence, where the picture stops dead (flash + snap)
THUD = [(0.00, "thud", G_THUD)]
SWOOSH = [(float(r["cut"]), "swoosh", G_SWOOSH)
          for r in json.load(io.open("ledger.json", encoding="utf-8"))["seams"]]

# ── PER-PROJECT ─────────────────────────────────────────────────────────────
BED = "assets/audio/bgm-little-things.mp3"     # the house bed; any track works — the gain below assumes
                                               # a file mean near -16 dB (re-measure a new track)
RISER = []        # e.g. [(1.36, "risercut3", G_RISER)]   -> peaks at 4.56
LASER = [(t - 0.05, "laser", G_LASER) for t in (
)]                # e.g. 18.04, 27.22 — the moment of each click
CLICK = [(t, "click", G_CLICK) for t in (
)]                # e.g. 35.50 — an important number landing
# (time, soft?) — only marks and objects that carry the point of their sentence (house-style §7:
# about one every 3-4 s), never within ~0.5 s of a swoosh; lead a mark that lands ON its word by 0.16 s
POP = [
]                 # e.g. (1.42, 0), (15.16, 0), (42.36, 1), ... and the end-card logo at EC + 0.06

rows = THUD + SWOOSH + RISER + LASER + CLICK + [(t, "pop", G_POP_SOFT if soft else G_POP) for t, soft in POP]
rows.sort()

s = io.open(P, encoding="utf-8").read()
before = len(re.findall(r'<audio\s[^>]*\bid="sx\d+"', s))
s = re.sub(r'[ \t]*<audio\s[^>]*\bid="sx\d+"[^>]*>\s*</audio>\n?', "", s)
s = re.sub(r'[ \t]*<audio\s[^>]*\bid="music-bed"[^>]*>\s*</audio>\n?', "", s, flags=re.S)

# The bed lifts once the voice stops so the end card is not silent, and is gone by the
# last frame (a late, steep drop: a dB-linear ramp is already at -30 halfway).
CHAIN = ('{"version":1,"nodes":[{"type":"gain","id":"bedlevel",'
         '"label":"Bed level","params":{"gain":0}}]}')
AUTO = ('{"version":1,"lanes":[{"target":"fx.bedlevel.gain","points":['
        '{"t":0,"v":-60},{"t":0.4,"v":0},'
        '{"t":%.2f,"v":0},{"t":%.2f,"v":3},{"t":%.2f,"v":3},'
        '{"t":%.2f,"v":-6},{"t":%.1f,"v":-60}]}]}'
        % (VO_END - 0.6, VO_END + 1.0, DUR - 1.4, DUR - 0.5, DUR))

import os
bed = "" if not os.path.exists(BED) else ('      <audio id="music-bed" class="clip" data-start="0" data-duration="%.1f"\n'
       '             data-track-index="9" src="%s"\n'
       '             data-volume="%.3f" data-audio-group="music"\n'
       "             data-fx-chain='%s'\n"
       "             data-automation='%s'></audio>\n\n" % (DUR, BED, G_BED, CHAIN, AUTO))

# ── PREMIX ──────────────────────────────────────────────────────────────────
# A 3.7-minute film with ~100 separate <audio> cues did not load: the runtime fetches
# and decodes every media element on its own (no de-duplication, cache: no-store), the
# Studio preview froze at 00:00 ("did not reload — took too long"), and every headless
# snapshot/thumbnail blew the 10 s navigation limit. So the cues are mixed here, once,
# into ONE track with exactly the same times and gains, and the page carries three
# audio elements (voice, bed, effects) instead of ~100. sfx-cues.json keeps the list.
# Set PREMIX = False to go back to one element per cue.
PREMIX = True
MIX = "assets/audio/sfx-mix.mp3"

block = []
if PREMIX:
    # Decode each sound once (48 kHz stereo float), add it in at its sample offset with
    # its gain, write 16-bit WAV, encode. (ffmpeg amix over ~100 delayed inputs crawled.)
    import subprocess
    import numpy as np
    SR = 48000
    pcm = {}
    for snd in sorted({r[1] for r in rows}):
        raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", "assets/audio/sfx-%s.mp3" % snd,
                              "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], check=True, capture_output=True).stdout
        pcm[snd] = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    mix = np.zeros((int(round(DUR * SR)), 2), dtype=np.float64)
    for t, snd, g in rows:
        clip = pcm[snd][:int(round(DURATION[snd] * SR))]
        a = int(round(t * SR))
        b = min(len(mix), a + len(clip))
        mix[a:b] += g * clip[:b - a]
    peak = float(np.abs(mix).max())
    assert peak < 1.0, "effects mix clips (peak %.3f) — lower the gains" % peak
    wav = "assets/audio/sfx-mix.wav"
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).round().astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav,
                    "-c:a", "libmp3lame", "-q:a", "2", MIX], check=True)
    import os
    os.remove(wav)
    print("  effects premix: %d cues -> %s (peak %.2f)" % (len(rows), MIX, peak))
    json.dump([{"t": round(t, 3), "sound": snd, "gain": g, "dur": DURATION[snd]} for t, snd, g in rows],
              io.open("sfx-cues.json", "w", encoding="utf-8"), indent=1)
    block.append(
        '      <audio id="sx000" class="clip" data-start="0" data-duration="%.1f"\n'
        '             data-track-index="12" src="%s"\n'
        '             data-volume="1" data-audio-group="sfx"></audio>\n' % (DUR, MIX))
else:
    for i, (t, snd, g) in enumerate(rows):
        block.append(
            '      <audio id="sx%03d" class="clip" data-start="%.3f" data-duration="%.2f"\n'
            '             data-track-index="%d" src="assets/audio/sfx-%s.mp3"\n'
            '             data-volume="%.2f" data-audio-group="sfx"></audio>\n'
            % (i, t, DURATION[snd], 12 + (i % 8), snd, g))

anchor = "      <!-- sfx cues are written by scripts/add-sfx.py -->"
assert s.count(anchor) == 1, "sfx anchor comment not found"
s = s.replace(anchor, anchor + "\n" + bed + "".join(block), 1)
io.open(P, "w", encoding="utf-8").write(s)

kinds = {}
for _, snd, _ in rows:
    kinds[snd] = kinds.get(snd, 0) + 1
print("  xoa %d cue cu, ghi %d cue moi" % (before, len(rows)))
print("  " + "  ".join("%s x%d" % (k, v) for k, v in sorted(kinds.items())))
print("  nhac nen: Little Things Immaterial tu 0:00, gain %.3f -> ~-33.0 dB (12 dB duoi giong)" % G_BED)
