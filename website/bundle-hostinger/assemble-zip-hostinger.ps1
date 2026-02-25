<#
  Create the Hostinger SaaS patch ZIP in one go.
  Output: Seraphinix_Bundle_Hostinger_SaaS.zip
#>
Param()

$root = (Get-Location).Path
$zipOut = Join-Path -Path $root -ChildPath 'Seraphinix_Bundle_Hostinger_SaaS.zip'
$src = @(
  'bundle-hostinger/*',
  'bundle/manifest.json',
  'bundle/README.md',
  'bundle/assemble-zip.ps1',
  'bundle/validate.ps1',
  'bundle/launch-hostinger.sh',
  'bundle-hostinger/*',
  'bundle-hostinger/nginx-seraphonix.conf',
  'bundle-hostinger/deploy-guide.md',
  'bundle-hostinger/setup.sh',
  'bundle-hostinger/health.sh'
)

Compress-Archive -Path $src -DestinationPath $zipOut -Force
Write-Output "Hostinger bundle created at $zipOut"
