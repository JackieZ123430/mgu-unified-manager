$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Inputs = Join-Path $Root "build_inputs"
New-Item -ItemType Directory -Force -Path $Inputs | Out-Null

# setup-node in CI places node.exe here; for local builds, copy a Node 22 LTS node.exe.
if (-not (Test-Path (Join-Path $Inputs "node.exe"))) {
  throw "Copy Node.js 22 LTS node.exe to build_inputs\node.exe before building."
}

$OpenSshDir = Join-Path $Inputs "openssh"
if (-not (Test-Path (Join-Path $OpenSshDir "ssh.exe"))) {
  $Zip = Join-Path $env:TEMP "OpenSSH-Win64.zip"
  $Extract = Join-Path $env:TEMP "OpenSSH-Win64"
  Invoke-WebRequest "https://github.com/PowerShell/Win32-OpenSSH/releases/latest/download/OpenSSH-Win64.zip" -OutFile $Zip
  if (Test-Path $Extract) { Remove-Item $Extract -Recurse -Force }
  Expand-Archive $Zip -DestinationPath $Extract -Force
  $Candidate = Get-ChildItem $Extract -Filter ssh.exe -Recurse | Select-Object -First 1
  if (-not $Candidate) { throw "OpenSSH archive did not contain ssh.exe" }
  New-Item -ItemType Directory -Force -Path $OpenSshDir | Out-Null
  Copy-Item (Join-Path $Candidate.DirectoryName "*") $OpenSshDir -Recurse -Force
}
Write-Host "Windows runtime inputs ready."
