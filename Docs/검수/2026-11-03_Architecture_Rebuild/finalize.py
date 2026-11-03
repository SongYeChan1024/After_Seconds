from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).parent;P=R.parent.parent;U=P/'Unity/After_Seconds_Build_V0.01';D=P/'Docs/검수/2026-11-03_Architecture_Rebuild';D.mkdir(parents=True,exist_ok=True);S=P/'SourceAssets/Architecture_Rebuilt';S.mkdir(parents=True,exist_ok=True)
manifest=json.loads((R/'rebuild_manifest.json').read_text());verification=json.loads((R/'export_verification.json').read_text());coverage=json.loads((R/'shell_coverage.json').read_text());guid=[]
for a in manifest:
 model=U/a['modelPath'];a['sha256']=hashlib.sha256(model.read_bytes()).hexdigest();a['status']='Imported and applied to existing B5 prefab instances; saved scene reloaded and collider snapshot preserved';a['qa']='Docs/검수/2026-11-03_Architecture_Rebuild/검수결과.md';f=model.parent.parent/'source_manifest.json';f.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8');old=(U/a['prefabPath']).parent.parent/'source_manifest.json';shutil.copy2(old,R/'PrefabBackup'/(a['name']+'_source_manifest.json'));data=json.loads(old.read_text(encoding='utf-8-sig'));data['architecturalRemake20261103']=a;old.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');guid.append({'prefab':a['prefabPath'],'metaPreserved':(U/(a['prefabPath']+'.meta')).read_bytes()==(R/'PrefabBackup'/(a['name']+'.prefab.meta')).read_bytes()})
 for suffix in ['high','retopo']:shutil.copy2(R/(a['name']+'_'+suffix+'.blend'),S/(a['name']+'_'+suffix+'.blend'))
assert all(x['metaPreserved'] for x in guid)
assert all(not any(z[k] for k in ['boundaryEdges','overusedEdges','zeroAreaFaces','strictEdgeTriangleCrossings','nonFiniteUVs']) for v in verification for z in v['objects'])
assert all(not x['unintendedPassThroughRays'] and not x['unexpectedOpaqueWindowHits'] for x in coverage)
(R/'rebuild_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');(R/'guid_preservation.json').write_text(json.dumps(guid,indent=2),encoding='utf-8')
for f in R.iterdir():
 if f.suffix in ['.json','.cs','.py','.png']:shutil.copy2(f,D/f.name)
for folder in ['PrefabBackup','SceneBackup']:shutil.copytree(R/folder,D/folder,dirs_exist_ok=True)
rows=[]
for a in manifest:
 final=sum(o['triangles'] for x in verification if x['floor']==a['name'] for o in x['objects']);rows.append(f"| {a['name']} | {a['highTriangles']:,} | {final:,} | 0 | 0 |")
