# House style — everything the author has asked for

Read this **before designing any SlimAI short**, not after the first review. Every
rule below was stated by the author at least once, usually as a correction to
something that had already been built. Applying them up front is the difference
between one review round and five.

Each rule carries the author's own words, so you can tell a standing preference
from a one-off.

---

## 1. Workflow

**Open the preview; never render unasked.**
> *"Luôn luôn mở lên browser tôi xem trước, không cần render ngay."*
> *"đừng render trước, mở preview tôi xem trước"*

Stated twice, weeks apart — it is a hard rule. Build, verify with snapshots, then run
`npx hyperframes preview --background` and hand over the link. Render only when they
say so. A render is four minutes that produces a file wrong in exactly the way the
composition is; the author catches it faster on playback.

**Don't poll a long render.** Run it in the background and wait for the notification.

**Confirm the voice plays from the first second to the last.**
> *"7 giây đầu đang bị mất voice / Từ 1 phút 25 trở đi bị mất voice"*

A voice track can be present in the file and still silent on screen — a `data-start`
past zero, a `data-duration` shorter than the recording, a clip cut by a later edit.
After placing it, check that `#vo`'s `data-duration` equals the recording's real length
(`ffprobe`), and measure the render's audio in a window at the very start and in the
last ten seconds of speech. The author heard both gaps immediately.

**Voice length is the author's call.** When a recording runs long, measure how much
pause-tightening can recover (usually 6–20s — TTS reads are already tight), show the
options with their real cost, and let them choose. They picked a 1.2× time-stretch
over every option offered, including the recommended one. Offer; don't decide.

**Carry the previous video's style forward.**
> *"Học phong cách của video trước"*

The channel is a series. Before designing, open the most recent project and reuse its
palette, type, bookends, sound set and scripts. Changing the look is a decision the
author makes, not a default.

---

## 2. Identity

| | |
|---|---|
| Canvas | 1080×1920, 30fps, TikTok |
| Type | **K2D**, localised woff2, 400–800. Never pair with DM Mono on Vietnamese — see memory `feedback-default-font-k2d` |
| Palette | violet `#7657FF` / `#A78BFA` on `#05061F`, gold `#FFC857` for chapter numbers only |
| Opening | a mascot (your own transparent `.webm`; none ships with the skill), lower-left, 0.25 s to the hook's dead stop; **big, feet off the frame** (below) |
| Closing | the end card: your logo, an oversized cursor clicks it, the slogan — `template/parts/script.js` (the author's: the SlimAI logo, "AI Agent Agency Việt Nam") |
| Slogan | **"AI Agent Agency Việt Nam"** |

> *"Thiếu mascot ở đầu video + end card về SlimAI tương tự các dự án trước"*

**The opening mascot is big, in the lower-left corner, feet off the frame.**
> *"cho vị trí mascot của tôi to lên ở góc dưới bên trái tương tự dự án "giải thích skill, MCP, Sub agent",
> không cần thiết thấy cả chân"* (2026-10-08)

The bear stands ~800 px tall with its head near y 1340 and its legs running off the bottom edge — the size
the author's skill / MCP / sub-agent video uses (576×1024 box at left −60, top 1180 for the 720×1280 clips; the 548×666
pointing clip at 694×843, left −60, top 1309). A full-body mascot at ~500 px was sent back. A pointing arm then
reaches x ≈ 600, so side captions start there (`.kc.side.hk { left:600px }`).

**The end card runs at 2x.**
> *"Phần SlimAI ở cuối hãy cho nhanh hơn 2 lần (tối đa 3 giây)"* (2026-09-27)

Every time and duration of the standard card scaled by 0.5: 5.5 s -> 2.75 s (logo, cursor
click, slogan, hold). Carried forward on the next video; say so in the BRIEF so the author
can ask for the full-length card back.

The bookends are not optional polish. A SlimAI short without them was sent back.
The end card ships ready in `template/parts/script.js` (logo + cursor click + slogan, at 2x) — keep it, change
only `BRAND_LOGO` and `SLOGAN` in `build.py`. A mascot does not ship: use your own transparent `.webm`.

