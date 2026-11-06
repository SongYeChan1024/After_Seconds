from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-07_C01_Lighting';T=R/'Docs/검수/2026-11-07_C01_PortalTiles';U=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
p=json.loads((O/'play_inside.json').read_text('utf-8'))
prefix='2026-11-07 실험동 타일/조명 보수:'
note=prefix+' 문 위 회색 비대칭 노출부는 생략된 벽 타일이었다. 실제 아치에 맞춘 곡면 타일20조각(14,337tri)을 추가해 기존 줄눈에 연결했다. 작업등4개의 꺼진 발광을 복구하고 광원 위치/방향을 확산판에 맞췄다. 등기구 없는 보조광6개는 비활성 보관, 포드 천장 등기구1개 추가, T01/T11 등15개 발광 연결. [타일 검수]({tiles})·[조명 검수]({lighting})를 우선한다. 사용자 Worklight_52 편집을 먼저 백업/보존했고 해당 보조광의 Transform/수치는 남아 있다. 새 타일 통행369표본 막힘0·신규 메시 퇴화0, Play '+str(p['framesAdvanced'])+'프레임·'+f"{p['displacement']:.3f}"+'m·새 경고/오류'+str(len(p['errors']))+'건. 게임 코드/프랍 배치/문/리브 유지. 로컬 저장, 커밋/push 미실시. 다음은 사용자 시야에서 타일/조명 확인 → 바닥 안내선 → T01/C02. 전체 아트0/34 유지.'
for fn in ['AGENTS.md','CLAUDE.md','Docs/이어하기_2026-11-06.md','Docs/회사_작업목록_2026-11-06.md']:
 f=R/fn;text=f.read_text('utf-8');first,rest=text.split('\n',1)
 if prefix in rest:continue
 first=re.sub(r'V0\.(\d+)',lambda m:'V0.'+str(int(m[1])+1).zfill(2),first,count=1);rel='' if fn.startswith('Docs/') else 'Docs/'
 f.write_text(first+'\n\n'+note.format(tiles=rel+'검수/2026-11-07_C01_PortalTiles/검수결과.md',lighting=rel+'검수/2026-11-07_C01_Lighting/검수결과.md')+'\n\n이전 단계 기록:\n'+rest.lstrip(),encoding='utf-8')