(D/'검수결과.md').write_text('''# 건축 모듈 재제작·리토폴로지·재적용 검수 V0.01

2026-11-03 · 작성자 송예찬

원본 형상에 남았던 관통 볼트 구멍·찌그러진 외곽·관찰창의 불투명막을 해결하기 위해 콘크리트벽, 금속벽, 문벽, 관찰창벽, 바닥, 천장 6종을 Blender에서 재제작했다. 기존 V0.01 회색 콘크리트·분체 도장 금속·밀폐형 볼트 톤을 따른다. 정확한 건축 외곽이 필요한 부분은 파라미터 모델링으로 만들었으며 VARCO 유료 재생성은 수행하지 않았다.

고해상도 베벨 모델을 먼저 저장하고, 구조 외곽을 보존하면서 베벨·볼트 메시를 감량한 뒤 용접·삼각형 정리·노멀 재계산을 수행했다. 전체 수동 사각형 리토폴로지나 500k VARCO 재생성을 한 것은 아니다. 볼트는 닫힌 구조체 위에 붙고 구멍을 뚫지 않는다. 관찰창은 구멍이 있는 하나의 닫힌 창틀과 별도의 닫힌 유리 메시이며, 유리만 URP 투명 재질이다.

| 에셋 | 고해상도 triangles | 최종 FBX triangles | 열린 경계 | 엄격한 면 관통 |
| --- | ---: | ---: | ---: | ---: |
'''+ '\n'.join(rows)+'''

최종 FBX를 다시 가져와 과다 공유 모서리·퇴화면·UV 비정상 값도 0건 확인했다. 41×41 레이 샘플로 벽/바닥/천장에 의도하지 않은 관통이 없는지 별도 검사했다. 관찰창의 의도된 개구부 459개 샘플에서는 불투명 창틀이 시야를 막지 않았다. 이 검사는 공면 접촉을 포함한 모든 가능한 중첩을 수학적으로 완전 증명하는 검사는 아니다.

## 반입과 적용

- 실제 반입: `Assets/Afrer_Seconds/05.Model/Environment/Architecture_Rebuilt/`의 모델별 FBX, 공유 URP 재질·미세 마모 텍스처, 관찰실 외형 프리팹.
- 편집 가능한 고해상도/감량 Blender 소스: `SourceAssets/Architecture_Rebuilt/`. Unity의 자동 .blend 변환을 피하도록 Assets 밖에 보관했다.
- 기존 6개 VARCO 프리팹 GUID와 원본 파일을 유지했다. 원본 렌더러를 비활성화하고 `RebuiltArchitectureVisual` 하위에 재제작 모델을 연결했다. B5의 해당 54개 기존 인스턴스에 적용된다. 펌프·전기함은 이전 복구본을 유지한다.
- B5 바닥 18개는 시각 하위 오브젝트만 Y +0.002m 보정해 기존 -0.122m 배치와 벽 바닥 0m 사이의 틈을 막았다. 바닥의 방 안쪽 면과 천장의 방 안쪽 면은 연속된 평면이다.
- 관찰창 뒤의 외부 하늘 노출을 막기 위해 관찰실 깊이를 표현하는 얕은 외형 2개를 추가했다. 각각 닫힌 기본 박스 9개, 108 triangles이며 별도 감량이 필요 없는 단순 케이지다. 새 통로·플레이 공간·게임 기능은 없다. 프리팹은 `Prefabs/ObservationRecess_VisualOnly.prefab`이다.
- 기존 Collider 전체 스냅샷 동일, 신규 Collider 0개. 게임 코드·Animator를 수정하지 않았다. 기존 추가 프랍 20종/60개 배치와 머티리얼 참조도 정상이다.
- 저장한 6개 층을 다시 열어 missing script·참조 문제·기존 프랍과 충돌체 겹침이 없음을 확인했다. 검수는 자동 메시 검사와 렌더 이미지 기준이며 직접 조작하는 플레이테스트는 하지 않았다. 기존 오클루전 데이터는 다시 베이크하지 않았다.

## 이미지와 재현 자료

- [B5 적용 화면](B5_scene_applied.png)
- [투명 관찰창과 창 뒤 외형](ObservationWindow_scene_applied.png)
- [수정 전후 6종](comparison.png)

build_architecture.py → verify_fbx.py / check_shell_coverage.py → ImportApply.cs → FinishScene.cs → VerifyArchitecture.cs 순서로 작성했다. ImportApply.cs 재실행 시 바닥 씬 보정은 FinishScene.cs로 다시 적용한다. 변경 전 프리팹·B5 씬과 메타 백업을 동봉했다.
''',encoding='utf-8')
for f,oldv,newv in [(P/'Docs/이어하기_2026-10-26.md','V0.13','V0.14'),(P/'Unity/README.md','V0.18','V0.19')]:
 s=f.read_text(encoding='utf-8-sig').replace(oldv,newv,1);i=s.index('\n');s=s[:i]+'''

## 2026-11-03 건축 모듈 재제작·재적용 완료

남아 있던 원본 형상 문제를 해결하려고 벽·관찰창·바닥·천장 6종을 Blender에서 재제작하고 고해상도 모델→감량·토폴로지 정리→최종 FBX 재검사→Unity 반입을 완료했다. B5 기존 54개 인스턴스에 적용했으며 관통 볼트 구멍·비뚤어진 외곽·관찰창의 불투명막을 제거했다. 관찰창 뒤에는 얕은 관찰실 외형 2개를 추가했다. 바닥 18개는 시각 오브젝트만 +2mm 보정해 경계 틈을 막았다. 기존 Collider와 게임 코드는 유지했다.

반입 폴더는 `05.Model/Environment/Architecture_Rebuilt`, Blender 원본은 저장소의 `SourceAssets/Architecture_Rebuilt`다. 검수 자료는 `Docs/검수/2026-11-03_Architecture_Rebuild/검수결과.md`에 있다. 아래 이전 기록의 '원본 형상 재제작 필요' 항목은 이번 결과로 해결했다. 유료 VARCO 재생성은 사용하지 않았다.
'''+s[i:];f.write_text(s,encoding='utf-8')
print(json.dumps({'models':len(manifest),'metaPreserved':all(x['metaPreserved'] for x in guid),'topologyPass':True,'shellCoveragePass':True}))
