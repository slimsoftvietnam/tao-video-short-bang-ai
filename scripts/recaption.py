# Captions, derived from beats.json — never hand-placed.
#
# Hand-placed captions survive exactly until the real voiceover lands and the timing
# map is rebuilt, at which point every one of them is subtly wrong and nobody can tell
# which. Generating them from the same sentence table the animation uses means one
# rebuild fixes picture and text together.
#
# A cue is 3-7 words. Sentences longer than that are split at the commas the author
# already wrote — Vietnamese comma placement tracks breath groups closely, so those are
# the natural cut points — and only failing that at word count. Each cue gets a share
# of its sentence's duration proportional to its syllable count, because a seven-word
# cue genuinely takes longer to say than a three-word one.
import io
import json
import re

MAXW = 7
# The gap is authored, so the timing map shrinks it wherever the reader went faster
# than estimated. The tightest chapter came back at ratio 0.686, and the cue fade-out
# is 0.18s and does NOT scale — so a 0.24s gap became 0.165s and the outgoing cue was
# still fading when the next one started. 0.34 leaves 0.233s at that ratio.
GAP = 0.34
HILITE = ["AI", "DESIGNER", "TẠO", "CHỌN", "ĐÁNH GIÁ", "Designer"]

beats = json.load(io.open("beats.json", encoding="utf-8"))


def words(s):
    return [w for w in s.split() if w]


def split_cue(text):
    """Break one sentence into cues of at most MAXW words."""
    if len(words(text)) <= MAXW:
        return [text.strip()]
    # try the author's own commas / colons first
    parts = [p.strip() for p in re.split(r"(?<=[,:;])\s+", text) if p.strip()]
    out = []
    for p in parts:
        w = words(p)
        if len(w) <= MAXW:
            out.append(p)
            continue
        # still too long: even chunks, as close to MAXW as divides cleanly
        n = (len(w) + MAXW - 1) // MAXW
        size = (len(w) + n - 1) // n
        for i in range(0, len(w), size):
            out.append(" ".join(w[i:i + size]))
    return out


def emphasise(text):
    """Wrap the words the design calls out. Longest first so 'ĐÁNH GIÁ' is not
    half-matched by a shorter token."""
    for term in sorted(HILITE, key=len, reverse=True):
        text = re.sub(r"(?<![\w>])(" + re.escape(term) + r")(?![\w<])",
                      r'<span class="vio">\1</span>', text)
    return text


cues = []
for s in beats["sentences"]:
    parts = split_cue(s["text"])
    syl = [max(len(words(p)), 1) for p in parts]
    total = sum(syl)
    t = s["start"]
    for p, n in zip(parts, syl):
        share = (s["end"] - s["start"]) * n / total
        cues.append({"text": p, "start": round(t, 2), "end": round(t + share, 2)})
        t += share

# strip the trailing period: a caption is not a paragraph
for c in cues:
    c["text"] = c["text"].rstrip(" .").strip()

dom = []
js = []
for i, c in enumerate(cues):
    dom.append('<div class="cue" id="cue%d">%s</div>' % (i, emphasise(c["text"])))
    end = c["end"] - GAP
    if end <= c["start"] + 0.25:          # a very short cue still needs to be readable
        end = c["start"] + 0.25
    js.append('      TL.fromTo("#cue%d", { autoAlpha: 0, y: 14 }, '
              '{ autoAlpha: 1, y: 0, duration: 0.22, ease: "power2.out" }, %.2f);\n'
              '      TL.to("#cue%d", { autoAlpha: 0, duration: 0.18, ease: "power2.in" }, %.2f);'
              % (i, c["start"], i, end))

html = io.open("index.html", encoding="utf-8").read()

# DOM. Not a regex: once this has run one time #caps holds 68 cue divs with nested
# spans, and a non-greedy `.*?</div>` closes on the FIRST child instead of on #caps,
# silently shredding the block. Walk the nesting instead. The opening tag is matched by
# pattern because Studio injects data-hf-id ahead of id when it opens the project.
_open = re.search(r'<div\s[^>]*\bid="caps"[^>]*>', html)
assert _open, "#caps not found"
i, depth = _open.end(), 1
for m in re.finditer(r'<div\b|</div>', html[_open.end():]):
    depth += 1 if m.group(0) == "<div" else -1
    if depth == 0:
        i = _open.end() + m.start()
        break
assert depth == 0, "#caps is not closed"
html = html[:_open.end()] + "".join(dom) + html[i:]

# timeline
a, b = "/* CAPTIONS-START */", "/* CAPTIONS-END */"
i, j = html.index(a), html.index(b)
html = html[:i + len(a)] + "\n" + "\n".join(js) + "\n      " + html[j:]

io.open("index.html", "w", encoding="utf-8").write(html)

longest = max(cues, key=lambda c: len(words(c["text"])))
print("  %d cue tu %d cau" % (len(cues), len(beats["sentences"])))
print("  dai nhat: %d tu — %s" % (len(words(longest["text"])), longest["text"]))
print("  cue cuoi ket thuc %.2fs (loi thoai het %.2fs)" % (cues[-1]["end"], beats["vo_end"]))
