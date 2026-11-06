import json,re,hashlib
from pathlib import Path
S=Path(__file__).resolve().parent;R=S.parents[1];D=R/'Docs';O=D/'검수/2026-11-06_B345_WideInterior';P=D/'도면/잠입_탐색'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def jwrite(p,obj):write(p,json.dumps(obj,ensure_ascii=False,indent=2))
def prepend(path,version,text):
 p=R/path;raw=p.read_text(encoding='utf-8-sig');head,body=raw.split('\n',1);head=re.sub(r'V\d+\.\d+',version,head)
 write(p,head+'\n\n'+text+'\n\n아래 날짜별 문단은 이전 작업 이력이다.\n'+body)
validation=read(O/'validation.json');audit=read(O/'art_audit.json');controller=read(O/'controller.json');layout=read(P/'layout.json');routes=read(P/'플레이어_예상이동/player_routes.json');arches=[read(S/(f+'_arches.json')) for f in ('B5','B4','B3')]
samples=sum(r['samples'] for f in validation for r in f['routes']);walks=sum(len(f['results']) for f in controller['reports'])
assert not any(r['blocked'] for f in validation for r in f['routes'])
assert all(r['passed'] for f in controller['reports'] for r in f['results'])
assert not any(d['clearanceHits'] for f in validation for d in f['doors'] if d['open'])
assert not any(p['overlaps'] for f in validation for p in f['props'])
assert not audit['errors'] and not any(f['archCollisions'] for f in audit['rows'])
summary='2026-11-06 최신: 사용자 요청에 따라 B5/B4/B3의 큰 복도 차폐벽12개를 제거하고 벽면 설비 엄폐12개로 대체했다. 도면V0.04와 단면 기준을 다시 작성해 복도4.2m·북측4.8m, 연속 반원 터널, 주요실 돔10곳, 문 접합부·리브·조명·충돌을 맞췄다. 기존 복도 조명은 정리하고 곡면 밀착등16개/층을 사용한다. 벽·상자 패턴은 장식 문양이 아닌 불규칙한 먼지·닦임·사용 흔적이며 상자309개에6마감을 혼합했다.'
link='[최신 구조 검수](Docs/검수/2026-11-06_B345_WideInterior/검수결과.md), [새 단면](Docs/도면/잠입_탐색/터널_돔_단면_기준.png), [이어하기](Docs/이어하기_2026-11-06.md)를 우선한다.'
tail=f' 활성 모델은 WC 건축/벽, WA 터널·돔이다. SourceAssets/B345_WideInterior가 최신 제작 원본이다. 정적 경로{samples:,}표본·열린 문74곳·프랍113개·Controller{walks}검사를 통과했다. 게임 C#·AI·문/키패드 동작·UI·미니맵은 사용자 직접 작성 범위이며 추가하지 않았다. 실제 키보드 Play/FPS 재검사는 남는다. 로컬 저장 상태이며 커밋/push하지 않았다.'
for path,version in [('AGENTS.md','V0.30'),('CLAUDE.md','V0.30')]:prepend(path,version,summary+' '+link+tail)
prepend('Unity/README.md','V0.43',summary+' [최신 검수](../Docs/검수/2026-11-06_B345_WideInterior/검수결과.md)와 [이어하기](../Docs/이어하기_2026-11-06.md)를 우선한다.'+tail)
handoff=summary+'\n\n'+'''- 최신 도면: [B5 평면](도면/잠입_탐색/B5_격리층_잠입.png), [터널·돔 단면](도면/잠입_탐색/터널_돔_단면_기준.png), [예상 이동 복사본](도면/잠입_탐색/플레이어_예상이동/B5_A_예상이동.png). B4/B3와 상층 도면도 같은 폴더다.
- 제작 씬은 `Stage/Level_B5_Stealth.unity`, B4/B3다. 기존6씬은 유지한다. B2/B1/1F는 도면만 갱신했고 새 Unity 레벨은 아직 없다.
- 기존 사각 천장과 큰 차폐벽을 파생 WC 모델에서 제거했다. `Wall_Surface_Wear`의 WS 이름은 재질별 묶음 이름이며 방화벽을 뜻하지 않는다. 기존 모델/GUID는 보존한다.
- `Arched_Interior`는 WA 모델·정적 곡면 충돌·조명을 포함한다. `Corridor_WallEquipment`는 기존 VARCO/Blender 공용 SD_PPEStation을 재사용한12개다. 이전 프랍101개도 유지한다.
- 주요실 돔은 B5 2개/B4 5개/B3 3개. B5 포드6.44m, B4 데크2.5m, B3 시료 랙 높이를 고려해 돔 시작 높이를 각각 잡았다. 계단A 상승7.8m/B 상승6.4m는 유지하고 코어는 동쪽3.6m·남쪽0.8m 이동했다.
- 벽/상자는 WS/SW 생활 흔적 마감이며 장식 띠/순차 문양으로 되돌리지 않는다. SW는 모든 LOD에 연결했다.
- 재개 시 `SourceAssets/B345_WideInterior/README.md`를 먼저 읽는다. 옛 도면 생성기와 LC/SD/WS/AR 단계 Apply를 현재 확장 씬에 재실행하지 않는다. 새 예상 동선은 실제 정적 충돌·바닥을 기준으로 재계산했으며 런타임 AI가 아니다.
- 다음은 사용자 직접 시야·길 찾기 확인 → 긴 복도의 경비/CCTV 배치와 엄폐 체감 조정 → B2 단면/새 레벨 순서다. 사용자의 추가 기능 요청 전에는 게임 C#을 작성하지 않는다.
'''+tail+'\n\n[검수 수치와 사진](검수/2026-11-06_B345_WideInterior/검수결과.md).'
prepend('Docs/이어하기_2026-11-06.md','V0.08',handoff)
prepend('Docs/회사_작업목록_2026-11-06.md','V0.07',summary+'\n\n완료: 큰 벽 철거·벽면 엄폐, 터널/돔 구조 정합, 평면·단면·예상 동선 재작성, 문/계단/프랍 정적 검수. 다음은 사용자 직접 Play 시야·길 찾기와 성능 확인, 경비/CCTV 배치 조정, B2 제작이다. [최신 이어하기](이어하기_2026-11-06.md)와 [검수 사진](검수/2026-11-06_B345_WideInterior/검수결과.md)를 따른다.'+tail)
prepend('Docs/AfterSeconds_메인기획서.md','V0.23',summary+'\n\n새 제작 기준은 [평면 V0.04](도면/잠입_탐색/layout.json), [터널·돔 단면](도면/잠입_탐색/터널_돔_단면_기준.png), [층간 단면](도면/잠입_탐색/층간_단면.md)이다. 네모난 통로에 아치 장식만 더하는 방식은 사용하지 않는다. 복도 곡면이 리브 사이에도 연속되고, 주요실은 돔형 천장으로 연결한다. 잠입과 탐색이 중심이며, 큰 평판 차폐 대신 벽면 설비와 문·코너를 엄폐 후보로 사용한다. 계단·포드·데크·랙·실내 출입 관계를 유지한다. 경비/CCTV/연구원의 역할과 게임 규칙은 그대로다.'+tail)
p=D/'AfterSeconds_메인기획서.md';t=p.read_text(encoding='utf-8');t=re.sub(r'\| 문서 버전 \|.*', '| 문서 버전 | V0.23 (2026-11-06). 터널·돔 구조 설계와 B5/B4/B3 제작 정합, 큰 차폐벽을 벽면 설비로 대체, 예상 이동 재계산. |',t)
t=t.replace('| 버전 | 날짜 | 작성자 | 변경 내용 |\n| --- | --- | --- | --- |','| 버전 | 날짜 | 작성자 | 변경 내용 |\n| --- | --- | --- | --- |\n| V0.23 | 2026-11-06 | 송예찬 | 큰 차폐벽12개 철거·벽면 설비 엄폐12개, 평면V0.04/터널·돔 단면 재작성, 돔10곳과 조명/충돌 정합, 현재 정적 공간 기준 예상 이동 재계산. 게임 코드 보존. |',1);write(p,t)
table='\n'.join('| '+a['floor']+' | '+str(a['arches'])+' | '+str(len(a.get('domes',[])))+' | 16 | '+str(len(a['lights'])-16)+' | '+format(v['trianglesHighestLOD'],',')+' |' for a,v in zip(arches,validation))
report=f'''# B5·B4·B3 터널·돔 설계 정합 검수 V0.01

작성자 송예찬 · 2026-11-06

{summary}

## 도면과 구조

방과 계단 크기를 줄이지 않고 일반 복도3→4.2m, 북측4→4.8m로 넓혔다. 건물 본체 외곽은51.6×34m이며 동측 코어에 단차가 있다. 계단·리프트 코어는 동쪽3.6m·남쪽0.8m 이동했다. 문 폭1.5m·높이2.8m, 계단A40단/7.8m와 계단B36단/6.4m를 유지한다.

[새 B5 평면](../../도면/잠입_탐색/B5_격리층_잠입.png) · [전체층 평면](../../도면/잠입_탐색/전체층_잠입.png) · [터널·돔 단면](../../도면/잠입_탐색/터널_돔_단면_기준.png) · [B5 예상 경로 비교](../../도면/잠입_탐색/플레이어_예상이동/B5_경로비교.png)

복도 천장은 연속 반원 터널이다. 24cm 두께·44cm 깊이 리브의 주 모서리에22mm 베벨을 넣었다. 발 돌출 약58cm로 일반 복도의 리브 사이 폭은 약3.04m다. 문 앞에는 측면 연결 곡면을 만들어 기존 문·키패드·수납부 높이를 피한다. 주요실 돔은 포드·데크·랙 높이를 기준으로 달리 잡고, 겹치던 기존 평천장과 등기구를 파생 모델에서 제거했다. 돔 등기구도 실제 곡면을 따라 붙인다.

| 층 | 복도 리브 | 주요실 돔 | 복도 조명 | 돔 조명 | 최고 LOD 삼각형 |
| --- | ---: | ---: | ---: | ---: | ---: |
{table}

큰 차폐벽은 층마다4개, 총12개를 시각 메시와 통행 충돌에서 제거했다. `Corridor_WallEquipment`에는 기존 공용 VARCO/Blender 보호구 수납 설비를4개씩 재사용했다. 약1.06×0.45×1.85m로 벽 쪽에 붙여 통로를 가로지르지 않는다. 기존 프랍101개를 합해 검사 대상은113개다. 긴 시야가 생긴 만큼 경비/CCTV 배치와 엄폐 체감은 실제 플레이에서 조정한다.

## 사진

| 큰 차폐벽 제거 후 B5 북측 터널 | B4 중앙 터널 |
| --- | --- |
| ![B5](After/B5_6.png) | ![B4](After/B4_8.png) |

| B5 냉각실 돔 | B4 관제 데크와 돔 |
| --- | --- |
| ![냉각실](After/B5_1.png) | ![관제](After/B4_3.png) |

사진은 검수용 임시 카메라 렌더다. Before 폴더는 복도 확장 전 상태다.

## 검증 결과와 범위

- 현재 충돌·바닥을 바탕으로 B5/B4/B3 예상 이동9개를 재계산했다. 도면 복사본에만 표시하며 미니맵을 만들지 않았다. 상층9개 경로는2D 가안이다.
- 예상 경로{samples:,}표본 막힘0, 열린 일반 문74곳 접근 간섭0, 프랍113개 겹침0.
- 임시 CharacterController 이동·계단·데크{walks}검사 통과. 실제 키보드 Play/FPS 측정은 이번 단계에서 하지 않았다.
- 원래 Transform6,798개의 회전·스케일·활성 상태를 보존하고 필요한 상위 배치를 이동했다. 새 구조와 설비는 별도 그룹이다. 기존 차폐벽 Collider12개는 껐다.
- 상자309개는6종 생활 흔적을 불규칙하게 섞었다. 1.05m 이내 동일 마감 이웃0쌍. 벽의 사용 흔적과 모든 LOD 재질을 확인했다.
- 누락 재질·스크립트0, 새 모델 재반입 경고/오류0. 정적 반사25개를 새 구조에 맞춰 갱신했다.
- 원본 에셋·프리팹·게임 C#·Animator·설정·Packages·기존6씬 보존은 protection.json을 따른다. 기존 반사 이미지25개만 갱신 대상이다.

검사 원본: validation.json, controller.json, art_audit.json, structure.json, replanned_routes.json, import.json, reflections.json, protection.json. B4 추가 조명 정리는 lighting_refine.json이다.

## 현재 파일

- 씬: `Stage/Level_B5_Stealth.unity`, B4/B3 동일 형식.
- 활성 건축/벽: `Environment/<층>/WC_<층>_Architecture.fbx`, `WC_<층>_Walls.fbx`. B4는 WC_B4_Details도 사용한다.
- 터널·돔: `WA_<층>_Interior.fbx`, 씬 `Arched_Interior`. 정적 곡면 MeshCollider와 리브 충돌을 포함한다.
- 생활 흔적: 공용 WS 벽 재질, SW_Case_* 상자 재질/프리팹. WS_Clean은 흰색 벽 마감 이름이며 방화벽이 아니다.
- 편집 원본/외부 제작 도구: `SourceAssets/B345_WideInterior`, `B345_WallSurfaces`. Blender 베벨 수정 원본을 보존했다.

게임 기능·UI를 추가하지 않았다. 로컬 저장 상태이며 커밋/push하지 않았다.
'''
write(O/'검수결과.md',report)
prepend('SourceAssets/B345_WideInterior/README.md','V0.02','현재 기준은 평면V0.04와 터널·돔 단면이다. 큰 차폐벽12개를 제거하고 벽면 설비12개를 배치했다. 주요실 돔10곳과 기존 평천장/조명 제거를 포함한다. 아래 V0.03 확장 설명 뒤의 제작 순서는 현재 후속 내용을 우선한다.\n\n1. `wide_plan.py`는 확장 전 스냅샷에서 설계 원안을 재생성한다. 최종 예상 동선을 덮어쓰므로 단독 재실행하지 않는다.\n2. `build_wide.py`, `prepare_tools.py` → `build_arches.py`가 WC/WA 모델을 만든다. 돔과 터널 함수는 dome_geometry.txt/tunnel_geometry.txt다.\n3. 최초 확장은 ApplyWide.Apply가1회 수행했고, 현재 후속 아트 교체는 Structure/RebuildArches다. 현재 씬에 최초 Apply를 다시 하지 않는다.\n4. `ReplanRoutes.Run`으로 B5/B4/B3 도면 동선을 현재 정적 충돌/바닥 기준으로 재계산한다. 게임 C#이 아니다.\n5. render_plans.ps1/render_routes.ps1/render_sections.ps1은 현재 JSON을 읽어 SVG/PNG만 갱신한다.\n6. WideValidate/WideWalk/WideAudit, 반사 갱신·사진·반입 검수를 수행한다. 최종 수치는 최신 검수 문서에 있다.\n\n새 조명은 복도16개/층 + 돔12/24/14개다. 기존 B4 조명 이름은 숫자 접미사 없는 Ceiling_A/AN/AS/B/D도 있으므로 함께 정리한다. 원본 Asset과 GUID를 보존하고, 현재 제작 모델만 업데이트한다.')
for path in ['SourceAssets/B345_ArchedInterior/README.md','SourceAssets/B345_WallSurfaces/README.md','SourceAssets/B345_Dressing/README.md']:
 prepend(path,'V0.02','후속 최신은 `SourceAssets/B345_WideInterior`와 [터널·돔 검수](../../Docs/검수/2026-11-06_B345_WideInterior/검수결과.md)다. 현재 모델은 WC/WA이며, 상자는 SW 생활 흔적 마감이다. 이 폴더의 이전 Apply를 현재 확장 씬에 덮어 실행하지 않는다.')
