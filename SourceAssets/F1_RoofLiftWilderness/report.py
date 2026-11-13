import json,pathlib,html
root=pathlib.Path(__file__).resolve().parents[2];out=root/'Docs/Review/2026-11-13_1F_RoofLiftWilderness'
def read(n):return json.loads((out/n).read_text(encoding='utf-8-sig'))
check=read('final_check.json');pres=read('preservation.json');walk=read('walk.json');floor=read('walk_floor.json');plays=[read(p.name) for p in sorted(out.glob('play_*.json'))]
report=f'''# 1F 천장·승강기·계단 연결·황야 검수 V0.01

작성자: 송예찬 · 2026-11-13 · Unity 6000.4.0f1

사용자가 요청한 네 가지 외형을 `Level_1F_Factory`에 저장했다. [전후 화면 비교](review.html)와 [가동 부품 연결 안내](../../../SourceAssets/F1_RoofLiftWilderness/README.md)를 함께 본다. 로컬 저장 상태이며 이번 변경은 커밋·push하지 않았다.

## 반영한 내용

- 천장 11곳(C01–C04, T01–T07)은 사각 타일 결손을 불규칙한 파손 면으로 바꾸고 철판 꺾임·철근을 넣었다. 기존 골조는 유지했다. VA/VB 연속 천장 보수도 유지했다.
- 승강기는 고정 승강로 안에 승강칸이 놓이도록 방향을 고쳤다. 승강칸·문·균형추·권상 도르래·로프를 분리하고 레일·모터·브레이크·피트 완충기와 1F/B1 승강장 문을 배치했다. 권상부 간격도 보수해 승강칸 상부와 도르래 사이 약 0.525m를 확보했다.
- `F1_VB_ArrivalFireDoor_01`에 실제 바닥 개구부, 도착참, 18m 계단, 난간을 연결했다. 첫 통행 검사에서 발견한 연장 난간과 열린 문 간섭을 없애고 왕복을 재검수했다.
- 서쪽 출구에서 마른 길과 낮은 구릉으로 이어지는 황야를 만들었다. 원경까지 지형을 연장하고, 강한 토양 반짝임을 건조 표면으로 고쳤다. `EndingWalkStart`, `EndingWalkMid`, `FreedomVista` 위치를 준비했다.

## 검수 결과

| 항목 | 결과 |
|---|---|
| 기존 1F 통행 | {floor['tested']}/{floor['tested']} 통과, 경로 탐색 실패 0 |
| 새 접속부·외부 길 | {walk['tested']}/{walk['tested']} 통과: VB 도착참 왕복, 18m 계단 왕복, 승강기 출입, 약 585m 황야 길 왕복 |
| 실제 Play | {len(plays)}개 지점, 실제 키보드 W 입력·프레임 진행·화면 확인, 검사 중 새 게임 경고/오류 0 |
| 누락 참조 | 스크립트/메시/재질 0 |
| 지형 접합 | {check['seamSamples']}표본, 최대 높이 차 {check['maxSeamError']*1000:.2f}mm(지형 높이 양자화) |
| 움직이는 부품 | 잘못 지정된 정적 배칭/가림 대상 0 |
| 반사·가림 | 반사 8개 갱신, 공장 가림 데이터 {check['occlusionBytes']:,}bytes 재생성 |
| 보호 파일 | 다른 층·게임 코드·Player/Animator·설정 등 추적 파일 {pres['protectedTrackedFiles']:,}개 변경 0 |
| 메타데이터 | 변경 모델 GUID 유지, 가림 데이터 .meta 보존, 신규 에셋 .meta 누락 0 |

실제 Play 기록은 `play_*.json/png`, 통행은 `walk.json`과 `walk_floor.json`, 접합/참조는 `final_check.json`, 보호 범위는 `preservation.json`에 있다. Play의 프레임 시간은 이 컴퓨터의 Editor 관찰값이며 배포 빌드 성능 보증이 아니다.

Unity AI MCP 연결의 Windows 실행 파일 서명 수집 경고 4건이 별도로 있었다. 게임/모델 오류와 구분했으며 Play 검사에서 새 경고는 없었다. 콘솔 기록은 `console.json`에 보관했다.

## 후속 구현 범위

승강기 운행·문 연동·엔딩 연출 스크립트는 사용자가 작성할 수 있도록 비워 뒀다. 1F/B1 계단의 additive 씬 통합과 중복 표시 제어는 아직 구현하지 않았다. 새 승강칸은 1F 정지 상태, 1F 문은 열림, B1 문은 닫힘이다. 기계 구조의 중간/하단 위치는 치수와 로프 길이 관계를 검토했으며 실제 승강 운행 테스트를 한 것은 아니다.

현재 저장된 씬이 최종본이다. 이전 전체 제작기와 이 작업의 첫 Apply/Import를 다시 실행하지 않는다. 사용자 화면 검수 후 지적 부분을 국소 보수한다.

변경 이력: V0.01 (2026-11-13) 네 가지 외형 요청 반영과 검수 기록. 송예찬.
'''
(out/'Review.md').write_text(report,encoding='utf-8')
parts=['''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>After Seconds · 1F 구조와 황야</title><style>body{margin:0;background:#171a19;color:#eae4d8;font:16px/1.65 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:32px}h1{font-size:32px}h2{margin-top:48px}p{max-width:900px;color:#c2c3b8}.pair,.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;background:#252a27;border-radius:9px;overflow:hidden}img{display:block;width:100%;height:auto}figcaption{padding:12px}a{color:#edce8c}.tag{color:#dfbe7b}@media(max-width:760px){.pair,.grid{grid-template-columns:1fr}main{padding:16px}}</style><main><div class="tag">2026.11.13 · 송예찬 · V0.01</div><h1>공장을 나와 황야로</h1><p>부서진 천장, 고정 승강로와 분리한 가동 부품, 계단 B 접속부, 엔딩을 위한 황야를 저장했습니다. 아래 전후 사진은 같은 위치에서 촬영했습니다. 조명·하늘 변경도 함께 보입니다.</p><p><a href="Review.md">검수 기록</a> · <a href="../../../SourceAssets/F1_RoofLiftWilderness/README.md">가동 부품 연결 안내</a></p>''']
for title,key in [('천장 — 찢어진 철판과 남은 골조','C01_roof'),('천장 — 콘크리트 파손과 철근','C03'),('통로 — 꺾인 철판 가장자리','T07'),('계단 B — 바닥 개구부와 도착참','VB_overview'),('승강기 — 전실에서 보이는 탑승구','VL_front'),('출구 — 황야로 이어지는 길','OUT')]:
 parts.append('<h2>'+title+'</h2><div class="pair">')
 for phase,label in [('before','이전'),('after','수정 후')]:parts.append(f'<figure><a href="{phase}/{key}.jpg"><img loading="lazy" src="{phase}/{key}.jpg" alt="{html.escape(title+label)}"></a><figcaption>{label}</figcaption></figure>')
 parts.append('</div>')
parts.append('<h2>추가 확인 화면</h2><div class="grid">')
for title,key in [('분리된 도르래·로프·권상기','LiftHoist'),('문에서 내려다본 계단 도착참','VB_arrival'),('황야 중간 지점','EndingWalkMid'),('자유를 향한 시야','FreedomVista')]:parts.append(f'<figure><a href="after/{key}.jpg"><img loading="lazy" src="after/{key}.jpg" alt="{title}"></a><figcaption>{title}</figcaption></figure>')
parts.append('</div><h2>실제 Play</h2><div class="grid">')
for p in plays:parts.append(f'<figure><a href="play_{p["label"]}.png"><img loading="lazy" src="play_{p["label"]}.png" alt="{p["label"]} Play"></a><figcaption>{p["label"]} · {p["framesAdvanced"]}프레임 진행 · 입력 이동 {p["displacement"]:.2f}m</figcaption></figure>')
parts.append('</div><p>승강기 운행·문 제어·엔딩 재생 로직은 추가하지 않았습니다. 저장된 1F 씬에서 구조와 피벗을 확인할 수 있습니다.</p></main></html>')
(out/'review.html').write_text(''.join(parts),encoding='utf-8')
print('Wrote Review.md and review.html')
