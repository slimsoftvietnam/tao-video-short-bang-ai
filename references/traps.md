# Traps

Every entry here cost real time. The ones marked **(check stays green)** are the
dangerous kind: the structural gate passes and the video is wrong.

## Things that make the picture wrong

- **`.scene { opacity:0 }` hides the whole film** (check stays green). Added to stop a
  one-frame flash; the framework gates clips by `data-start` and never touches
  opacity, so nothing turned it back on. The film rendered as background plus
  captions. The anti-flash job belongs to the inner `.wrap`, which `seam-stamp`
  already parks at `autoAlpha:0` until its entry tween.
- **`autoAlpha` only in a `fromTo`'s from-vars** (check stays green). GSAP re-applies
  a completed tween's *end* state on every seek; a property living only in fromVars is
  not part of it, so an earlier `tl.set(el, {autoAlpha:0}, 0)` wins forever. A
  five-path fan diagram rendered as one dot. Put `autoAlpha:1` in the to-vars as well.
- **Dropping `class="pad"` drops `position:absolute`.** The element falls to the top
  of the frame in document flow and covers the title. To widen one padded element,
  keep the class and override `left`/`right` inline in its single `style`.
- **Two `style` attributes on one tag** — the browser keeps the first. Studio also
  drops duplicates. Always merge into one.
- **`style="top:1920"` is ignored** — CSS lengths need a unit (check stays green).
  Nine scenes stacked. Grep `(top|left|width|height):[0-9]+"` before trusting a layout.
- **An opaque element after a background video hides it.** Order matters.
- **Absolutely positioned children need a positioned container.**
- **`transformOrigin` only in a `fromTo`'s to-vars** (check stays green). The from-state is
  rendered at creation with the default `50% 50%`, so a zoom meant to sit on a toolbar in
  the top-left corner (`scale:2.2` → `1`) showed the empty middle of the screen recording
  for a whole second. Put `transformOrigin` in the from-vars too.
- **Hiding a covered letter with `color:transparent` fails `check`** (`text_not_painted`).
  Give the letter its own span and toggle `autoAlpha` on it.
- **`video_nested_in_timed_element` is only reported when no closing tag sits between the
  timed wrapper and the `<video>`** — a window frame's title bar (`<div class="vb">…</div>`)
  hid it on every earlier project. Those rendered right because the nested videos carry
  ABSOLUTE `data-start`, but the clean structure is an untimed `<div class="scene">` (seam-stamp's
  `.wrap` autoAlpha already gates it) holding the one timed `<video>`.
- **`transform-origin:0 0` plus scale pushes content off the right edge.**

## Studio rewrites the file — every time

Opening the preview re-serialises `index.html`:

- injects `data-hf-id="…"` **before** `id` — 507 of them in one pass
- turns `<br />` into `<br>`, collapses multi-line attributes
- converts single-quoted attributes to `&quot;` entities
- **drops duplicate attributes** — HTML keeps the first

It leaves CSS and the `<script>` block alone. So:

- **HTML edits go through `scripts/edit_helpers.py`** (`replace_el`, `retop`), which
  anchor on the id and walk tag depth. Literal HTML matching died on the first attempt
  in two consecutive projects.
- **CSS and JS edits may use literal `sub()`.**
- A regex for `id="x"` also matches inside `data-hf-id="x"` when the ids collide; the
  helpers anchor on the full `id="…"` inside the same tag.
- After a preview, confirm `data-fx-chain` and `data-automation` each appear **once**
  on the bed.
- Keep backups **outside the project root**. A `index.v1-backup.html` beside
  `index.html` is a second root composition — lint errors with
  `multiple_root_compositions`, and the runtime may play both audio tracks.
- **A running preview rewrites every `.html` in the project, not just `index.html`** —
  including build fragments. On `6-cap-do-su-dung-claude` it injected ids into
  `parts/head.html` and appended `</div></body></html>` to it; the next build closed
  `#root` right after the background, every scene fell outside the composition, and
  `check` failed with *"sweep_static — Timeline did not advance under seek"* while
  snapshots still looked right. Name fragments `.part` (not `.html`), and stop the
  preview (`preview --stop`) while a build-and-check loop is running.

## Long films: the 10-second navigation limit

`snapshot` and `check` give the page 10 s to reach DOMContentLoaded. A 3.5-minute film
(a 215 s voice + a 234 s bed + ~100 cues) did not make it — every snapshot failed with
*"Navigation timeout of 10000 ms exceeded"*, even with a smaller FLAC voice and a
trimmed bed; removing the long audio made it pass, so it is duration, not bytes.
`snapshot --timeout` does **not** help (that is the runtime wait). Raise the limit
through the environment: `PRODUCER_PAGE_NAVIGATION_TIMEOUT_MS=90000`, and give `check`
`--timeout 90000` (it also sets the navigation minimum).

The **Studio** has its own limits that no variable reaches: a 15 s ready timeout on each
reload ("The preview did not reload (it took too long to load)") and a fixed 10 s for
the scene thumbnails, which it renders one by one — 31 scenes of failing thumbnails
kept the CPU busy for minutes and the preview sat frozen at 00:00. What made it usable:

