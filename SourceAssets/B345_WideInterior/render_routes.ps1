# 확장 예상 경로 렌더러 V0.01 · 작성자 송예찬. player_routes.json을 읽기만 한다.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$base=Join-Path $repo 'Docs/도면/잠입_탐색'
$out=Join-Path $base '플레이어_예상이동'
$utf8=[System.Text.UTF8Encoding]::new($false)
$layout=Get-Content (Join-Path $base 'layout.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$routes=(Get-Content (Join-Path $out 'player_routes.json') -Encoding UTF8 -Raw | ConvertFrom-Json).routes
# 원안의 SVG/PNG를 읽어 복사본에만 표기한다.
$script:rtSvg=$null;$script:rtGraphics=$null
function C($value){[System.Drawing.ColorTranslator]::FromHtml($value)}
function RouteRect($x,$y,$w,$h,$fill){$script:rtSvg.AppendLine("<rect x='$x' y='$y' width='$w' height='$h' fill='$fill'/>")|Out-Null;$b=[System.Drawing.SolidBrush]::new((C $fill));$script:rtGraphics.FillRectangle($b,[single]$x,[single]$y,[single]$w,[single]$h);$b.Dispose()}
function L($x1,$y1,$x2,$y2,$color,$width=3,$dash=$false){$d=if($dash){" stroke-dasharray='11 6'"}else{''};$script:rtSvg.AppendLine("<line x1='$x1' y1='$y1' x2='$x2' y2='$y2' stroke='$color' stroke-width='$width' stroke-linecap='round'$d/>")|Out-Null;$pen=[System.Drawing.Pen]::new((C $color),[single]$width);$pen.StartCap=[System.Drawing.Drawing2D.LineCap]::Round;$pen.EndCap=[System.Drawing.Drawing2D.LineCap]::Round;if($dash){$pen.DashStyle=[System.Drawing.Drawing2D.DashStyle]::Dash};$script:rtGraphics.DrawLine($pen,[single]$x1,[single]$y1,[single]$x2,[single]$y2);$pen.Dispose()}
function T($x,$y,$txt,$size=17,$color='#203047',$anchor='start'){$safe=[System.Security.SecurityElement]::Escape([string]$txt);$script:rtSvg.AppendLine("<text x='$x' y='$y' font-size='$size' text-anchor='$anchor' fill='$color'>$safe</text>")|Out-Null;$font=[System.Drawing.Font]::new('Malgun Gothic',[single]$size,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel);$brush=[System.Drawing.SolidBrush]::new((C $color));$fmt=[System.Drawing.StringFormat]::new();$fmt.Alignment=if($anchor-eq'middle'){[System.Drawing.StringAlignment]::Center}else{[System.Drawing.StringAlignment]::Near};$script:rtGraphics.DrawString([string]$txt,$font,$brush,[single]$x,[single]($y-$size*1.05),$fmt);$fmt.Dispose();$brush.Dispose();$font.Dispose()}
function Dot($x,$y,$txt,$color,$radius=13){$script:rtSvg.AppendLine("<circle cx='$x' cy='$y' r='$radius' fill='white' stroke='$color' stroke-width='2.5'/>")|Out-Null;$b=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::White);$pen=[System.Drawing.Pen]::new((C $color),2.5);$script:rtGraphics.FillEllipse($b,[single]($x-$radius),[single]($y-$radius),[single](2*$radius),[single](2*$radius));$script:rtGraphics.DrawEllipse($pen,[single]($x-$radius),[single]($y-$radius),[single](2*$radius),[single](2*$radius));$b.Dispose();$pen.Dispose();T $x ($y+5) $txt 14 $color middle}
function PX($x){70+$x*22};function PY($y){112+$y*22}
function Arrow($x1,$y1,$x2,$y2,$color){$dx=$x2-$x1;$dy=$y2-$y1;$len=[math]::Sqrt($dx*$dx+$dy*$dy);if($len-lt25){return};$ux=$dx/$len;$uy=$dy/$len;$cx=$x1+$dx*.65;$cy=$y1+$dy*.65;L ($cx-$ux*9-$uy*6) ($cy-$uy*9+$ux*6) $cx $cy '#ffffff' 6;L ($cx-$ux*9+$uy*6) ($cy-$uy*9-$ux*6) $cx $cy '#ffffff' 6;L ($cx-$ux*9-$uy*6) ($cy-$uy*9+$ux*6) $cx $cy $color 2.5;L ($cx-$ux*9+$uy*6) ($cy-$uy*9-$ux*6) $cx $cy $color 2.5}
foreach($r in $routes){
 $stem=$r.floor+'_'+$r.floorName.Replace(' ','_')+'_잠입';$raw=[System.IO.File]::ReadAllText((Join-Path $base ($stem+'.svg')));$inner=$raw.Substring($raw.IndexOf('>')+1);$inner=$inner.Substring(0,$inner.LastIndexOf('</svg>'));$inner=[regex]::Replace($inner,'(?s)<title>.*?</title>|<desc>.*?</desc>','')
 $script:rtSvg=[System.Text.StringBuilder]::new();$script:rtSvg.AppendLine("<svg xmlns='http://www.w3.org/2000/svg' width='1660' height='1190' viewBox='0 0 1660 1190' font-family='Malgun Gothic, sans-serif'><title>$($r.floor) 예상 이동 $($r.variant) V0.04</title><desc>원안 도면의 복사본. 플레이어 예상 보행과 관찰 지점. Unity 또는 미니맵 아님.</desc>$inner")|Out-Null
 $image=[System.Drawing.Image]::FromFile((Join-Path $base ($stem+'.png')));$bitmap=[System.Drawing.Bitmap]::new(1660,1190);$script:rtGraphics=[System.Drawing.Graphics]::FromImage($bitmap);$script:rtGraphics.DrawImage($image,0,0,1660,1190);$image.Dispose();$script:rtGraphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias;$script:rtGraphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
 foreach($leg in $r.legs){for($i=0;$i-lt$leg.points.Count-1;$i++){$a=$leg.points[$i];$b=$leg.points[$i+1];L (PX $a[0]) (PY $a[1]) (PX $b[0]) (PY $b[1]) '#ffffff' 8;L (PX $a[0]) (PY $a[1]) (PX $b[0]) (PY $b[1]) $r.color 3.5 ($r.variant-ne'A');Arrow (PX $a[0]) (PY $a[1]) (PX $b[0]) (PY $b[1]) $r.color}}
 for($i=0;$i-lt$r.nodes.Count;$i++){$pt=$r.nodes[$i];$label=if($r.variant-eq'C'){if($i-eq0){'D'}elseif($i-eq$r.nodes.Count-1){'H'}else{"$i"}}elseif($i-eq0){'E'}elseif($i-eq$r.nodes.Count-1){'T'}else{"$i"};Dot (PX $pt.x) (PY $pt.y) $label $r.color}
 foreach($risk in $r.cameraOverlaps){Dot (PX $risk.x) (PY $risk.y) '!' '#9a5800' 9}
 RouteRect 0 0 1660 82 '#ffffff';T 70 42 ("AFTER SECONDS / "+$r.floor+' 예상 이동 '+$r.variant+' · '+$r.name+' V0.04') 26;T 70 73 '설계도 복사본 · 화살표는 진행 방향 · 정적 보행만 검사 · 적 대응과 성공 여부는 가안' 17 '#475569'
 RouteRect 1250 100 410 1050 '#ffffff';$lx=1280;T $lx 140 ($r.variant+' · '+$r.name) 23 $r.color
 T $lx 180 ('보행 약 '+$r.walkingMetres+'m · 평면 계산') 18
 T $lx 211 '이동 중 대기·관찰 시간은 미포함' 15 '#64748b'
 $yy=260;for($i=0;$i-lt$r.nodes.Count;$i++){$pt=$r.nodes[$i];$label=if($r.variant-eq'C'){if($i-eq0){'D'}elseif($i-eq$r.nodes.Count-1){'H'}else{"$i"}}elseif($i-eq0){'E'}elseif($i-eq$r.nodes.Count-1){'T'}else{"$i"};Dot ($lx+10) ($yy-6) $label $r.color 11;T ($lx+30) $yy ($pt.label -replace '^[ET] · ','') 16;$yy+=44}
 $yy=[math]::Max(590,$yy+24);T $lx $yy '감시 구간 확인' 21;$yy+=36
 if($r.cameraOverlaps.Count){T $lx $yy ('!  표시 범위와 겹침: '+(($r.cameraOverlaps|ForEach-Object camera)-join', ')) 15 '#9a5800';$yy+=28;T $lx $yy '현재 도면 자세 기준. 무발각 보장 아님.' 15 '#9a5800'}else{T $lx $yy '표시된 CCTV 부채꼴과 직접 겹침 없음' 15 '#475569';$yy+=28;T $lx $yy '다른 시각·문 너머 감시는 미검증' 15 '#475569'}
 $yy+=65;T $lx $yy '읽는 기준' 21;$yy+=34
 foreach($txt in @('굵은 색 선: 이 복사본의 예상 이동','빨간 점선: 원안 경비 순찰','황색 점선: 원안 연구원 도주','보라 점선: 원안 교환 검토 구간')){T $lx $yy $txt 15 '#475569';$yy+=27}
 if($r.variant-eq'C'){T $lx ($yy+18) 'D는 발각 가정 지점, H는 재관찰 후보.' 15 $r.color;T $lx ($yy+45) '추격을 따돌렸다는 판정은 하지 않음.' 15 $r.color}
 elseif($r.floor-eq'B5'){T $lx ($yy+18) '원안 교환은 계단 반대쪽으로 향함.' 15 '#7352a3';T $lx ($yy+45) '이번 보행선에 교환을 포함하지 않음.' 15 '#7352a3'}
 RouteRect 0 1138 1660 52 '#ffffff';T 70 1160 '2026-11-06 · 작성자 송예찬 · 예상 이동안 V0.04 · 확장 도면의 경로 복사본 · UI 미구현 · 실제 플레이와 시간에 따른 안전성 미검증' 14 '#64748b'
 $script:rtSvg.AppendLine('</svg>')|Out-Null;$file=$r.floor+'_'+$r.variant+'_예상이동';[System.IO.File]::WriteAllText((Join-Path $out ($file+'.svg')),$script:rtSvg.ToString(),$utf8);$bitmap.Save((Join-Path $out ($file+'.png')),[System.Drawing.Imaging.ImageFormat]::Png);$script:rtGraphics.Dispose();$bitmap.Dispose()
}
function Contact($files,$name,$cols){$rows=[math]::Ceiling($files.Count/$cols);$bmp=[System.Drawing.Bitmap]::new(($cols*830),([int]$rows*595));$g=[System.Drawing.Graphics]::FromImage($bmp);$g.Clear([System.Drawing.Color]::White);for($i=0;$i-lt$files.Count;$i++){$img=[System.Drawing.Image]::FromFile((Join-Path $out $files[$i]));$g.DrawImage($img,($i%$cols)*830,([int][math]::Floor($i/$cols))*595,830,595);$img.Dispose()};$bmp.Save((Join-Path $out $name),[System.Drawing.Imaging.ImageFormat]::Png);$g.Dispose();$bmp.Dispose()}
Contact @($layout.floors|ForEach-Object{$_.floor+'_A_예상이동.png'}) '전체층_A_탐색경로.png' 3
Contact @('B5_A_예상이동.png','B5_B_예상이동.png','B5_C_예상이동.png') 'B5_경로비교.png' 3