# Current source provenance lives with game data, not in the model folders.
provenance=dict(title='B345 Tunnel Dome and Surface Wear V0.01',author='송예찬',date='2026-11-06',reference='Docs/Reference/Reference_004.jpg',floors=['B5','B4','B3'],planVersion='V0.04',models=['WC_<floor>_Architecture.fbx','WC_<floor>_Walls.fbx','WA_<floor>_Interior.fbx'],sources='SourceAssets/B345_WideInterior',originalAssetsPreserved=True,removedLargeBaffles=12,newWallEquipment=12,reusedEquipmentPrefab='SD_PPEStation.prefab',equipmentOrigin='Existing VARCO V0.03 + Blender asset',newRuntimeScripts=0,wallWear='WS Clean/Staff/Steel/Concrete, dust/wipes/contact marks',caseWear='SW six irregular use-wear materials, all LODs',validation='Docs/검수/2026-11-06_B345_WideInterior/검수결과.md')
jwrite(R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B345_TunnelDome_20261106.json',provenance)
# Refresh design metadata that otherwise still referred to the old 48x32m plan.
checks=[]
for f in layout['floors']:
 overlaps=[]
 for i,a in enumerate(f['rooms']):
  for b in f['rooms'][i+1:]:
   if min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])>1e-4 and min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])>1e-4:overlaps.append([a['id'],b['id']])
 assert not overlaps
 checks.append(dict(floor=f['floor'],version='V0.04',footprintArea=round(sum(r['w']*r['h'] for r in f['rooms'] if r['kind']!='exterior'),3),roomOverlapCount=0,largeBaffles=0,wallEquipment=4,unityVerified=f['floor'] in ('B5','B4','B3'),limits='게임 감시/추격/시간 안전성 미검증. B5/B4/B3 정적 통행은 최신 검수 참조.'))
