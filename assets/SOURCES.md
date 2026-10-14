# Nguồn tài nguyên đi kèm

Tài nguyên trong `assets/` là bộ dùng chung của loạt video SlimAI. `scripts/new-project.py` chép chúng vào mỗi dự án.
Mỗi video vẫn ghi nguồn tư liệu riêng của nó (ảnh chụp, clip, logo) trong `assets/logos/SOURCES.md` của dự án đó.

## Âm thanh — `assets/audio/`

Lấy từ thư viện sound effect và nhạc nền của tác giả. Tên file gốc cho biết nguồn khi có (Pixabay ghi ID số ở cuối tên).
Giấy phép thuộc về tác giả gốc của từng file: hãy kiểm tra trước khi dùng cho mục đích thương mại.

| file | file gốc trong thư viện của tác giả | cách dùng trong video |
|---|---|---|
| `sfx-thud.mp3` | `thud-sound-effect-405470.mp3` (Pixabay) | 1 lần ở giây 0, gain 0,30 |
| `sfx-swoosh.mp3` | `universfield-swoosh-ngắn.mp3` (Universfield, Pixabay) | mỗi điểm chuyển cảnh, gain 0,70 |
| `sfx-pop.mp3` | `pop-402324.mp3` (Pixabay) | chỉ khi icon quan trọng xuất hiện, gain 0,40 (0,26 trong chuỗi nhanh) |
| `sfx-laser.mp3` | sound "laser" trong thư viện của tác giả | khi bấm vào một nút trên màn hình, gain 0,55 |
| `sfx-click.mp3` | cắt 1 tiếng từ `sound chụp ảnh nhanh.m4a` | tiếng chụp ảnh cho con số quan trọng, gain 0,60 |
| `sfx-riser.mp3` | `cinematic-riser-sound kịch tính.mp3` | bản đầy đủ |
| `sfx-risercut3.mp3` | 3,20 giây đầu của file trên (tới đỉnh) | đoạn mở đầu: đỉnh rơi đúng lúc "dừng phụt", gain 0,17 |
| `bgm-little-things.mp3` | `Little Things Immaterial.mp3` (thư mục nhạc nền của tác giả) | nhạc nền cả video từ 0:00, gain 0,219 (~12 dB dưới giọng) |

## Nền — `assets/background/`

| file | nguồn | ghi chú |
|---|---|---|
| `paper-bg.mp4` | `Backrunground giấy.mov` trong thư viện của tác giả | 26 tờ giấy đã chỉnh sáng, mỗi tờ 0,5 giây, dựng sẵn dài 124 giây, 1080×1920 |
| `paper.webp` | một khung hình của file trên | nền giấy đứng yên ("dừng hình") |

## Font — `assets/fonts/`

K2D (Cadson Demak), bản tách latin / latin-ext / vietnamese, đậm 400–800, woff2. Giấy phép SIL Open Font License 1.1 —
[fonts/OFL.txt](fonts/OFL.txt).

## Logo — `assets/logos/`

Logo là nhãn hiệu của chủ sở hữu, chỉ dùng để nhận diện sản phẩm được nhắc tới. Không tạo bằng AI, không vẽ lại bằng tay.

| file | nguồn |
|---|---|
| `openai.svg`, `openai-path.txt` | logo OpenAI chính thức (bản lưu của loạt video) |
| `claude.svg` | logo Claude chính thức (bản lưu của loạt video) |
| `github-mark.svg` | logo GitHub chính thức (bản lưu của loạt video) |
| `google-g.png` | chữ "G" của Google (bản lưu của loạt video) |
| `brand-logo.svg` | logo giữ chỗ — thay bằng logo của bạn (`build.py BRAND_LOGO`) |

## Icon

Bộ icon vẽ trong `template/parts/head.part` lấy từ [Lucide](https://lucide.dev) (giấy phép ISC). Biểu tượng PDF, laptop,
tách trà… vẽ riêng cho loạt video.
