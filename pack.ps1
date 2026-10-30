$src = "C:\Users\ABID\Documents\Qoder\2026-10-29\c80c96df"
$out = Join-Path ([Environment]::GetFolderPath('Desktop')) "FavourHouse.zip"
if (Test-Path $out) { Remove-Item $out -Force }

$stage = Join-Path $env:TEMP "favourhouse-pack"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null
robocopy $src $stage /E /XD __pycache__ /XF *.pyc *.log /NFL /NDL /NJH /NJS /NP | Out-Null

Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $out -CompressionLevel Optimal
Remove-Item $stage -Recurse -Force

$z = Get-Item $out
"zip: $($z.FullName)"
"size: {0:N1} MB" -f ($z.Length / 1MB)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$a = [System.IO.Compression.ZipFile]::OpenRead($out)
"entries: " + $a.Entries.Count
$names = $a.Entries | ForEach-Object { $_.FullName }
foreach ($n in @('manage.py','db.sqlite3','start.bat','launch.vbs','requirements.txt')) {
  "check $n : " + ($names -contains $n)
}
"media: " + ($names | Where-Object { $_ -like 'media*' }).Count + "  static: " + ($names | Where-Object { $_ -like 'static*' }).Count + "  templates: " + ($names | Where-Object { $_ -like 'templates*' }).Count
$a.Dispose()
