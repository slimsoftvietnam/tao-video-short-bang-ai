# Sentence list + scene plan for the aligner.
#
# Voice-first: the recording already exists, so the estimate below is only the scaffold
# align-asr.py matches against. Every cue in index.html is written in the recorded seconds that
# align-asr.py / syl-times.py measure — nothing is remapped.
#
# SCRIPT.md holds ONE SENTENCE PER PLAIN LINE, exactly as spoken. Lines starting with # - > |
# are skipped (a script written as a markdown table yields zero sentences).
import io
import json
import re
import sys

PACE = 3.62          # syllables per second — only seeds the aligner
GAP = 0.35
GAP_Q = 0.55

SENT = [s.strip() for s in io.open("SCRIPT.md", encoding="utf-8").read().split("\n")
        if s.strip() and not s.strip().startswith(("#", "-", ">", "|"))]

# ── PER-PROJECT ──────────────────────────────────────────────────────────────────
# sentence index (1-based, inclusive) -> scene: (id, label, the idea the picture must show, first, last)
# Every sentence belongs to exactly one scene; the ids become the wrappers #w-<id> and the seam ledger.
SCENES = [
    ("h1",  "HOOK",   "the promise in one picture: the product, its logo, something moving", 1, 1),
    ("s1",  "STEP 1", "first step",                                                            2, 2),
    ("p1",  "PROMPT", "the prompt card, lit word by word",                                     3, 4),
    ("cta", "CTA",    "comment keyword in a chat input",                                       5, 5),
]
# ──────────────────────────────────────────────────────────────────────────────────


def syllables(s):
    return len([w for w in re.split(r"\s+", re.sub(r"[^\w\sÀ-ỹ]", " ", s)) if w])


if not SENT:
    sys.exit("SCRIPT.md has no sentences — one sentence per plain line")
covered = sorted(i for _, _, _, a, b in SCENES for i in range(a, b + 1))
if covered != list(range(1, len(SENT) + 1)):
    print("  WARNING: SCENES cover sentences %s, SCRIPT.md has 1-%d" % (covered, len(SENT)))

t = 0.0
sent = []
for i, s in enumerate(SENT, 1):
    n = syllables(s)
    d = n / PACE
    sent.append({"i": i, "text": s, "syl": n, "start": round(t, 2), "end": round(t + d, 2), "dur": round(d, 2)})
    t += d + (GAP_Q if s.rstrip().endswith("?") else GAP)

VO_END = round(sent[-1]["end"], 2)
scenes = []
for sid, label, idea, a, b in SCENES:
    if b > len(sent):
        continue
    scenes.append({"id": sid, "label": label, "idea": idea, "start": sent[a - 1]["start"], "end": sent[b - 1]["end"],
                   "dur": round(sent[b - 1]["end"] - sent[a - 1]["start"], 2), "sentences": [a, b]})

CTA_HOLD = 2.2
EC_IN = round(VO_END + CTA_HOLD, 2)
EC_DUR = 2.75        # the house end card runs at 2x (5.5 s -> 2.75 s)
plan = {"pace": PACE, "vo_end": VO_END, "ec_in": EC_IN, "duration": round(EC_IN + EC_DUR, 2),
        "sentences": sent, "scenes": scenes}
json.dump(plan, io.open("beats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("  %d sentences, %d scenes" % (len(sent), len(scenes)))
for s in scenes:
    print("  %-4s %-10s %6.2fs %6.2fs %6.2fs   %d-%d" % (s["id"], s["label"], s["start"], s["end"], s["dur"],
                                                     s["sentences"][0], s["sentences"][1]))
