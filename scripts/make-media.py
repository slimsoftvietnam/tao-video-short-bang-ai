# Cut every clip and still the film uses (record provenance in assets/logos/SOURCES.md).
#
# The author's screen recordings are RETIMED onto the voice: each output clip is a list of segments
# (source a -> b, film time A -> B). a == b holds that frame (a freeze). Film times are RECORDED
# seconds (syl-times.json), so a clip placed at data-start = its first A plays every moment on its
# word. Every segment is rendered with an exact frame count, then the pieces are joined.
#
# PRIVACY is baked into the pixels before anything else (house rule: scrub the author's recordings):
# blur boxes per segment (a menu opening over a blurred sidebar needs a different box), crop to the
# part that does the work, and CUT what must not be seen (a file picker with the user's name in the
# path) instead of blurring it.
#
# usage: python scripts/make-media.py        (edit the PER-PROJECT block first)
import io
import os
import shutil
import subprocess
import tempfile

from PIL import Image

V = "assets/video/"
SRC = "assets/video/src/"
SH = "research/shots/"
FPS = 30
os.makedirs("assets/img", exist_ok=True)


def blur_graph(boxes, crop):
    """filter_complex from [0:v] to [out]: blur each (x, y, w, h) box, then crop (w, h, x, y)."""
    parts, cur = [], "0:v"
    for k, (x, y, w, h) in enumerate(boxes):
        r = max(2, min(26, min(w, h) // 4 - 1))      # the 4:2:0 chroma plane is half size
        parts.append("[%s]split=2[m%d][s%d];[s%d]crop=%d:%d:%d:%d,boxblur=%d:3[b%d];[m%d][b%d]overlay=%d:%d[o%d]"
                     % (cur, k, k, k, w, h, x, y, r, k, k, k, x, y, k))
        cur = "o%d" % k
    tail = "crop=%d:%d:%d:%d," % crop if crop else ""
    parts.append("[%s]%sformat=yuv420p,setsar=1[out]" % (cur, tail))
    return ";".join(parts)


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def build(name, src, segs, crop=None, blur=lambda a: []):
    """segs: [(a, b, A, B)] — source a..b plays over film A..B; a == b freezes source a.
    crop: (w, h, x, y) in source pixels or None; blur(a) -> [(x, y, w, h)] boxes for the segment at a."""
    t0 = segs[0][2]
    tmp = tempfile.mkdtemp(prefix="seg-")
    pieces = []
    for k, (a, b, A, B) in enumerate(segs):
        n = int(round((B - t0) * FPS)) - int(round((A - t0) * FPS))
        if n <= 0:
            continue
        g = blur_graph(blur(a), crop)
        out = os.path.join(tmp, "p%02d.mp4" % k)
        enc = ["-an", "-c:v", "libx264", "-preset", "ultrafast", "-qp", "0", "-r", str(FPS), out]
        if a == b:
            png = os.path.join(tmp, "f%02d.png" % k)
            run(["-ss", "%.3f" % a, "-i", src, "-filter_complex", g, "-map", "[out]", "-frames:v", "1", png])
            run(["-loop", "1", "-framerate", str(FPS), "-i", png, "-frames:v", str(n), "-vf", "format=yuv420p"] + enc)
        else:
            k_ = (B - A) / (b - a)
            g2 = g.replace("[out]", "[pre]") + ";[pre]setpts=(PTS-STARTPTS)*%.6f,fps=%d[out]" % (k_, FPS)
            run(["-ss", "%.3f" % a, "-t", "%.3f" % (b - a + 0.5), "-i", src, "-filter_complex", g2, "-map", "[out]",
                 "-frames:v", str(n)] + enc)
        pieces.append(out)
    lst = os.path.join(tmp, "list.txt")
    with io.open(lst, "w", encoding="utf-8") as f:
        for p in pieces:
            f.write("file '%s'\n" % p.replace("\\", "/"))
    run(["-f", "concat", "-safe", "0", "-i", lst, "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", V + name + ".mp4"])
    shutil.rmtree(tmp)
    d = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                        "stream=nb_read_frames,width,height", "-of", "csv=p=0", V + name + ".mp4"],
                       capture_output=True, text=True).stdout.strip()
    want = int(round((segs[-1][3] - t0) * FPS))
    print("  %-8s film %.2f-%.2f  %s  (want %d frames)" % (name, t0, segs[-1][3], d, want))


def frame(src, t):
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "%.3f" % t, "-i", src, "-frames:v", "1",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB")


# ── PER-PROJECT ──────────────────────────────────────────────────────────────────────────
# One entry per output clip: (name, source, segments, crop, blur). Example — a desktop recording laid
# onto the voice, its sidebar blurred, a menu held while it is talked about, the slow part cut out:
#
#   APP = SRC + "my recording.mp4"                     # 1886x1014
#   def app_blur(a):
#       return [(1530, 930, 356, 84),                   # a Windows notification naming someone
#               (0, 158, 290, 856)]                     # the sidebar: conversation and project titles
#   CLIPS = [("app", APP, [
#       (0.40, 2.20, 21.80, 23.85),     # the app; the menu opens on "chuyển sang"
#       (2.40, 2.40, 23.85, 26.95),     # held while "ChatGPT" and "Codex" are said
#       (2.62, 2.98, 26.95, 27.22),     # the click lands on "Codex"
#       (4.10, 4.24, 27.22, 27.36),     # the next screen (the loading in between is cut)
#       (4.24, 4.24, 27.36, 30.30),     # held to the scene's end
#   ], None, app_blur)]
#
# A clip the author supplies full frame (9:16) plays uncropped: [(0.0, 6.0, 4.77, 9.57)] (1.25x).
CLIPS = []

# Stills cropped from own captures of PUBLIC pages (scripts/cdp.mjs shot … --dpr 2): (name, png, box, width)
CROPS = []

if __name__ == "__main__":
    if not CLIPS and not CROPS:
        print("nothing to cut — fill CLIPS / CROPS in the PER-PROJECT block")
    if CLIPS:
        print("clips:")
    for name, src, segs, crop, blur in CLIPS:
        build(name, src, segs, crop, blur)
    if CROPS:
        print("stills:")
    for name, src, box, w in CROPS:
        im = Image.open(src).convert("RGB").crop(box)
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save("assets/img/%s.webp" % name, "WEBP", quality=92, method=6)
        print("  %-10s %dx%d" % (name, im.width, im.height))
