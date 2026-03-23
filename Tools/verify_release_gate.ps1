param(
    [string]$RepoRoot = "D:\feiji1111111111111\telegram-official-master-latest"
)

$ErrorActionPreference = "Stop"

$apkPath = Join-Path $RepoRoot "TMessagesProj_App\build\outputs\apk\afat\release\app.apk"
$mappingPath = Join-Path $RepoRoot "TMessagesProj_App\build\outputs\mapping\afatRelease\mapping.txt"

Write-Host "== Release Gate =="
Write-Host "RepoRoot: $RepoRoot"

$head = (& git -C $RepoRoot rev-parse --short HEAD).Trim()
$branch = (& git -C $RepoRoot branch --show-current).Trim()
$dirtyLines = (& git -C $RepoRoot status --short | Measure-Object -Line).Lines

Write-Host "Branch: $branch"
Write-Host "HEAD: $head"
Write-Host "Dirty: $dirtyLines"

if ($dirtyLines -ne 0) {
    Write-Error "Release gate failed: working tree is not clean."
}

if (-not (Test-Path $apkPath)) {
    Write-Error "Release gate failed: release APK not found at $apkPath"
}

if (-not (Test-Path $mappingPath)) {
    Write-Error "Release gate failed: mapping.txt not found at $mappingPath"
}

$apk = Get-Item $apkPath
$hash = (Get-FileHash $apkPath -Algorithm SHA256).Hash

Write-Host "APK: $($apk.FullName)"
Write-Host "APK Size: $($apk.Length)"
Write-Host "APK Updated: $($apk.LastWriteTime)"
Write-Host "APK SHA256: $hash"
Write-Host "Mapping: $mappingPath"

Write-Host "Result: PASS"
