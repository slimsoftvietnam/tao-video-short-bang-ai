# Tạo video ngắn bằng AI — skill `tao-video-short-bang-ai` cho Claude Code

Skill giúp Claude dựng **video dọc 9:16 (TikTok, Reels, Shorts)** từ **kịch bản + file giọng đọc**. Hình khớp với giọng tới
từng âm tiết, theo đúng phong cách các video của SlimAI:

- nền giấy chuyển động, font K2D, màu tím chủ đạo;
- logo thật của công cụ được nhắc tới;
- video, ảnh chụp trang web và đồ họa thay cho chữ;
- phụ đề karaoke sáng từng chữ;
- prompt hiện đầy đủ, sáng theo lời đọc;
- ô comment ở cuối;
- bộ sound effect, nhạc nền và end card.

Bạn chỉ cần đưa kịch bản và file giọng đọc. **Chưa có giọng đọc?** Skill có sẵn giọng tiếng Việt miễn phí của Microsoft (nữ HoaiMy, nam NamMinh) — Claude sẽ hỏi bạn muốn tự thu, dùng API TTS của bạn, hay dùng giọng miễn phí này. Claude tự căn giọng, dựng hình, đặt âm thanh, rồi **mở bản xem trước** để bạn
duyệt. Claude chỉ xuất MP4 khi bạn yêu cầu.

## Skill làm được gì

| | |
|---|---|
| **Đầu vào** | Kịch bản (mỗi câu một dòng) và giọng đọc: tự thu (`.wav .mp3 .m4a`), dịch vụ TTS của bạn (ElevenLabs…), hoặc **giọng Microsoft miễn phí có sẵn trong skill** (không cần API key). Tùy chọn: clip quay màn hình, video 9:16, link trang web, logo của bạn |
| **Căn giọng** | Nhận dạng giọng nói bằng Whisper chạy trên máy, khớp từng âm tiết của kịch bản với bản thu. Điểm cắt cảnh luôn nằm trong khoảng lặng |
| **Hình ảnh** | Dùng video thật (tự cắt, tua cho khớp lời, làm mờ thông tin riêng tư) và ảnh tự chụp trang công khai, kèm logo chính hãng. Có thẻ prompt, thanh tiến trình các bước, ô comment và end card |
| **Âm thanh** | Chuẩn hóa giọng về −21 LUFS, đặt sẵn: thud lúc mở đầu, swoosh mỗi lần chuyển cảnh, pop cho icon quan trọng, laser lúc bấm, tiếng chụp ảnh cho con số quan trọng, riser kịch tính tự cắt cho đoạn mở đầu, nhạc nền |
| **Kiểm tra** | Lint và runtime của HyperFrames, chụp khung hình để soát, kiểm tra từng điểm chuyển cảnh |
| **Đầu ra** | Bản xem trước HyperFrames Studio (link `localhost`). Xuất MP4 1080×1920 30fps khi bạn yêu cầu |

Phần "house style" ([references/house-style.md](references/house-style.md)) ghi lại mọi yêu cầu tác giả đã đưa ra qua
hàng chục video: hạn chế chữ, cỡ chữ tối thiểu, logo đặt ở đâu, khi nào dùng tiếng pop… Claude đọc file này trước khi
dựng, nên bản đầu đã gần đúng ý.

## Cài đặt

**Yêu cầu:** Windows 10/11, [Claude Code](https://claude.com/claude-code), khoảng 1,5 GB trống (model Whisper, trình
duyệt dựng hình của HyperFrames). macOS/Linux cũng chạy được nếu đã có Python 3.10+, Node.js 22+, FFmpeg và bash.

1. Tải skill vào thư mục skills của Claude Code:
   ```powershell
   git clone https://github.com/slimsoftvietnam/tao-video-short-bang-ai "$env:USERPROFILE\.claude\skills\tao-video-short-bang-ai"
   ```
   Chỉ muốn dùng trong một thư mục dự án thì clone vào `<thư mục>\.claude\skills\tao-video-short-bang-ai`.
