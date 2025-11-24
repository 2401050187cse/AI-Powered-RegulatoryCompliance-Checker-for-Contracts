<#
.SYNOPSIS
  Publish `deliverables.zip` as a GitHub Release using the GitHub CLI (`gh`).

.DESCRIPTION
  This script will create an annotated tag (if missing), push it, and create a
  GitHub Release attaching `deliverables.zip` as an asset. It requires `gh` to
  be installed and authenticated (run `gh auth login` if necessary).

.PARAMETER Tag
  The git tag to create/use for the release. Default: v1.0

.PARAMETER File
  The file to upload as release asset. Default: deliverables.zip

.EXAMPLE
  .\publish_release.ps1 -Tag v1.0 -File .\deliverables.zip
#>

param(
    [string]$Tag = 'v1.0',
    [string]$File = 'deliverables.zip',
    [string]$Message = 'Milestone deliverables'
)

Set-StrictMode -Version Latest

function Abort([string]$msg, [int]$code = 1) {
    Write-Error $msg
    exit $code
}

if (-not (Test-Path $File)) {
    Abort "Missing file: $File" 2
}

# Check for gh
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Abort "GitHub CLI 'gh' not found. Install from https://cli.github.com/ and authenticate with 'gh auth login' before running this script." 3
}

Write-Output "Using tag: $Tag"

# Ensure working tree is clean or commit outstanding changes
$status = git status --porcelain
if ($status) {
    Write-Output "Staging and committing outstanding changes..."
    git add -A
    git commit -m "Prepare release $Tag" 2>$null
}

# Create tag if it doesn't exist
$tagExists = git tag -l $Tag
if (-not $tagExists) {
    Write-Output "Creating tag $Tag"
    git tag -a $Tag -m "$Message"
    git push origin $Tag
} else {
    Write-Output "Tag $Tag already exists. Skipping tag creation."
}

Write-Output "Creating GitHub release and uploading asset..."
try {
    gh release create $Tag $File --title "$Message $Tag" --notes "$Message"
    Write-Output "Release created. Visit: $(gh release view $Tag --json url -q .url)"
} catch {
    Abort "Failed to create release: $_" 4
}

Write-Output "Done."