tile_report='''# 실험동 문 위 타일 연결 검수 V0.01

작성자: 송예찬 · 2026-11-07

사용자가 지적한 부분은 문 본체가 아니라 문 위 회색 바탕이었다. 기존 제작기에서 출입축17도 이내·높이4.01m 아래의 타일을 통째로 빼면서 비대칭으로 드러났다. 해당 영역에 기존 곡률·두께24mm·줄눈과 같은 타일을 추가하고 실제 아치 단면에 맞춰 절단했다. 기존 벽/문/리브 모델은 변경하지 않았다.

![전후](BeforeAfter.jpg)

20조각·1메시·14,337tri. 베벨3mm, 퇴화면0, 누락 재질0. 새 타일 Collider와 메시 일치. 출입구3곳×123 =369개 통행 표본 막힘0. 실제 안/밖/상부 사진18장을 확인했다. 삼각화 중 작은 퇴화면3개를 제거해 최종 재반입 경고/오류0이다.

타일 도중 사용자 조명 편집이 감지됐다. 미저장 상태를 Temp의 CurrentUserEdit_BeforeTiles.unity로 별도 백업하고 저장한 다음 적용했다. 유효 기준은 baseline.json의 effectiveSceneBackup이다. 조명 보수 직전 씬과 대조하면 기존 객체 삭제0, 변경은 C01_Experiment_Art의 자식 목록1건뿐이다. 승인된 프랍·문·리브·플레이어 Transform을 건드리지 않았다.

보호3254파일 중 기존 모델/텍스처/게임 코드는 동일하다. 씬 저장 시 URP 자동 재검증으로15개 기존 재질의 직렬화 해시가 달라져 preservation.json에 기록했다. 타일 적용기는 기존 S1_Coat을 참조하며 새 재질이나 공용 재질 수정을 만들지 않았다. 바이트 전체 동일이라고 보고하지 않는다. 이어서 수행한 조명 변경은 별도 검수에 기록했다.

모델은 05.Model/Environment/B5/AF_C01_PortalTileInfill.fbx, 원본은 SourceAssets/C01_PortalTiles/AF_C01_PortalTileInfill.blend다. 로컬 저장, 커밋/push 미실시. 게임 기능 변경0. 최종 조명 상태는 ../2026-11-07_C01_Lighting/검수결과.md를 따른다.
'''
(T/'검수결과.md').write_text(tile_report,encoding='utf-8')
lighting_report=f'''# 실험동 조명 연결 검수 V0.01

작성자: 송예찬 · 2026-11-07

실제 작업등은 EmissionColor가 설정되어도 `_EMISSION` 키워드가 꺼져 어두웠다. 외곽 보조 Spot5개와 중앙 보조 Point1개는 대응하는 등기구가 없이 빛을 내고 있었다. 사용자 Worklight_52 위치 조정은 먼저 별도 백업해 현재 값과 의도를 보존한 뒤 원인을 수정했다.

![조명 전후](BeforeAfter.jpg)

벽 작업등4개의 확산판을 전용 CL_Lamp로 연결했다. 발광색/키워드와 BakedEmissive 플래그를 함께 설정해 재로드 뒤에도 발광이 유지된다. 이 재질 플래그를 사용했지만 GI나 Lightmap을 새로 베이크한 것은 아니다. 실제 광원은 확산판 아래47.5mm, 수직 아래에서 실내 쪽6.84도다. Spot135/Inner90도, Intensity6.5, Range11m로 조절해 작업대의 과한 흰색 번짐을 줄였다.

포드의 Point 광원은 아래 방향 Spot으로 전환했다. 확산판이 광원 위58mm에 있는 천장 등기구1개를 붙였고 기존 Intensity12/Range12m를 유지했다. 신규 모델1,632tri·퇴화0. 외곽 보조광5개와 Measurement_Indirect1개는 Light 컴포넌트만 비활성 보관했으며 위치/회전/Intensity/Range는 삭제하거나 초기화하지 않았다. 실험동 안의 활성 Light는 벽4+포드1=5개다. T01/T11에 실제 등기구가 있는 밀폐등15개의 발광 표면도 연결했다. 다른 복도나 전체 B5 조명 완성을 뜻하지 않는다.

## 검증

- 벽 작업등4개 모두 발광 표면 연결, 확산판/광원 오프셋47.5mm·방향 차6.84도.
- 포드 확산판/광원 오프셋58mm·방향 차0도. 새 모델 퇴화면0.
- 발광 키워드와 BakedEmissive 플래그는 저장/재로드/Play 진입 후에도 유지.
- 실제 기존 W 입력: {p['framesAdvanced']}프레임 진행, {p['displacement']:.3f}m 이동, 새 경고/오류{len(p['errors'])}건.
- 1920×1080 Editor 프레임 시간 중앙{p['medianMs']:.2f}ms, p95 {p['p95Ms']:.2f}ms. 최종 빌드 성능 보장은 아니다.
- 동일 시점 수정 전8장/수정 후8장으로 등기구·작업대·포드·방 전체를 확인했다.

조명 작업 직전 기준3322개 기존 파일의 해시는 모두 동일하다. 공용 Lamp 재질은 직접 고치지 않고 새 전용 재질을 씬의 해당 Renderer에 연결했다. 기존 씬 객체 삭제0, 수정36개는 Light/광원 Transform/등기구 Renderer와 신규 자식 목록이다. 승인된 작업대·프랍·문·기존 벽/리브·플레이어 시작 위치, 게임 C#을 보존했다. 사용자 편집 백업은 SourceAssets/C01_PortalTiles/baseline.json과 C01_Lighting/baseline.json에 기록돼 있다.

Play 종료 후 저장 씬 복원 및 background=false. 문은 기존 열린 상태다. 광원 스위치·점멸·경보/구역 점등 코드는 추가하지 않았다. 사용자 시야에서 최종 밝기를 확인하고 다음은 바닥 안내선→T01/C02다. 전체 아트0/34 유지. 로컬 저장, 커밋/push 미실시.
'''
(O/'검수결과.md').write_text(lighting_report,encoding='utf-8')
for name,model,source,tri,scope in [('C01_PortalTiles','AF_C01_PortalTileInfill','C01_PortalTiles',14337,'C01 T01/T03/T11 wall tile infill'),('C01_Lighting','CL_PodCeilingLight','C01_Lighting',1632,'C01 four wall lights and pod; T01/T11 diffuser emission')]:
 d=dict(author='송예찬',date='2026-11-07',source=f'SourceAssets/{source}/{model}.blend',asset=f'Assets/Afrer_Seconds/05.Model/Environment/B5/{model}.fbx',triangles=tri,scope=scope,runtimeCodeAdded=False,externalGenerationUsed=False)
 (U/f'06.Data/AssetSources/{name}_20261107.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Updated handoffs, two reports and provenance records')
