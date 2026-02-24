<#
  Create the Hostinger SaaS patch ZIP in one go (updated output name).
  Output: Seraphonix_Bundle_Hostinger_SaaS.zip
 #>
Param()

$root = (Get-Location).Path
$zipOut = Join-Path -Path $root -ChildPath 'Seraphinix_Bundle_Hostinger_SaaS.zip'
# NOTE: Rename to Seraphonix_Bundle_Hostinger_SaaS.zip in final bundle for branding accuracy.
$src = @(
  'bundle-hostinger/*',
  'bundle/manifest.json',
  'bundle/README.md',
  'bundle/assemble-zip-hostinger.ps1',
  'bundle/validate.ps1',
  'bundle/launch-hostinger.sh',
  'bundle-hostinger/*',
  'bundle-hostinger/nginx-seraphonix.conf',
  'bundle-hostinger/deploy-guide.md',
  'bundle-hostinger/setup.sh',
  'bundle-hostinger/health.sh',
  'bundle-hostinger/test-end-to-end-hostinger.sh'
)

Compress-Archive -Path $src -DestinationPath $zipOut -Force
Write-Output "Hostinger bundle created at $zipOut"
