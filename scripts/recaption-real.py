# Captions, generated from the REAL sentence times in vo-alignment.json.
#
# This is the variant of recaption.py for a project whose voice existed before the
# picture. The original reads beats.json (authored estimate) and relies on the
# runtime's OLD/NEW remap to land the cues on the recording. There is no remap in
# this composition — the timeline is authored in recorded seconds — so the captions
# read their times straight from the alignment. One fewer indirection, one fewer
# thing that can silently drift.
#
# Sole owner of #captions and the <captions:auto> block: it clears both and
# regenerates them, so it is safe to re-run after any retiming.
import io
import json
import re

MAXW = 7           # words per cue
GAP = 0.20         # dead air between cues, in recorded seconds
FADE = 0.16

# Words the design calls out. Kept deliberately short: "các con vợ" and "ChatGPT"
# recur in almost every sentence, and highlighting a word that appears constantly
# teaches the eye nothing.
HILITE = ["PROMPT", "chuyên gia", "đào sâu", "Đừng dừng", "đặt câu hỏi đúng",
          "10 cách", "nhìn ra nhiều hướng"]

align = json.load(io.open("vo-alignment.json", encoding="utf-8"))


def words(s):
    return [w for w in s.split() if w]


def split_cue(text):
    """Break one sentence into cues of at most MAXW words, preferring the author's
    own commas — Vietnamese comma placement tracks breath groups closely."""
    if len(words(text)) <= MAXW:
        return [text.strip()]
    parts = [p.strip() for p in re.split(r"(?<=[,:;])\s+", text) if p.strip()]
    out = []
    for p in parts:
        w = words(p)
        if len(w) <= MAXW:
            out.append(p)
            continue
        n = (len(w) + MAXW - 1) // MAXW
        size = (len(w) + n - 1) // n
        for i in range(0, len(w), size):
            out.append(" ".join(w[i:i + size]))
    return out


def emphasise(text):
    """Longest term first, so a short term cannot half-match a longer one."""
    for term in sorted(HILITE, key=len, reverse=True):
        text = re.sub("(?<![\\w>])(" + re.escape(term) + ")(?![\\w<])",
                      r"<b>\1</b>", text, flags=re.IGNORECASE)
    return text


cues = []
for s in align["sentences"]:
    a, b = s["newA"], s["newB"]
    span = b - a
    parts = split_cue(s["text"])
    total = sum(max(1, len(words(p))) for p in parts)
    t = a
    for p in parts:
        share = span * max(1, len(words(p))) / total
        cues.append((round(t, 3), round(max(0.45, share - GAP), 3), p))
        t += share

# The cue div is the CLIP — the framework owns its visibility. The fade lives on an
# inner span, because a GSAP exit ending exactly on a clip boundary can leave stale
# visibility behind after a non-linear seek (lint: gsap_exit_missing_hard_kill).
block = []
for i, (t, d, text) in enumerate(cues):
    block.append(
        '        <div class="cap clip" id="cap%03d" data-start="%.3f" data-duration="%.3f"'
        ' data-track-index="6"><span class="capin" id="capi%03d">%s</span></div>\n'
        % (i, t, d, i, emphasise(text)))

P = "index.html"
s = io.open(P, encoding="utf-8").read()
# Rebuild the container LINE BY LINE, not with a regex.
#
# Two regex attempts got this wrong. `(.*?)</div>` stops at the first cue div;
# anchoring the close on `\n {6}</div>` still left cap001-cap105 behind, because a
# previous run's cue divs wrapped onto a second line and the shortest match landed
# somewhere inside them. Nested closing tags cannot be matched by a non-greedy
# scan — the only reliable rule here is structural: the container's own closing
# line is the first following line whose entire content is "</div>".
lines = s.split("\n")
# Match the container by its id, not by `<div id="captions">`: Studio rewrites it to
# `<div data-hf-id="hf-…" id="captions">` on the first preview, and a literal match
# then finds nothing. This worked in the project it was written for only because it
# ran before the author opened Studio; the skill's own test caught it.
_cap = re.compile(r'<div\b[^>]*(?<![-\w])id="captions"')
opens = [k for k, ln in enumerate(lines) if _cap.search(ln)]
assert len(opens) == 1, "expected exactly one #captions container, found %d" % len(opens)
k = opens[0]
if "</div>" in lines[k]:
    end = k                       # empty scaffold: <div id="captions"></div>
else:
    end = next(j for j in range(k + 1, len(lines)) if lines[j].strip() == "</div>")
s = "\n".join(lines[:k] + ['      <div id="captions">']
              + "".join(block).rstrip("\n").split("\n")
              + ["      </div>"] + lines[end + 1:])
io.open(P, "w", encoding="utf-8").write(s)

# Animation written separately so the cue divs stay pure data.
anim = []
for i, (t, d, _) in enumerate(cues):
    anim.append('      tl.fromTo("#capi%03d", { autoAlpha: 0, y: 16 },'
                ' { autoAlpha: 1, y: 0, duration: %.2f, ease: "power2.out" }, %.3f);\n'
                % (i, FADE, t))
    anim.append('      tl.to("#capi%03d", { autoAlpha: 0, duration: %.2f,'
                ' ease: "power2.in" }, %.3f);\n' % (i, FADE, t + d - FADE - 0.05))
    anim.append('      tl.set("#capi%03d", { autoAlpha: 0 }, %.3f);\n' % (i, t + d - 0.05))

s = io.open(P, encoding="utf-8").read()
s = re.sub(r"[ \t]*/\* <captions:auto> \*/.*?/\* </captions:auto> \*/\n", "", s, flags=re.S)
# The timeline's tail pin — `tl.set({}, {}, <duration>);` — is found by pattern so
# this script needs no per-project edit. It lives in <script>, which Studio never
# rewrites, so matching it is safe.
tails = re.findall(r"[ \t]*tl\.set\(\{\}, \{\}, [0-9.]+\);", s)
assert len(tails) == 1, "expected one `tl.set({}, {}, <dur>);` tail pin, found %d" % len(tails)
anchor = tails[0]
s = s.replace(anchor, "      /* <captions:auto> */\n" + "".join(anim)
              + "      /* </captions:auto> */\n\n" + anchor, 1)
io.open(P, "w", encoding="utf-8").write(s)

print("  %d cue phu de, %.2fs -> %.2fs" % (len(cues), cues[0][0], cues[-1][0] + cues[-1][1]))
longest = max(cues, key=lambda c: len(c[2]))
print("  cue dai nhat: %d ky tu — %s" % (len(longest[2]), longest[2]))