jwrite(P/'validation.json',checks)
jwrite(P/'플레이어_예상이동/route_validation.json',[dict(floor=r['floor'],variant=r['variant'],walkingMetres=r['walkingMetres'],legs=len(r['legs']),staticGeometryChecked=r.get('staticGeometryChecked',False),temporalSafetyVerified=False) for r in routes['routes']])
write(P/'README.md','''# 터널·돔 구조 설계도 안내 V0.01

작성자 송예찬 · 평면 기준 V0.04

- [전체층 평면](전체층_잠입.png), [B5 평면](B5_격리층_잠입.png), [터널·돔 단면](터널_돔_단면_기준.png), [층간 단면](층간_단면.md)
- [B5 예상 이동 비교](플레이어_예상이동/B5_경로비교.png). 예상 이동은 도면 복사본이며 Unity UI가 아니다.
- 큰 차폐벽을 제거하고 벽면 설비를4개/층 배치한다. 일반 복도4.2m·북측4.8m, 천장4m의 연속 반원 터널이다. 주요실 돔 높이는 각 평면과 단면에 적었다.
- B5/B4/B3는 새 Unity 제작 씬과 정합했다. B2/B1/1F는 수직 코어 좌표와 구조 원칙만 반영한 가안이다.
- 기존 기믹 도면과 V0.02 생성기는 과거 기준이다. 현재 생성·재계산 절차는 `SourceAssets/B345_WideInterior/README.md`를 따른다.
''')
print('Documentation and provenance updated; samples',samples,'controller',walks)
