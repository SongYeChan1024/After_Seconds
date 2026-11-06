from pathlib import Path
S=Path(__file__).resolve().parent;R=S.parents[1];D=R/'Docs/도면/잠입_탐색'
raw=(D/'make_stealth_plans.ps1').read_text(encoding='utf-8-sig')
a=raw.index('# 같은 도형 명령');b=raw.index('$document=',a)
p=raw[a:b]+raw[raw.index('$sheet=',b):raw.index('$validation.ToArray() |',b)]
p=p.replace('PlanScale=24','PlanScale=22').replace('*24','*22').replace('*12)', '*11)').replace('-le48','-le52').replace('-le32','-le34')
p=p.replace('V0.02','V0.04').replace('48×32m','51.6×34m (코어 단차)').replace('Unity 미적용','B5/B4/B3 제작 기준 · 상층 가안')
p=p.replace('잠입·탐색 평면도','터널·돔 구조 평면도')
p=p.replace("{1070}else{940}","{1010}else{940}")
p=p.replace("if($b.kind-ne'baffle'){Txt (X ($b.x+$b.w/2)) (Y ($b.y+$b.h/2+.15)) $b.name", "if($b.kind-ne'baffle'){$dy=.15;if($b.kind-eq'equipment'){$cy=$b.y+$b.h/2;$dy=if($cy-lt1-or($cy-gt25-and$cy-lt26)){1.0}else{-.7}};Txt (X ($b.x+$b.w/2)) (Y ($b.y+$b.h/2+$dy)) $b.name")
p=p.replace(" foreach($d in $p.doors){",''' foreach($room in $p.rooms){if($room.roof.kind -eq 'dome'){$cx=X ($room.x+$room.w/2);$cy=Y ($room.y+$room.h/2);$rw=($room.w-.8)*22;$rh=($room.h-.8)*22;$script:svg.AppendLine("<ellipse cx='$cx' cy='$cy' rx='$($rw/2)' ry='$($rh/2)' fill='none' stroke='#a2bcbc' stroke-width='1.4' stroke-dasharray='6 5'/>")|Out-Null;$pen=[System.Drawing.Pen]::new((Col '#a2bcbc'),1.4);$pen.DashStyle=[System.Drawing.Drawing2D.DashStyle]::Dash;$script:planGraphics.DrawEllipse($pen,[single]($cx-$rw/2),[single]($cy-$rh/2),[single]$rw,[single]$rh);$pen.Dispose();Txt $cx (Y ($room.y+$room.h-1)) ('돔 '+$room.roof.spring+' → '+$room.roof.crown+'m') 12 '#578181'}elseif($room.roof.kind -eq 'barrel'){Txt (X ($room.x+$room.w/2)) (Y ($room.y+$room.h/2+.5)) '반원 터널 H4m' 11 '#578181'}}
 foreach($d in $p.doors){''',1)
p=p.replace("'회색 블록  가림물 / 설비'","'회색 블록  설비 · 큰 차폐벽 없음'").replace("'청회색 면  피트 · 보행 불가'","'청회색 면  피트 / 청록 점선 돔 지붕'")
p=p.replace("Txt (X ($room.x+$room.w/2)) (Y ($room.y+$room.h/2+.5)) '반원 터널 H4m' 11 '#578181'", "if($room.h-gt$room.w){Txt (X ($room.x+$room.w/2+.7)) (Y ($room.y+$room.h/2)) '반원 터널 H4m' 11 '#578181' middle -90}else{Txt (X ($room.x+$room.w/2)) (Y ($room.y+$room.h/2+.7)) '반원 터널 H4m' 11 '#578181'}")
head="""# 확장 평면 렌더러 V0.01 · 작성자 송예찬. layout.json을 읽기만 한다.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$out=Join-Path $repo 'Docs/도면/잠입_탐색'
$utf8=[System.Text.UTF8Encoding]::new($false)
$plans=(Get-Content (Join-Path $out 'layout.json') -Encoding UTF8 -Raw | ConvertFrom-Json).floors
function GetRoom($p,$id){@($p.rooms | Where-Object id -eq $id)[0]}
"""
(S/'render_plans.ps1').write_text(head+p,encoding='utf-8-sig')
raw=(D/'플레이어_예상이동/make_player_routes.ps1').read_text(encoding='utf-8-sig')
p=raw[raw.index('# 원안의 SVG/PNG'):raw.index('$export=$routes')].replace('*24','*22').replace('V0.02','V0.04')
p=p.replace('원안 도면/Unity 미수정','확장 도면의 경로 복사본 · UI 미구현')
head="""# 확장 예상 경로 렌더러 V0.01 · 작성자 송예찬. player_routes.json을 읽기만 한다.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$base=Join-Path $repo 'Docs/도면/잠입_탐색'
$out=Join-Path $base '플레이어_예상이동'
$utf8=[System.Text.UTF8Encoding]::new($false)
$layout=Get-Content (Join-Path $base 'layout.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$routes=(Get-Content (Join-Path $out 'player_routes.json') -Encoding UTF8 -Raw | ConvertFrom-Json).routes
"""
(S/'render_routes.ps1').write_text(head+p,encoding='utf-8-sig')
# Old topology generators must not silently overwrite the current coordinate system.
for name in ('make_stealth_plans.ps1','플레이어_예상이동/make_player_routes.ps1'):
 p=D/name;t=p.read_text(encoding='utf-8-sig');marker="$ErrorActionPreference='Stop'"
 if 'WideInterior' not in t:t=t.replace(marker,marker+"\nthrow 'V0.02 이력 생성기입니다. 확장 도면은 SourceAssets/B345_WideInterior의 wide_plan.py / render_plans.ps1 / render_routes.ps1을 사용하세요.'",1)
 p.write_text(t,encoding='utf-8-sig')
