from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-13_1F_WildernessDetail';E=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/1F'
read=lambda p:json.loads((O/p).read_text(encoding='utf8'))
c,p,w,protected=map(read,['final_check.json','play.json','walk.json','protected_check.json'])
models=json.loads((H/'models.json').read_text())+json.loads((H/'approach_models.json').read_text())
assert c['saved'] and not c['playing'] and not c['runInBackground'] and not c['unexpectedTransformChanges']
assert c['transforms']==4790 and c['colliders']==165 and c['cameraFar']==4500
assert not c['shaderMessages'] and not any(c[k] for k in ['missingMeshes','missingMaterials','missingScripts','consoleErrors','consoleWarnings'])
assert all(q['heightsUnchanged'] for q in c['terrainGround'])
assert p['complete'] and p['views']==3 and p['mainCameraFar']==4500 and p['framesAdvanced']>0 and not p['errors']
assert not w['widthIssues'] and all(q['passed'] for q in w['results'])
assert not protected['changed'] and all(q['unchanged'] for q in protected['acceptedSkyAndBloom'])
size=sum((E/(m['name']+'.fbx')).stat().st_size for m in models)/1048576
review=f'''# 1F 황야 디테일 보수 검수 V0.01

작성자 송예찬 · 2026-11-13

사용자가 수용한 석양·태양·빛번짐을 그대로 보존하고, 남은 황야의 바위·식생·지면·원경을 보수했다. 출구와 황야 사이의 예전 식생도 함께 정리했다.

[전후 비교](review.html) · [황야](after/Wilderness.jpg) · [지면과 식생](after/Ground.jpg) · [먼 풍경](after/Vista.jpg)

- 바위3형태: 풍화된 둥근 어깨·불규칙한 면과 층리·광물/먼지 표면을 적용했다. 기존의 큰 삼각 면을 줄였다.
- 마른 풀4형태·관목3형태·작은 돌 군집2형태를 제작했다. 곡선 잎·가느다란 이삭·분기 가지·작은 잎을 구분했다.
- 기존 황야643배치의 메시를 교체하고 자갈/풀465배치를 추가했다. 공장 서쪽 접근부27청크·306포기의 예전 식생도 보수했다. 경사 정렬 대상1,057배치 중 기존531Transform의 회전값이 달라졌다. 기존 위치·스케일·활성·엔딩 위치 변경0.
- 마른 흙·자갈·밝은 먼지·다져진 흙4개 TerrainLayer를 추가해 서쪽 지면에 불규칙하게 섞었다. 원래 이미지 파일은 재사용했고 픽셀은 수정하지 않았다. 공장과 보행 지형의 높이 데이터는 동일하다.
- 서쪽 원경 지형에 겹친 낮은 구릉을 추가했다. 기존 햇빛·안개·환경광은 유지했다.
- 실제 카메라를 제어하는 `Camera/CM_Player_1st`의 렌즈 Far Clip이1,000m여서 Main Camera 설정을 다시 덮어쓰고 있었다. 1F 씬의 해당 렌즈만4,500m로 맞췄고 씬 재개방과 Play에서 유지되는 것을 확인했다. FOV·시점 제어·공유 카메라 프리팹은 보존했다.

새 FBX39개는 모두3단계 LOD이며 합계{size:.2f}MiB다. 새 재질7개와1F 전용 자연 표면 셰이더를 사용한다. 기존 FW/AE 원본 모델과 GUID는 유지하고 씬의 메시 참조를 새 모델로 연결했다. 바위51개의 기존 MeshCollider는 새 LOD1 형상에 맞췄다. 전체 Collider165개 유지, 새 식생/자갈 Collider0. 반사8개를 갱신했다.

검수 결과:

- 출구부터 황야585m 왕복 CharacterController 이동2/2 통과. 경로1,171지점과 폭879표본에서 막힘0. Player 오브젝트를 이동시키지 않고 동일 치수의 임시 Controller를 사용했다.
- 실제 Play3시점·{p['framesAdvanced']}프레임 진행·새 경고/오류0. Main Camera Far Clip4,500m 확인. 프레임 중앙값{p['medianMs']:.2f}ms·95백분위{p['p95Ms']:.2f}ms는 짧은 에디터 관측이며 빌드 성능 수치는 아니다.
- Transform2,108→4,790. 허용한 황야 식생의 경사 회전 외 기존 Transform 변경0. 메시/재질/스크립트 누락0·셰이더/콘솔 오류0.
- 게임 코드·프리팹·Animator·입력·다른 씬·설정{protected['files']}개 해시 일치. 승인된 하늘 셰이더/재질과.meta·Bloom 프로필의 바이트 일치. 조명·안개·환경광 동일.

현재 저장된1F 편집 상태, `WildernessEnding` 선택. 스카이박스는 사용자 수용 상태다. 승강기 운행·문·엔딩 연출 스크립트는 추가하지 않았다. 커밋·push 미실시. 백업은 `%LOCALAPPDATA%/Temp/AfterSeconds_WildernessDetail_20261113/before`이며 첫 Apply와 이전 전체 제작기는 현재 씬에 재실행하지 않는다.

[제작 원본과 조절 항목](../../../SourceAssets/F1_WildernessDetail/README.md)

변경 기록: V0.01 — 수용한 하늘 보존·황야/접근부 보수·이동/보존/Play 검수. 송예찬.
'''
(O/'Review.md').write_text(review,encoding='utf8')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>1F 황야 디테일 보수 V0.01</title><style>body{margin:0;background:#211c20;color:#eee1d6;font:16px/1.7 system-ui}main{max-width:1500px;margin:auto;padding:32px}section{margin:40px 0}h1{font-size:30px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{width:100%;display:block}a{color:#efb58c}figure{margin:0}figcaption{margin-bottom:6px;color:#cbb9ad}@media(max-width:850px){.pair{grid-template-columns:1fr}}</style><main><h1>1F 황야 디테일 보수 V0.01</h1><p>수용한 석양을 유지하고 바위의 형태와 표면, 마른 식생, 지면 분포와 겹친 원경을 보수했습니다.</p><p>송예찬 · 2026-11-13 · <a href="Review.md">검수 기록</a></p>'''
for key,title in [('Wilderness','황야 입구'),('Exit','공장 출구'),('Ground','근접 식생과 지면'),('MidRoute','중간 보행 구간'),('Vista','먼 풍경'),('Factory','공장 내부 보존'),('Lift','승강기 보존')]:
 html+=f'<section><h2>{title}</h2><div class="pair">'
 for phase,label in [('before','보수 전'),('after','황야 디테일 보수')]:
  assert (O/phase/(key+'.jpg')).exists();html+=f'<figure><figcaption>{label}</figcaption><a href="{phase}/{key}.jpg"><img src="{phase}/{key}.jpg" alt="{title} {label}"></a></figure>'
 html+='</div></section>'
html+='</main>';(O/'review.html').write_text(html,encoding='utf8')
intro=f'2026-11-13 최신 황야 보수: 사용자가 수용한 석양/태양/Bloom을 보존하고 바위·식생12형태, 출구 접근부27청크·306포기, 지면4층과 겹친 원경을 보수했다. 기존643배치 메시 교체·465추가, 기존531식생 경사 회전 외 Transform 변경0. 총4,790Transform·Collider165. 585m왕복2/2·폭879표본 막힘0·실제Play3시점{p["framesAdvanced"]}프레임 새 경고/오류0. 보호215파일·승인 하늘/Bloom 보존. 1F Cinemachine 렌즈 거리4,500m로 원경 표시 고정. 저장된1F 편집·WildernessEnding 선택, 커밋/push 미실시. 첫 Apply/Before와 이전 제작기 일괄 재실행 금지. 작성자 송예찬. '
for file,old,new,prefix in [('AGENTS.md','V1.14','V1.15',''),('CLAUDE.md','V1.14','V1.15',''),('Docs/이어하기_2026-11-12.md','V0.13','V0.14','../')]:
 f=R/file;s=f.read_text(encoding='utf-8-sig');title,rest=s.split('\n',1);assert old in title;reviewpath=('Review/' if prefix else 'Docs/Review/')+'2026-11-13_1F_WildernessDetail/'
 f.write_text(title.replace(old,new)+'\n\n'+intro+f'[검수]({reviewpath}Review.md) · [전후 화면]({reviewpath}review.html) · [제작 원본]({prefix}SourceAssets/F1_WildernessDetail/README.md).\n\n이전 단계 기록:\n'+rest+f'\n- {new} (2026-11-13): 수용한 하늘 보존·황야/접근부 보수·이동/보존/Play 검수. 송예찬.\n',encoding='utf8')
f=H/'README.md';s=f.read_text(encoding='utf8').replace('V0.01\n','V0.02\n',1);s+='''

최종 파일: `WD_RockA–C`, `WD_GrassA–D`, `WD_ShrubA–C`, `WD_StonePatchA–B`와 서쪽 접근부27청크. 모두3단계 LOD다. 기존 배치의 루트 위치·스케일을 유지하고 메시를 연결했으며, 풀/작은 돌은 지면 법선에 맞춰 회전했다. 바위 Collider51개는 새 LOD1 메시를 사용한다. 신규 자갈·풀465배치에는 Collider가 없다.

표면은 `WDNaturalLit.shader`와 `WDNaturalSurface.hlsl`, 재질은 `Materials/WD_M_*`다. 표준 조명 패스는 Unity URP17.4.0에서 파생했으며 [Unity Companion License](../F1_AbandonedCamouflage/Unity-URP-LICENSE.md)를 따른다. 기존 AE 공장 셰이더와 아이비를 변경하지 않는다. `WD_Earth`, `WD_Gravel`, `WD_PaleDust`, `WD_CompactedSoil` TerrainLayer는 기존 이미지의 타일/법선/색 범위를 다르게 사용한다.

카메라 표시 거리는 Main Camera만 바꾸면 Cinemachine이 덮어쓴다. 1F 씬의 `Camera/CM_Player_1st` → Lens → Far Clip Plane4,500m가 실제 제어값이며 FOV는 유지했다. 공용 카메라 프리팹에는 적용하지 않았다.

`Apply.cs`는 최초643배치 교체/465배치 추가·지면·원경, `Refine.cs`는 접근부27청크와 경사 정렬, `CameraRig.Fix`는1F 카메라 거리의 최종 보정 이력이다. 첫 Apply/Inventory/Before/report를 재실행하지 않는다. [검수](../../Docs/Review/2026-11-13_1F_WildernessDetail/Review.md) · [전후 화면](../../Docs/Review/2026-11-13_1F_WildernessDetail/review.html).

변경 기록: V0.02 — 최종 에셋·조절점·카메라 거리·검수 연결. 송예찬.
''';f.write_text(s,encoding='utf8')
print('WILDERNESS_REPORT_READY',len(models),round(size,2),p['framesAdvanced'])
