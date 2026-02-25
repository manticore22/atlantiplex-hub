<#
  Bundle assembler for Seraphonix design system and brand site.
  Produces Seraphonix_Bundle.zip containing brand-site/ and design-system/
#>
Param()
 
$root = (Get-Location).Path
$src = @("brand-site/*","design-system/*")
$dest = Join-Path -Path $root -ChildPath "Seraphonix_Bundle.zip"
Compress-Archive -Path $src -DestinationPath $dest -Force
Write-Output "Bundle created at $dest"
