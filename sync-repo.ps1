param(
  [string]$Message = "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

$git = 'C:\Program Files\Git\cmd\git.exe'

& $git add .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$status = & $git status --short
if (-not $status) {
  Write-Host 'Nothing to commit.'
  exit 0
}

& $git commit -m $Message
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $git push -u origin main
exit $LASTEXITCODE
