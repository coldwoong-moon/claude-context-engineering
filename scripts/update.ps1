# Claude Context Engineering - Windows 업데이트 스크립트

Write-Host "Claude Context Engineering - Update" -ForegroundColor Blue

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Git pull
Set-Location $ProjectRoot
Write-Host "Pulling latest changes..." -ForegroundColor Yellow
try {
    git pull origin main 2>$null
} catch {
    try { git pull origin master 2>$null } catch { Write-Host "Git pull skipped" }
}

# 설치 스크립트 재실행
Write-Host "Reinstalling..." -ForegroundColor Yellow
& (Join-Path $ScriptDir "install.ps1")

Write-Host "Update complete!" -ForegroundColor Green
