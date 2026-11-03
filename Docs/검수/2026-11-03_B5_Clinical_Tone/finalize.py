from pathlib import Path
import json,shutil
R=Path(__file__).parent;P=R.parent.parent;D=P/'Docs/검수/2026-11-03_B5_Clinical_Tone';D.mkdir(parents=True,exist_ok=True)
for f in R.iterdir():
 if f.suffix in ['.json','.cs','.py','.png']:shutil.copy2(f,D/f.name)
shutil.copytree(R/'Backup',D/'Backup',dirs_exist_ok=True)
(D/'검수결과.md').write_text('''# B5 벽 접합면·임상 연구시설 톤 조정 V0.01

2026-11-03 · 작성자 송예찬

사용자가 직접 천장을 180도 뒤집어 패턴을 보이게 한 현재 씬을 먼저 저장·백업했다. 천장 관련 Transform 76개의 로컬 위치·회전·크기를 보호 대상으로 잡고 유지했다. 현재 B5 씬을 닫거나 과거 버전으로 되돌리지 않았다.

일반 벽 24개를 미터 UV 공용 머티리얼 1개로 묶고, 서로 겹치는 내부 면과 동일 평면의 중복 영역을 잘라낸 시각용 메시로 교체했다. 21개 벽에서 접합면 정리가 일어났고, 일반 벽끼리의 동일 방향 공면 사각형 겹침은 0건이다. BoxCollider와 오브젝트 위치·크기는 보존했다. 개별 접합 메시에는 이웃 벽이 덮는 부분을 제거했으므로 열린 접합 모서리가 있을 수 있다. 독립 소품용 닫힌 메시 검사와 목적이 다르다.

회녹색 하단 도장을 밝은 회색으로 바꾸고 상단은 흰색에 가깝게 조정했다. 검은 프레임·얇은 경계선 대비는 남겼다. 기존 머티리얼을 재사용해 총 94개이며 신규 머티리얼은 0개다. 천장/감방/에어록의 Realtime 조명 18개는 RGB (0.80, 0.89, 1.00)의 옅은 청백색으로 바꾸고 발광 커버도 맞췄다. 위험 표시의 적색/황색과 설비 고유 색상은 유지했다.

## 남은 검수

전체 건축 표면 91개에서 큰 축 정렬 삼각형 3,928개를 추가 검사하니 공면 후보가 26쌍 남았다. 일반 벽끼리 검사는 통과했지만 전체 레벨의 모든 깜빡임을 해결했다고 판정하지 않는다. surface_overlap_audit.json에 실제 경로·면적을 기록했다.

우선 확인할 곳은 Connector_Airlock의 Ceiling_CrossLeg/EntryLeg/ExitLeg, 계단 Ceiling_Stair/TopLanding, 냉각조 Pit_Wall 상면과 데크 바닥, 재제작 벽 상면과 뒤집은 천장 상면이다. 위쪽 외부 면의 접촉도 포함되므로 Scene/Game 시점으로 가시성을 나눠 확인해야 한다. 사용자 퇴근 전 마무리 요청으로 추가 메시 수정을 멈추고 다음 작업으로 넘겼다. 천장 방향을 원래대로 되돌리는 방식으로 처리하지 않는다.

같은 카메라의 전후 렌더로 벽·에어록·계단·천장 톤을 확인했다. 전체 Collider 스냅샷과 사용자 천장 Transform 비교는 모두 동일했다. 최종 저장 완료, missing script 0개. 직접 이동하며 모든 접합부를 보는 플레이테스트는 하지 않았다.
''',encoding='utf-8')
# Keep the folder cleanup follow-up and its original importer backup available at home.
F=P/'tmp/ModelFolderCleanup_20261103';FD=P/'Docs/검수/2026-11-03_ModelFolderCleanup'
for name in ['legacy_rig_import_fix.json','final_model_ids.json','final_verification.json','FixUnusedStaticModel.cs','RecheckModels.cs','AS05_original_importer.meta.txt']:
 if (F/name).exists():shutil.copy2(F/name,FD/name)
