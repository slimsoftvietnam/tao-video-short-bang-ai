# Hướng dẫn sử dụng — tạo video ngắn bằng AI

Dành cho người không biết lập trình. Làm theo đúng thứ tự, mỗi bước chỉ cần làm một lần trừ bước 3 trở đi.

## 1. Cài đặt (một lần)

1. Cài [Claude Code](https://claude.com/claude-code) và đăng nhập.
2. Mở **PowerShell**, dán lệnh sau rồi Enter:
   ```powershell
   git clone https://github.com/slimsoftvietnam/tao-video-short-bang-ai "$env:USERPROFILE\.claude\skills\tao-video-short-bang-ai"
   ```
   Chưa có `git`? Tải file ZIP của repo (nút **Code → Download ZIP**), giải nén vào
   `C:\Users\<tên bạn>\.claude\skills\tao-video-short-bang-ai`.
3. Vào thư mục vừa tải, nhấp đúp **`CAI-DAT.bat`**. Đợi đến dòng **"Xong!"**. Nếu script báo cài Python xong và yêu cầu
   chạy lại, hãy đóng cửa sổ rồi nhấp đúp `CAI-DAT.bat` lần nữa.
4. Khởi động lại Claude Code.

## 2. Chuẩn bị nội dung

- **Kịch bản:** mỗi câu một dòng, viết đúng như lời sẽ đọc. Câu prompt muốn hiện đầy đủ trên video cũng là một dòng.
- **Giọng đọc** — chọn 1 trong 3:
  - **Tự thu** (tự nhiên nhất), lưu `.wav` hoặc `.mp3`. Thu ở chỗ yên tĩnh, ngừng một nhịp giữa các câu.
  - **API TTS bạn đang dùng** (ElevenLabs…): dán API key khi Claude hỏi; Claude không lưu key vào file. Nên đổi key sau đó.
  - **Giọng miễn phí của Microsoft** có sẵn trong skill, không cần tài khoản hay key (cần internet). Giọng nữ HoaiMy hoặc nam NamMinh, chỉnh được tốc độ. Nghe hơi máy hơn giọng thật.
- **Tùy chọn:**
  - clip quay màn hình các bước thao tác;
  - video bạn muốn chèn, và câu nói muốn chèn video vào;
  - link trang web cần chụp;
  - logo và slogan của bạn cho end card;
  - từ khóa cho ô comment.

## 3. Yêu cầu Claude dựng video

Mở Claude Code trong một thư mục chứa video (ví dụ `D:\video-tiktok`), rồi gõ một tin nhắn gồm:

```
Tạo video tiktok về <chủ đề>. Đây là file âm thanh nói: "D:\thu-am\giong-doc.wav"
1. Phải có logo của các công cụ xuất hiện trong video.
2. Hạn chế chữ, dùng video / hình ảnh để giải thích.
3. Đoạn đầu dùng video này: "D:\clip\mo-dau.mp4"
4. Phần comment dùng từ khóa CHATBOT.
Kịch bản:
<dán kịch bản, mỗi câu một dòng>
```

Chưa có file giọng đọc thì bỏ dòng "Đây là file âm thanh nói" — Claude sẽ hỏi bạn chọn cách tạo giọng. Muốn dùng luôn giọng miễn phí, viết thêm: `Dùng giọng AI miễn phí, giọng nam` (hoặc `giọng nữ`, `đọc nhanh hơn`).

Claude sẽ hỏi lại nếu thiếu thông tin. Có clip quay màn hình chứa thông tin riêng (tên hội thoại, email, đường dẫn trên
máy…) thì Claude tự làm mờ hoặc cắt bỏ, và báo cho bạn.

## 4. Xem trước và sửa

Khi xong, Claude gửi một link dạng `http://localhost:3002/#project/<tên>`. Mở link trong trình duyệt, bấm ▶ để xem.

Muốn sửa thì nói thẳng chỗ chưa ưng, ví dụ:

| bạn nói | Claude sẽ |
|---|---|
| "hình nhanh hơn voice" | dời các hiệu ứng về đúng chữ |
| "lướt qua nhanh quá" | cho cảnh đó ở lâu hơn |
| "chữ nhỏ quá", "chưa đẹp" | làm lại theo quy định cỡ chữ / phong cách |
| "đoạn đầu dùng video này …" | thay video và căn lại thời gian |
| "cho mascot to lên ở góc dưới bên trái" | đổi vị trí, cỡ mascot (nếu bạn có mascot) |

Nếu trang xem trước báo "preview did not reload" hoặc vẫn hiện bản cũ: bấm **F5** và đợi khoảng 20 giây.

## 5. Xuất video

Gõ **"render video"**. Claude xuất file MP4 1080×1920 vào thư mục dự án (`renders/`), thường mất vài phút.

## Lỗi thường gặp

| lỗi | cách xử lý |
|---|---|
| `motion-doctrine not found` | chạy lại `CAI-DAT.bat` (bước cài skill HyperFrames) |
| `ffmpeg` / `node` / `python` không tìm thấy | chạy lại `CAI-DAT.bat`, rồi khởi động lại máy |
| Căn giọng sai nhiều (tỉ lệ khớp < 90%) | nói Claude dùng model Whisper lớn hơn (`medium`) |
| Video dài hơn 2 phút, nền giấy hết giữa chừng | nói Claude "kéo dài nền giấy" |