**Match the rhythm to the voice, keep the palette.** When the narration is playful
("các con vợ", `[laughs]`), the author chose *"Giữ tím #7657FF, nhịp vui hơn"* — same
identity, faster cuts, bouncier type. Tone changes the motion, not the brand.

**Keep the author's own voice in captions.** "các con vợ", "anh em" and similar
address terms are the channel's character. Transcribe them as spoken; never "correct"
them.

---

## 3. Text economy — the rule that reshapes every scene

> *"Hãy hạn chế sử dụng chữ trong video, chỉ có đầy đủ chữ cho phần cung cấp prompt.
> Các phần khác hãy cố gắng sử dụng đồ họa hoặc capture ảnh trên mạng/video/... để
> minh họa câu nói"*

- **Full sentences appear only where the viewer will pause and copy them** — a prompt,
  a command, a template. Nothing else gets a paragraph.
- **Everything else is a picture**: an icon, a diagram, a real screenshot, a screen
  recording, a chart. The narration already says the words; the frame should show
  what the words mean.
- Titles, one-line theses and punchlines may stay as text. Explanations may not.

**But size is not negotiable.**
> *"chữ và icon trên video đang bị nhỏ quá, và nhìn xấu"*

Fewer words means each one can be big. Floors that survived review:

| element | minimum |
|---|---|
| chapter title | 104px / 800 |
| a time, number or key label | 62px / 800, in a pill or panel |
| body line | 44–46px / 600 |
| icon or glyph | 130–190px |
| chip | 44px |

Anything below 40px reads as a mistake on a phone. Three 50px circles holding "7h"
at 26px were sent back; 62px times in wide pills were accepted.

---

## 4. What each scene needs

**Give a key idea its own page, not a caption.**
> *"thêm 1 trang riêng thể hiện chứ không phải mỗi chữ"*

When the narration states the video's central claim, it gets a dedicated visual beat
— a scene built for it — not a line of text over whatever was already on screen.

**Every chapter opener carries a picture of its meaning.**
> *"chỗ hóa thân thành chuyên gia thì thêm 1 cái hình hoặc icon chuyên gia… phần 2
> Đào sâu thì thêm 1 cái hình hoặc icon người đang đào"*

A number and a title are not enough. The icon must *depict the concept*: an expert
(person + tie + verified badge), digging (a spade planted in the ground), money (a
coin with a currency mark). Test it at a glance — two first attempts failed exactly
there: a shovel read as a pen, a coin stack read as a database. Zoom into every glyph
before handing over (`snapshot --zoom "#id"`).

**Name a product, show its logo.**
> *"Thêm logo chatgpt vào các nơi phù hợp"* · *"có logo của Claude AI (logo này có thể
> thêm vào các nơi khác phù hợp)"* · *"Đoạn nói file PDF thì nên thêm icon logo PDF"*

When the narration names ChatGPT, Claude, a PDF, a website — the mark appears. Best
placements: beside the product name in the hook, as the assistant's avatar on every
answer panel, beside a file-type the scene is about.

**The opening must be beautiful — and it is a picture, not a title.**
> *"Đoạn cảnh mở đầu phải đẹp hơn, có logo"* · *"Đoạn đầu (5 giây) phải có logo…
> thêm các hiệu ứng kính glass"* · *"hãy sửa đoạn đầu làm sao thể hiện cảm giác huyền bí"*
> · *"Phần mở đầu xấu quá, Hạn chế chữ, có hình minh họa hay gì đó đẹp hơn."*

The first five seconds decide the view. They need the product logo, one picture that
states the promise, something moving, and the mascot. Openings were sent back twice
for being text: a text card, then (OpenCode ep. 1) a kicker + two-line title + outline
wallet + slogan — four text blocks around one thin icon. The captions already carry
the words. The opening's own text is a small series pill plus at most one or two words
*inside* the picture ("0đ" on a price tag).

A picture-first opening: the real product — its own screen recording, its logo — in a
glass window tilted in 3D, lit from behind, turning toward the viewer, plus one object
that carries the claim (a gold price tag reading 0đ that slides out from under the
window). Before handing it over:
- **Nothing covers the logo, at any moment.** Snapshot the hook at 5–8 times. Product
  footage zooms and pans, so a spot that is clear at 1s can sit on the logo at 4s.
