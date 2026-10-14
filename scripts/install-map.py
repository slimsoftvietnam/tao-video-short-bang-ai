# Replace the OLD[]/NEW[] arrays in index.html from timing-map.json, and read them back.
#
# Separate from apply-voiceover.py because the map gets reinstalled whenever the
# alignment is re-solved, while the audio elements and durations are placed once.
#
# The read-back is not ceremony. On an earlier video the JSON and the arrays baked into
# the HTML drifted apart, so a Python-side tool computed T() from the fresh JSON while
# the runtime used stale arrays — sound and picture disagreed and every automated gate
# still passed. 4 decimal places: %g truncates to six significant figures and fails the
# comparison below.
import io
import json
import re

P = "index.html"
s = io.open(P, encoding="utf-8").read()
m = json.load(io.open("timing-map.json", encoding="utf-8"))
OLD, NEW = m["OLD"], m["NEW"]


def fmt(pairs):
    return "[" + ", ".join("[%.4f, %.4f]" % (a, b) for a, b in pairs) + "]"


pat = re.compile(r"      var OLD = \[.*?\];\n      var NEW = \[.*?\];", re.S)
assert pat.search(s), "OLD/NEW arrays not found"
s = pat.sub("      var OLD = %s;\n      var NEW = %s;" % (fmt(OLD), fmt(NEW)), s, count=1)
io.open(P, "w", encoding="utf-8").write(s)

back = io.open(P, encoding="utf-8").read()
gotO = json.loads(re.search(r"var OLD = (\[.*?\]);", back, re.S).group(1))
gotN = json.loads(re.search(r"var NEW = (\[.*?\]);", back, re.S).group(1))
assert len(gotO) == len(OLD) and len(gotN) == len(NEW), "anchor count changed"
for i in range(len(OLD)):
    for a, b in ((gotO[i], OLD[i]), (gotN[i], NEW[i])):
        assert abs(a[0] - b[0]) < 5e-4 and abs(a[1] - b[1]) < 5e-4, "anchor %d drifted" % i

align = json.load(io.open("vo-alignment.json", encoding="utf-8"))
print("  installed and read back: %d anchor pairs" % len(gotO))
# two possible producers: the pause-based solver (reports a rate band) and the
# transcription-based one (reports the model it heard with)
if align.get("source") == "asr":
    print("  from transcription (%s)  ·  script ends %.2fs"
          % (align["model"], align["scriptEndsAt"]))
else:
    print("  band %s  ·  script ends %.2fs" % (align["band"], align["scriptEndsAt"]))
if align.get("tail"):
    t = align["tail"]
    print("  UNSCRIPTED TAIL %.2f - %.2f  (%.2fs of speech, no caption)"
          % (t["start"], t["end"], t["speech"]))
