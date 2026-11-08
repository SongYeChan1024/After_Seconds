from pathlib import Path
import json,shutil,hashlib,html
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_Observation'
audit=json.loads((O/'audit.json').read_text(encoding='utf-8'));walk=json.loads((O/'walk.json').read_text(encoding='utf-8'));preserve=json.loads((O/'preservation.json').read_text(encoding='utf-8'));models=json.loads((H/'models.json').read_text(encoding='utf-8'));plays=[json.loads((O/f'play_{n}.json').read_text(encoding='utf-8')) for n in ['corridor','stairs','deck']]
assert not audit['issues'] and not preserve['changed'] and not preserve['missing']
assert all(r['passed'] for r in walk['results']) and all(p['complete'] and not p['errors'] and p['displacement']>.1 for p in plays)
for n in ['corridor','stairs','deck']:shutil.copy2(P/f'Assets/Temp/B4_Observation/play_{n}.png',O/f'play_{n}.png')
source={'author':'송예찬','date':'2026-11-08','task':'B4 중앙 관찰동 대표 구역 / T02 접근 복도','scene':audit['scene'],'source':'로컬 Blender 제작 및 Pillow 정적 화면 제작. 기존 공용 PBR·의자·터널 리브 재사용. 외부 생성/다운로드 에셋 없음.','newModels':[{'name':n,'asset':Path(m['asset']).relative_to(P).as_posix(),'triangles':m['triangles'],'parts':m['parts'],'source':f'SourceAssets/B4_Observation/{n}.blend','sha256':hashlib.sha256(Path(m['asset']).read_bytes()).hexdigest()} for n,m in models.items()],'reusedAssets':['Assets/Afrer_Seconds/05.Model/Props/B5/SF_TaskChair.fbx','Assets/Afrer_Seconds/05.Model/Environment/Common/CFD_TunnelRib.prefab','Assets/Afrer_Seconds/05.Model/Environment/Common/Textures/LP_Coating_Base.png','Assets/Afrer_Seconds/05.Model/Environment/Common/Textures/LP_Concrete_Base.png','Assets/Afrer_Seconds/05.Model/Environment/Common/Textures/LP_Stainless_Base.png'],'authoring':['SourceAssets/B4_Observation/architecture.py','SourceAssets/B4_Observation/props.py','SourceAssets/B4_Observation/textures.py'],'sceneAssembly':['SourceAssets/B4_Observation/Build.cs','SourceAssets/B4_Observation/Refine.cs','SourceAssets/B4_Observation/FinishArt.cs'],'report':'Docs/검수/2026-11-08_B4_Observation/검수결과.md','originalAssetsPreserved':True,'limitations':['C01/T02 대표 구역만 구현','모니터/문/실험 장비는 정적 아트','나머지 B4 공간·층간 연결·게임 기능은 후속']}
(P/'Assets/Afrer_Seconds/06.Data/AssetSources/B4_Observation_20261108.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows='\n'.join(f"| {p['label']} | {p['displacement']:.3f}m | {p['rise']:.3f}m | {p['framesAdvanced']} | {p['medianMs']:.2f} / {p['p95Ms']:.2f}ms | 0 |" for p in plays)
report=f'''# B4 중앙 관찰동 검수 V0.01

작성자 송예찬 · 2026-11-08

사용자가 B5 현재 외형·조명을 1차 기준으로 수용한 뒤 요청한 다음 층 제작이다. 최신 Decision 도면에 따라 **B4 C01 중앙 관찰동과 T02 접근 복도**를 새 `Level_B4_Circular.unity`로 만들었다. 층 전체 완료 판정은 아니다. B5와 기존 Old B4 씬은 보존했다.

## 이번 공간

- C01 반지름12m, 바닥 Y=-66m, 4개 출입 방향 유지. T02만 열린 접근 복도이고 나머지3개 문과 C02 쪽 끝문은 닫힌 정적 외형이다.
- 중앙에는 직경5.2m 측정 영역·광학 추적 카메라4개·보정 타깃, 지상에는 시험 제어석2개·센서 준비대·측정 기록 랙·보관장·동기화 카트가 있다.
- 북측 높이2.5m 관찰 데크와 2개15단 계단, 유리 난간과 지지 구조. 상부2관측석은 시험 바닥을 바라보고 뒤로 지나갈 수 있다. 계단 위 데크를 절개해 머리 공간을 확보했다.
- 무채색 회색/흑연색, 중성 작업광. 천장8·데크하부4·관측석2·복도4 = 실제 광원18개이며 모두 등기구에 연결했다. 복도 조명은 리브 사이에 배치했다.
- 안내선과 목적지 표기는 T02 복도에만 있다. 돔 내부 중앙 원과 눈금은 실험 측정 표시다.
- `B4_구역코드_한글용도_번호` 이름으로 건축·관측설비·출입구·조명·접근복도를 구분했다.

## 검증

신규 모델 {len(models)}종, 새 씬 건축/설비 Renderer {audit['renderers']}개·Collider {audit['colliders']}개·Light {audit['lights']}개, 인스턴스 메시 {audit['triangles']:,}tri. 재질 누락0, 발광/광원 방향 오류0. 원본 공용 PBR의 Base/Normal을 새 B4 재질로 적용하고 정적 화면6장과 바닥 목적지1장을 제작했다. 액정의 베젤·후면 통풍/단자·VESA·케이블을 별도 형상으로 구성했다.

실제 플레이어 CharacterController(반지름0.28m, 높이1.8m, 단차0.3m)로 복도→중앙, 양쪽 계단 상하, 데크 횡단, 준비/제어 장비 접근 **7/7 경로 통과**. 발높이 오차 약8cm는 기존 skinWidth0.08m 범위다. 안내선의 돔 중심 최단 거리 {audit['minGuideRadius']:.3f}m로 반지름12m 밖에만 존재한다.

| 실제 키보드 Play | 수평 이동 | 높이 변화 | 진행 프레임 | 중앙값 / P95 | 새 경고·오류 |
|---|---:|---:|---:|---:|---:|
{rows}

1920×1080 Editor Play 측정이며 출시 빌드 성능 확정값은 아니다. Play 캡처는 Game View 1280×720 출력이다. 조명/그림자는 현재 대표 구역 기준이며 B4 전체 확장 후 가림·LOD·성능을 다시 마감한다. 마지막 카메라 벽고정대4개는 정적 아트 보강이며 이동/게임 코드 변경은 없다.

작업 시작 시점의 기존 Assets/Packages/ProjectSettings **{preserve['protectedFiles']:,}파일 전부 SHA-256 동일**. B5 씬·기존 모델/재질·사용자 설정·게임 C#/Animator를 보존했다. Player/Camera 연결은 Unity 네이티브 Save As Copy로 유지한 뒤 새 씬에서 B5 환경 루트만 제거했다. 파일 YAML 직접 수정은 없다. 임시 Play 입력과 백그라운드 실행 설정은 복원했다.

## 다음 작업

1. C01 대표 구역의 외형·밝기·공간 용도 사용자 확인과 보수.
2. T02 끝 C02 진단동 → T01/VA 계단A 연결부 확장. B5↔B4 실제 연결은 별도 검증.
3. 나머지 중앙 지원동·분석동·기록동, 동서 측정/진단 구역, N01/S01, VB/VL과 복도 확장. 현재 후속 범위는12돔·3코어·21복도다.
4. 전체 층 완성 후 조명·색감·가림·성능 마감. 모니터 애니메이션, 문 개폐, 실험 기믹, 감시/AI, 층 전환 코드는 사용자 직접 구현 범위로 남긴다.

현재 로컬 저장 상태이며 이번 변경은 커밋·push하지 않았다. [검수 화면](review.html), [이동 결과](walk.json), [구조 검사](audit.json), [보존 확인](preservation.json).

## Revision History

- V0.01 (2026-11-08): B4 C01/T02 대표 구역 제작과 이동·Play·보존 검증. 송예찬.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
pictures=[('02_deck','중앙 측정 공간과 관찰 데크'),('04_console','시험 바닥을 바라보는 상부 관측석'),('03_from_deck','데크에서 보는 시험 공간'),('05_preparation','광학 센서 준비대'),('07_stairs','양측 계단과 난간'),('06_corridor','T02 복도 전용 안내'),('01_arrival','진입부 공간 관계'),('play_corridor','실제 Play · 복도'),('play_stairs','실제 Play · 계단'),('play_deck','실제 Play · 데크')]
cards=''.join(f'<figure><a href="{n}.png"><img loading="lazy" src="{n}.png" alt="{html.escape(t)}"></a><figcaption>{html.escape(t)}</figcaption></figure>' for n,t in pictures)
(O/'review.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B4 중앙 관찰동 검수</title><style>body{{margin:0;background:#10151b;color:#e0e7e8;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1250px;margin:auto;padding:36px 24px}}h1{{font-size:32px;margin-bottom:8px}}p{{color:#aebbc5}}article{{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:24px}}figure{{margin:0;background:#1b242c;border:1px solid #35414a;border-radius:8px;overflow:hidden}}figure:first-child{{grid-column:1/-1}}img{{display:block;width:100%}}figcaption{{padding:12px 16px}}a{{color:#b8d8cc}}@media(max-width:500px){{article{{grid-template-columns:1fr}}}}</style><main><h1>B4 · 중앙 관찰동</h1><p>능력 측정·관찰층 대표 구역 / C01 + T02 · 송예찬 · 2026-11-08<br>상부 관찰 데크2.5m · 양측 계단 · 광학 측정/준비/기록 설비 · 복도 전용 안내<br>이동7/7 · Play3구역 새 로그0 · 기존5,788파일 동일</p><p>사진을 누르면 원본을 볼 수 있습니다. <a href="검수결과.md">검수 결과와 다음 작업</a></p><article>{cards}</article><p>현재 대표 구역만 제작. 남은 B4 구역과 층간 연결은 후속이며 장비/모니터/문은 정적 아트입니다.</p></main></html>''',encoding='utf-8')
note=f'''2026-11-08 B4 중앙 관찰동 대표 구역 제작: 사용자가 B5 외형·조명을 1차 기준으로 수용하고 다음 층을 요청했다. 새 `Level_B4_Circular.unity`에 Decision C01(반지름12m, Y=-66m)과 T02 접근 복도, 높이2.5m 관찰 데크·양쪽15단 계단·관측석/시험 제어/센서 준비·기록 장비를 제작했다. 회색/흑연색과 중성 작업광18개, 신규 모델{len(models)}종, 안내선은 복도에만 유지했다. Controller7/7·Play3구역 실제 이동·새 게임 로그0, 기존5,788파일 해시 동일로 B5/게임 C#/Animator 보존. **다음은 C01 사용자 검수 → C02 진단동/T01/VA 확장 → 나머지 B4 구역**. 현재 대표 구역만 완료이며 남은12돔·3코어·21복도, B5↔B4 연결·게임 기능은 후속이다. B5 1차 수용을 전체 최종 아트 판정과 구분한다. 로컬 저장, 이번 변경 커밋·push 미실시. 작성자 송예찬.'''
for rel,old,new,prefix in [('AGENTS.md','V0.60','V0.61','Docs/'),('CLAUDE.md','V0.60','V0.61','Docs/'),('Docs/이어하기_2026-11-06.md','V0.44','V0.45',''),('Docs/회사_작업목록_2026-11-06.md','V0.42','V0.43',''),('Unity/README.md','V0.45','V0.46','../Docs/')]:
 p=R/rel;s=p.read_text(encoding='utf-8');title,body=s.split('\n',1);assert old in title,(rel,title)
 link=f' [{"검수 화면"}]({prefix}검수/2026-11-08_B4_Observation/review.html) · [검수 결과]({prefix}검수/2026-11-08_B4_Observation/검수결과.md).'
 p.write_text(title.replace(old,new)+'\n\n'+note+link+'\n\n이전 단계 기록:\n'+body.lstrip()+f'\n- {new} (2026-11-08): B5 1차 수용과 B4 C01/T02 대표 구역 제작·검수·후속 순서. 송예찬.\n',encoding='utf-8')
p=H/'README.md';s=p.read_text(encoding='utf-8').replace('V0.01','V0.02',1);s+='''
최종 반영 순서는 `Build.cs` → `Refine.cs` → `FinishArt.cs`다. 기존 B4 씬이 있으면 Build는 중단한다. 이후 수정은 해당 오브젝트만 대상으로 한다. `Refine`은 상부 관측석을 시험 바닥 방향으로 돌리고 좌석 뒤 통행을 확보한다. `FinishArt`는 벽 하단 밀폐 마감과 카메라 벽고정대를 추가한다.

완료 검증·화면·후속 범위: `Docs/검수/2026-11-08_B4_Observation/검수결과.md`. SourceAssets의 검수 C#은 게임 런타임에 반입하지 않는다. `prepare.py`와 `report.py`의 인수인계 버전 갱신은 최초1회용이며 다시 실행하지 않는다.

- V0.02 (2026-11-08): C01/T02 대표 구역 구현과 검수 결과, 재실행 주의점. 송예찬.
''';p.write_text(s,encoding='utf-8')
print(json.dumps({'models':len(models),'triangles':audit['triangles'],'docsUpdated':5,'preserved':preserve['unchanged']},ensure_ascii=True))
