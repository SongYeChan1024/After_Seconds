Add-Type -AssemblyName System.Drawing
$imageRoot=$PSScriptRoot
$records=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $imageRoot 'image_results.json') | ConvertFrom-Json
$sheet=New-Object System.Drawing.Bitmap 1600,1360
$graphics=[System.Drawing.Graphics]::FromImage($sheet)
$graphics.Clear([System.Drawing.Color]::White)
$graphics.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$font=New-Object System.Drawing.Font 'Segoe UI',12
for($i=0;$i -lt $records.Count;$i++){
 $record=$records[$i]
 $path=Join-Path $imageRoot ($record.id+'_source.png')
 if(-not(Test-Path -LiteralPath $path)){continue}
 $source=[System.Drawing.Image]::FromFile($path)
 $x=($i%5)*320;$y=[math]::Floor($i/5)*340
 $ratio=[math]::Min(300/$source.Width,300/$source.Height)
 $width=[int]($source.Width*$ratio);$height=[int]($source.Height*$ratio)
 $graphics.DrawImage($source,[int]($x+(320-$width)/2),[int]($y+(310-$height)/2),$width,$height)
 $graphics.DrawString(($record.id+' '+$record.name),$font,[System.Drawing.Brushes]::Black,[single]($x+8),[single]($y+312))
 $source.Dispose()
}
$sheet.Save((Join-Path $imageRoot 'batch02_image_contact_sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$font.Dispose();$graphics.Dispose();$sheet.Dispose()
