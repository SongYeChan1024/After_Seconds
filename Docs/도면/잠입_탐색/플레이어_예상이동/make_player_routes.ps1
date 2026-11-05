# 플레이어 예상 이동 도면 복사본 생성기 V0.01 · 작성자 송예찬
# 의사코드: 원안 좌표 읽기 → 관찰/우회/재배치 지점 지정 → 정적 보행 경로 계산
# → 원안 도면 복사본에 방향·순서를 표시 → 원안 보존/경로 검사. Unity·미니맵을 수정하지 않는다.
param([string]$OutputDirectory=$PSScriptRoot)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$base=Split-Path -Parent $PSScriptRoot
$out=[System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $out | Out-Null
$utf8=[System.Text.UTF8Encoding]::new($false)
$layoutPath=Join-Path $base 'layout.json'
$layout=Get-Content -Raw -Encoding UTF8 -LiteralPath $layoutPath | ConvertFrom-Json
$source=[System.IO.File]::ReadAllText((Join-Path $base 'make_stealth_plans.ps1'))
$cs=[regex]::Match($source,"(?s)Add-Type @'\r?\n(.*?)\r?\n'@")
if(!$cs.Success){throw 'PlanGrid source not found'}
if(-not('PlanGrid'-as[type])){Add-Type -TypeDefinition $cs.Groups[1].Value}
function Flat($items){$a=[System.Collections.Generic.List[double]]::new();foreach($r in $items){$a.AddRange([double[]]@($r.x,$r.y,$r.w,$r.h))};return ,$a.ToArray()}
function Simple($grid,$ids){$p=[System.Collections.Generic.List[object]]::new();for($i=0;$i-lt$ids.Count;$i++){if($i-gt0-and$i-lt$ids.Count-1-and($ids[$i]-$ids[$i-1])-eq($ids[$i+1]-$ids[$i])){continue};$x=(($ids[$i]%$grid.W)+.5)*$grid.Cell;$y=([math]::Floor($ids[$i]/$grid.W)+.5)*$grid.Cell;$p.Add(@($x,$y))};return ,$p.ToArray()}
function Point($x,$y,$label){[pscustomobject]@{x=[double]$x;y=[double]$y;label=$label}}
$configs=@{
 B5=@{
  A=@((Point 20.5 21 '중앙 복도로 이동'),(Point 22.5 26 '모니터링실 문밖 관찰'),(Point 31.5 29.5 '유틸리티실로 돌아 접근'))
  B=@((Point 4.5 29.5 '경비 초소 접근 상태 확인'),(Point 13.5 29.5 '격리 전실 통과'),(Point 26 29.5 '모니터링실 가장자리 검토'),(Point 31.5 29.5 '동측 남구간으로 합류'))
  C=@((Point 29 20 '냉각조 남측에서 발각 가정'),(Point 20.5 21 '문과 코너를 지나 이탈'),(Point 13.5 29.5 '격리 전실에서 재관찰'))
 }
 B4=@{
  A=@((Point 24.5 21.5 '관제 데크 아래쪽 관찰'),(Point 24 8 '분석실 진입 전 연구원 확인'))
  B=@((Point 31.5 29.5 '유틸리티실 우회'),(Point 7.5 19 '남측 관찰실 경유'),(Point 7.5 9 '북측 관찰실로 이동'),(Point 37.5 5.5 '동측 북구간 접근'))
  C=@((Point 29 8 '분석실에서 발각 가정'),(Point 20.5 2 '북측 복도로 빠짐'),(Point 1.5 9 '서측으로 돌아감'),(Point 7.5 9 '관찰실에서 재관찰'))
 }
 B3=@{
  A=@((Point 29 17 '청정 구역 관찰'),(Point 25 11 '서쪽 제염 출입구로 접근'))
  B=@((Point 31.5 29.5 '환복실 경유'),(Point 8 13.5 '랙 사이 중앙 통로 이용'),(Point 20.5 2 '북측 복도로 돌아감'))
  C=@((Point 29 21.5 '청정 구역에서 발각 가정'),(Point 20.5 20 '중앙 복도로 이탈'),(Point 8 13.5 '랙 뒤에서 재관찰'))
 }
 B2=@{
  A=@((Point 29 9 '전기 제어실 관찰'),(Point 24.5 22 '관제 섬 서쪽으로 돌아감'))
  B=@((Point 11 13 '원심분리기 사이 경유'),(Point 13.5 29.5 '펌프실로 돌아감'),(Point 31.5 29.5 '설비실 경유'),(Point 24.5 22 '관제실 하단으로 합류'))
  C=@((Point 24 19 '관제실에서 발각 가정'),(Point 20.5 25.5 '남측 복도로 이탈'),(Point 13.5 29.5 '펌프실에서 재관찰'))
 }
 B1=@{
  A=@((Point 33.5 14 '챔버 동측을 따라 관찰'),(Point 29 6 '북측 관찰 부스 경유'))
  B=@((Point 22.5 29.5 '의료 준비실 경유'),(Point 11 22 '기록실 하단 통과'),(Point 17.5 9 '준비실 문 근처 관찰'),(Point 29 6 '북측 관찰 부스로 합류'))
  C=@((Point 33 14 '챔버에서 발각 가정'),(Point 20.5 14 '중앙 복도로 이탈'),(Point 11 22 '기록 랙 뒤에서 재관찰'))
 }
 '1F'=@{
  A=@((Point 32 15 '하역 구역 가장자리 관찰'),(Point 32 22 '검문소 측면으로 접근'))
  B=@((Point 8 13.5 '적재물 사이로 이동'),(Point 6 29.5 '사무실 경유'),(Point 18 29.5 '탈의실에서 출구 전실로'))
  C=@((Point 32 21.5 '검문소에서 발각 가정'),(Point 20.5 20 '중앙 복도로 이탈'),(Point 8 13.5 '적재물 뒤에서 재관찰'))
 }
}
function RoomAt($p,$x,$y){@($p.rooms|Where-Object{$x-ge$_.x-and$x-le$_.x+$_.w-and$y-ge$_.y-and$y-le$_.y+$_.h})}
function CameraAt($p,$x,$y){$hit=@();foreach($c in $p.cameras){$r=@($p.rooms|Where-Object id -eq $c.room)[0];if($x-lt$r.x-or$x-gt$r.x+$r.w-or$y-lt$r.y-or$y-gt$r.y+$r.h){continue};$dx=$x-$c.x;$dy=$y-$c.y;if($dx*$dx+$dy*$dy-gt$c.range*$c.range){continue};$angle=[math]::Atan2($dy,$dx)*180/[math]::PI;$delta=[math]::Abs((($angle-$c.angle+540)%360)-180);if($delta-le$c.fov/2){$hit+=$c.id}};return $hit}
$routes=[System.Collections.Generic.List[object]]::new()
foreach($p in $layout.floors){
 $doorRects=@($p.doors|Where-Object state -eq open|ForEach-Object{if($_.axis-eq'V'){[pscustomobject]@{x=$_.x-.7;y=$_.y-$_.width/2+.3;w=1.4;h=$_.width-.6}}else{[pscustomobject]@{x=$_.x-$_.width/2+.3;y=$_.y-.7;w=$_.width-.6;h=1.4}}})
 $grid=[PlanGrid]::new(192,152,.25,(Flat $p.rooms),(Flat $p.blocks),(Flat $doorRects))
 foreach($key in @('A','B','C')){
  $nodes=[System.Collections.Generic.List[object]]::new();if($key-ne'C'){$nodes.Add((Point $p.entry[0] $p.entry[1] 'E · 층 진입'))};foreach($pt in $configs[$p.floor][$key]){$nodes.Add($pt)};if($key-ne'C'){$nodes.Add((Point $p.exit[0] $p.exit[1] 'T · 다음 층 / 외부 전실'))}
  $legs=[System.Collections.Generic.List[object]]::new();$metres=0.;$exposure=[ordered]@{}
  for($i=0;$i-lt$nodes.Count-1;$i++){$a=$nodes[$i];$b=$nodes[$i+1];$ids=$grid.Search($a.x,$a.y,$b.x,$b.y);if(!$ids.Count){throw "Blocked route $($p.floor)/$key/$i $($a.label) -> $($b.label)"};$length=($ids.Count-1)*.25;$metres+=$length;$legs.Add([pscustomobject]@{from=$i;to=$i+1;length=$length;points=(Simple $grid $ids)});foreach($id in $ids){$cx=(($id%$grid.W)+.5)*.25;$cy=([math]::Floor($id/$grid.W)+.5)*.25;foreach($cam in (CameraAt $p $cx $cy)){if(!$exposure.Contains($cam)){$exposure[$cam]=[pscustomobject]@{camera=$cam;x=$cx;y=$cy;leg=$i}}}}
  }
  $name=switch($key){A{'탐색·보행 예시'}B{'다른 접근 경로'}C{'발각 후 재배치 가정'}}
  $color=switch($key){A{'#1569b5'}B{'#087f74'}C{'#c24d19'}}
  $routes.Add([pscustomobject]@{floor=$p.floor;floorName=$p.name;variant=$key;name=$name;color=$color;nodes=$nodes.ToArray();legs=$legs.ToArray();walkingMetres=[math]::Round($metres,1);cameraOverlaps=@($exposure.Values);status='설계용 예상·성공 보장 아님';notes=@('각 관찰 지점 사이의 정적 보행 예시. 전체 최단·최적 경로가 아님.','적의 시간 변화·연구원 시야·추격·경보·은신 성공은 미검증.');sourceFloor=$p})
 }
}

# 원안의 SVG/PNG를 읽어 복사본에만 표기한다.
$script:rtSvg=$null;$script:rtGraphics=$null
function C($value){[System.Drawing.ColorTranslator]::FromHtml($value)}
function RouteRect($x,$y,$w,$h,$fill){$script:rtSvg.AppendLine("<rect x='$x' y='$y' width='$w' height='$h' fill='$fill'/>")|Out-Null;$b=[System.Drawing.SolidBrush]::new((C $fill));$script:rtGraphics.FillRectangle($b,[single]$x,[single]$y,[single]$w,[single]$h);$b.Dispose()}
function L($x1,$y1,$x2,$y2,$color,$width=3,$dash=$false){$d=if($dash){" stroke-dasharray='11 6'"}else{''};$script:rtSvg.AppendLine("<line x1='$x1' y1='$y1' x2='$x2' y2='$y2' stroke='$color' stroke-width='$width' stroke-linecap='round'$d/>")|Out-Null;$pen=[System.Drawing.Pen]::new((C $color),[single]$width);$pen.StartCap=[System.Drawing.Drawing2D.LineCap]::Round;$pen.EndCap=[System.Drawing.Drawing2D.LineCap]::Round;if($dash){$pen.DashStyle=[System.Drawing.Drawing2D.DashStyle]::Dash};$script:rtGraphics.DrawLine($pen,[single]$x1,[single]$y1,[single]$x2,[single]$y2);$pen.Dispose()}
function T($x,$y,$txt,$size=17,$color='#203047',$anchor='start'){$safe=[System.Security.SecurityElement]::Escape([string]$txt);$script:rtSvg.AppendLine("<text x='$x' y='$y' font-size='$size' text-anchor='$anchor' fill='$color'>$safe</text>")|Out-Null;$font=[System.Drawing.Font]::new('Malgun Gothic',[single]$size,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel);$brush=[System.Drawing.SolidBrush]::new((C $color));$fmt=[System.Drawing.StringFormat]::new();$fmt.Alignment=if($anchor-eq'middle'){[System.Drawing.StringAlignment]::Center}else{[System.Drawing.StringAlignment]::Near};$script:rtGraphics.DrawString([string]$txt,$font,$brush,[single]$x,[single]($y-$size*1.05),$fmt);$fmt.Dispose();$brush.Dispose();$font.Dispose()}
function Dot($x,$y,$txt,$color,$radius=13){$script:rtSvg.AppendLine("<circle cx='$x' cy='$y' r='$radius' fill='white' stroke='$color' stroke-width='2.5'/>")|Out-Null;$b=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::White);$pen=[System.Drawing.Pen]::new((C $color),2.5);$script:rtGraphics.FillEllipse($b,[single]($x-$radius),[single]($y-$radius),[single](2*$radius),[single](2*$radius));$script:rtGraphics.DrawEllipse($pen,[single]($x-$radius),[single]($y-$radius),[single](2*$radius),[single](2*$radius));$b.Dispose();$pen.Dispose();T $x ($y+5) $txt 14 $color middle}
function PX($x){70+$x*24};function PY($y){112+$y*24}
function Arrow($x1,$y1,$x2,$y2,$color){$dx=$x2-$x1;$dy=$y2-$y1;$len=[math]::Sqrt($dx*$dx+$dy*$dy);if($len-lt25){return};$ux=$dx/$len;$uy=$dy/$len;$cx=$x1+$dx*.65;$cy=$y1+$dy*.65;L ($cx-$ux*9-$uy*6) ($cy-$uy*9+$ux*6) $cx $cy '#ffffff' 6;L ($cx-$ux*9+$uy*6) ($cy-$uy*9-$ux*6) $cx $cy '#ffffff' 6;L ($cx-$ux*9-$uy*6) ($cy-$uy*9+$ux*6) $cx $cy $color 2.5;L ($cx-$ux*9+$uy*6) ($cy-$uy*9-$ux*6) $cx $cy $color 2.5}
foreach($r in $routes){
 $stem=$r.floor+'_'+$r.floorName.Replace(' ','_')+'_잠입';$raw=[System.IO.File]::ReadAllText((Join-Path $base ($stem+'.svg')));$inner=$raw.Substring($raw.IndexOf('>')+1);$inner=$inner.Substring(0,$inner.LastIndexOf('</svg>'));$inner=[regex]::Replace($inner,'(?s)<title>.*?</title>|<desc>.*?</desc>','')
 $script:rtSvg=[System.Text.StringBuilder]::new();$script:rtSvg.AppendLine("<svg xmlns='http://www.w3.org/2000/svg' width='1660' height='1190' viewBox='0 0 1660 1190' font-family='Malgun Gothic, sans-serif'><title>$($r.floor) 예상 이동 $($r.variant) V0.01</title><desc>원안 도면의 복사본. 플레이어 예상 보행과 관찰 지점. Unity 또는 미니맵 아님.</desc>$inner")|Out-Null
 $image=[System.Drawing.Image]::FromFile((Join-Path $base ($stem+'.png')));$bitmap=[System.Drawing.Bitmap]::new(1660,1190);$script:rtGraphics=[System.Drawing.Graphics]::FromImage($bitmap);$script:rtGraphics.DrawImage($image,0,0,1660,1190);$image.Dispose();$script:rtGraphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias;$script:rtGraphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
 foreach($leg in $r.legs){for($i=0;$i-lt$leg.points.Count-1;$i++){$a=$leg.points[$i];$b=$leg.points[$i+1];L (PX $a[0]) (PY $a[1]) (PX $b[0]) (PY $b[1]) '#ffffff' 8;L (PX $a[0]) (PY $a[1]) (PX $b[0]) (PY $b[1]) $r.color 3.5 ($r.variant-ne'A');Arrow (PX $a[0]) (PY $a[1]) (PX $b[0]) (PY $b[1]) $r.color}}
 for($i=0;$i-lt$r.nodes.Count;$i++){$pt=$r.nodes[$i];$label=if($r.variant-eq'C'){if($i-eq0){'D'}elseif($i-eq$r.nodes.Count-1){'H'}else{"$i"}}elseif($i-eq0){'E'}elseif($i-eq$r.nodes.Count-1){'T'}else{"$i"};Dot (PX $pt.x) (PY $pt.y) $label $r.color}
 foreach($risk in $r.cameraOverlaps){Dot (PX $risk.x) (PY $risk.y) '!' '#9a5800' 9}
 RouteRect 0 0 1660 82 '#ffffff';T 70 42 ("AFTER SECONDS / "+$r.floor+' 예상 이동 '+$r.variant+' · '+$r.name+' V0.01') 26;T 70 73 '설계도 복사본 · 화살표는 진행 방향 · 정적 보행만 검사 · 적 대응과 성공 여부는 가안' 17 '#475569'
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
 RouteRect 0 1138 1660 52 '#ffffff';T 70 1160 '2026-11-05 · 작성자 송예찬 · 예상 이동안 V0.01 · 원안 도면/Unity 미수정 · 실제 플레이와 시간에 따른 안전성 미검증' 14 '#64748b'
 $script:rtSvg.AppendLine('</svg>')|Out-Null;$file=$r.floor+'_'+$r.variant+'_예상이동';[System.IO.File]::WriteAllText((Join-Path $out ($file+'.svg')),$script:rtSvg.ToString(),$utf8);$bitmap.Save((Join-Path $out ($file+'.png')),[System.Drawing.Imaging.ImageFormat]::Png);$script:rtGraphics.Dispose();$bitmap.Dispose()
}
function Contact($files,$name,$cols){$rows=[math]::Ceiling($files.Count/$cols);$bmp=[System.Drawing.Bitmap]::new(($cols*830),([int]$rows*595));$g=[System.Drawing.Graphics]::FromImage($bmp);$g.Clear([System.Drawing.Color]::White);for($i=0;$i-lt$files.Count;$i++){$img=[System.Drawing.Image]::FromFile((Join-Path $out $files[$i]));$g.DrawImage($img,($i%$cols)*830,([int][math]::Floor($i/$cols))*595,830,595);$img.Dispose()};$bmp.Save((Join-Path $out $name),[System.Drawing.Imaging.ImageFormat]::Png);$g.Dispose();$bmp.Dispose()}
Contact @($layout.floors|ForEach-Object{$_.floor+'_A_예상이동.png'}) '전체층_A_탐색경로.png' 3
Contact @('B5_A_예상이동.png','B5_B_예상이동.png','B5_C_예상이동.png') 'B5_경로비교.png' 3
$export=$routes|Select-Object * -ExcludeProperty sourceFloor
[System.IO.File]::WriteAllText((Join-Path $out 'player_routes.json'),([pscustomobject]@{version='V0.01';author='송예찬';sourceSHA256=(Get-FileHash -LiteralPath $layoutPath -Algorithm SHA256).Hash;scope='설계도 복사본만 생성. Unity/미니맵/UI 미수정.';routeMeaning='정답·최적·안전 경로가 아닌 설계 검토용 예상 이동. CCTV 중첩은 현재 표시 자세의 2D 겹침.';b5SwapIssue='원안은 냉각조 남측→북측 교환으로 계단(동측 남단)과 멀어진다. 예상 보행에 포함하지 않았으며 새 B5 구현 전에 방향/표적 배치 검토 필요.';routes=@($export)}|ConvertTo-Json -Depth 24),$utf8)
[System.IO.File]::WriteAllText((Join-Path $out 'route_validation.json'),(@($routes|ForEach-Object{[pscustomobject]@{floor=$_.floor;variant=$_.variant;walkingMetres=$_.walkingMetres;legs=$_.legs.Count;allWalkingLegsConnected=$true;cameraOverlapCount=$_.cameraOverlaps.Count;temporalSafetyVerified=$false}})|ConvertTo-Json -Depth 6),$utf8)
$routes|Select-Object floor,variant,walkingMetres,@{n='cameraOverlaps';e={$_.cameraOverlaps.Count}}|Format-Table -AutoSize
