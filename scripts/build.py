# Assemble index.html from parts/ and write ledger.json.
#
# Only for the first build, before the author opens Studio: Studio re-serialises index.html on load,
# after which an author's edits in Studio are patched with scripts/edit_helpers.py, not rebuilt over.
# (A file that differs from a fresh build only in serialisation — data-hf-id, &#160; — holds no edits
# and may be rebuilt.)
#
# One table owns the scene cuts; every scene's data-start/data-duration, the seam ledger (and so every
# swoosh) and the end-card clock derive from it. Times are RECORDED seconds (syl-times.json); every cut
# sits in a silence of the recording (scripts/silences.py: 20 ms RMS < -45 dB).
import io
import json
import os
import re
import subprocess

# ── PER-PROJECT ──────────────────────────────────────────────────────────────────────────
SC = [("h1", 0.00), ("s1", 4.60), ("p1", 9.90), ("cta", 17.50), ("ec", 24.20)]   # scene id, cut (s)
EC_DUR = 2.75                     # the house end card at 2x (5.5 s -> 2.75 s)
CHAPTERS = {"s1"}                 # cuts INTO these climb (UP); every other cut slides LEFT
STEPS = ["i-laptopdl", "i-code", "i-send"]       # the step tracker's icons (sprite ids); [] for none
PROMPTS = {4: "p1"}               # SCRIPT.md sentence -> prompt card id; its words light as they are said
CTA_WORD = "VIDEO"                # typed into the comment box on its word
BRAND_LOGO = "assets/logos/brand-logo.svg"       # the end card's logo — put your own in assets/logos/
SLOGAN = "Slogan của bạn"         # the end card's line (the author's: "AI Agent Agency Việt Nam")
PARTS = ["head.part", "scenes.part", "script.js"]
# ──────────────────────────────────────────────────────────────────────────────────────────

START = dict(SC)
END = round(SC[-1][1] + EC_DUR, 2)
NEXT = {sid: (SC[k + 1][1] if k + 1 < len(SC) else END) for k, (sid, _) in enumerate(SC)}
DUR = {sid: round(NEXT[sid] - START[sid], 2) for sid in START}


def probe(path):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                    capture_output=True, text=True).stdout.strip())
    except ValueError:
        return None


VO = probe("assets/audio/voiceover.mp3")
assert VO, "assets/audio/voiceover.mp3 missing — run scripts/prep-voice.py first"
BG = probe("assets/video/paper-bg.mp4")
if BG and BG < END:
    print("  WARNING: paper-bg.mp4 is %.1fs, the film %.1fs — extend it (README: 'nền giấy dài hơn')" % (BG, END))
TITLE = json.load(io.open("meta.json", encoding="utf-8")).get("name", "Video")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def path_of(f):
    """The d of a brand file's single path — read from the file, never retyped."""
    txt = io.open(f, encoding="utf-8").read().strip()
    m = re.search(r'\bd="([^"]+)"', txt)
    return m.group(1) if m else txt


# the step tracker: 112 px tiles, 40 px apart, centred; top 92 -> centres (TK_X + 56, 148)
TK_X = [round((1080 - (len(STEPS) * 112 + (len(STEPS) - 1) * 40)) / 2) + k * 152 for k in range(len(STEPS))]


def trk():
    out = []
    for k, ic in enumerate(STEPS):
        out.append('<div class="tk" id="tk%d" style="left:%dpx;"><svg class="ic" viewBox="0 0 24 24"><use href="#%s" /></svg>'
                   '<span class="tn">%d</span><i class="tr" id="tk%d-r"></i>'
                   '<div class="dn" id="tk%d-dn"><svg class="ic" viewBox="0 0 24 24"><use href="#i-check" /></svg></div></div>'
                   % (k, TK_X[k], ic, k + 1, k, k))
    return "\n        ".join(out)


def typed(prefix, text):
    return "".join('<span class="ch" id="%s%d">%s</span>' % (prefix, k, "&nbsp;" if c == " " else esc(c))
                   for k, c in enumerate(text))


# the prompts: each word lights as it is said (syl-times.json)
syl = json.load(io.open("syl-times.json", encoding="utf-8")) if os.path.exists("syl-times.json") else []
p_html, p_js = {}, []
for sent, pre in PROMPTS.items():
    words = [x for x in syl if x["i"] == sent]
    if not words:
        print("  WARNING: no syllable times for prompt sentence %d (run the alignment chain)" % sent)
    p_html[sent] = " ".join('<span class="w" id="%s-%d">%s</span>' % (pre, k, esc(w["syl"])) for k, w in enumerate(words))
    for k, w in enumerate(words):
        p_js.append('      tl.to("#%s-%d", { opacity: 1, duration: 0.14, ease: "none" }, %.2f);' % (pre, k, max(0.0, w["s"] - 0.04)))

html = "".join(io.open("parts/" + f, encoding="utf-8").read() for f in PARTS)
ff = io.open("parts/fontfaces.txt", encoding="utf-8").read().rstrip("\n")
assert html.count("      /* @fontfaces */") == 1
html = html.replace("      /* @fontfaces */", ff, 1)
for name, f in (("openai", "assets/logos/openai-path.txt"), ("claude", "assets/logos/claude.svg"),
                ("github", "assets/logos/github-mark.svg")):
    html = html.replace("@@path:%s@@" % name, path_of(f))
blocks = {"@@trk@@": trk(), "@@ctaq@@": typed("cta-c", CTA_WORD), "@@title@@": esc(TITLE),
          "@@slogan@@": esc(SLOGAN), "@@logo@@": BRAND_LOGO}
for tok, val in blocks.items():
    html = html.replace(tok, val)
for sent, h in p_html.items():
    html = html.replace("@@p:%d@@" % sent, h)
html = html.replace("/* @pwords */", "/* the prompts light word by word */\n" + "\n".join(p_js), 1)
html = html.replace("/* @geo */", "var GEO = %s;" % json.dumps({"tk": TK_X, "cta": len(CTA_WORD)}), 1)
for sid in START:
    html = html.replace("@@start:%s@@" % sid, "%.2f" % START[sid])
    html = html.replace("@@dur:%s@@" % sid, "%.2f" % DUR[sid])
html = html.replace("@@vo@@", "%.2f" % VO).replace("@@end@@", "%.2f" % END)
assert "@@" not in html, "unfilled token: " + html[html.index("@@") - 40: html.index("@@") + 40]
assert "<!-- @" not in html and "/* @" not in html, "unfilled placeholder"
io.open("index.html", "w", encoding="utf-8").write(html)

# the seam ledger: every cut is a seam; into a step the film climbs (UP), else LEFT
seams = []
for k in range(1, len(SC)):
    a, b = SC[k - 1][0], SC[k][0]
    up = b in CHAPTERS
    ax, tech = ("y", "cut-the-curve UP") if up else ("x", "cut-the-curve LEFT")
    seams.append({"id": "%s->%s" % (a, b), "cut": SC[k][1], "technique": tech,
                  "exit": {"selector": "#w-" + a, "axis": ax, "dir": -1},
                  "entry": {"selector": "#w-" + b, "axis": ax, "dir": -1}})
io.open("ledger.json", "w", encoding="utf-8").write(json.dumps({"fps": 30, "seams": seams}, ensure_ascii=False, indent=1))
print("index.html: %d scenes, %.2fs (voice %.2fs); ledger: %d seams" % (len(SC), END, VO, len(seams)))
