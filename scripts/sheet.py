# Contact sheet of a video: one frame every STEP seconds, labelled with its time.
# usage: python scripts/sheet.py <video> <out.jpg> [step] [start] [end] [cols]
import io
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
step = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
t0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                           capture_output=True, text=True).stdout.strip())
t1 = min(float(sys.argv[5]), dur) if len(sys.argv) > 5 else dur
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 6
W, H = 320, 180
font = None
for f in ("C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    try:
        font = ImageFont.truetype(f, 22)
        break
    except OSError:
        pass
font = font or ImageFont.load_default()
tiles = []
t = t0
while t < t1 - 0.05:
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "%.2f" % t, "-i", src, "-frames:v", "1",
                          "-vf", "scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2" % (W, H, W, H),
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    if raw:
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        d = ImageDraw.Draw(im)
        d.text((6, 4), "%.1f" % t, fill=(255, 230, 0), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
        tiles.append(im)
    t += step
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * W, rows * H), (20, 20, 20))
for k, im in enumerate(tiles):
    sheet.paste(im, ((k % cols) * W, (k // cols) * H))
sheet.save(out, quality=82)
print(out, len(tiles), "frames", sheet.size)
