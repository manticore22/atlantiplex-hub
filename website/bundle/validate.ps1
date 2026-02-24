<# Validate the bundle before patching or shipping #>
Param()
$root = (Get-Location).Path
if(!(Test-Path (Join-Path -Path $root -ChildPath 'Seraphinix_Bundle.zip'))){
  Write-Error 'Bundle ZIP not found. Run assemble-zip.ps1 to generate.'
  exit 1
}
Write-Output 'Bundle ZIP exists. Ready for shipping.'
