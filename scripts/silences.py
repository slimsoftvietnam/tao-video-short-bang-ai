# For every gap between two sentences of the recording: the silent stretch around it
# (20 ms RMS < -45 dBFS) and its midpoint, so each scene cut can sit in silence.
import json
import subprocess
import sys

import numpy as np

SR = 16000
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "assets/audio/voiceover.mp3", "-ac", "1", "-ar", str(SR),
                      "-f", "s16le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
W = int(0.02 * SR)
n = len(x) // W
rms = np.sqrt(np.mean(x[: n * W].reshape(n, W) ** 2, axis=1) + 1e-12)
db = 20 * np.log10(rms)
quiet = db < -45.0

syl = json.load(open("syl-times.json", encoding="utf-8"))
lines = {}
for s in syl:
    a, b = lines.get(s["i"], (1e9, -1e9))
    lines[s["i"]] = (min(a, s["s"]), max(b, s["e"]))
ids = sorted(lines)
print("voice %.2fs, %d sentences" % (len(x) / SR, len(ids)))
for k in range(len(ids) - 1):
    e, s = lines[ids[k]][1], lines[ids[k + 1]][0]
    i0, i1 = int(e / 0.02), int(s / 0.02)
    # widen to the quiet run that contains the gap's middle
    m = (i0 + i1) // 2
    if not quiet[m]:
        print("%2d|%2d  gap %.2f-%.2f  middle NOT quiet" % (ids[k], ids[k + 1], e, s))
        continue
    a = m
    while a > 0 and quiet[a - 1]:
        a -= 1
    b = m
    while b + 1 < n and quiet[b + 1]:
        b += 1
    print("%2d|%2d  words %.2f-%.2f   silence %.2f-%.2f   mid %.2f" % (ids[k], ids[k + 1], e, s, a * 0.02, (b + 1) * 0.02,
                                                                       (a + b + 1) * 0.01))
if len(sys.argv) > 1:
    for t in map(float, sys.argv[1:]):
        i = int(t / 0.02)
        print("t=%.2f  %s  (%.1f dB)" % (t, "quiet" if quiet[i] else "LOUD", db[i]))
