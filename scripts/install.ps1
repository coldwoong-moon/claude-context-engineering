# Claude Context Engineering - Windows 설치 스크립트
# PowerShell 5.1+ 지원

$ErrorActionPreference = "Stop"

Write-Host @"
╔═══════════════════════════════════════════════════════════╗
║       Claude Context Engineering - Installer (Windows)    ║
╚═══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Blue

# 경로 설정
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ClaudeSrc = Join-Path $ProjectRoot "claude"
$ClaudeHome = if ($env:CLAUDE_HOME) { $env:CLAUDE_HOME } else { Join-Path $env:USERPROFILE ".claude" }

Write-Host "[1/5] 환경 확인..." -ForegroundColor Yellow

# Python 확인
$PythonCmd = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} else {
    Write-Host "Error: Python이 설치되어 있지 않습니다." -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python: $($PythonCmd)" -ForegroundColor Green

# 디렉토리 확인
if (-not (Test-Path $ClaudeHome)) {
    New-Item -ItemType Directory -Path $ClaudeHome -Force | Out-Null
}
Write-Host "  ✓ Claude Home: $ClaudeHome" -ForegroundColor Green

if (-not (Test-Path $ClaudeSrc)) {
    Write-Host "Error: 소스 디렉토리 없음: $ClaudeSrc" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Source: $ClaudeSrc" -ForegroundColor Green

Write-Host "[2/5] 백업..." -ForegroundColor Yellow
$BackupDir = Join-Path $ClaudeHome "backups" (Get-Date -Format "yyyyMMdd_HHmmss")
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
foreach ($item in @("commands", "hooks", "agents", "skills", "settings.json")) {
    $itemPath = Join-Path $ClaudeHome $item
    if (Test-Path $itemPath) {
        Copy-Item -Path $itemPath -Destination $BackupDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "  ✓ $BackupDir" -ForegroundColor Green

Write-Host "[3/5] 디렉토리 생성..." -ForegroundColor Yellow
foreach ($dir in @("commands", "hooks", "agents", "skills", "knowledge")) {
    $dirPath = Join-Path $ClaudeHome $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}

Write-Host "[4/5] 파일 설치..." -ForegroundColor Yellow
$srcDirs = @("commands", "hooks", "agents", "skills")
foreach ($dir in $srcDirs) {
    $srcPath = Join-Path $ClaudeSrc $dir
    $destPath = Join-Path $ClaudeHome $dir
    if (Test-Path $srcPath) {
        Copy-Item -Path (Join-Path $srcPath "*") -Destination $destPath -Recurse -Force -ErrorAction SilentlyContinue
    }
}
$settingsSrc = Join-Path $ClaudeSrc "settings.json"
if (Test-Path $settingsSrc) {
    Copy-Item -Path $settingsSrc -Destination (Join-Path $ClaudeHome "settings.json") -Force
}
Write-Host "  ✓ 완료" -ForegroundColor Green

Write-Host "[5/5] 검증..." -ForegroundColor Yellow
$checks = @(
    @{Path = "commands\loop.md"; Name = "/loop"},
    @{Path = "commands\continuous.md"; Name = "/continuous"},
    @{Path = "hooks\unified-loop.py"; Name = "unified-loop.py"}
)
foreach ($check in $checks) {
    $fullPath = Join-Path $ClaudeHome $check.Path
    if (Test-Path $fullPath) {
        Write-Host "  ✓ $($check.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($check.Name)" -ForegroundColor Red
    }
}

Write-Host "`n설치 완료!`n" -ForegroundColor Green
Write-Host "명령어: /loop, /continuous, /research"
Write-Host "완료: LOOP_COMPLETE | 취소: LOOP_CANCEL"
