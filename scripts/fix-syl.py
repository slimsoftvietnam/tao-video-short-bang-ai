# Snap syllable starts out of silence.
#
# Whisper sometimes stamps the first word after a pause at the START of the pause
# ("Tiếp" at 27.70 when the voice resumes at 28.21; "Hãy" at 60.74 vs 60.99). A caption
# or a prompt word lit on that stamp lights up to half a second before it is heard.
# Rule, measured on the recording: if a syllable's stamped start sits inside a run of
# 20 ms frames under -45 dB, move it to the end of that run (never past its own end).
# Run after syl-times.py; idempotent.
import io
import json
import subprocess

import numpy as np

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "assets/audio/src/voiceover-master.wav",
                      "-f", "s16le", "-ac", "1", "-ar", "24000", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
hop = 480
n = len(a) // hop
db = 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
quiet = db < -45

syl = json.load(io.open("syl-times.json", encoding="utf-8"))
moved = []
for x in syl:
    i = int(round(x["s"] / 0.02))
    if i < n and quiet[i]:
        j = i
        while j < n and quiet[j]:
            j += 1
        t = round(j * 0.02, 2)
        if t - x["s"] >= 0.06 and t < x["e"] - 0.04:
            moved.append((x["i"], x["syl"], x["s"], t))
            x["s"] = t
            continue
    # the other failure: the stamp sits on the previous word's tail and the syllable's
    # own span swallows the whole pause ("Tiếp" 27.70-28.36 around a 27.76-28.22 gap)
    i0, i1 = int(round(x["s"] / 0.02)), int(round(x["e"] / 0.02))
    k = i0
    while k < min(i1, n):
        if quiet[k]:
            j = k
            while j < n and quiet[j]:
                j += 1
            t = round(j * 0.02, 2)
            if (j - k) * 0.02 >= 0.2 and t < x["e"] - 0.06:
                moved.append((x["i"], x["syl"], x["s"], t))
                x["s"] = t
                break
            k = j
        k += 1
json.dump(syl, io.open("syl-times.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for m in moved:
    print("  sent %2d  %-10s %6.2f -> %6.2f" % m)
print("  %d syllable starts moved out of silence" % len(moved))
