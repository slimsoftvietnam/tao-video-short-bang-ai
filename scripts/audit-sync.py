# Audit every narration-bound cue against the sentence actually playing when it fires.
#
# Reading the picture against the CAPTIONS is circular — both come from the same map, so
# a shifted map looks self-consistent. This instead maps each authored cue time through
# T() and reports which recorded sentence covers that instant, plus how far into that
# sentence it lands. A cue that fires in the sentence BEFORE the one it illustrates is
# the picture running ahead of the voice.
import io
import json
import re
import sys

align = json.load(io.open("vo-alignment.json", encoding="utf-8"))
SENT = align["sentences"]
OLD = [[s["oldA"], s["oldB"]] for s in SENT]
NEW = [[s["newA"], s["newB"]] for s in SENT]


def T(t):
    if t <= 0:
        return max(t, 0.0)
    for i in range(len(OLD)):
        if t <= OLD[i][1] or i == len(OLD) - 1:
            span = OLD[i][1] - OLD[i][0]
            f = (t - OLD[i][0]) / span if span > 0 else 0.0
            return NEW[i][0] + f * (NEW[i][1] - NEW[i][0])
    return t


def sentence_at(rt):
    for i, s in enumerate(SENT, 1):
        if s["newA"] <= rt <= s["newB"]:
            frac = (rt - s["newA"]) / max(s["newB"] - s["newA"], 1e-6)
            return i, s, frac
    return None, None, None


src = io.open("index.html", encoding="utf-8").read()
lo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
hi = float(sys.argv[2]) if len(sys.argv) > 2 else 1e9

# every TL.* call ends with `, <number>);` — capture the selector and that time
rows = []
for m in re.finditer(r'TL\.(?:to|fromTo|set)\(\s*"([^"]+)"[^;]*?,\s*([\d.]+)\s*\)\s*;', src, re.S):
    sel, at = m.group(1), float(m.group(2))
    rt = T(at)
    if lo <= rt <= hi:
        rows.append((rt, at, sel))
# show(...) / hide(...) helpers
for m in re.finditer(r'\b(show|hide)\("([^"]+)",\s*([\d.]+)', src):
    kind, sel, at = m.group(1), m.group(2), float(m.group(3))
    rt = T(at)
    if lo <= rt <= hi:
        rows.append((rt, at, ("%s %s" % (kind, sel))))
# cam(k, t, d)
for m in re.finditer(r'\bcam\((\d+),\s*([\d.]+)', src):
    k, at = m.group(1), float(m.group(2))
    rt = T(at)
    if lo <= rt <= hi:
        rows.append((rt, at, "CAMERA -> scene %s" % k))

rows.sort()
seen = set()
print("  real   authored  in-sentence            cue")
for rt, at, sel in rows:
    if sel.startswith("#cue") or " #cue" in sel:
        continue                      # captions come from the same map; not evidence
    key = (round(rt, 2), sel)
    if key in seen:
        continue
    seen.add(key)
    i, s, frac = sentence_at(rt)
    where = "s%-2d %3d%%" % (i, frac * 100) if i else "(no speech)"
    txt = s["text"][:30] if s else ""
    print("  %6.2f  %7.2f  %-11s %-32s %s" % (rt, at, where, txt, sel))
