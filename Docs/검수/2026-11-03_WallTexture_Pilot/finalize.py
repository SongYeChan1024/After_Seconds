from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).parent;P=R.parent.parent;D=P/'Docs/검수/2026-11-03_WallTexture_Pilot';D.mkdir(parents=True,exist_ok=True);A=P/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Shared/FacilityWall';facts=json.loads((R/'application_facts.json').read_text());verify=json.loads((R/'verification.json').read_text());spec=json.loads((R/'texture_spec.json').read_text())
manifest={'name':'FacilityWall_PaintedConcrete','author':'SongYeChan1024','generation':'Deterministic procedural PBR texture set generated with Blender and NumPy','sourceScript':'Docs/검수/2026-11-03_WallTexture_Pilot/create_wall_maps.py','scope':'B5 Room01_Isolation general walls only','spec':spec,'application':facts,'verification':verify,'files':{f.relative_to(A).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in A.rglob('*') if f.is_file() and f.suffix in ['.png','.mat','.asset']}}
(A/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for f in R.iterdir():
 if f.suffix in ['.json','.cs','.py','.png']:shutil.copy2(f,D/f.name)
shutil.copytree(R/'Backup',D/'Backup',dirs_exist_ok=True)
(D/'검수결과.md').write_text('''# B5 일반 벽 텍스처 매핑 시범 적용 V0.01

2026-11-03 · 작성자 송예찬

B5 Room01_Isolation의 일반 벽 7개에 공용 URP/Lit 머티리얼 **1개만 신규 생성**해 적용했다. 기존 재질을 복제하거나 벽별 머티리얼 인스턴스를 만들지 않았다. 다른 층과 나머지 벽은 이번 시범 범위에 포함하지 않았다.

상단은 밝은 회색 도장 콘크리트, 하단 1.15m는 회녹색 보호 도장으로 구성했다. 미세 기공·약한 도장 마모·얕은 거푸집 이음선을 절차적으로 생성하고 동일 높이 정보로 노멀과 표면 거칠기를 만들었다. 첫 렌더의 강한 하단 마모는 줄여 기존 시설 톤에 맞췄다.

- 머티리얼: `05.Model/Environment/Shared/FacilityWall/Materials/FacilityWall_PaintedConcrete.mat`.
- 텍스처: 1024×2048 BaseColor·Normal·Mask, 총 3개. Mask R=Metallic, G=AO, A=Smoothness이며 같은 한 장을 URP MetallicGlossMap/OcclusionMap에서 공유한다.
- 매핑: 가로 2m × 세로 4m, 약 512px/m. U 반복, V Clamp. 벽의 현재 월드 치수에 따라 UV만 다시 만들어 길이가 다른 벽에서도 질감 크기와 도장 높이를 맞췄다. 별도 커스텀 셰이더·MaterialPropertyBlock은 사용하지 않았다.
- 벽별 미터 UV 메시 7개를 저장했다. 원본 꼭짓점·삼각형·노멀은 그대로이고 UV·탄젠트만 달라졌다. BoxCollider와 위치·크기는 이번 적용에서 변경하지 않았다.
- 현재 UV는 편집 시점의 월드 위치를 기준으로 굽는다. 이후 벽의 위치·회전·크기를 변경하면 UV를 다시 계산해야 한다. 이는 실시간 월드 트라이플래너 셰이더가 아니다.

## 검증

저장한 B5 씬을 다시 열어 7개 벽이 하나의 동일 머티리얼을 참조하고, 세 텍스처 참조와 UV가 정상이며 missing script가 없음을 확인했다. 적용 직전/직후 전체 Collider 스냅샷은 동일했다. 재열기 후 대상 7개 벽 Collider도 그대로다.

작업 중 별도 좌표 편집이 확인된 에어록 `Wall_East_Outer`(Z -2→-1.875), `Wall_West_Exit`(Z -3→-2.98)는 시범 적용 대상 밖이며 현재 좌표를 유지했다. 이 편집은 일반 벽 UV 작업에서 수행한 변경이 아니다. 최초 디스크 씬과 적용 전 현재 편집 상태를 Backup에 보관했다.

같은 카메라·조명에서 전후 렌더 2쌍을 확인했다. 비교 렌더에서만 플레이어 렌더러를 잠시 숨긴 뒤 원래 상태로 복원했다. 캐릭터·게임 로직·조명은 변경하지 않았고 이번 검증은 직접 이동하는 플레이테스트를 포함하지 않는다.

[수정 전후 비교](comparison.png) · [일반 벽](NorthWall_after.png) · [감방 안쪽 벽](CellWall_after.png)
''',encoding='utf-8')
for f,old,new in [(P/'Unity/README.md','V0.19','V0.20'),(P/'Docs/이어하기_2026-10-26.md','V0.14','V0.15')]:
 s=f.read_text(encoding='utf-8-sig').replace(old,new,1);i=s.index('\n');s=s[:i]+'''

## 2026-11-03 B5 일반 벽 텍스처 시범 적용

B5 격리실 일반 벽 7개에 신규 공용 머티리얼 1개와 PBR 텍스처 3개를 적용했다. 상단 도장 콘크리트·하단 회녹색 보호 도장을 미터 기준 UV로 매핑했다. 위치·형상·대상 벽의 Collider는 유지했고, 다른 층은 아직 확장하지 않았다. 반입 위치는 `05.Model/Environment/Shared/FacilityWall`, 전후 비교와 재현 스크립트는 `Docs/검수/2026-11-03_WallTexture_Pilot/검수결과.md`에 있다. 벽을 이동·크기 변경하면 해당 UV 재계산이 필요하다.
'''+s[i:];f.write_text(s,encoding='utf-8')
print(json.dumps({'newMaterials':facts['newMaterials'],'walls':verify['walls'],'uniqueMaterials':verify['uniqueWallMaterials'],'textures':verify['textureAssets'],'pilotCollidersPreserved':verify['pilotWallCollidersPreserved']}))
