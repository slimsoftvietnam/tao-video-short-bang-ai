# Place the sound effects. Sole owner of the sfx cues: it deletes every element it
# previously wrote and regenerates them, so it is safe to re-run after any retiming.
#
# WHY THE TIMES ARE COMPUTED HERE. `data-start` on an <audio> element is a plain
# attribute the framework reads directly — nothing puts it through the runtime's T().
# Every other narration-bound cue in this composition IS mapped, so if these were
# written as authored times the sound would drift away from the picture by exactly the
# amount the reader deviated from the estimate. So T() is applied in Python, from the
# same timing-map.json that install-map.py wrote into the HTML and read back.
#
# RESTRAINT. The brief bans overusing whoosh/flash/glitch and a video that pings on
# every element becomes a slot machine. Most cues here are ticks at 0.18-0.22 gain,
# which lands them about level with the music bed and well under the voice. Only four
# sounds are allowed to be noticed: the opening bloom, the two strike-throughs, and the
# selection — the moment the whole argument turns on.
import io
import json
import re

P = "index.html"
s = io.open(P, encoding="utf-8").read()
m = json.load(io.open("timing-map.json", encoding="utf-8"))
OLD, NEW = m["OLD"], m["NEW"]


def T(t):
    if t <= 0:
        return max(t, 0.0)
    for i in range(len(OLD)):
        if t <= OLD[i][1] or i == len(OLD) - 1:
            span = OLD[i][1] - OLD[i][0]
            f = (t - OLD[i][0]) / span if span > 0 else 0.0
            return NEW[i][0] + f * (NEW[i][1] - NEW[i][0])
    return t


DUR = {"bloom": 1.80, "gen": 0.75, "swipe": 0.30, "done": 0.55,
       "select": 0.85, "tick": 0.10, "pop": 0.16, "click": 0.06}

# (authored_time, sound, gain). Times are AUTHORED and go through T() below. They mirror
# the timeline exactly — every one of these was moved in revision 7 onto the measured
# position of the word it accompanies, so this list must be updated whenever the
# timeline is. A cue left at an old position is a sound with nothing under it.
CUES = [
    # hook — the bloom under the question, then the answer surfacing behind it
    (0.05, "bloom", 0.19),
    (2.30, "pop", 0.13), (2.52, "pop", 0.13), (3.08, "pop", 0.13), (3.56, "pop", 0.13),

    # chapter 2 — the tool works, fast
    (7.90, "gen", 0.15), (8.70, "done", 0.28),
    (10.30, "tick", 0.22), (12.00, "tick", 0.22), (12.90, "tick", 0.22), (15.40, "tick", 0.22),
    (15.45, "done", 0.22),

    # chapter 3 — six things done by hand, then four of them handed over
    (27.05, "tick", 0.20), (28.05, "tick", 0.20), (28.55, "tick", 0.20),
    (29.75, "tick", 0.20), (30.45, "tick", 0.20), (31.05, "tick", 0.20),
    (33.25, "pop", 0.20), (33.97, "pop", 0.20), (34.69, "pop", 0.20), (35.41, "pop", 0.20),

    # chapter 5 — six options, four questions, one decision
    (39.85, "done", 0.22),
    (47.30, "tick", 0.20), (51.05, "tick", 0.20), (54.95, "tick", 0.20), (57.60, "tick", 0.20),
    (60.20, "select", 0.34),

    # chapter 6 — the old question struck out, then the two columns
    (64.60, "swipe", 0.30),
    (67.30, "tick", 0.18), (67.92, "tick", 0.18), (68.54, "tick", 0.18), (69.16, "tick", 0.18),
    (72.80, "tick", 0.20), (73.44, "tick", 0.20), (74.11, "tick", 0.20), (75.03, "tick", 0.20),

    # chapter 7 — VS struck out, the two names join
    (81.70, "swipe", 0.30), (83.05, "pop", 0.26),
    (84.05, "tick", 0.20), (84.77, "tick", 0.20), (85.49, "tick", 0.20),

    # chapter 8 — the count, then the closing question
    (93.30, "tick", 0.18), (93.80, "tick", 0.18), (94.30, "tick", 0.18), (94.80, "tick", 0.18),
    (94.00, "done", 0.24),

    # CTA
    (101.00, "click", 0.30), (102.90, "pop", 0.24),
]

# The end card has no narration under it, so these are REAL seconds and must NOT be
# mapped — T() past the last anchor extrapolates and would land them early.
EC = 101.39
REAL_CUES = [(EC + 1.95, "click", 0.32), (EC + 2.10, "select", 0.30)]

# ── remove whatever a previous run wrote ───────────────────────────────────
before = len(re.findall(r'<audio\s[^>]*\bid="sx\d\d"', s))
s = re.sub(r'[ \t]*<audio\s[^>]*\bid="sx\d\d"[^>]*>\s*</audio>\n?', "", s)

rows = [(round(T(t), 3), snd, g) for t, snd, g in CUES]
rows += [(round(t, 3), snd, g) for t, snd, g in REAL_CUES]
rows.sort()

block = []
for i, (t, snd, g) in enumerate(rows):
    block.append(
        '      <audio id="sx%02d" class="clip" data-start="%.3f" data-duration="%.2f"\n'
        '             data-track-index="%d" src="assets/audio/sfx-%s.wav"\n'
        '             data-volume="%.2f" data-audio-group="sfx"></audio>\n'
        % (i, t, DUR[snd], 12 + (i % 8), snd, g))

anchor = re.search(r'[ \t]*<div\s[^>]*\bid="mascot"[^>]*>', s)
assert anchor, "mascot wrapper not found (used as the insertion point)"
s = s[:anchor.start()] + "".join(block) + "\n" + s[anchor.start():]

io.open(P, "w", encoding="utf-8").write(s)

kinds = {}
for _, snd, _ in rows:
    kinds[snd] = kinds.get(snd, 0) + 1
print("  removed %d old cue(s), wrote %d" % (before, len(rows)))
print("  " + "  ".join("%s x%d" % (k, v) for k, v in sorted(kinds.items())))
print("  first %.2fs  last %.2fs" % (rows[0][0], rows[-1][0]))
