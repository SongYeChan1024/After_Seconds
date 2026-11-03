Add-Type -AssemblyName System.Drawing
$root=$PSScriptRoot
$records=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $root 'image_results.json') | ConvertFrom-Json
$sheet=New-Object System.Drawing.Bitmap 2000,1750
$g=[System.Drawing.Graphics]::FromImage($sheet);$g.Clear([System.Drawing.Color]::FromArgb(80,80,80));$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$font=New-Object System.Drawing.Font 'Segoe UI',12
for($i=0;$i -lt $records.Count;$i++){
 $record=$records[$i];$path=Join-Path $root ($record.id+'_mesh_review.png');if(-not(Test-Path -LiteralPath $path)){continue}
 $source=[System.Drawing.Image]::FromFile($path);$x=($i%4)*500;$y=[math]::Floor($i/4)*350
 $g.DrawImage($source,[int]($x+5),[int]($y+5),490,318)
 $g.DrawString(($record.id+' '+$record.name),$font,[System.Drawing.Brushes]::White,[single]($x+10),[single]($y+327));$source.Dispose()
}
$sheet.Save((Join-Path $root 'batch02_mesh_contact_sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png);$font.Dispose();$g.Dispose();$sheet.Dispose()
