# After Seconds 잠입·탐색 평면도 생성기 V0.01
# 작성자 송예찬. 의사코드: 방·공용 코어 정의 → 공유 벽에 출입구 연결 → 감시·도주 경로 배치
# → 평면상 통행 검사 → 같은 좌표에서 SVG/PNG/JSON 생성. Unity 씬이나 원안 SVG는 수정하지 않는다.
param([string]$OutputDirectory = $PSScriptRoot)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
if (-not ('PlanGrid' -as [type])) {
Add-Type @'
using System;using System.Collections.Generic;
public class PlanGrid {
 public int W,H;public double Cell;public bool[] Free;
 public PlanGrid(int w,int h,double c,double[] rooms,double[] blocks,double[] doors){W=w;H=h;Cell=c;Free=new bool[w*h];for(int y=0;y<h;y++)for(int x=0;x<w;x++){double px=(x+.5)*c,py=(y+.5)*c;bool ok=false;for(int k=0;k<rooms.Length;k+=4)if(In(px,py,rooms,k,.42))ok=true;for(int k=0;k<doors.Length;k+=4)if(In(px,py,doors,k,0))ok=true;for(int k=0;k<blocks.Length;k+=4)if(In(px,py,blocks,k,-.3))ok=false;Free[y*w+x]=ok;}}
 static bool In(double x,double y,double[] a,int k,double m){return x>=a[k]+m&&x<=a[k]+a[k+2]-m&&y>=a[k+1]+m&&y<=a[k+1]+a[k+3]-m;}
 public int Index(double x,double y){int ix=(int)(x/Cell),iy=(int)(y/Cell);return ix<0||iy<0||ix>=W||iy>=H?-1:iy*W+ix;}
 public int[] Search(double sx,double sy,double tx,double ty){int start=Index(sx,sy),goal=Index(tx,ty);if(start<0||goal<0||!Free[start]||!Free[goal])return new int[0];var prev=new int[Free.Length];for(int i=0;i<prev.Length;i++)prev[i]=-2;prev[start]=-1;var q=new Queue<int>();q.Enqueue(start);int[] dx={1,0,-1,0},dy={0,1,0,-1};while(q.Count>0){int p=q.Dequeue();if(p==goal)break;int x=p%W,y=p/W;for(int i=0;i<4;i++){int nx=x+dx[i],ny=y+dy[i];if(nx<0||ny<0||nx>=W||ny>=H)continue;int n=ny*W+nx;if(Free[n]&&prev[n]==-2){prev[n]=p;q.Enqueue(n);}}}if(prev[goal]==-2)return new int[0];var path=new List<int>();for(int p=goal;p>=0;p=prev[p])path.Add(p);path.Reverse();return path.ToArray();}
}
'@
}
$out=[System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $out | Out-Null
$utf8=[System.Text.UTF8Encoding]::new($false)
$plans=[System.Collections.Generic.List[object]]::new()
function Room($p,$id,$name,$x,$y,$w,$h,$kind='room') {
 $p.rooms.Add([pscustomobject]@{id=$id;name=$name;x=[double]$x;y=[double]$y;w=[double]$w;h=[double]$h;kind=$kind})
}
function GetRoom($p,$id){$r=@($p.rooms | Where-Object id -eq $id);if($r.Count -ne 1){throw "Room ID: $($p.floor)/$id"};return $r[0]}
function Door($p,$a,$b,$at,$state='open',$width=1.5){
 $ra=GetRoom $p $a;$rb=GetRoom $p $b;$eps=.001
 if([math]::Abs($ra.x+$ra.w-$rb.x)-lt $eps -or [math]::Abs($rb.x+$rb.w-$ra.x)-lt $eps){$axis='V';$x=[math]::Max($ra.x,$rb.x);$y=[double]$at;$lo=[math]::Max($ra.y,$rb.y);$hi=[math]::Min($ra.y+$ra.h,$rb.y+$rb.h)}
 elseif([math]::Abs($ra.y+$ra.h-$rb.y)-lt $eps -or [math]::Abs($rb.y+$rb.h-$ra.y)-lt $eps){$axis='H';$x=[double]$at;$y=[math]::Max($ra.y,$rb.y);$lo=[math]::Max($ra.x,$rb.x);$hi=[math]::Min($ra.x+$ra.w,$rb.x+$rb.w)}
 else{throw "Nonadjacent doorway $($p.floor): $a -> $b"}
 if($at-$width/2-lt $lo+.15 -or $at+$width/2-gt $hi-.15){throw "Door outside shared wall: $a/$b at $at"}
 $p.doors.Add([pscustomobject]@{a=$a;b=$b;x=$x;y=$y;axis=$axis;width=$width;state=$state})
}
function Block($p,$name,$x,$y,$w,$h,$kind='cover'){$p.blocks.Add([pscustomobject]@{name=$name;x=[double]$x;y=[double]$y;w=[double]$w;h=[double]$h;kind=$kind})}
function Mark($p,$id,$kind,$x,$y,$label=''){$p.markers.Add([pscustomobject]@{id=$id;kind=$kind;x=[double]$x;y=[double]$y;label=$label})}
function Camera($p,$id,$room,$x,$y,$angle){$p.cameras.Add([pscustomobject]@{id=$id;room=$room;x=[double]$x;y=[double]$y;angle=[double]$angle;range=5;fov=65})}
function Guard($p,$id,$points){$p.guards.Add([pscustomobject]@{id=$id;points=$points})}
function Base($floor,$name,$theme,$entry,$exit){
 $p=[pscustomobject]@{floor=$floor;name=$name;theme=$theme;version='V0.01';width=48;height=32;entry=$entry;exit=$exit;rooms=[System.Collections.Generic.List[object]]::new();doors=[System.Collections.Generic.List[object]]::new();blocks=[System.Collections.Generic.List[object]]::new();markers=[System.Collections.Generic.List[object]]::new();guards=[System.Collections.Generic.List[object]]::new();cameras=[System.Collections.Generic.List[object]]::new();researcher=$null;swap=$null;notes=@()}
 Room $p N '북측 직원 복도' 0 0 39 4 corridor
 Room $p W '서측 복도' 0 4 3 20 corridor
 Room $p M '중앙 복도' 19 4 3 20 corridor
 Room $p EN '동측 북구간' 36 4 3 10 corridor
 Room $p ES '동측 남구간' 36 14 3 18 corridor
 Room $p S '남측 직원 복도' 0 24 36 3 corridor
 Room $p HVAC '설비실 · 점검 샤프트' 39 0 9 6 service
 Room $p LIFT '화물 리프트 전실' 39 6 9 12 core
 Room $p STA '계단 A' 39 18 4.5 14 core
 Room $p STB '계단 B' 43.5 18 4.5 14 core
 Door $p N W 1.5;Door $p N M 20.5;Door $p N EN 37.5
 Door $p W S 1.5;Door $p M S 20.5;Door $p S ES 25.5
 # 동측 북/남 구간은 벽으로 나뉜다. 실내/다른 복도를 거쳐 돌아가야 한다.
 Door $p N HVAC 2 'locked'
 Door $p EN LIFT 10 $(if($floor -in @('B4','B3','B2','B1','1F')){'open'}else{'locked'})
 Door $p ES STA 25 $(if($floor -in @('B5','B4','B3')){'open'}else{'locked'})
 Door $p LIFT STB 46 $(if($floor -in @('B4','B1','1F')){'open'}else{'locked'})
 if($floor-eq'B3'){(GetRoom $p STA).name='계단 전실';Door $p STA STB 26}
 return $p
}
function Supports($p,$names){for($i=0;$i-lt4;$i++){Room $p ('SUP'+($i+1)) $names[$i] ($i*9) 27 9 5;Door $p S ('SUP'+($i+1)) ($i*9+4.5)}}
function SupportLink($p,$i){Door $p ('SUP'+$i) ('SUP'+($i+1)) 29.5}
function WestBig($p,$name){Room $p A $name 3 4 16 20;Door $p W A 10;Door $p A M 10;Door $p A M 20}
function EastBig($p,$name){Room $p B $name 22 4 14 20;Door $p M B 8;Door $p M B 20;Door $p B EN 8;Door $p B ES 20}
function Researcher($p,$room){$r=GetRoom $p $room;$p.researcher=[pscustomobject]@{id='R1';room=$room;x=$r.x+$r.w/2;y=$r.y+$r.h/2;target=@(4.5,29.5);path=@()}}

$p=Base B5 '격리층' '포드 탈출 이후, 계단 위치를 찾고 감시를 피해 접근' @(17,10) @(41,26)
WestBig $p '피험체 격리실';EastBig $p '냉각조 구역'
Supports $p @('경비 초소','격리 전실','모니터링실','유틸리티실')
SupportLink $p 1;SupportLink $p 2;SupportLink $p 3;Door $p SUP4 ES 29.5
Block $p '냉각조 · 보행 불가' 22 12 14 5 pit
Block $p '유리 포드 · Ø8.43' 6.785 12.785 8.43 8.43 pod
Block $p '관찰 콘솔' 5 6 5 1;Block $p '모니터 콘솔' 19.2 30.5 6.5 .8
Mark $p P tutorial 11 17 '시작 포드';Mark $p E entry 17 10 '포드 탈출 후 검증 시작';Mark $p T exit 41 26 'B4행'
Guard $p G1 @(@(4,25.5),@(33,25.5));Guard $p G2 @(@(25,9),@(33,9));Mark $p G0 sleeping 15.7 10 '시작 경비'
Camera $p C1 ES 37.5 25 -90;Researcher $p SUP3
$p.swap=[pscustomobject]@{from=@(29,20);to=@(29,9);label='교환 지름길 · 선택'}
$p.notes=@('격리실 안 포드·생활 배치를 재사용. 탈출 상호작용은 별도 검증.','초소/모니터링실/유틸리티실을 실제 실내로 연결.','냉각조는 위험한 지름길. 직원 복도로 걸어서 우회 가능.')
$plans.Add($p)

$p=Base B4 '관찰층' '관찰창과 높이 차로 다음 구역을 먼저 읽는 잠입' @(41,26) @(46,24)
Room $p A '관찰 복도' 12 4 7 20;Room $p AN '북측 관찰실' 3 4 9 10;Room $p AS '남측 관찰실' 3 14 9 10
Door $p W AN 9;Door $p AN A 9;Door $p W AS 19;Door $p AS A 19;Door $p A M 9;Door $p A M 20
Room $p B '데이터 분석실' 22 4 14 8;Room $p D '관제 데크' 22 12 14 12
Door $p M B 8;Door $p B EN 8;Door $p M D 20;Door $p D ES 20;Door $p B D 29
Supports $p @('관찰 지원실','장비 준비실','기록실','유틸리티실');SupportLink $p 1;SupportLink $p 3;Door $p SUP4 ES 29.5
Block $p '관측 데크 +2.5m' 27 15 7 5 platform
Block $p '분석 콘솔' 24 5.5 4 1;Block $p '장비 랙' 15 12 2 3
Mark $p E entry 41 26 'B5에서 도착';Mark $p T exit 46 24 'B3행'
Guard $p G1 @(@(5,2),@(33,2));Guard $p G2 @(@(20.5,6),@(20.5,21));Guard $p G3 @(@(4,25.5),@(33,25.5))
Camera $p C1 A 15 6 90;Camera $p C2 EN 37.5 10 -90;Researcher $p B
$p.notes=@('관찰실-복도 사이 일부 벽을 관찰창으로 검토. 양면 시야 판정 필요.','관제 데크에는 걸어서 접근하는 계단/경사를 추후 배치.','도착 계단A와 출발 계단B는 분리된 계단실. 실내를 거쳐 이동.')
$plans.Add($p)

$p=Base B3 '시료층' '랙과 여러 출입문 사이로 이동, 도주하는 연구원의 전파 경로 판단' @(46,24) @(43.5,11)
WestBig $p '시료 저장고';Room $p B '오염 구역' 22 4 14 10;Room $p D '청정 구역' 22 14 14 10
Door $p M B 8;Door $p B EN 8;Door $p M D 20;Door $p D ES 20;Door $p B D 25;Door $p B D 33
Supports $p @('냉동 보관실','시료 전처리실','폐기물 보관실','직원 환복실');SupportLink $p 1;SupportLink $p 3;Door $p SUP4 ES 29.5
foreach($x in @(5,10,15)){Block $p '시료 랙' $x 7 1.5 5;Block $p '시료 랙' $x 16 1.5 5}
Block $p '세척 피트' 27 7 3 3 pit;Block $p '검사대' 27 19 5 1
Mark $p E entry 46 24 'B4에서 도착';Mark $p T exit 43.5 11 'B2행 리프트'
Guard $p G1 @(@(5,2),@(33,2));Guard $p G2 @(@(4,25.5),@(33,25.5));Guard $p G3 @(@(20.5,6),@(20.5,21))
Camera $p C1 B 34 6 160;Camera $p C2 EN 37.5 10 90;Researcher $p SUP2
$p.notes=@('시료 랙은 보행로를 여러 갈래로 나누는 가림물.','두 제염 출입구는 통과 시점과 접근 방향을 선택.','셔터·압력판 원안은 선택 장치 후보이며 필수 단일 풀이로 고정하지 않음.')
$plans.Add($p)

$p=Base B2 '기계층' '큰 기계와 설비 복도, 위험한 직선 경로와 먼 우회 비교' @(43.5,11) @(34.5,22.5)
WestBig $p '원심분리기 홀';Room $p B '전기 제어실' 22 4 14 10;Room $p D '중앙 관제실' 22 14 14 10
Door $p M B 8;Door $p B EN 8;Door $p M D 20;Door $p D ES 20;Door $p B D 29
Supports $p @('설비 작업실','펌프실','정비 창고','기계 설비실');SupportLink $p 1;SupportLink $p 2;Door $p SUP4 ES 29.5
Block $p '원심분리기' 5 7 5 5;Block $p '원심분리기' 12 16 5 5
Block $p '수직갱' 4 14 8 4 pit;Block $p '관제 섬 +2.5m' 27 17 6 4 platform
Mark $p E entry 43.5 11 'B3에서 도착';Mark $p T exit 34.5 22.5 'B1행 점검 사다리'
Guard $p G1 @(@(5,2),@(33,2));Guard $p G2 @(@(4,25.5),@(33,25.5));Guard $p G3 @(@(20.5,6),@(20.5,21))
Camera $p C1 N 34 2 180;Camera $p C2 D 34 16 150;Researcher $p SUP2
$p.notes=@('기존 전층 폭 구덩이를 구역 내부의 위험 구간으로 재구성.','전기실/설비 복도를 통행 가능한 경로로 사용.','관제실 사다리를 B1 남측 관찰 부스와 같은 위치에 둠. 등반·층 전환은 별도 구현.')
$plans.Add($p)

$p=Base B1 '실험층' '중앙 챔버 주변의 관찰·연구 공간을 돌며 감시 조합에 대응' @(34.5,22.5) @(46,24)
Room $p A '사전 준비 실험실' 3 4 16 10;Room $p D '기록 보관실' 3 14 16 10
Door $p W A 9;Door $p A M 9;Door $p W D 19;Door $p D M 19;Door $p A D 11
Room $p BN '북측 관찰 부스' 22 4 14 4;Room $p B '피험 챔버' 22 8 14 12;Room $p BS '남측 관찰 부스' 22 20 14 4
Door $p N BN 29;Door $p M B 14;Door $p B ES 16;Door $p S BS 29;Door $p BN B 25;Door $p B BS 33
Supports $p @('직원 대기실','시료 준비실','의료 준비실','유틸리티실');SupportLink $p 1;SupportLink $p 3;Door $p SUP4 ES 29.5
Block $p '준비 실험대' 5 6 4 1.5;Block $p '준비 실험대' 13 6 4 1.5
Block $p '기록 랙' 5 17 2 4;Block $p '기록 랙' 14 17 2 4
Block $p '챔버 하부 피트' 27 11 4 6 pit
Mark $p E entry 34.5 22.5 'B2에서 도착';Mark $p T exit 46 24 '1F행 비상계단'
Guard $p G1 @(@(5,2),@(33,2));Guard $p G2 @(@(4,25.5),@(33,25.5));Guard $p G3 @(@(20.5,6),@(20.5,21))
Camera $p C1 B 34 10 160;Camera $p C2 N 34 2 180;Researcher $p A
$p.notes=@('챔버 구덩이 주변에 보행 경로를 남김. 연쇄 교환은 지름길 후보.','관찰 부스와 준비실에서 다음 구역을 관찰. 연구원의 도주로는 직원 구역으로.','북/남 부스의 유리·문 판정과 계단B의 1F 도착 위치를 검증.')
$plans.Add($p)

$p=Base '1F' '물류 위장층' '창고와 직원 공간을 지나 외부 검문소에 접근, 소장은 엔딩 전용' @(46,24) @(30,30)
WestBig $p '물류 창고';Room $p B '하역 준비 구역' 22 4 14 13;Room $p D '출입 검문소' 22 17 14 7
Door $p M B 8;Door $p B EN 8;Door $p M D 20;Door $p D ES 20;Door $p B D 29
Room $p SUP1 '물류 사무실' 0 27 12 5;Room $p SUP2 '직원 탈의실' 12 27 12 5;Room $p SUP3 '외부 출구 전실' 24 27 12 5
Door $p S SUP1 6;Door $p S SUP2 18;Door $p S SUP3 30;Door $p SUP1 SUP2 29.5;Door $p SUP2 SUP3 29.5;Door $p SUP3 ES 29.5
Room $p OUT '외부 착지 구역 · 엔딩' 24 32 12 6 exterior;Door $p SUP3 OUT 30
foreach($x in @(5,10,15)){Block $p '적재물' $x 7 2 4;Block $p '적재물' $x 16 2 4};Block $p '검문 데스크' 26 19 5 1.5
Mark $p E entry 46 24 'B1에서 도착';Mark $p T exit 30 30 '외부 출구 전실';Mark $p Z director 30 37 '연구소장 · 엔딩'
Guard $p G1 @(@(5,2),@(33,2));Guard $p G2 @(@(4,25.5),@(33,25.5));Guard $p G3 @(@(20.5,6),@(20.5,21))
Camera $p C1 D 34 18 150;Camera $p C2 EN 37.5 10 90;Researcher $p B
Block $p '마지막 출구 경계 · 피트 가안' 24 32 12 4 pit
$p.swap=[pscustomobject]@{from=@(30,30);to=@(30,37);label='마지막 교환 · 엔딩'}
$p.notes=@('계단B 도착 후 창고/직원 구역을 통해 검문소에 접근.','외부 전실까지 보행 접근. 마지막 피트/교환 경계는 엔딩 가안으로 별도 검증.','연구소장 전투·추격 AI 없음. 엔딩 위치/안전한 착지와 탄약 회복은 검증 대상.')
$plans.Add($p)

# 정합성 검사와 평면상 보행 경로. 이는 실제 Unity 충돌·시야·층고 검증이 아니다.
foreach($planRefuge in $plans){Mark $planRefuge F refuge $planRefuge.researcher.target[0] $planRefuge.researcher.target[1] '피난·호출 지점';Block $planRefuge '복도 차폐벽' 12.5 .2 .3 2.2 baffle;Block $planRefuge '복도 차폐벽' 25 1.7 .3 2.1 baffle;Block $planRefuge '복도 차폐벽' 11 24 .3 1.2 baffle;Block $planRefuge '복도 차폐벽' 26 25.7 .3 1.3 baffle}
$validation=[System.Collections.Generic.List[object]]::new()
function FlatRects($items){$a=[System.Collections.Generic.List[double]]::new();foreach($r in $items){$a.AddRange([double[]]@($r.x,$r.y,$r.w,$r.h))};return ,$a.ToArray()}
function SimplifyPath($grid,$ids){$pts=[System.Collections.Generic.List[object]]::new();for($i=0;$i-lt$ids.Length;$i++){if($i-gt0-and$i-lt$ids.Length-1-and($ids[$i]-$ids[$i-1])-eq($ids[$i+1]-$ids[$i])){continue};$px=(($ids[$i]%$grid.W)+.5)*$grid.Cell;$py=([math]::Floor($ids[$i]/$grid.W)+.5)*$grid.Cell;$pts.Add(@($px,$py))};return ,$pts.ToArray()}
foreach($p in $plans){
 $area=0;foreach($r in $p.rooms){if($r.kind-ne'exterior'){$area+=$r.w*$r.h};foreach($b in $p.rooms){if($r.id-ge$b.id){continue};$overlap=[math]::Min($r.x+$r.w,$b.x+$b.w)-[math]::Max($r.x,$b.x);$oy=[math]::Min($r.y+$r.h,$b.y+$b.h)-[math]::Max($r.y,$b.y);if($overlap-gt.001-and$oy-gt.001){throw "Room overlap $($p.floor): $($r.id)/$($b.id)"}}};if($area-ne1536){throw "Footprint area mismatch $($p.floor): $area"}
 $dr=@($p.doors | Where-Object state -eq open | ForEach-Object {if($_.axis-eq'V'){[pscustomobject]@{x=$_.x-.7;y=$_.y-$_.width/2+.3;w=1.4;h=$_.width-.6}}else{[pscustomobject]@{x=$_.x-$_.width/2+.3;y=$_.y-.7;w=$_.width-.6;h=1.4}}})
 $blocks=@($p.blocks)
 $grid=[PlanGrid]::new(192,152,.25,(FlatRects $p.rooms),(FlatRects $blocks),(FlatRects $dr))
 $ids=$grid.Search($p.entry[0],$p.entry[1],$p.exit[0],$p.exit[1]);if($ids.Length-eq0){throw "Exit unreachable: $($p.floor)"}
 $p | Add-Member -NotePropertyName walkingExample -NotePropertyValue (SimplifyPath $grid $ids)
 $ri=$p.researcher;$rpath=$grid.Search($ri.x,$ri.y,$ri.target[0],$ri.target[1]);if($rpath.Length-eq0){throw "Researcher refuge unreachable: $($p.floor)"};$ri.path=SimplifyPath $grid $rpath
 foreach($g in $p.guards){$original=@($g.points);$route=[System.Collections.Generic.List[object]]::new();for($i=0;$i-lt$original.Count-1;$i++){$gi=$grid.Search($original[$i][0],$original[$i][1],$original[$i+1][0],$original[$i+1][1]);if($gi.Length-eq0){throw "Guard route unreachable $($p.floor)/$($g.id)"};foreach($point in (SimplifyPath $grid $gi)){$route.Add($point)}};$g.points=$route.ToArray()}
 $visited=[System.Collections.Generic.HashSet[string]]::new();$queue=[System.Collections.Generic.Queue[string]]::new();$entryRoom=@($p.rooms | Where-Object {$p.entry[0]-gt$_.x-and$p.entry[0]-lt$_.x+$_.w-and$p.entry[1]-gt$_.y-and$p.entry[1]-lt$_.y+$_.h})[0].id;$visited.Add($entryRoom)|Out-Null;$queue.Enqueue($entryRoom)
 while($queue.Count-gt0){$id=$queue.Dequeue();foreach($d in $p.doors | Where-Object state -eq open){$other=if($d.a-eq$id){$d.b}elseif($d.b-eq$id){$d.a}else{$null};if($other-and$visited.Add($other)){$queue.Enqueue($other)}}}
 $edges=@($p.doors | Where-Object {$_.state-eq'open'-and$visited.Contains($_.a)-and$visited.Contains($_.b)}).Count;$loops=$edges-$visited.Count+1;if($loops-lt2){throw "Not enough loops: $($p.floor)"}
 $validation.Add([pscustomobject]@{floor=$p.floor;footprintArea=$area;rooms=$p.rooms.Count;doors=$p.doors.Count;reachableRooms=$visited.Count;independentLoops=$loops;walkingCells=$ids.Length;exitReachable=$true;researcherRefugeReachable=$true;gridCell=.25;bodyDiameter=.6;limits='2D 정적 통행 검사. Unity 물리·AI·시야·경보·계단 실제 높이는 미검증.'})
}

# 같은 도형 명령으로 SVG와 Windows GDI+ 미리보기를 동시에 만든다.
$script:PlanScale=24;$script:OX=70;$script:OY=112;$script:Ink='#203047';$script:svg=$null;$script:planGraphics=$null
function Col($c){[System.Drawing.ColorTranslator]::FromHtml($c)}
function Brush($c){[System.Drawing.SolidBrush]::new((Col $c))}
function Escape($s){[System.Security.SecurityElement]::Escape([string]$s)}
function Rect($x,$y,$w,$h,$fill,$stroke='none',$sw=1){$script:svg.AppendLine("<rect x='$x' y='$y' width='$w' height='$h' fill='$fill' stroke='$stroke' stroke-width='$sw'/>")|Out-Null;if($fill-ne'none'){$br=Brush $fill;$script:planGraphics.FillRectangle($br,[single]$x,[single]$y,[single]$w,[single]$h);$br.Dispose()};if($stroke-ne'none'){$pen=[System.Drawing.Pen]::new((Col $stroke),$sw);$script:planGraphics.DrawRectangle($pen,[single]$x,[single]$y,[single]$w,[single]$h);$pen.Dispose()}}
function Line($x1,$y1,$x2,$y2,$color,$width=2,$dash=$false){$da=if($dash){" stroke-dasharray='8 5'"}else{''};$script:svg.AppendLine("<line x1='$x1' y1='$y1' x2='$x2' y2='$y2' stroke='$color' stroke-width='$width'$da/>")|Out-Null;$pen=[System.Drawing.Pen]::new((Col $color),$width);if($dash){$pen.DashStyle=[System.Drawing.Drawing2D.DashStyle]::Dash};$script:planGraphics.DrawLine($pen,[single]$x1,[single]$y1,[single]$x2,[single]$y2);$pen.Dispose()}
function Txt($x,$y,$value,$size=17,$color='#203047',$anchor='middle',$angle=0){$str=Escape $value;$tr=if($angle){" transform='rotate($angle $x $y)'"}else{''};$script:svg.AppendLine("<text x='$x' y='$y' font-size='$size' fill='$color' text-anchor='$anchor'$tr>$str</text>")|Out-Null;$font=[System.Drawing.Font]::new('Malgun Gothic',[single]$size,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel);$br=Brush $color;$format=[System.Drawing.StringFormat]::new();$format.Alignment=if($anchor-eq'middle'){[System.Drawing.StringAlignment]::Center}else{[System.Drawing.StringAlignment]::Near};$state=$script:planGraphics.Save();$script:planGraphics.TranslateTransform([single]$x,[single]$y);if($angle){$script:planGraphics.RotateTransform($angle)};$script:planGraphics.DrawString([string]$value,$font,$br,[single]0,[single](-$size*1.05),$format);$script:planGraphics.Restore($state);$format.Dispose();$br.Dispose();$font.Dispose()}
function Circle($x,$y,$radius,$fill,$stroke='#203047',$sw=2){$script:svg.AppendLine("<circle cx='$x' cy='$y' r='$radius' fill='$fill' stroke='$stroke' stroke-width='$sw'/>")|Out-Null;if($fill-ne'none'){$br=Brush $fill;$script:planGraphics.FillEllipse($br,[single]($x-$radius),[single]($y-$radius),[single](2*$radius),[single](2*$radius));$br.Dispose()};$pen=[System.Drawing.Pen]::new((Col $stroke),$sw);$script:planGraphics.DrawEllipse($pen,[single]($x-$radius),[single]($y-$radius),[single](2*$radius),[single](2*$radius));$pen.Dispose()}
function X($n){return $script:OX+$n*$script:PlanScale};function Y($n){return $script:OY+$n*$script:PlanScale}
function Route($points,$color,$width=2,$dash=$true){for($i=0;$i-lt$points.Count-1;$i++){Line (X $points[$i][0]) (Y $points[$i][1]) (X $points[$i+1][0]) (Y $points[$i+1][1]) $color $width $dash}}
function Node($id,$x,$y,$color){Circle (X $x) (Y $y) 13 '#ffffff' $color 2;Txt (X $x) ((Y $y)+5) $id 14 $color}
foreach($p in $plans){
 $script:svg=[System.Text.StringBuilder]::new();$script:svg.AppendLine("<svg xmlns='http://www.w3.org/2000/svg' width='1660' height='1190' viewBox='0 0 1660 1190' font-family='Malgun Gothic, sans-serif'><title>After Seconds $($p.floor) $($p.name) 잠입 평면도 V0.01</title><desc>48×32m 가안. 실내와 직원 통로, 실제 출입구, 순찰과 연구원 도주로, 감시 위치. Unity 미적용.</desc><rect width='1660' height='1190' fill='white'/>")|Out-Null
 $bitmap=[System.Drawing.Bitmap]::new(1660,1190);$script:planGraphics=[System.Drawing.Graphics]::FromImage($bitmap);$script:planGraphics.Clear([System.Drawing.Color]::White);$script:planGraphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias;$script:planGraphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
 Txt 70 43 ("AFTER SECONDS / "+$p.floor+' '+$p.name+' 잠입·탐색 평면도 V0.01') 27 $script:Ink start
 Txt 70 74 $p.theme 18 '#475569' start;Txt 1510 43 'N ↑' 22 $script:Ink
 foreach($r in $p.rooms){$fill=switch($r.kind){corridor{'#edf2f7'}service{'#e5e7eb'}core{'#e8eef7'}exterior{'#eef5ed'}default{'#ffffff'}};Rect (X $r.x) (Y $r.y) ($r.w*24) ($r.h*24) $fill $script:Ink 6}
 foreach($d in $p.doors){$px=X $d.x;$py=Y $d.y;$dw=$d.width*24;if($d.axis-eq'V'){Rect ($px-5) ($py-$dw/2) 10 $dw '#ffffff';Line $px ($py-$dw/2) ($px+$dw*.6) ($py+$dw*.1) $(if($d.state-eq'locked'){'#9a3412'}else{'#334155'}) 2}else{Rect ($px-$dw/2) ($py-5) $dw 10 '#ffffff';Line ($px-$dw/2) $py ($px+$dw*.1) ($py-$dw*.6) $(if($d.state-eq'locked'){'#9a3412'}else{'#334155'}) 2};if($d.state-eq'locked'){Line ($px-6) ($py-6) ($px+6) ($py+6) '#9a3412' 2;Line ($px-6) ($py+6) ($px+6) ($py-6) '#9a3412' 2}}
 foreach($c in $p.cameras){$r=GetRoom $p $c.room;$px=X $c.x;$py=Y $c.y;$rad=$c.range*24;$a1=($c.angle-$c.fov/2)*[math]::PI/180;$a2=($c.angle+$c.fov/2)*[math]::PI/180;$x1=$px+$rad*[math]::Cos($a1);$y1=$py+$rad*[math]::Sin($a1);$x2=$px+$rad*[math]::Cos($a2);$y2=$py+$rad*[math]::Sin($a2);$clip='clip'+$c.id;$script:svg.AppendLine("<defs><clipPath id='$clip'><rect x='$(X ($r.x+.15))' y='$(Y ($r.y+.15))' width='$(($r.w-.3)*24)' height='$(($r.h-.3)*24)'/></clipPath></defs><path d='M$px,$py L$x1,$y1 A$rad,$rad 0 0,1 $x2,$y2 Z' fill='#fbe1df' clip-path='url(#$clip)'/>")|Out-Null;$state=$script:planGraphics.Save();$script:planGraphics.SetClip([System.Drawing.RectangleF]::new((X ($r.x+.15)),(Y ($r.y+.15)),(($r.w-.3)*24),(($r.h-.3)*24)));$br=Brush '#fbe1df';$script:planGraphics.FillPie($br,[single]($px-$rad),[single]($py-$rad),[single](2*$rad),[single](2*$rad),[single]($c.angle-$c.fov/2),[single]$c.fov);$br.Dispose();$script:planGraphics.Restore($state)}
 foreach($b in $p.blocks){$fill=switch($b.kind){pit{'#cbd5e1'}platform{'#e5e0d7'}pod{'#dceff1'}default{'#d6dde5'}};if($b.kind-eq'pod'){Circle (X ($b.x+$b.w/2)) (Y ($b.y+$b.h/2)) ($b.w*12) 'none' '#24848e' 3;Txt (X ($b.x+$b.w/2)) (Y ($b.y+$b.h/2-1)) '유리 포드 Ø8.43m' 16 '#24616a'}else{Rect (X $b.x) (Y $b.y) ($b.w*24) ($b.h*24) $fill '#64748b' 1;if($b.kind-ne'baffle'){Txt (X ($b.x+$b.w/2)) (Y ($b.y+$b.h/2+.15)) $b.name 13 '#334155'}}}
 foreach($r in $p.rooms){$cx=$r.x+$r.w/2;$cy=$r.y+$r.h/2;if($r.kind-eq'corridor'){if($r.h-gt$r.w){Txt (X ($cx-.7)) (Y $cy) $r.name 14 '#526273' middle -90}else{Txt (X $cx) (Y ($cy-.65)) $r.name 15 '#526273'}}elseif($r.kind-eq'exterior'){Txt (X $cx) (Y ($r.y+$r.h+.7)) $r.name 16 '#475569'}elseif($r.kind-eq'core'-and$r.w-lt5){Txt (X $cx) (Y ($r.y+2)) $r.name 17;for($s=0;$s-lt8;$s++){Line (X ($r.x+.6)) (Y ($r.y+5+$s*.6)) (X ($r.x+$r.w-.6)) (Y ($r.y+5+$s*.6)) '#75859a' 1}}else{Txt (X $cx) (Y ($r.y+1.2)) $r.name 17;Txt (X $cx) (Y ($r.y+2)) ($r.w.ToString('0.#')+' × '+$r.h.ToString('0.#')+'m · 가안') 13 '#64748b'}}
 Route $p.researcher.path '#b7791f' 2 $true
 foreach($g in $p.guards){Route $g.points '#b0403c' 2 $true;Node $g.id $g.points[0][0] $g.points[0][1] '#b0403c'}
 if($p.swap){Route @($p.swap.from,$p.swap.to) '#7352a3' 3 $true;Txt (X ($p.swap.from[0]+2)) (Y ($p.swap.from[1]+1)) $p.swap.label 14 '#7352a3'}
 foreach($c in $p.cameras){Node $c.id $c.x $c.y '#9e3530'};Node R1 $p.researcher.x $p.researcher.y '#a66b17'
 foreach($m in $p.markers){$color=switch($m.kind){entry{'#166a9e'}exit{'#247451'}tutorial{'#166a9e'}director{'#7352a3'}refuge{'#a66b17'}default{'#b0403c'}};Node $m.id $m.x $m.y $color}
 # 길이 눈금과 범례. 실제 조감 축척이 아닌 동일 좌표계의 설계 가안.
 for($i=0;$i-le48;$i+=4){Line (X $i) 96 (X $i) 104 '#64748b' 1;Txt (X $i) 94 $i 12 '#64748b'};for($i=0;$i-le32;$i+=4){Txt 48 ((Y $i)+4) $i 12 '#64748b'}
 $lx=1280;Txt $lx 140 '설계 기준 · 가안' 22 $script:Ink start
 $entryLabel=($p.markers | Where-Object id -eq E).label;$exitLabel=($p.markers | Where-Object id -eq T).label
 $legend=@(('E  '+$entryLabel),('T  '+$exitLabel),'G  경비 · 점선 왕복 순찰','R  연구원 · 황색 도주 경로','F  연구원 피난·호출 지점','C  CCTV · 붉은 감시 구간','Z  연구소장 · 엔딩 전용','×  잠긴 점검문 · 뒤 공간 있음','회색 블록  가림물 / 설비','청회색 면  피트 · 보행 불가')
 for($i=0;$i-lt$legend.Count;$i++){Txt $lx (181+$i*32) $legend[$i] 16 '#334155' start}
 Txt $lx 510 '공용 수직 코어' 21 $script:Ink start
 $core=@('계단A: B5 ↔ B4','계단B: B4 ↔ B3 / B1 ↔ 1F','화물 리프트: B3 ↔ B2','점검 사다리: B2 관제실 ↔ B1','남측 관찰 부스 (동일 평면 위치)','계단B 두 구간은 중간에서 단절.','전층 직통 계단으로 취급하지 않음.')
 for($i=0;$i-lt$core.Count;$i++){Txt $lx (548+$i*28) $core[$i] 15 '#475569' start}
 Txt $lx 760 '검수 범위' 21 $script:Ink start
 foreach($line in @('방·문 인접 / 보행 연결 검사','연구원 피난처까지 연결 검사','감시 부채꼴은 현재 방 내부 가안','실제 시야·소리·추격은 미검증')){Txt $lx ($script:legendY=if($script:legendY){$script:legendY+28}else{800}) $line 15 '#475569' start};$script:legendY=$null
 $ny=if($p.floor-eq'1F'){1070}else{940};foreach($note in $p.notes){Txt 70 $ny ('• '+$note) 17 '#334155' start;$ny+=31}
 Txt 70 1160 '2026-11-05 · 작성자 송예찬 · 외곽 48×32m / 출입구 폭 1.5m / 모든 신규 치수·적 배치는 💡 가안 · Unity 미적용' 15 '#64748b' start
 $script:svg.AppendLine('</svg>')|Out-Null;$stem=$p.floor+'_'+$p.name.Replace(' ','_')+'_잠입';[System.IO.File]::WriteAllText((Join-Path $out ($stem+'.svg')),$script:svg.ToString(),$utf8);$bitmap.Save((Join-Path $out ($stem+'.png')),[System.Drawing.Imaging.ImageFormat]::Png);$script:planGraphics.Dispose();$bitmap.Dispose()
}
$document=[pscustomobject]@{title='After Seconds 잠입·탐색 층별 평면 V0.01';author='송예찬';date='2026-11-05';status='제작 가안 · Unity 미적용';coordinates='북서 모서리 (u=0,v=0), u 동쪽+, v 남쪽+, m. Unity 새씬 배치는 층 부모에서 변환. 기존 포드의 자식 Transform은 보존.';enemyRoles=@{guard='발견한 플레이어 추격';cctv='감지 후 담당 경비 호출';researcher='도망가며 주변에 알림';director='마지막 엔딩 역할'};pending=@('A/B 손 힘 타이밍','연구원/CCTV의 교환·제압 판정','경보 범위·통신 지속·수색 시간','층별 높이와 계단 단면','탄약 보충·체크포인트','포드 탈출 상호작용과 엔딩 경계');floors=$plans.ToArray()}
[System.IO.File]::WriteAllText((Join-Path $out 'layout.json'),($document|ConvertTo-Json -Depth 22),$utf8)
foreach($v in $validation){$v.limits='2D 정적 통행 검사. Unity 물리·AI·시야·경보·계단 실제 높이는 미검증.'}
[System.IO.File]::WriteAllText((Join-Path $out 'validation.json'),($validation.ToArray()|ConvertTo-Json -Depth 8),$utf8)
$sheet=[System.Drawing.Bitmap]::new(2490,1190);$gg=[System.Drawing.Graphics]::FromImage($sheet);$gg.Clear([System.Drawing.Color]::White);for($i=0;$i-lt$plans.Count;$i++){$p=$plans[$i];$img=[System.Drawing.Image]::FromFile((Join-Path $out ($p.floor+'_'+$p.name.Replace(' ','_')+'_잠입.png')));$gg.DrawImage($img,($i%3)*830,([math]::Floor($i/3))*595,830,595);$img.Dispose()};$sheet.Save((Join-Path $out '전체층_잠입.png'),[System.Drawing.Imaging.ImageFormat]::Png);$gg.Dispose();$sheet.Dispose()
$overview=[System.Text.StringBuilder]::new();$overview.AppendLine("<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='2490' height='1190' viewBox='0 0 2490 1190'><title>After Seconds 전체층 잠입 평면도 V0.01</title>")|Out-Null
for($i=0;$i-lt$plans.Count;$i++){$p=$plans[$i];$file=$p.floor+'_'+$p.name.Replace(' ','_')+'_잠입.svg';$raw=[System.IO.File]::ReadAllText((Join-Path $out $file));$inner=$raw.Substring($raw.IndexOf('>')+1);$inner=$inner.Substring(0,$inner.LastIndexOf('</svg>'));$inner=$inner.Replace("id='clip","id='"+$p.floor+"-clip").Replace('url(#clip','url(#'+$p.floor+'-clip');$overview.AppendLine("<svg x='$(($i%3)*830)' y='$(([math]::Floor($i/3))*595)' width='830' height='595' viewBox='0 0 1660 1190'>$inner</svg>")|Out-Null};$overview.AppendLine('</svg>')|Out-Null;[System.IO.File]::WriteAllText((Join-Path $out '전체층_잠입.svg'),$overview.ToString(),$utf8)
$transitions=[System.Collections.Generic.List[object]]::new()
$carriers=@('계단A','계단B 하부 구간','화물 리프트','점검 사다리','계단B 상부 구간')
for($i=0;$i-lt5;$i++){$a=$plans[$i];$b=$plans[$i+1];if($a.exit[0]-ne$b.entry[0]-or$a.exit[1]-ne$b.entry[1]){throw "Vertical coordinate mismatch: $($a.floor)/$($b.floor)"};$transitions.Add([pscustomobject]@{from=$a.floor;to=$b.floor;carrier=$carriers[$i];position=@($a.exit);matched=$true;sectionStatus='평면 위치 일치 · 실제 층고/단면 미검증'})}
[System.IO.File]::WriteAllText((Join-Path $out 'transitions.json'),($transitions.ToArray()|ConvertTo-Json -Depth 8),$utf8)
$validation.ToArray() | Format-Table floor,rooms,doors,independentLoops,exitReachable,researcherRefugeReachable -AutoSize
