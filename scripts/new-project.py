# Start a new video project from the skill: the template (parts/, package.json, hyperframes.json,
# SCRIPT.md), the pipeline scripts, and the house assets (sound effects, music bed, paper background,
# K2D fonts, brand marks) — everything the series uses, in the places the scripts expect.
#
# usage:
#   python "<skill>/scripts/new-project.py" <project-folder> [--name "Tên video"] [--voice "<recording>"]
#
# Then, from inside the project folder, follow SKILL.md (voice first): put the script in SCRIPT.md,
# one sentence per line, and run the alignment chain. Nothing here overwrites an existing file unless
# --force is given.
import argparse
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the voice-first pipeline (and the voice-last helpers) that every project carries in scripts/
PIPELINE = [
    "prep-voice.py", "tts.py", "asr.py", "plan-beats.py", "align-asr.py", "syl-times.py", "fix-syl.py", "silences.py",
    "karaoke.py", "add-sfx.py", "build.py", "make.sh", "make-media.py", "cdp.mjs", "sheet.py", "edit_helpers.py",
    "audit-sync.py", "word-times.py", "install-map.py", "recaption.py", "resfx.py", "synth-sfx.py",
]
# (skill source, project destination)
ASSETS = [
    ("assets/audio", "assets/audio"),
    ("assets/fonts", "assets/fonts"),
    ("assets/logos", "assets/logos"),
    ("assets/background/paper-bg.mp4", "assets/video/paper-bg.mp4"),
    ("assets/background/paper.webp", "assets/img/paper.webp"),
]


def slug(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "video"


def put(src, dst, force):
    if os.path.isdir(src):
        for name in os.listdir(src):
            if name in ("__pycache__",) or name.endswith(".pyc"):
                continue
            put(os.path.join(src, name), os.path.join(dst, name), force)
        return
    if os.path.exists(dst) and not force:
        return
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    shutil.copy2(src, dst)


ap = argparse.ArgumentParser()
ap.add_argument("dest")
ap.add_argument("--name", default=None)
ap.add_argument("--voice", default=None)
ap.add_argument("--force", action="store_true")
a = ap.parse_args()

dest = os.path.abspath(a.dest)
os.makedirs(dest, exist_ok=True)
pid = slug(os.path.basename(dest))
name = a.name or os.path.basename(dest)

put(os.path.join(SKILL, "template"), dest, a.force)
for f in PIPELINE:
    put(os.path.join(SKILL, "scripts", f), os.path.join(dest, "scripts", f), a.force)
for src, dst in ASSETS:
    put(os.path.join(SKILL, src), os.path.join(dest, dst), a.force)
for d in ("assets/video/src", "assets/img", "research/shots", "snapshots"):
    os.makedirs(os.path.join(dest, d), exist_ok=True)

meta = os.path.join(dest, "meta.json")
if a.force or not os.path.exists(meta) or json.load(io.open(meta, encoding="utf-8")).get("id") == "my-video":
    json.dump({"id": pid, "name": name, "createdAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")},
              io.open(meta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pkg = os.path.join(dest, "package.json")
p = json.load(io.open(pkg, encoding="utf-8"))
if p.get("name") in (None, "my-video"):
    p["name"] = pid
    json.dump(p, io.open(pkg, "w", encoding="utf-8"), indent=2)
    io.open(pkg, "a", encoding="utf-8").write("\n")

print("project: %s  (id %s)" % (dest, pid))
if a.voice:
    subprocess.run([sys.executable, os.path.join("scripts", "prep-voice.py"), os.path.abspath(a.voice)], cwd=dest, check=True)
print('''
next (from the project folder):
  1. SCRIPT.md        the script, one sentence per line, exactly as spoken
  2. python scripts/prep-voice.py "<recording>"        (skip if you passed --voice)
  3. python scripts/asr.py small
     python scripts/plan-beats.py                     (edit SCENES first)
     python scripts/align-asr.py
     python scripts/syl-times.py
     python scripts/fix-syl.py
     python scripts/silences.py                       (cut points in silence)
  4. author parts/ at the times in syl-times.json, set SC in scripts/build.py
  5. bash scripts/make.sh  ->  npm run check  ->  npx hyperframes snapshot ...
  6. npx hyperframes preview --background   — hand over the link; render only when asked
''')
