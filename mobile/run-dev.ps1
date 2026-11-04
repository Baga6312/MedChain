param(
    [string]$Device
)

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $repositoryRoot ".env"

if (-not (Test-Path $envPath)) {
    throw "Missing $envPath. Copy .env.example to .env first."
}

$values = @{}
Get-Content $envPath | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)\s*$') {
        $values[$matches[1]] = $matches[2].Trim()
    }
}

$apiBaseUrl = $values["MOBILE_API_BASE_URL"]
if ([string]::IsNullOrWhiteSpace($apiBaseUrl)) {
    $apiBaseUrl = "http://10.0.2.2:8000/api"
}

$googleClientId = $values["GOOGLE_OAUTH_CLIENT_ID"]
if ([string]::IsNullOrWhiteSpace($googleClientId)) {
    throw "GOOGLE_OAUTH_CLIENT_ID is missing from .env."
}

$arguments = @(
    "run",
    "--dart-define=API_BASE_URL=$apiBaseUrl",
    "--dart-define=GOOGLE_SERVER_CLIENT_ID=$googleClientId"
)
if (-not [string]::IsNullOrWhiteSpace($Device)) {
    $arguments += @("-d", $Device)
}

Set-Location $PSScriptRoot
& flutter @arguments
exit $LASTEXITCODE
