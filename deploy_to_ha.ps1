param (
    [Parameter(Mandatory=$true)]
    [string]$HaIpAddress
)

$haConfigShare = "\\$HaIpAddress\config"

Write-Host "Checking connection to Home Assistant at $haConfigShare..."
if (!(Test-Path $haConfigShare)) {
    Write-Error "Could not connect to Home Assistant at $haConfigShare. Please ensure the Samba/Windows File Sharing add-on is installed and running in Home Assistant."
    exit
}

Write-Host "Connection successful! Deploying Dryad integration..."

# 1. Copy Custom Component
$targetComponent = "$haConfigShare\custom_components\dryad"
if (!(Test-Path $targetComponent)) {
    New-Item -ItemType Directory -Force -Path $targetComponent | Out-Null
}
Copy-Item -Path ".\custom_components\dryad\*" -Destination $targetComponent -Recurse -Force
Write-Host "✅ Integration copied to custom_components/dryad/"

# 2. Copy Lovelace Card
$targetWww = "$haConfigShare\www"
if (!(Test-Path $targetWww)) {
    New-Item -ItemType Directory -Force -Path $targetWww | Out-Null
}
Copy-Item -Path ".\www\dryad-card.js" -Destination $targetWww -Force
Write-Host "✅ Lovelace card copied to www/dryad-card.js"

Write-Host "`nDeployment Complete! 🎉"
Write-Host "Next Steps in Home Assistant:"
Write-Host "1. Restart Home Assistant."
Write-Host "2. Go to Settings -> Devices & Services -> Add Integration -> search 'Dryad'."
Write-Host "3. Add the Lovelace resource '/local/dryad-card.js' if not automatically added."