- **Never crop footage that zooms.** A crop tuned to the wide phase cuts the zoomed one
  off at both sides. Use the full frame.
- **Trim the source's static intro.** Official demos often hold a wide frame with a tiny
  logo for a second before zooming in — that became two seconds of black rectangle.
  Start at the motion; slowing a 60fps source up to 2× stays smooth.
- **Reveal with an edge, not a fade.** An object emerging from behind another is opaque
  from its first frame and revealed by the front object's edge (z-index). Cross-fading
  it while it travels shows a dirty half-transparent block mid-way.

**When the author supplies the opening footage, it is the picture — no badge clutter.**
> *"Tôi muốn đoạn đầu video hạn chế icon, tập trung hiện video tôi đã gửi"* · *"ý tôi là đoạn đầu vẫn cần logo
> chatgpt và claude"* · *"Video đó sẽ toàn màn hình và không có icon nào trên video"* (2026-10-08)

A hook built around the author's clip carries the product marks (ChatGPT, Claude) and nothing else: no ✓, no tag,
no people chip, no bot badge — the mascot, the captions and the riser's motion are enough. A full-screen clip gets
no overlay at all; the mascot leaves before it (under the flash). Put a clip where the author points ("chèn … ở
phần nói …"), not where it would also fit.

**Result panels must show substance, not quantity.**
> *"Phần giải thích của các kết quả sau khi áp dụng prompt tôi thấy chưa đẹp và chưa
> thể hiện được nội dung lắm"*

Skeleton bars are right for text the viewer need not read — but a *result* is the one
place they do need the content. "Two grey bars vs three violet bars" says *more words*,
not *a better answer*. Show three short real phrases instead: `① Ngân sách thực tế
② Ai là người quyết định ③ Chỉ số đo hiệu quả`. When a prompt asks for X, Y, Z, the
result panel shows `+ X · + Y · + Z` — the causal link is the point.

**A comment CTA is a chat input.**
> *"Phần nói comment hãy tạo 1 ô chat điền comment"*

Not a big word on its own. A rounded input with the keyword typed in and a send button
that pops when the word lands.

**Scenes may change setting; the language may not.**
> *"Không bắt buộc toàn bộ video diễn ra trong một workspace cố định… phải giữ cùng
> visual identity, palette, typography, icon system và motion language. Các cảnh cần
> được kết nối bằng object, hình ảnh hoặc transition có ý nghĩa thay vì reset hoàn toàn."*

Use `/motion-doctrine`'s seam law for the connections.

---

## 5. Real media

**Prefer the real thing when the author supplies it.** Their footage, screenshots and
screen recordings beat any simulation. When they send one, the mock-up it replaces is
deleted outright — a recording of the real control proves what a mock-up only claims.

> *"Đoạn bấm edit cuộc hội thoại thì chèn video ấn vào nút edit này"*
> *"tự cắt video sao cho bỏ phần thừa"*

- Trim to the action. Crop to the region that shows it, then let it bleed wider than
  the safe margin (a desktop UI strip in a 9:16 frame only gets bigger by going wider).
- Frame it as a browser window with a short URL line so it reads as evidence.
- `muted`, stage-level or inside a scene wrapper — never nested in another timed clip.

**A vertical clip the author supplies plays full-frame, uncropped.**
> *"Đoạn chatbot lên website sử dụng video này (nên giữ nguyên toàn cảnh video)"* (2026-10-08, a 9:16 3D motion
> graphic)

**Phone recordings play full-frame, not in a window.**
> *"Video tôi gửi cũng chủ yếu là quay tỉ lệ 9:16 nên có thể khi đến đoạn video không cần
> video background mà hãy lấy toàn bộ tỉ lệ video tôi quay; đoạn nào lộ đoạn chat thì che đi
> và cắt xén 1 ít ở bên trên đang bị thừa biểu tượng record video là được."* (2026-10-03)

- Cut only the status bar (the red record pill sits in it) and keep every other pixel of the
  UI: an iPhone recording is narrower than 9:16, so scale it to the frame HEIGHT and fill the
  two side strips with the same frame blurred and darkened — never crop the input bar or the
  top bar to fill the width.
- The paper background steps aside while a recording plays; overlays (prompt cards, a ring on
  the control being tapped, a card flying into the attachment chip) sit on top of it.
- Captions over the black app UI switch to white capitals with a dark halo.
- Privacy still applies frame by frame: an animated greeting with the account's name can
  slide through more than one position — step through it at 0.05 s before trusting a box.

**Capture public pages with `npx hyperframes capture <url>`**, not the browser pane —
the pane's viewport is ~800px and scales up blurry. `capture` writes 1920×1080 PNGs.
Then crop to **the two sentences that carry the claim**, at a width that lands near
1:1 in the frame. A whole help-page slab shrunk to 888px proves a document exists and
lets nobody read it.

**Never screenshot the author's own logged-in account.** A Claude or ChatGPT sidebar
lists every conversation title; a TikTok upload publishes them. Use a public page, a
UI simulation, or ask them for a clean recording. If media *they* send contains
legible private detail (project names, task text), use it — they sent it — but say so
in one line so they can choose to blur it.

**Treat a background plate before using it.** A supplied loop is often brightest where
the captions sit. Darken with a graded scrim, heaviest at the bottom. Loop it
seamlessly (see traps.md) and pre-render it to the full duration — do not rely on
runtime looping.

---

**A cut must land on something.** Snapshot 0.2-0.4s after every seam. The wrapper
entry animates an empty frame if the scene's first element still waits for its word:
three cuts here opened on bare background for up to 0.8s. The scene's opening element —
the chapter number, the warning sign, the first logo — fires ON the cut; only the title
waits for the word that names it.

**Scrub the author's recordings for their own data before using them.** Three of three
screen recordings carried something private: Google's suggestion list held their search
history, the agent's home screen showed usage statistics, and the task list named live
client work. None of it was noticed when the clips were sent. Blur the region (keep the
typed query visible, it carries the story) or crop to the part that does the work — the
input box, the result, the button — which is also the part big enough to read on a phone.

---

## 6. Logos and brand marks

**Official assets only. Never generate a brand logo with AI, never trace one by hand.**

| mark | where it lives | how it renders |
|---|---|---|
| OpenAI / ChatGPT | `assets/logos/openai.svg` (its path in `openai-path.txt`, read by build.py) | black on a white tile; `filter:invert(1)` for white |
| Claude | `assets/logos/claude.svg` | white on a `#D97757` terracotta tile |
| GitHub | `assets/logos/github-mark.svg` | black on white |
| Google | `assets/logos/google-g.png` | as-is |
| your brand | `assets/logos/brand-logo.svg` is a placeholder — put your logo there (the author's: SlimAI) | as-is |
| PDF | draw it: document outline + folded corner + "PDF" in red | not a brand mark |

Copy into the project's `assets/logos/` and record provenance in a `SOURCES.md` beside
them.

---

## 7. Sound — the author's rules

> *"Mỗi lần chuyển cảnh sẽ dùng sound effect này: universfield-swoosh-ngắn.mp3; mỗi lần
> có cái gì đó nổi lên là sẽ dùng sound effect này: pop-402324.mp3. Mỗi lần bắt đầu
> video sẽ dùng sound effect này: thud-sound-effect-405470.mp3"*
> *"Các sound effect và âm thanh nền tương tự video trước"*

| cue | file | when | target |
|---|---|---|---|
| thud | `assets/audio/sfx-thud.mp3` (was `thud-sound-effect-405470.mp3`) | once, t=0 | −22 dB |
| swoosh | `assets/audio/sfx-swoosh.mp3` (was `universfield-swoosh-ngắn.mp3`) | **every** scene cut = every ledger row | −28 dB |
| pop | `assets/audio/sfx-pop.mp3` (was `pop-402324.mp3`) | **only an important icon** appearing — see below | −29 dB (−33 inside a fast cascade) |
| laser | `assets/audio/sfx-laser.mp3` | a click on a control the picture shows | −26 dB |
| shutter | `assets/audio/sfx-click.mp3` (cut from `sound chụp ảnh nhanh.m4a`) | an important number (99%, a count) | −30 dB |
| riser | `assets/audio/sfx-risercut3.mp3` (the first 3.20 s of `cinematic-riser-sound kịch tính.mp3`) | the hook: peaks on its dead stop | −24 dB |
| bed | `assets/audio/bgm-little-things.mp3` (*Little Things Immaterial*) | whole film | −31 to −33 dB (10–12 under the voice) |

Levels are computed, not tuned by ear: see [audio-mix.md](audio-mix.md). The voice is
normalised to **−21.0 LUFS** first so every video lands at the same loudness.

**Pop is rationed, not per element.**
> *"hạn chế sound effect pop này, các icon quan trọng hiện ra mới dùng"*

The first rule ("mỗi lần có cái gì đó nổi lên") produced 115 pops in a 100-second video
and was sent back. Give a pop only to an icon that carries the point of its sentence: a
product or logo arriving, the object the claim is about (a piggy bank for "tiết kiệm", a
meter running dry, a lock, a picture landing in a page, a star for "điểm mạnh"), the
summary points, the end-card logo. Titles, labels, chapter numbers, skeleton lines,
cascades and anything within ~0.5s of a swoosh stay silent. The accepted density was 28
pops in 101s — roughly one every 3–4 seconds.

---

## 8. Content and accuracy

**API keys never enter a project.**
> *"Không hardcode API key. Không lưu API key trong source code. Không đưa API key vào
> video."*

Read a key only from the environment (`OPENAI_API_KEY`); if it is absent, fall back to
native SVG/CSS and never error. If the author pastes a key into chat, use it only as an
inline environment variable on the one command that needs it, never write it to a file,
and tell them once that it is now in the transcript and should be rotated.

**Plain language.**
> *"chèn vào nhưng dùng ngôn ngữ dễ hiểu"*

No jargon on screen ("Critical threshold", "ExploitBench"). Say what it means.

**Fact-check every claim against the primary source** before it goes on screen. The
author's drafts have had a wrong attribution (a benchmark score belonging to a
different model version) and an unsupported figure. Correct the error, drop the
unverifiable, and say which in `BRIEF.md`.

**The picture must never promise more than the source does.** When a recorded line
overstates (e.g. "dùng full ngày không lo hết token" — the plan also has a weekly
cap), don't silently re-word the voice and don't contradict it on screen. Show the
source untranslated so the picture stays honest, and tell the author what the line
omits so they can decide whether to re-record.

**A money figure inside a prompt is an example, not a result.** Set it at body size,
inside the prompt, no count-up, no chart — and if the narration later disowns it, the
picture recedes with it.

---

## 9. The script — write the way the author talks

**Flowing spoken sentences, not clipped lines.**
> *"Sửa văn nói tự nhiên hơn, đang bị hơi ngắt và không tự nhiên"*

A draft built from short fragments ("Bí mật nằm ở AI Agent." / "Bước hai, cài
HyperFrames.") reads as a list being recited, not a person talking. The author's own
scripts run long, comma-paced sentences joined with "thì", "là", "rồi", "mà", "nhé",
"đấy", "luôn", with the odd rhetorical question answered at once ("Vậy cài có khó
không?" — "Dễ lắm anh em ạ."). Write in that register: 15–25 syllables with a natural
breath at each comma is the norm; anything under ~10 syllables should be a deliberate
beat, not the default. `template/SCRIPT.md` shows the register; read the author's last script before drafting a new one.

**A dictated line is kept as dictated.**
> *"Sửa "Vào trang chủ của nó, copy một dòng lệnh, dán vào Terminal là xong." thành
> "Anh em chỉ cần gõ claude hoặc codex trên google rồi cài như app bình thường về""*

When the author writes "sửa X thành Y", Y is the line. Smooth only its grammar and
word order; do not rephrase it into your own style. If Y introduces a claim, fact-check
it like any other (here: both Claude and Codex do ship desktop apps for Windows) and
raise a problem rather than quietly rewriting.

**Name both halves when a video does two things.**
> *"Video này hướng dẫn vừa edit video vừa tạo video"*

A how-to that creates *and* edits must say both in the hook and label both in the steps
("tạo video" / "edit video"); a hook that promises only one undersells the video.