f=FD/'정리결과.md';s=f.read_text(encoding='utf-8');s+='''

## 재반입 시 노출된 기존 더미 오류

미사용 AS05_PlayerDummy 정적 모델에 Humanoid가 설정되어 Hips 오류가 발생했다. 전체 Assets의 역참조가 0개이고 스킨/인간 본이 없는 정적 원본임을 확인한 뒤 Animation Type을 None으로 수정했다. 원본 파일과 GUID·메시/머티리얼/Transform 내부 ID·꼭짓점·삼각형은 유지했다. 미사용 Animator/Avatar와 ImportLog 서브에셋만 제거됐다. 실제 사용 V0.2·V0.3 Humanoid 리그와 Controller는 유지했고 V0.3 Avatar 정상도 확인했다. 53개 모델의 실제 geometry/reference ID를 다시 검증했고 성공적인 재반입 이후 Console 오류/경고는 0건이었다. 원래 .meta와 수정 기록을 보관했다.
''';f.write_text(s,encoding='utf-8')
for f,old,new in [(P/'Unity/README.md','V0.21','V0.22'),(P/'Docs/이어하기_2026-10-26.md','V0.16','V0.17')]:
 s=f.read_text(encoding='utf-8-sig').replace(old,new,1);i=s.index('\n');s=s[:i]+'''

## 2026-11-03 퇴근 전 저장 및 다음 시작점

최신 이어하기는 `Docs/이어하기_2026-11-03.md`를 먼저 읽는다. B5 일반 벽 24개를 공용 PBR 재질 1개로 정리하고 겹친 일반 벽의 접합면을 잘랐다. 흰색·회색·검은색 대비와 천장 조명 18개의 옅은 청백색을 적용했다. 사용자가 뒤집은 천장 Transform과 Collider는 유지했다. 전체 표면 추가 검사에서 천장·데크 접합 후보 26쌍이 남아 다음 검수 대상으로 기록했다. 상세는 `Docs/검수/2026-11-03_B5_Clinical_Tone/검수결과.md`를 따른다.

시작 감방을 유리 돔 관찰 포드와 배식구로 바꾸는 구상은 **레퍼런스만 제작**했다. 실제 돔 모델과 탈출 기능은 만들지 않았다. 이미지는 `Docs/Reference/GlassObservationPod_Concept.png`에 있다.
'''+s[i:];f.write_text(s,encoding='utf-8')
(P/'Docs/이어하기_2026-11-03.md').write_text('''# After Seconds — 2026-11-03 이어하기 V0.01

작성자 송예찬 · 학원 PC에서 퇴근 전 저장한 상태

## 시작 순서

1. 프로젝트 AGENTS.md·CLAUDE.md와 이 문서를 읽는다.
2. Unity는 `Unity/After_Seconds_Build_V0.01`, 버전 6000.4.0f1 / URP 17.4.0을 유지한다.
3. `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Isolation.unity`를 열어 현재 모습부터 본다. 사용자가 천장을 180도 뒤집어 패턴이 보이게 한 상태를 유지한다.
4. `Docs/검수/2026-11-03_B5_Clinical_Tone/surface_overlap_audit.json`의 남은 접합부를 Scene/Game 시점으로 확인한다. 일반 벽끼리는 정리했지만 전체 표면 후보 26쌍은 남아 있다.

## 오늘 완료한 것

- B5~1F의 6개 층 초안과 환경·프랍 반입 상태를 보존했다. VARCO 추가 설비 6종은 10개, Batch02 20종은 60개 시각 인스턴스로 배치돼 있다.
- 기존 환경·프랍 8종의 손상 감량 메시를 원본에서 복구했다. 건축 벽·관찰창·바닥·천장 6종은 정확한 모듈로 재제작해 B5 54개 인스턴스에 적용했다. 관찰창 유리와 창 뒤 얕은 외형도 분리했다.
- 모델 폴더를 Player/Enemy/Props/Environment로 정리했다. Props·Environment는 층별 및 Common, 그 아래 Materials·Textures만 둔다. 모델·프리팹·메시는 층 폴더에 바로 둔다. VARCO/Batch02/Models/Prefabs 같은 중간 폴더를 다시 만들지 않는다.
- 414개 파일 이동 시 대상 443개 GUID, 6개 씬 참조, 53개 FBX 내부 ID, 40개 프리팹을 검증했다. 출처·반입 기록은 06.Data/AssetSources다. 이동표는 Docs/검수/2026-11-03_ModelFolderCleanup/move_plan.json이다.
- 오래된 미사용 AS05_PlayerDummy의 잘못된 Humanoid 설정만 None으로 수정했다. Hips가 없는 정적 원본이며 역참조 0개였다. 실제 V0.2/V0.3 리그와 Animator는 보존했다. 재반입 후 Console 오류·경고 0건을 확인했다.
- B5 일반 벽 24개에 공용 PBR 머티리얼 1개를 사용한다. BaseColor/Normal/Mask 3장, Mask R=Metallic/G=AO/A=Smoothness, 2m×4m 미터 UV다. 벽별 머티리얼 복제는 하지 않았다. 전체 모델 관련 머티리얼은 94개로 유지했다.
- 일반 벽 21개에서 내부/동일 평면 접합을 정리했다. 기존 Collider와 위치/크기는 그대로다. 접합용 렌더 메시의 열린 내부 경계는 이웃 면이 덮는 구조다.
- 감옥 같은 회녹색 띠를 줄이고 흰색·회색·검은 프레임 대비로 바꿨다. 천장/감방/에어록 실시간 조명 18개는 옅은 청백색이다. 경고 색과 설비 고유 색은 유지했다.
- 사용자가 직접 수정한 천장 방향과 현재 벽 위치를 보존해 저장했다. 게임 코드와 Collider를 이번 톤 작업에서 바꾸지 않았다.

## 바로 이어갈 미완료 작업

- **깜빡임 잔여 검사:** 전체 건축 표면 공면 후보 26쌍. 에어록 천장 3개, 계단 천장/랜딩, 냉각조 벽 상면/데크, 뒤집은 천장과 벽 상면이 대상이다. 외부 상면의 보이지 않는 접촉도 섞여 있으므로 위치를 보고 판단한다. 천장을 원복하지 않는다.
- B5 임상 연구시설 톤을 사람이 실제 이동하며 확인한다. 지금은 고정 카메라 전후 렌더와 메시/참조 검사까지 했다.
- 다른 층 일반 벽의 텍스처·톤은 아직 확장하지 않았다. 현재 B5 기준으로 사용자 확인 후 진행한다.
- 미터 UV는 편집 시점에 구운 값이다. 이후 벽 Transform을 바꾸면 UV/접합 메시를 재계산한다. 과거 검수 스크립트 경로를 그대로 실행하면 옛 폴더가 생길 수 있으니 새 경로표를 적용한다.

## 유리 돔과 배식구 구상 — 모델 미제작

사용자는 처음 갇힌 공간을 네모 감방보다 실험체를 관찰하기 쉬운 유리 돔으로 바꾸고 싶어 한다. 배식구를 탈출의 계기로 쓰는 구상도 나왔다. 현재 결정은 **참고 이미지 한 장을 만들어 생각해 보는 것까지**다. 사용자가 Blender에서 형태를 만들고 머티리얼 설정을 도움받을 가능성이 있다.

참조: [유리 관찰 포드](Reference/GlassObservationPod_Concept.png). 투명 원통/반구, 흰색 받침, 검은 얇은 프레임, 옅은 청백색 조명과 작은 배식구가 있는 기획 이미지다. 치수·실제 개구부·탈출 수단·Collider는 미확정이다. 배식구로 기어 나가는 기능이나 새로운 게임 규칙을 확정하지 않는다. 사용자 요청 없이 돔 모델이나 탈출 코드를 먼저 구현하지 않는다.

공용 투척 소품 후보는 상자·시료 용기·물류 용기, 추가 후보는 빈 금속통·손전등·소형 공구 케이스다. 모델 존재와 실제 투척 기능 구현은 구분한다.

## 확인 자료

- Docs/검수/2026-11-03_B5_Clinical_Tone/검수결과.md
- Docs/검수/2026-11-03_WallTexture_Pilot/검수결과.md
- Docs/검수/2026-11-03_ModelFolderCleanup/정리결과.md
- Docs/검수/2026-11-03_Architecture_Rebuild/검수결과.md
- Docs/검수/2026-11-03_VARCO_V002_Batch02/반입_적용결과.md

블로그는 별도 저장소 `02.Kasil_DevLog`의 오늘 프로젝트 일일개발일지와 261103_NCAI_Unity_실습 데일리로그를 갱신한다. 게시글은 짧은 메모 말투를 사용하고 두 프로젝트의 코드를 섞지 않는다.
''',encoding='utf-8')
f=P/'AGENTS.md';s=f.read_text(encoding='utf-8');s+='\n집에서 이어갈 때는 먼저 [2026-11-03 이어하기](Docs/이어하기_2026-11-03.md)를 읽습니다. 사용자가 뒤집은 천장 방향과 유리 돔은 참고 이미지까지만 만든 상태라는 점을 유지합니다.\n';f.write_text(s.replace('V0.05','V0.06',1),encoding='utf-8')
shutil.copy2(P/'Docs/Reference/GlassObservationPod_Concept.png',D/'GlassObservationPod_Concept.png')
print('Saved today handoff, clinical QA and reference')
