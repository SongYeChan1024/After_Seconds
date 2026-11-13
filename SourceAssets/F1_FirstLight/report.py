from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-13_1F_FirstLight'
read=lambda p:json.loads((O/p).read_text(encoding='utf8'))
c,p,post,protected=map(read,['final_check.json','play.json','post_check.json','protected_check.json'])
assert c['saved'] and not c['playing'] and not c['runInBackground']
assert c['beforeTransforms']==2107 and c['transforms']==2108 and c['colliders']==165 and not c['unexpectedTransformChanges']
assert not any(c[k] for k in ['shaderErrors','missingMeshes','missingMaterials','missingScripts'])
assert p['complete'] and p['views']==3 and p['framesAdvanced']>0 and not p['errors']
assert post['effectiveActive'] and post['effectiveIntensity']==.7 and post['consoleErrors']==0 and post['consoleWarnings']==0
assert not protected['changed']
report=f'''# 1F 태양과 빛번짐 보수 검수 V0.01

작성자 송예찬 · 2026-11-13

태양의 지름을 기존의 약2.9배로 키우고 밝은 중심부, 가까운 광륜, 넓은 주황빛 산란을 겹쳐 출구 너머 햇빛의 존재감을 보강했다. 1F 전용 Bloom으로 밝은 부분의 빛번짐을 더했다. 석양의 위치·기존 조명·안개·공장과 황야 배치는 유지했다.

[전후 화면](review.html) · [황야](after/Wilderness.jpg) · [출구](after/Exit.jpg)

| 조절 항목 | 최종 값 |
| --- | --- |
| 태양 반지름 `_SunRadius` | 0.009 → 0.026 |
| 태양 HDR 색 `_SunColor` | (7.5, 5.2, 2.8) |
| 가까운 광륜 `_CoronaStrength` | 1.2 |
| 넓은 광륜 강도 / 폭 | 0.6 / 0.16 |
| Bloom Threshold / Intensity / Scatter | 1.2 / 0.7 / 0.78 |

기존 `Environment/1F/FS_SunsetSky.shader`와 `Materials/FS_SunsetSky.mat`의 GUID를 보존했다. 새 프로필은 `06.Data/Rendering/1F/FL_FirstLightBloom.asset`이고 Bloom 한 효과만 포함한다. 씬의 `1F_AbandonedFactory/Lighting/FirstLightBloom`에 연결했다. Default 레이어0·Global·Priority10·Weight1이며 기존 Main Camera의 Volume Mask1·후처리·HDR 설정에서 실제 적용을 확인했다. 기존 PC_RPAsset·PC_Renderer·카메라 설정은 변경하지 않았다.

출구·황야·생산동·외벽·승강기 화면을 확인했다. 태양과 광륜을 강조하면서 길과 바위 윤곽, 실내 구조가 읽히는 것을 확인했다. 반사8개는 새 하늘로 다시 구웠다. Bloom 자체는 화면 후처리이며 반사 베이크에 포함되지 않는다.

- 기존2,107 Transform의 위치·회전·스케일·활성 변경0. Volume1개 추가로2,108. Collider165개 유지.
- 셰이더 오류·누락 메시/재질/스크립트0. 콘솔 경고/오류0.
- 게임 코드·프리팹·Animator·입력·다른 씬·설정 등 보호{protected['files']}파일 해시 일치. 하늘 셰이더/재질.meta 보존.
- 실제 Play에서 후처리를 켠 임시 카메라3시점·{p['framesAdvanced']}프레임 진행·새 경고/오류0. 프레임 중앙값{p['medianMs']:.2f}ms, 95백분위{p['p95Ms']:.2f}ms는 짧은 에디터 관측이다.

정적인 햇빛 표현이다. 출구를 넘을 때 화면이 밝아졌다 적응하는 시간 연출, 엔딩 기능은 추가하지 않았다. Player/Input·승강기 가동부·게임 코드는 유지했다. 구조 변경이 없어 통행 검사를 반복하지 않았다. 검수 카메라는 기존 검수와 같은 시점/FOV와 far8500을 사용했고, 실제 Main Camera의 far1000은 유지했다.

저장된1F 편집 상태이며 석양 재질을 선택했다. 커밋·push 미실시. 백업은 `%LOCALAPPDATA%/Temp/AfterSeconds_FirstLight_20261113/before`. 최신 제작 원본은 [F1_FirstLight](../../../SourceAssets/F1_FirstLight/README.md)이며 이전 전체 제작기와 첫 Apply는 재실행하지 않는다.

변경 기록: V0.01 — 태양·광륜·Bloom·반사 보수와 보존/Play 검수. 송예찬.
'''
(O/'Review.md').write_text(report,encoding='utf8')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>1F 태양과 빛번짐 V0.01</title><style>body{margin:0;background:#211c20;color:#eee1d6;font:16px/1.7 system-ui}main{max-width:1500px;margin:auto;padding:32px}section{margin:40px 0}h1{font-size:30px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{width:100%;display:block}a{color:#efb58c}figure{margin:0}figcaption{margin-bottom:6px;color:#cbb9ad}@media(max-width:850px){.pair{grid-template-columns:1fr}}</style><main><h1>1F 태양과 빛번짐 V0.01</h1><p>태양 지름 약2.9배, 밝은 중심과 겹친 광륜, 부드러운 Bloom. 기존 석양의 색과 황야의 길을 유지했습니다.</p><p>송예찬 · 2026-11-13 · <a href="Review.md">검수 기록</a></p>'''
for key,title in [('Wilderness','황야에서 마주하는 태양'),('Exit','출구 너머의 햇빛'),('Sky','태양과 광륜'),('Factory','공장 실내'),('Facade','외벽'),('Lift','승강기 내부')]:
    html+=f'<section><h2>{title}</h2><div class="pair">'
    for phase,label in [('before','보수 전'),('after','태양·광륜·Bloom 보수')]:
        assert (O/phase/(key+'.jpg')).exists()
        html+=f'<figure><figcaption>{label}</figcaption><a href="{phase}/{key}.jpg"><img src="{phase}/{key}.jpg" alt="{title} {label}"></a></figure>'
    html+='</div></section>'
html+='</main>';(O/'review.html').write_text(html,encoding='utf8')
intro=f'2026-11-13 최신 태양 보수: 태양 지름 약2.9배·가까운 광륜·넓은 대기 산란과1F 전용 Bloom을 반영하고 반사8개를 갱신했다. 기존2,107Transform 변경0·Volume1개 추가→2,108·Collider165유지. 기존 조명/안개/카메라 보존, 실제Play3시점{p["framesAdvanced"]}프레임·새 경고/오류0. 보호{protected["files"]}파일 해시와 하늘2.meta 일치. 저장된1F 편집, FS_SunsetSky 재질 선택. 정적 표현이며 눈 적응/엔딩 기능은 미구현. 커밋/push 미실시. 최신 제작 원본은 F1_FirstLight이며 첫 Apply/Before와 이전 전체 제작기는 재실행하지 않는다. 작성자 송예찬. '
for file,old,new,prefix in [('AGENTS.md','V1.13','V1.14',''),('CLAUDE.md','V1.13','V1.14',''),('Docs/이어하기_2026-11-12.md','V0.12','V0.13','../')]:
    f=R/file;s=f.read_text(encoding='utf-8-sig');title,rest=s.split('\n',1);assert old in title
    review=('Review/' if prefix else 'Docs/Review/')+'2026-11-13_1F_FirstLight/'
    f.write_text(title.replace(old,new)+'\n\n'+intro+f'[검수]({review}Review.md) · [전후 화면]({review}review.html) · [제작 원본]({prefix}SourceAssets/F1_FirstLight/README.md).\n\n이전 단계 기록:\n'+rest+f'\n- {new} (2026-11-13): 1F 태양 확대·광륜·Bloom·반사와 보존/Play 검수. 송예찬.\n',encoding='utf8')
f=H/'README.md';s=f.read_text(encoding='utf8').replace('V0.01\n','V0.02\n',1)
s+='''

최종 태양 반지름0.026, HDR 색(7.5,5.2,2.8), 가까운 광륜1.2, 넓은 광륜0.6/폭0.16이다. `FS_SunsetSky.mat`에서 크기와 광륜을 조절한다. `FL_FirstLightBloom.asset`에서 Threshold1.2·Intensity0.7·Scatter0.78을 조절한다. Bloom 전용 Global Volume이며 원래1F 카메라의 HDR/후처리/Default 레이어를 이용한다. 기존 공용 URP 설정은 변경하지 않았다.

[검수 결과](../../Docs/Review/2026-11-13_1F_FirstLight/Review.md) · [전후 화면](../../Docs/Review/2026-11-13_1F_FirstLight/review.html). 기존 셰이더 최신 원본은 이 폴더의 `FS_SunsetSky.shader`이며 이전 F1_SunsetSky 원본은 최초 제작 당시 자료다.

변경 기록: V0.02 — 최종 조절값·프로필·검수·최신 원본 안내. 송예찬.
''';f.write_text(s,encoding='utf8')
f=H.parent/'F1_SunsetSky/README.md';s=f.read_text(encoding='utf8');title,rest=s.split('\n',1);assert 'V0.02' in title
f.write_text(title.replace('V0.02','V0.03')+'\n\n최신 태양 확대·광륜·Bloom 보수 원본은 [F1_FirstLight](../F1_FirstLight/README.md)다. 아래 내용과 이 폴더의 셰이더는 최초 석양 제작 당시 기록이며 최신 에셋에 덮어쓰지 않는다.\n'+rest+'\n변경 기록: V0.03 — 후속 태양/Bloom 제작 원본 연결. 송예찬.\n',encoding='utf8')
print('FIRSTLIGHT_REPORT_READY',p['framesAdvanced'])