2. Nhấp đúp **`CAI-DAT.bat`** trong thư mục vừa tải. Script tự cài những gì còn thiếu: Python, FFmpeg, Node.js, Git Bash,
   các thư viện Python (gồm `edge-tts` — giọng đọc miễn phí của Microsoft), các skill HyperFrames (có `motion-doctrine` lo phần chuyển cảnh) và model Whisper.
3. Khởi động lại Claude Code.

## Sử dụng

Mở Claude Code trong thư mục bạn muốn chứa video, kéo file giọng đọc vào khung chat rồi gõ, ví dụ:

- `Tạo video tiktok về cách tạo chatbot AI. Đây là file âm thanh nói: D:\thu-am\chatbot.wav. Kịch bản: …`
- `Dùng video này cho đoạn mở đầu: D:\clip\demo.mp4` · `Đoạn nói "gắn vào website" dùng video này, toàn màn hình`
- `Phần comment dùng từ khóa CHATBOT` · `Logo của tôi ở D:\brand\logo.png, slogan "…"`

Claude sẽ:

1. tạo thư mục dự án,
2. chuẩn hóa giọng và căn từng âm tiết,
3. dựng các cảnh và đặt âm thanh,
4. tự soát khung hình,
5. gửi link xem trước.

Bạn xem, nói chỗ cần sửa ("hình nhanh hơn voice", "chữ nhỏ quá", "đổi video đoạn đầu"…). Khi đã ưng, gõ **"render
video"** để xuất file MP4.

Hướng dẫn từng bước cho người không biết lập trình: [HUONG-DAN-SU-DUNG.md](HUONG-DAN-SU-DUNG.md). Quy trình Claude làm
theo: [SKILL.md](SKILL.md).

## Cấu trúc

```
SKILL.md                    quy trình cho Claude
README.md                   trang này
HUONG-DAN-SU-DUNG.md        hướng dẫn người dùng
CAI-DAT.bat, setup.ps1      cài đặt 1 lần
requirements.txt            thư viện Python
references/                 house style, các bẫy kỹ thuật, căn giọng, trộn âm, kiểm tra
scripts/                    chuẩn hóa giọng, Whisper, căn âm tiết, tìm khoảng lặng, cắt clip, chụp trang,
                            ghép cảnh, phụ đề karaoke, đặt sound effect, tạo dự án mới
template/                   dự án mẫu: style dùng chung, cảnh mẫu, end card
assets/audio/               sound effect (thud, swoosh, pop, laser, chụp ảnh, riser) + nhạc nền
assets/background/          nền giấy chuyển động (124 giây) + nền giấy tĩnh
assets/fonts/               font K2D (có tiếng Việt)
assets/logos/               logo OpenAI, Claude, GitHub, Google + logo giữ chỗ cho thương hiệu của bạn
```

Skill **không kèm mascot**. Nếu bạn có mascot riêng (file `.webm` nền trong suốt), báo Claude đặt vào góc dưới bên trái
đoạn mở đầu.

## Ghi chú

- **Nền giấy dài hơn 124 giây:** `ffmpeg -stream_loop 1 -i paper-bg.mp4 -c copy paper-bg-long.mp4`.
- **Phiên bản HyperFrames** được ghim trong `package.json` của mỗi dự án (0.8.140) để video dựng lại vẫn y hệt.
- **Bản xem trước báo "did not reload":** tải lại trang (F5) và đợi khoảng 20 giây.

## Bản quyền tài nguyên

Mã nguồn và tài liệu của skill dùng tự do. Tài nguyên đi kèm thuộc về tác giả gốc, chi tiết trong
[assets/SOURCES.md](assets/SOURCES.md):

- **Font K2D:** SIL Open Font License 1.1 ([assets/fonts/OFL.txt](assets/fonts/OFL.txt)).
- **Icon:** Lucide, giấy phép ISC.
- **Logo:** thuộc chủ sở hữu thương hiệu, chỉ dùng để nhận diện sản phẩm được nhắc tới trong video.
- **Sound effect, nhạc nền, nền giấy:** lấy từ thư viện của tác giả (phần lớn tải từ Pixabay). Hãy kiểm tra giấy phép
  của từng file trước khi dùng cho mục đích thương mại.
