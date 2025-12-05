<#
.SYNOPSIS
  Create a GitHub Release and upload an asset (deliverables.zip).

USAGE
  # Preferred: set GITHUB_TOKEN in environment and run from repo root
  $env:GITHUB_TOKEN = 'ghp_...'
  .\scripts\create_github_release.ps1 -Tag v1.0 -Title 'v1.0 deliverables' -AssetPath .\deliverables.zip

  # Or pass token explicitly (less safe):
  .\scripts\create_github_release.ps1 -Token 'ghp_...' -Tag v1.0 -AssetPath .\deliverables.zip

REQUIREMENTS
  - PowerShell with Invoke-RestMethod / Invoke-WebRequest
  - Repo owner/name defaults are set for this workspace; adjust -Owner and -Repo if needed.
#>

param(
    [string]$Token = $env:GITHUB_TOKEN,
    [string]$Owner = '2401050187cse',
    [string]$Repo = 'AI-Powered-RegulatoryCompliance-Checker-for-Contracts',
    [string]$Tag = 'v1.0',
    [string]$Title = 'v1.0 deliverables',
    [string]$Body = 'Release containing deliverables.zip with reports and PDFs',
    [string]$AssetPath = "deliverables.zip",
    [switch]$Prerelease
)

if (-not $Token) {
    Write-Error "No GitHub token provided. Set GITHUB_TOKEN env var or pass -Token parameter. Aborting."
    exit 1
}

if (-not (Test-Path $AssetPath)) {
    Write-Error "Asset not found: $AssetPath"
    exit 2
}

$api = "https://api.github.com/repos/$Owner/$Repo/releases"

$bodyObj = @{
    tag_name = $Tag
    name = $Title
    body = $Body
    prerelease = [bool]$Prerelease.IsPresent
    draft = $false
}
$json = ConvertTo-Json -InputObject $bodyObj -Depth 3

Write-Host "Creating release $Tag on $Owner/$Repo..."

try {
    $resp = Invoke-RestMethod -Method Post -Uri $api -Headers @{ Authorization = "token $Token"; Accept = 'application/vnd.github+json' } -Body $json -ContentType 'application/json'
} catch {
    Write-Error "Failed to create release: $_"
    exit 3
}

$upload_url = $resp.upload_url
if (-not $upload_url) {
    Write-Error "No upload_url returned from GitHub API. Response: $($resp | ConvertTo-Json -Depth 2)"
    exit 4
}

# upload_url looks like: https://uploads.github.com/repos/:owner/:repo/releases/:id/assets{?name,label}
# Remove template parameters
$upload_url = $upload_url -replace '\{.*\}$', ''
$assetName = Split-Path $AssetPath -Leaf
$upload_uri = "${upload_url}?name=${assetName}"

Write-Host "Upload URL: $upload_uri" -ForegroundColor Cyan

Write-Host "Uploading asset $assetName to release..."

try {
    # Use Invoke-RestMethod with -InFile for binary upload
    $fileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $AssetPath))
    $hdr = @{ Authorization = "token $Token"; "Content-Type" = 'application/zip'; Accept = 'application/vnd.github+json' }
    $resp2 = Invoke-RestMethod -Method Post -Uri $upload_uri -Headers $hdr -Body $fileBytes
    Write-Host "Upload complete. Asset URL: $($resp2.browser_download_url)" -ForegroundColor Green
} catch {
    Write-Error "Asset upload failed: $_"
    exit 5
}

Write-Host "Release created: $($resp.html_url)"
