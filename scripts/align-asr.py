# Build the timing map from the transcription instead of from pause lengths.
#
# The previous aligner inferred sentence boundaries from silence structure and a
# reading-rate model. That works when the reader pauses cleanly at every full stop; on
# this take they do not, and it put boundaries 0.3-1.8s early — the picture running
# slightly ahead of the voice, twice reported and not fixable by re-weighting, because
# the rate band rather than the seam term was binding.
#
# Here the script is aligned to the RECOGNISED WORDS by edit distance, so a boundary is
# the timestamp of an actual word rather than a guess about a gap. ASR gets Vietnamese
# wrong in predictable ways — diacritics dropped, syllables merged or split, homophones
# swapped — so the matcher scores a diacritic-insensitive match almost as well as an
# exact one and tolerates insertions and deletions on both sides.
import io
import json
import re
import unicodedata

# ── normalisation ──────────────────────────────────────────────────────────
def strip_marks(s):
    """Fold diacritics so 'nghiệp' and 'nghiep' compare as near-equal. Vietnamese đ/Đ
    is a distinct letter, not a combining mark, so it is handled explicitly."""
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def syllables(text):
    text = re.sub(r"[^\w\sÀ-ỹĐđ]", " ", text)
    return [w.lower() for w in text.split() if w]


# ── inputs ─────────────────────────────────────────────────────────────────
beats = json.load(io.open("beats.json", encoding="utf-8"))
asr = json.load(io.open("asr-words.json", encoding="utf-8"))

# script side: one flat syllable stream, remembering which sentence each came from
SCRIPT = []
for s in beats["sentences"]:
    for syl in syllables(s["text"]):
        SCRIPT.append((syl, s["i"]))

# ASR side: whisper sometimes emits several syllables in one token; split them and
# divide the token's span proportionally so every syllable carries a time.
HEARD = []
for w in asr["words"]:
    parts = syllables(w["w"])
    if not parts:
        continue
    span = (w["e"] - w["s"]) / len(parts)
    for k, p in enumerate(parts):
        HEARD.append((p, w["s"] + k * span, w["s"] + (k + 1) * span))

print("  script %d syllables · heard %d syllables · audio %.2fs"
      % (len(SCRIPT), len(HEARD), asr["duration"]))

# ── edit-distance alignment ────────────────────────────────────────────────
SUB_EXACT, SUB_FOLDED, SUB_BAD, GAP = 0.0, 0.25, 1.0, 0.7

sf = [strip_marks(x[0]) for x in SCRIPT]
hf = [strip_marks(x[0]) for x in HEARD]
n, m = len(SCRIPT), len(HEARD)

INF = float("inf")
prev = [j * GAP for j in range(m + 1)]
back = [[0] * (m + 1) for _ in range(n + 1)]
for j in range(m + 1):
    back[0][j] = 2                       # came from the left (ASR insertion)
for i in range(1, n + 1):
    cur = [i * GAP] + [INF] * m
    back[i][0] = 1                       # came from above (script deletion)
    a, af = SCRIPT[i - 1][0], sf[i - 1]
    for j in range(1, m + 1):
        if a == HEARD[j - 1][0]:
            c = SUB_EXACT
        elif af == hf[j - 1]:
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

# walk back, recording for each script syllable which heard syllable it matched
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

matched = sum(1 for x in match if x is not None)
exact = sum(1 for k, x in enumerate(match)
            if x is not None and SCRIPT[k][0] == HEARD[x][0])
print("  matched %d/%d syllables (%.1f%%), %d exact (%.1f%%)"
      % (matched, n, 100.0 * matched / n, exact, 100.0 * exact / n))
if matched < 0.6 * n:
    print("\n  TOO FEW MATCHES — the transcription does not resemble the script well")
    print("  enough to align against. Try a larger model before trusting this.")
    raise SystemExit(3)

# ── sentence windows from matched word times ───────────────────────────────
SENT = []
for s in beats["sentences"]:
    idx = [k for k in range(n) if SCRIPT[k][1] == s["i"] and match[k] is not None]
    if not idx:
        print("  sentence %d matched nothing" % s["i"])
        raise SystemExit(3)
    SENT.append({"i": s["i"], "text": s["text"], "syl": s["syl"],
                 "oldA": s["start"], "oldB": s["end"],
                 "firstHeard": HEARD[match[idx[0]]][1],
                 "lastHeard": HEARD[match[idx[-1]]][2]})

# A boundary sits midway through the silence between one sentence's last word and the
# next sentence's first word, so neither cue fires while the previous line is still
# being said nor after the next has begun.
for k, x in enumerate(SENT):
    x["newA"] = round(x["firstHeard"] if k == 0
                      else (SENT[k - 1]["lastHeard"] + x["firstHeard"]) / 2, 4)
for k, x in enumerate(SENT):
    x["newB"] = round(SENT[k + 1]["newA"] if k + 1 < len(SENT) else x["lastHeard"], 4)

sceneOf = {}
for sc in beats["scenes"]:
    for i in range(sc["sentences"][0], sc["sentences"][1] + 1):
        sceneOf[i] = sc["id"]

print()
print("  #  scene  syl   authored        recorded        syl/s  line")
for x in SENT:
    d = x["newB"] - x["newA"]
    print("  %2d  %-5s  %3d   %5.1f-%-5.1f   %6.2f-%-6.2f  %5.2f  %s"
          % (x["i"], sceneOf[x["i"]], x["syl"], x["oldA"], x["oldB"],
             x["newA"], x["newB"], x["syl"] / d, x["text"][:34]))

tail = asr["duration"] - SENT[-1]["newB"]
print()
print("  script ends %.2fs · audio %.2fs · unscripted tail %.2fs"
      % (SENT[-1]["newB"], asr["duration"], tail))

scenes = {}
for sc in beats["scenes"]:
    inS = [x for x in SENT if sceneOf[x["i"]] == sc["id"]]
    scenes[sc["id"]] = [inS[0]["newA"], inS[-1]["newB"]]
print("\n  scene windows:")
for k, v in scenes.items():
    o = next(x for x in beats["scenes"] if x["id"] == k)
    print("    %-4s %6.2f-%-6.2f ->  %6.2f-%.2f" % (k, o["start"], o["end"], v[0], v[1]))

json.dump({"source": "asr", "model": asr["model"], "duration": asr["duration"],
           "scriptEndsAt": SENT[-1]["newB"], "scenes": scenes, "sentences": SENT},
          io.open("vo-alignment.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump({"OLD": [[x["oldA"], x["oldB"]] for x in SENT],
           "NEW": [[x["newA"], x["newB"]] for x in SENT]},
          io.open("timing-map.json", "w", encoding="utf-8"), indent=2)
print("\n  wrote timing-map.json and vo-alignment.json")
