# 터널·돔 단면 기준 V0.01 · 작성자 송예찬
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$out=Join-Path $repo 'Docs/도면/잠입_탐색'
$svg=[Text.StringBuilder]::new()
$svg.AppendLine("<svg xmlns='http://www.w3.org/2000/svg' width='1800' height='1150' viewBox='0 0 1800 1150' font-family='Malgun Gothic,sans-serif'><rect width='1800' height='1150' fill='#f6f8fa'/>")|Out-Null
$bmp=[Drawing.Bitmap]::new(1800,1150);$g=[Drawing.Graphics]::FromImage($bmp);$g.Clear([Drawing.ColorTranslator]::FromHtml('#f6f8fa'));$g.SmoothingMode='AntiAlias';$g.TextRenderingHint='AntiAliasGridFit'
function Color($c){[Drawing.ColorTranslator]::FromHtml($c)}
function Line($x1,$y1,$x2,$y2,$c='#273b4e',$w=3){$svg.AppendLine("<line x1='$x1' y1='$y1' x2='$x2' y2='$y2' stroke='$c' stroke-width='$w'/>")|Out-Null;$p=[Drawing.Pen]::new((Color $c),$w);$g.DrawLine($p,[single]$x1,[single]$y1,[single]$x2,[single]$y2);$p.Dispose()}
function Txt($x,$y,$s,$size=20,$c='#273b4e'){$t=[Security.SecurityElement]::Escape($s);$svg.AppendLine("<text x='$x' y='$y' font-size='$size' fill='$c'>$t</text>")|Out-Null;$f=[Drawing.Font]::new('Malgun Gothic',$size,[Drawing.FontStyle]::Regular,[Drawing.GraphicsUnit]::Pixel);$b=[Drawing.SolidBrush]::new((Color $c));$g.DrawString($s,$f,$b,[single]$x,[single]($y-$size*1.03));$f.Dispose();$b.Dispose()}
function Arch($x,$springY,$w,$rise,$c='#557d86',$pen=8){$svg.AppendLine("<path d='M$x,$springY A$($w/2),$rise 0 0,1 $($x+$w),$springY' fill='none' stroke='$c' stroke-width='$pen'/>")|Out-Null;$p=[Drawing.Pen]::new((Color $c),$pen);$g.DrawArc($p,[single]$x,[single]($springY-$rise),[single]$w,[single](2*$rise),180,180);$p.Dispose()}
Txt 55 55 'AFTER SECONDS / 터널·돔 실내 구조 기준 V0.04' 32
Txt 55 90 '작성자 송예찬 · 2026-11-06 · 평면도 V0.04와 함께 보는 단면·연결·엄폐 기준' 18 '#5e7180'
Txt 65 150 '01  복도는 연속된 반원 터널' 25
$x=95;$floor=600;$scale=93;$width=4.2*$scale;$spring=$floor-2.015*$scale
Line $x $floor ($x+$width) $floor '#273b4e' 9
Line $x $floor $x $spring '#557d86' 12;Line ($x+$width) $floor ($x+$width) $spring '#557d86' 12
Arch $x $spring $width (1.94*$scale) '#557d86' 12
Arch ($x+.32*$scale) ($floor-2.04*$scale) ($width-.64*$scale) (1.78*$scale) '#273b4e' 19
Line ($x+.32*$scale) ($floor-2.04*$scale) ($x+.46*$scale) $floor '#273b4e' 19
Line ($x+$width-.32*$scale) ($floor-2.04*$scale) ($x+$width-.46*$scale) $floor '#273b4e' 19
Line ($x+160) ($floor-3.86*$scale) ($x+230) ($floor-3.86*$scale) '#c4a35e' 8
Line 105 643 475 643 '#75959c' 2;Txt 180 676 '벽 기준 4.2m / 북측 4.8m' 20
Txt 85 715 '천장 높이 4m · 아치 사이에도 곡면이 이어짐' 19
Txt 85 750 '리브 24cm × 44cm / 하단 돌출 약58cm' 19
Txt 85 785 '리브 사이 통행 폭: 일반3.04m · 북측3.64m' 18
Txt 625 150 '02  주요 방은 돔, 높은 설비부터 확인' 25
$x=645;$w=490;$base=600;$sy=450
Line $x $base ($x+$w) $base '#273b4e' 9
Line $x $base $x $sy '#557d86' 10;Line ($x+$w) $base ($x+$w) $sy '#557d86' 10
Arch $x $sy $w 185 '#557d86' 12
Arch ($x+18) ($sy+1) ($w-36) 173 '#273b4e' 6
Txt 670 650 'B5 격리실: 5.95 → 7.2m / 포드 최고6.44m' 18
Txt 670 686 'B5 냉각실: 3.1 → 5.2m' 18
Txt 670 722 'B4 관제 데크: 4.5 → 5.6m / 데크 머리 공간 유지' 18
Txt 670 758 'B3 시료실: 3.6 → 4.8m / 랙 윗공간 유지' 18
Txt 1220 150 '03  문과 벽면 설비를 계획에 포함' 25
Arch 1300 410 260 135 '#557d86' 12
Line 1315 410 1315 610 '#557d86' 12;Line 1545 410 1545 610 '#557d86' 12
Line 1360 610 1360 350 '#273b4e' 8;Line 1500 610 1500 350 '#273b4e' 8;Line 1360 350 1500 350 '#273b4e' 8
Line 1270 610 1600 610 '#273b4e' 8
Txt 1245 650 '문 앞은 측면 아치 연결부로 천장을 전환' 18
Txt 1245 686 '문 폭1.5m / 문 높이2.8m / 수납부 유지' 18
Txt 1245 722 '큰 차폐벽 철거 → 벽 쪽 설비4개/층' 18
Txt 1245 758 '설비 약1.06 × 0.45 × 1.85m' 18
Line 55 845 1745 845 '#cbd5df' 2
Txt 65 895 '함께 맞추는 항목' 23
Txt 65 938 '평면도: 방·문·설비·예상 이동  /  단면: 터널·돔·문 접합  /  Unity: 같은 치수의 메시·충돌·조명' 21
Txt 65 980 '계단·리프트 연결 위치와 방 크기는 유지하며, 기존 사각 천장과 큰 차폐벽을 새 곡면 구조에 남겨 겹치지 않는다.' 19
Txt 65 1022 '엄폐는 벽 쪽 설비에서 제공한다. 긴 시야·경비 배치와 감시 난이도는 이후 사용자 플레이로 조정한다.' 19
Txt 65 1090 'B5/B4/B3 제작 기준 · B2/B1/1F는 수직 코어를 공유하는 설계 가안 · 게임 C# / UI / 미니맵은 미구현' 17 '#5e7180'
$svg.AppendLine('</svg>')|Out-Null
[IO.File]::WriteAllText((Join-Path $out '터널_돔_단면_기준.svg'),$svg.ToString(),[Text.UTF8Encoding]::new($false))
$bmp.Save((Join-Path $out '터널_돔_단면_기준.png'),[Drawing.Imaging.ImageFormat]::Png);$g.Dispose();$bmp.Dispose()
