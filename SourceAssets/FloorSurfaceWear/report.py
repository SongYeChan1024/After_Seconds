from pathlib import Path
import json,html,hashlib,collections
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'SourceAssets/B4_DeskAndCollision';O=R/'Docs/Review/2026-11-09_FloorSurfaceWear'
def read(p):return json.loads(p.read_text(encoding='utf8'))
applied=[x for x in read(H/'applied.json') if x['changedTriangles']]
verify=read(O/'verification.json');final=read(O/'verification_final.json') if (O/'verification_final.json').exists() else verify
walk4=read(O/'walk.json');walk5=read(O/'walk_B5.json');proxies=read(D/'proxies_verification.json')
plays=[read(p) for p in sorted(O.glob('play_*Pole.json'))]+([read(O/'play_E02_Gap.json')] if (O/'play_E02_Gap.json').exists() else [])
base=read(H/'protected_before.json');diff=[p for p,h in base.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
(H/'protected_diff.json').write_text(json.dumps(diff,indent=2),encoding='utf8')
text=f'''# 바닥·화물 승강기·기록대·충돌 보수 V0.01

작성자 송예찬 · 2026-11-09 · 로컬 저장, 커밋·push 미실시

사용자 요청은 B5/B4의 은은한 바닥 패턴, 화물 승강기 사용감, E02 기록대의 겹침/부족한 컴퓨터 구성, E02·C02 작업등 주변과 그 외의 통행 충돌 보수다. 현재 작업 씬은 `Level_B5_Circular.unity`, `Level_B4_Circular.unity`다.

## 반영 내용

- **바닥**: 매우 옅은 2m 이음선과 불규칙한 미세 얼룩·거칠기를 추가했다. 복도 전용 안내선은 유지했다. 바닥·화물 설비 시각 메시 총 {len(applied)}개(B5 20, B4 39)에 UV/재질을 분리 적용했으며, 위치와 삼각형 형상은 그대로다. 공용 벽 재질을 덮어쓰지 않았다. PBR 15장, 새 재질 14개.
- **화물 승강기**: 바퀴 자국, 벽 하단 운반 접촉, 문/문턱의 마모를 더했다. 하중 표기·호출 버튼·경고 표시를 가리지 않았고 과도한 녹·폐허 표현은 사용하지 않았다.
- **기록대 4곳**: E02/C05/E01/N01의 ProtocolTable에 본체, 키보드, 마우스, 배선, 전원부, 서류함을 넣었다. 서류를 모니터 지지대에서 분리했다. 본체 통풍구·단자·체결부와 베벨을 포함한 Blender 모델 {read(D/"models.json")["PD_ProtocolTable"]["triangles"]:,}tri이다. 책상·의자 위치, 원래 충돌 범위는 유지했다.
- **작업등 36곳**: 전체 외곽을 감싼 박스를 받침·기둥·암·등기구·스위치에 맞는 5개 충돌체로 교체했다. 큰 박스가 빈 공기를 막던 원인을 제거했다.
- **추가 설비 55곳(B5 10, B4 45)**: 높은 프랍 70종을 시각 메시와 캡슐로 비교하여 15종의 과도한 박스를 확인했다. 탱크·배관 설비·계측 기둥·모니터 벽·카트 등에 원본 Blender 파트 기반 정적 충돌 메시 15종을 적용했다. 고유 충돌 메시 합계 47,340tri이며 원래 시각 모델 {sum(x['renderTriangles'] for x in proxies):,}tri보다 가볍다. 이전 박스는 비활성 보존했다.

## 검수

| 항목 | 결과 |
|---|---|
| 활성 충돌 오브젝트 목록 | B5 762개 / B4 442개 조사 |
| B5 실제 CharacterController 경로 | {sum(x['passed'] for x in walk5['results'])}/{len(walk5['results'])} |
| B4 실제 CharacterController 경로 | {sum(x['passed'] for x in walk4['results'])}/{len(walk4['results'])}, 계획 실패 {len(walk4['planningFailures'])} |
| E02·C02 작업등 전면, E02 준비대 사이 | 최종 6방향 통과; 작업등 이동 불필요 |
| 바닥 파생 메시 형상 | {sum(len(x['meshChecks']) for x in verify)}개, 원본 대비 추가/누락 삼각형 0, 잘못된 UV/재질 누락 0 |
| 기존 Transform | B5 {final[0]['transforms']}, B4 {final[1]['transforms']} 보존 |
| 기존 Light | B5 {final[0]['lights']}, B4 {final[1]['lights']} 설정·위치 보존 |
| 충돌 프록시 | 15종 퇴화 삼각형 0, 원본 외곽 차이 최대 {max(x['boundsSizeDelta'] for x in proxies)*1000:.3f}mm |
| 보호 파일 | {len(base):,}개 중 두 대상 씬만 변경, {len(base)-len(diff):,}개 동일 |

실제 Play 검증:
'''
for p in plays:text+=f"\n- `{p['label']}`: 프레임 {p['framesAdvanced']}, 실제 키보드 이동 {p['displacement']:.3f}m, 새 게임 경고/오류 {len(p['errors'])}개."
text+='''

Player 크기/이동 코드, 물리 레이어 설정, 다른 씬, 기존 재질·원본 모델을 수정하지 않았다. Play 검사를 위한 `Application.runInBackground`와 입력/카메라 설정은 검사 후 복원했다. 최종은 저장된 B4 편집 모드다.

## 범위와 한계

주요 연결·설비 접근과 사용자 지적 구간을 검사한 결과다. 모든 임의 위치의 통과나 동적 NPC 충돌을 보장하는 검사는 아니다. 원본의 몇 mm~cm 베벨을 생략한 충돌 메시에는 가장자리의 작은 여유 차이가 있다. 문/승강기 기능과 AI, 전체 층 아트/성능 최종 판정은 이번 작업에 포함하지 않는다.

높이별 박스 중간 실험은 실제 형상에 맞는 최종 프록시로 교체했다. `bounds_verification.json`은 중간 결과이며 최종 수치는 `proxies_verification.json`을 따른다. 최초 작업등 시험 중 E02의 한 끝점이 옆 준비대 내부에 있었으므로, 실제 열린 통로를 쓰는 `local_walk.json`의 최종 6방향 검사를 따른다. 이 기록은 실패를 숨기지 않고 검증 구간을 구분하기 위해 남긴다.

## 이어하기

사용자가 바닥 패턴의 강도, 화물 승강기의 마모, 기록대 디테일과 통행을 확인한다. 필요하면 해당 재질/배치만 보수하고 그 뒤 B4 전체 색감·성능 마감을 진행한다. 현재 씬에 이전 전체 제작기나 `Apply.Run`을 재실행하지 않는다. 게임 내부 C#은 사용자 주도 구현 방침을 유지한다.

[전후 화면](review.html) · [바닥 제작 원본](../../../SourceAssets/FloorSurfaceWear/README.md) · [기록대·충돌 제작 원본](../../../SourceAssets/B4_DeskAndCollision/README.md)
'''
(O/'Review.md').write_text(text,encoding='utf8')
pairs=[('B4_E02_ProtocolTable_01','E02 기록대'),('DeskRear','기록대 후면 배선'),('B5_C01','B5 실험동 바닥'),('B4_C04','B4 작업실 바닥'),('B5_Cargo','B5 화물 승강기'),('B4_CargoDetail','B4 화물실 하단·바닥')]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>바닥·설비·통행 보수 V0.01</title><style>body{background:#141b20;color:#e6ecef;font:16px/1.65 system-ui;margin:32px auto;max-width:1400px;padding:0 20px}h1{font-size:28px}h2{margin:40px 0 12px;font-size:21px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0}img{width:100%;display:block;border:1px solid #3d4b55}figcaption{padding:6px;color:#aec1ce}a{color:#83caff}.note{padding:15px;background:#202d37;border-left:3px solid #83caff}@media(max-width:760px){.pair{grid-template-columns:1fr}}</style><h1>바닥·화물 승강기·기록대·충돌 보수 V0.01</h1><p>2026-11-09 · 송예찬 · Unity 네이티브 카메라, 전후 동일 시점</p><p class="note">B5/B4 바닥 패턴과 화물 사용감, 기록대 4곳 보강. 작업등 36개와 추가 설비 55개의 충돌 형상 보수. B5 128 / B4 331 경로 및 E02·C02 국소 통행 검사 통과.</p><p><a href="Review.md">검수 기록</a></p>'''
for name,label in pairs:
 page+=f'<h2>{html.escape(label)}</h2><div class="pair">'
 for phase,caption in [('before','변경 전'),('after','변경 후')]:
  path=f'{phase}_{name}.png';assert (O/path).exists(),path
  page+=f'<figure><a href="{path}"><img loading="lazy" src="{path}" alt="{html.escape(label)} {caption}"></a><figcaption>{caption}</figcaption></figure>'
 page+='</div>'
page+='<p>바닥은 기존 회색 톤 안에서 표면감만 더했다. 충돌 보수는 보이는 설비 형태와 빈 공간을 구분하며, 게임 기능·문/승강기 동작은 이번 범위에 포함하지 않는다.</p></html>'
(O/'review.html').write_text(page,encoding='utf8')
prefix='''2026-11-09 바닥·설비·통행 후속 보수: B5/B4 바닥에 은은한 표면 패턴과 화물 승강기 사용감을 반영했다(파생 시각 메시59, PBR15, 재질14). E02 등 ProtocolTable4곳에 본체·입력 장치·배선·서류함을 추가하고 서류/지지대 겹침을 해소했다. 작업등36개와 추가 설비55개의 과도한 충돌을 형상에 맞게 보수했다. B5 128/128·B4 331/331 경로와 E02/C02 6방향 통과. 기존5922 Transform·645 Light, Player/게임 코드·물리 설정 보존. **다음은 사용자 외형·통행 확인 → 지적 부분만 보수 → B4 전체 색감·성능 마감**. 저장된 B4 편집 모드이며 이번 변경 커밋·push 미실시. [검수](Docs/Review/2026-11-09_FloorSurfaceWear/Review.md) · [전후 화면](Docs/Review/2026-11-09_FloorSurfaceWear/review.html). 작성자 송예찬.
'''
for name in ['AGENTS.md','CLAUDE.md']:
 p=R/name;s=p.read_text(encoding='utf8');lines=s.splitlines();lines[0]=lines[0].replace('V0.67','V0.68');s='\n'.join(lines)+'\n'
 if '2026-11-09 바닥·설비·통행 후속 보수:' not in s:s=s.replace('\n\n','\n\n'+prefix+'\n아래는 이전 단계 기록이다.\n\n',1);s+='\n- V0.68 (2026-11-09): 바닥/화물 표면·기록대 디테일과 작업등/설비 충돌 보수. 송예찬.\n'
 p.write_text(s,encoding='utf8')
source=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/SurfaceDeskCollision_20261109.json'
source.write_text(json.dumps(dict(version='0.01',author='송예찬',date='2026-11-09',source='Original procedural PBR and Blender source models; no external paid generation',floorMeshes=applied,deskModel=read(D/'models.json'),collisionModels=read(D/'collision_models.json'),collisionInstances=read(D/'proxies_applied.json'),review='Docs/Review/2026-11-09_FloorSurfaceWear/Review.md'),ensure_ascii=False,indent=2),encoding='utf8')
print('Reports updated; protected changes',len(diff),'play views',len(plays))
