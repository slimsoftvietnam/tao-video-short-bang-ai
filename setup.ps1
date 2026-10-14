# Cài đặt skill tạo video ngắn bằng AI — chạy 1 lần. Mọi công cụ đều miễn phí, chạy trên máy.
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$skill = Split-Path -Parent $MyInvocation.MyCommand.Path
$HF = "hyperframes@0.8.140"
Write-Host "=== CÀI ĐẶT SKILL TẠO VIDEO NGẮN BẰNG AI ===" -ForegroundColor Cyan

function Refresh-Path {
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# 1. Python 3.10+
$py = $null
foreach ($c in @("python", "py")) { if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break } }
if ($py) { & $py -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)"; if ($LASTEXITCODE -ne 0) { $py = $null } }
if (-not $py) {
  Write-Host "[1/7] Chưa có Python 3.10+ -> đang cài Python 3.12 bằng winget..." -ForegroundColor Yellow
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  Write-Host "Đã cài Python. HÃY ĐÓNG cửa sổ này và chạy lại CAI-DAT.bat." -ForegroundColor Green
  Read-Host "Nhấn Enter để đóng"; exit
}
Write-Host "[1/7] Python: OK" -ForegroundColor Green

# 2. FFmpeg (cắt, đo và trộn âm thanh / video)
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host "[2/7] Đang cài FFmpeg bằng winget..." -ForegroundColor Yellow
  winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
  Refresh-Path
} else { Write-Host "[2/7] FFmpeg: OK" -ForegroundColor Green }

# 3. Node.js 22+ (HyperFrames chạy bằng npx; chụp trang web bằng scripts/cdp.mjs)
$nodeOk = $false
if (Get-Command node -ErrorAction SilentlyContinue) {
  $v = (node -p "process.versions.node.split('.')[0]") 2>$null
  if ([int]$v -ge 22) { $nodeOk = $true }
}
if (-not $nodeOk) {
  Write-Host "[3/7] Đang cài Node.js LTS bằng winget..." -ForegroundColor Yellow
  winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
  Refresh-Path
} else { Write-Host "[3/7] Node.js: OK" -ForegroundColor Green }

# 4. Git Bash (scripts/make.sh chạy bằng bash; Claude Code trên Windows cũng cần Git)
if (-not (Get-Command bash -ErrorAction SilentlyContinue) -and -not (Test-Path "$env:ProgramFiles\Git\bin\bash.exe")) {
  Write-Host "[4/7] Đang cài Git (kèm Git Bash) bằng winget..." -ForegroundColor Yellow
  winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
  Refresh-Path
} else { Write-Host "[4/7] Git Bash: OK" -ForegroundColor Green }

# 5. Thư viện Python
Write-Host "[5/7] Đang cài thư viện Python (vài phút)..." -ForegroundColor Yellow
& $py -m pip install --user --upgrade -r (Join-Path $skill "requirements.txt")

# 6. Các skill HyperFrames (dựng video bằng HTML; motion-doctrine lo phần chuyển cảnh)
Write-Host "[6/7] Đang cài các skill HyperFrames..." -ForegroundColor Yellow
npx --yes $HF skills update motion-doctrine hyperframes-core hyperframes-cli media-use

# 7. Model Whisper "small" (~460 MB, tải 1 lần) để căn giọng đọc với kịch bản
Write-Host "[7/7] Đang tải model Whisper (lần đầu có thể mất vài phút)..." -ForegroundColor Yellow
& $py -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('Whisper: OK')"

Write-Host ""
npx --yes $HF doctor
Write-Host ""
Write-Host "Xong! Khởi động lại Claude Code, rồi nói ví dụ:" -ForegroundColor Cyan
Write-Host "  'Tạo video tiktok về <chủ đề>. Đây là file giọng đọc: <đường dẫn>. Kịch bản: ...'" -ForegroundColor Cyan
Read-Host "Nhấn Enter để đóng"