- **Premix the effects.** The runtime fetches and decodes every media element on its
  own (no de-duplication, `cache: no-store`); ~100 `<audio>` cues on a long film is too
  many. `add-sfx.py` with `PREMIX = True` mixes them (numpy, ~3 s) into one
  `sfx-mix.mp3` at the same times and gains and writes a single element. ffmpeg `amix`
  over ~100 delayed inputs is far too slow — do not use it.
- **Don't let the server inline a heavy image.** Studio embeds images as base64 in the
  page; a 945 KB PNG cutout became 1.26 MB of HTML. WebP with alpha: 121 KB.
- The first open still takes ~20 s while the server compiles; after that seeking and
  playback work. Tell the author to wait for the duration to appear (03:42).

## Generators that must stay idempotent

`recaption-real.py` and `add-sfx.py` delete what they wrote and regenerate. Prove it:
run twice and confirm the element count does not change.

- **Never clear a container with `(.*?)</div>`** — it stops at the first child. A
  second regex attempt anchored on indentation *still* left 105 of 106 caption divs
  orphaned outside the container (check stays green — ids duplicated, captions
  doubled). The only reliable rule is structural: rebuild line by line, and the
  container's close is the first following line whose whole content is `</div>`.
- **A GSAP exit that ends exactly on another clip's start** raises
  `gsap_exit_missing_hard_kill`. The fix is a `tl.set(el, {autoAlpha:0}, t)` at
  **exactly** the exit's end instant — two hundredths late does not count as matching.
  Put the fade on an inner span, not on the clip itself.

## Shell and escaping

- **`\b` in a regex becomes a literal backspace (0x08)** when Python passes through a
  Bash heredoc or `python -c`. Happened twice in one session. Symptom: a pattern that
  matches when tested alone fails inside the script; `cat -A` shows `^H`. Write
  regex-heavy scripts with the **Write tool**. Emergency fix: `sed -i 's/\x08//g' f`.
- **`python3` does not exist on this Windows machine** — it opens the Store stub. Use
  `python`.
- **Nested quotes in a Python tuple** — `("s4", ""Sửa lại" rất tốn", …)` is a syntax
  error. Use `‘ ’` inside, or escape.
- `%%` is only an escape inside a format string.
- grep ERE has no `\d`. `grep -o` cannot match a multi-line element.
- Windows drive-letter colons break ffmpeg's `movie=` filter.

## ffmpeg on this machine (9.0)

- **`-vsync` is gone** — use `-fps_mode passthrough`.
- **`-v error` silences filter output** — `volumedetect`, `psnr`, `loudnorm` all print
  at info level. Use `-hide_banner -nostats` instead, then grep the labelled line.
- `atempo` stretches pitch-preserved within 0.5–2.0 in one pass.
- **Two chained `tpad` filters drop the second pad.** `tpad=start_mode=clone:…,tpad=stop_mode=clone:…`
  produced a clip without its held tail (3.6 s instead of 5.5 s) and the window went blank
  once the clip ran out. Use one `tpad` with both options, and compare every clip's
  `ffprobe` duration with the `data-duration` that shows it.
- **`boxblur` fails on 4:2:0 video when the radius exceeds a quarter of the box** — the
  chroma planes are half size, so a 26 px blur on an 84 px-tall box errors out (`-22`).
  Use `radius = min(26, min(w, h) // 4 - 1)`.
- **Retiming an author's recording onto the voice:** render each segment (source a→b over film
  A→B, or a held frame) with an exact frame count and join them —
  `scripts/make-media.py` `build()`. Bake privacy blurs into the
  pixels before cropping, per segment (a menu opening over a blurred sidebar needs a different
  box). One `filter_complex` with `split` + `trim` per segment buffers every later branch in
  memory — do not.

## Type

- **K2D throughout.** Never DM Mono on Vietnamese — it has no Vietnamese subset.
- **`≠` (U+2260) is outside every K2D subset.** Draw it as SVG.
- **`line-height` under 1.14 on Vietnamese** stacks tone marks into the line above.
  Prompt cards want 1.42.

## Contrast

- Text at 16:1 can still fail to read over busy footage — panel opacity and
  background chroma matter more than luminance.
- **Decode a contrast warning's selector path by counting `nth-of-type`.** A
  `4.35:1` warning looked like the source line and was the fake browser URL bar — the
  first guess was wrong because the path was not counted.

## Media

- **Loop seam:** compare loop-point PSNR with consecutive-frame PSNR. Directional
  footage (a grid flying forward) → **crossfade** the last second into the first
  (31.4 → 34.25 dB against a 36.9 baseline). Ping-pong only for non-directional
  footage — reversing forward motion is visible.
- **Pre-render the loop to full length** with `-stream_loop`; do not trust runtime
  looping.
- **`sfx-pop.mp3` opens on 0.18 s of silence** (the laser on 0.05 s). A pop cue at t is
  heard at t + 0.18 — fine for an icon easing in, late for a hard slam (a stamp, a ✗, a medal
  landing ON its word): lead those cues by ~0.16 s.
