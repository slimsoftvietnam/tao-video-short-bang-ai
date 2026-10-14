# Where is a given phrase, in authored time?
#
# With word-level transcription available, a cue no longer has to be placed by
# estimating syllable offsets inside a sentence. This finds the phrase in the
# recognised words, takes its real start time, and inverts the timing map back to the
# authored time the timeline should use — so `show(..., <that number>)` lands the cue on
# the word itself.
#
# Inversion, not T(): the timeline is authored in estimate-time and T() maps forward to
# the recording. To place a cue ON a heard word we need the opposite direction.
import io
import json
import re
import sys
import unicodedata

asr = json.load(io.open("asr-words.json", encoding="utf-8"))
m = json.load(io.open("timing-map.json", encoding="utf-8"))
OLD, NEW = m["OLD"], m["NEW"]


def fold(s):
    s = s.replace("đ", "d").replace("Đ", "D")
    s = "".join(c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\s]", "", s).lower()


WORDS = [(fold(w["w"]), w["s"], w["e"]) for w in asr["words"]]


def invert(rt):
    """real second -> authored second"""
    for i in range(len(NEW)):
        if rt <= NEW[i][1] or i == len(NEW) - 1:
            span = NEW[i][1] - NEW[i][0]
            f = (rt - NEW[i][0]) / span if span > 0 else 0.0
            return OLD[i][0] + f * (OLD[i][1] - OLD[i][0])
    return rt


def find(phrase, after=0.0):
    """First occurrence of the phrase at or after `after` seconds."""
    toks = fold(phrase).split()
    for i in range(len(WORDS)):
        if WORDS[i][1] < after:
            continue
        if [w[0] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i][1], WORDS[i + len(toks) - 1][2]
    return None, None


QUERIES = [
    # chapter 2 — the five capabilities inside one sentence
    ("tao ra poster", 7), ("chinh anh", 7), ("xoa nen", 7),
    ("doi kich thuoc", 7), ("nhieu phien ban", 7),
    # chapter 3 — the six manual tasks
    ("nghi y tuong", 22), ("tim hinh", 22), ("chinh bo cuc", 22),
    ("chon mau", 22), ("nhieu phien ban", 25),
    # chapter 4 — the handover
    ("con bay gio", 30), ("nhanh hon rat nhieu", 30),
    # chapter 5 — the four questions
    ("khach hang", 40), ("thuong hieu", 44), ("truyen sai thong diep", 48),
    ("chon ra ban tot nhat", 52),
    # chapter 6
    ("van de khong con la", 56), ("chi biet dung cong cu", 60),
    ("biet nghi", 64), ("biet chon", 64), ("biet danh gia", 64),
    ("biet dung ai", 64), ("cang co gia tri hon", 70),
    # chapter 7
    ("noi cach khac", 72), ("thay doi cach designer lam viec", 76),
    # chapter 8
    ("trong tuong lai", 80), ("bang tay", 82), ("tao ra nhieu phuong an", 85),
    ("phuong an dung nhat", 88),
    # cta
    ("comment designer", 94),
]

print("  %-34s %8s %10s" % ("cum tu", "thuc te", "authored"))
prev = None
for q, after in QUERIES:
    s0, s1 = find(q, after)
    if s0 is None:
        print("  %-34s %8s" % (q, "KHONG THAY"))
        continue
    print("  %-34s %8.2f %10.2f" % (q, s0, invert(s0)))
