# Per-syllable times, for cues that land on a word and for karaoke captions.
#
# align-asr.py only keeps sentence windows. This runs the same edit-distance match
# (script syllables against recognised syllables, diacritics folded) and keeps the
# time of EVERY script syllable, so a cue can be written at the instant its word
# starts and a caption can light each word as it is spoken.
#
# Unmatched syllables (none on a clean take) are interpolated between their matched
# neighbours so every syllable still carries a time.
#
# Writes syl-times.json: [{"i": sentence, "k": index in sentence, "syl": text as
# written in SCRIPT.md (with its punctuation), "s": start, "e": end}]
import io
import json
import re
import sys
import unicodedata


def fold(s):
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def clean(tok):
    return re.sub(r"[^\w]", "", tok).lower()


beats = json.load(io.open("beats.json", encoding="utf-8"))
asr = json.load(io.open("asr-words.json", encoding="utf-8"))
align = json.load(io.open("vo-alignment.json", encoding="utf-8"))
WIN = {x["i"]: (x["newA"], x["newB"]) for x in align["sentences"]}

SCRIPT = []            # (clean, raw token, sentence, index in sentence)
for s in beats["sentences"]:
    toks = [t for t in s["text"].split() if clean(t)]
    for k, t in enumerate(toks):
        SCRIPT.append((clean(t), t, s["i"], k))

HEARD = []
for w in asr["words"]:
    parts = [p for p in (clean(x) for x in re.split(r"[\s\-]+", w["w"])) if p]
    if not parts:
        continue
    span = (w["e"] - w["s"]) / len(parts)
    for k, p in enumerate(parts):
        HEARD.append((p, w["s"] + k * span, w["s"] + (k + 1) * span))

SUB_EXACT, SUB_FOLDED, SUB_BAD, GAP = 0.0, 0.25, 1.0, 0.7
sf = [fold(x[0]) for x in SCRIPT]
hf = [fold(x[0]) for x in HEARD]
n, m = len(SCRIPT), len(HEARD)
INF = float("inf")
prev = [j * GAP for j in range(m + 1)]
back = [[2] * (m + 1)] + [[1] + [0] * m for _ in range(n)]
for i in range(1, n + 1):
    cur = [i * GAP] + [INF] * m
    for j in range(1, m + 1):
        if SCRIPT[i - 1][0] == HEARD[j - 1][0]:
            c = SUB_EXACT
        elif sf[i - 1] == hf[j - 1]:
            c = SUB_FOLDED
        else:
            c = SUB_BAD
        best, bk = prev[j - 1] + c, 0
        if prev[j] + GAP < best:
            best, bk = prev[j] + GAP, 1
        if cur[j - 1] + GAP < best:
            best, bk = cur[j - 1] + GAP, 2
        cur[j], back[i][j] = best, bk
    prev = cur

match = [None] * n
i, j = n, m
while i > 0 and j > 0:
    b = back[i][j]
    if b == 0:
        match[i - 1] = j - 1
        i, j = i - 1, j - 1
    elif b == 1:
        i -= 1
    else:
        j -= 1

out = []
for k, (c, raw, si, sk) in enumerate(SCRIPT):
    if match[k] is not None:
        h = HEARD[match[k]]
        out.append({"i": si, "k": sk, "syl": raw, "s": round(h[1], 3), "e": round(h[2], 3), "m": 1})
    else:
        out.append({"i": si, "k": sk, "syl": raw, "s": None, "e": None, "m": 0})

# interpolate the unmatched ones inside their sentence window
for k, x in enumerate(out):
    if x["s"] is None:
        a = next((out[q]["e"] for q in range(k - 1, -1, -1) if out[q]["s"] is not None), WIN[x["i"]][0])
        b = next((out[q]["s"] for q in range(k + 1, len(out)) if out[q]["s"] is not None), WIN[x["i"]][1])
        x["s"], x["e"] = round(a, 3), round(b, 3)

json.dump(out, io.open("syl-times.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("  %d syllables, %d matched" % (len(out), sum(x["m"] for x in out)))

if "-q" not in sys.argv:
    cur = None
    line = ""
    for x in out:
        if x["i"] != cur:
            if line:
                print(line)
            cur = x["i"]
            line = "%2d |" % cur
        line += " %s@%.2f" % (x["syl"], x["s"])
    print(line)