- **DOM order is z-order: a drawn object added later covers what flies into it.** Two app tiles
  that "landed on the laptop screen" were hidden under the laptop SVG (its screen is filled) —
  give the travelling element a `z-index`, then snapshot the landing.
- **A scene must open on something even when its first word comes late.** A use-case scene
  opened on bare paper for 1.7 s because its cards waited for "chăm sóc"; the chatbot icon now
  opens it on the cut and steps aside when the cards arrive.
- **The browser pane's viewport is ~800px** — screenshots from it scale up blurry.
  Use `npx hyperframes capture <url>` (1920×1080).
- The pane's `navigate` strips URL paths; `preview_start` with a full URL does not.

### Evidence crops from official pages (the "bôi đậm chữ" highlighter)

First built for the author's video on new Claude and ChatGPT models (a `make-evidence.py` of that
project); `scripts/cdp.mjs` now covers the capture.
- **Capture at a 430-px phone viewport, deviceScaleFactor 3.** The paragraph wraps to a
  width that lands near 1:1 in a 920-px card, so body text reads at ~45px. A desktop
  capture of the same paragraph shrinks to ~33px.
- **Use `ElementHandle.screenshot()`, not `page.screenshot({clip})`.** anthropic.com
  scrolls inside its own container: a clip computed from `getBoundingClientRect()` shot
  the wrong region, and a quote in an off-screen carousel slide came out blank. Hide
  `position:fixed/sticky` chrome first so the header never lands on a crop.
- **Measure the phrase boxes in the same pass** (`Range.getClientRects()` relative to the
  element) and draw the highlighter from them: a `mix-blend-mode:multiply` gold bar,
  `scaleX 0→1` from the left, one line box after another, fired on the spoken word.
- **Slice between line boxes, not at them** — a crop edge inside a line's box leaves
  descenders of the line above as a grey fringe. Clamp every slice to the capture: PIL
  fills a crop outside the image with black (it showed as a black rule beside a card).
- **Dim, never cut**, the words of a crop that are outside the quoted sentence: a veil in
  the page's own background colour (take the most frequent colour of that box).
- **openai.com/index/… answers automated browsers with a bot check.** Do not work around
  it. The same numbers are on developers.openai.com model pages (price cards, context
  window, tool list), which capture cleanly.

## Processes

- **Every `snapshot`, `check`, `seam-gate` and preview launches chrome-headless-shell**,
  which on Windows opens a black console window. The author asked why tabs kept
  opening. Batch the checks.
- **A timed-out `check` leaves an orphaned Chrome tree** — 6 processes held memory for
  25 minutes. Find orphans by parent PID, kill only those. This machine has ~1.8 GB
  free of 15.7; below the threshold renders drop to one worker.
- **`preview --status` lies after a restart** — it reported nothing running while port
  3002 served the project. Check the port, not the status line.
- **`seam-gate.mjs` needs `CHROME_PATH`** here, pointing into
  `~/.cache/hyperframes/chrome/chrome-headless-shell/…/chrome-headless-shell.exe`, and
  its `--project` mode fails; use `--url` against the running preview.
- **Against a 0.8.128 preview the seam gate reports false FAILs.** That runtime defers
  some `__player.seek()` calls (big jumps: 30→86 s, 93→10 s), and the gate reads the
  page straight after seeking, so it measures the previous time: "not visible in its
  window (op 0.00)" on scenes the snapshots show plainly. The same film passed 10/10
  against `npx hyperframes@0.8.80 preview --background`. Measure seams on an 0.8.80
  preview, then restart the pinned version for the author.

## Tooling

- **`hyperframes capture --skip-assets` still downloads the page's videos and web fonts**
  (it only skips images/SVGs): one PixVerse capture pulled 12 MP4s (86 MB) before it was
  stopped. Downloads need the author's per-file permission, so for a screenshot of a public
  page use `scripts/cdp.mjs shot <url> <out.png> --dpr 2`
  (crisp 2x PNG, nothing else saved), and `cdp.mjs eval` to write a logo's inline `<svg>`
  straight from the DOM to disk. **Never retype an SVG path by hand** — a hand-copied
  PixVerse logo lost a `0` and every point after it shifted.
- **Google Search answers headless Chrome with a reCAPTCHA; app.pixverse.ai with a
  Cloudflare check.** Do not get around either: re-draw the search box (Google "G" + typed
  query + the official result's real title and URL) and set official numbers in type.
- **`yt-dlp` audio can 403 while the video downloads** (Runway's Gen-4.5 reel). The film
  mutes every clip, so the video-only file is enough; rename `*.f616.mp4`.
- **`carve.mjs` cannot run on Node 24** — memory `reference-carve-broken-node24`.
- **`hyperframes transcribe` needs whisper-cpp**, which is not installed. The
  faster-whisper path in `scripts/asr.py` works.
- `inspect` is deprecated — `check` includes it. Its `#camera` overflow warnings on a
  camera-over-workspace build are architecture false positives.
- Bump the pinned CLI before a render (`npx hyperframes@latest upgrade --project .
  --check`), verify with `check`, name both versions.
