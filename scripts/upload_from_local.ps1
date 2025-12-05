Param(
    [string]$ZipPath = "deliverables.zip",
    [string]$UploadUrl = "https://transfer.sh/"
)

Write-Host "This script uploads a ZIP to transfer.sh and prints the public URL." -ForegroundColor Cyan
if (-Not (Test-Path $ZipPath)) {
    Write-Error "File not found: $ZipPath"
    exit 1
}

Write-Host "Uploading $ZipPath to $UploadUrl ..."

# Use curl if available; on Windows curl maps to Invoke-WebRequest in some shells — prefer Invoke-RestMethod
try {
    $response = Invoke-RestMethod -Method Put -InFile $ZipPath -Uri ($UploadUrl + (Split-Path $ZipPath -Leaf)) -UseBasicParsing
    Write-Host "Upload response:`n$response" -ForegroundColor Green
} catch {
    Write-Warning "Invoke-RestMethod failed: $_. Exception. Trying curl.exe if present..."
    if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
        curl.exe --upload-file $ZipPath $UploadUrl$(Split-Path $ZipPath -Leaf)
    } else {
        Write-Error "Neither Invoke-RestMethod nor curl.exe succeeded. Please run this script on a machine with outbound HTTP access." 
        exit 2
    }
}

Write-Host "Done. If successful, the response above contains the public URL." -ForegroundColor Cyan
