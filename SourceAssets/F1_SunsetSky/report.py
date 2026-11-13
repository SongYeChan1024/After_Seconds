from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-13_1F_SunsetSky'
read=lambda n:json.loads((O/n).read_text(encoding='utf8'))
c=read('final_check.json');p=read('play.json');b=read('before_lighting.json');a=read('after_lighting.json')
assert c['saved'] and not c['playing'] and not c['runInBackground'] and not c['unexpectedTransformChanges'] and c['transforms']==2107
assert not c['shaderErrors'] and not c['missingMeshes'] and not c['missingMaterials'] and not p['errors'] and p['complete']
before={q['path']:q for q in b['lights']};changed=[q['path'] for q in a['lights'] if q!=before[q['path']]]
assert len(changed)==8 and all(x.endswith('_DiffuseSkyBounce') or x.endswith('/OvercastDirectional') for x in changed)
checks=read('protected_check.json');assert not checks['changed']
baseline=json.loads((O.parent/'2026-11-13_1F_EnvironmentalStory/protected_before.json').read_text());q='Unity/After_Seconds_Build_V0.01/ProjectSettings/ProjectSettings.asset';assert hashlib.sha256((R/q).read_bytes()).hexdigest()==baseline[q]
report=f'''# 1F 석양 하늘 검수 V0.01

작성자 송예찬 · 2026-11-13

HDRI 없이 1F 전용 절차적 석양 스카이박스를 제작해 저장했다. 서쪽 출구·황야 진행 방향에 고도5°의 태양을 두고 주황빛 수평선, 분홍·보랏빛 상공, 얇은 구름과 해 주변 광륜을 표현했다. 햇빛 방향·색과 거리 안개를 맞추고 실내 보조광7개와 환경광을 조정해 공장 구조가 읽히도록 했다. 기존 하늘 재질 `FW_WildernessSky`는 보존한다.

[전후 비교](review.html) · [황야 화면](after/Wilderness.jpg) · [출구 화면](after/Exit.jpg)

- 새 에셋: `Environment/1F/FS_SunsetSky.shader`, `Environment/1F/Materials/FS_SunsetSky.mat`.
- 하늘: `AfterSeconds/1F/WildernessSunset`. 상공·수평선·반대편 색, 태양 크기, 구름 양, 노출을 재질에서 조절할 수 있다.
- 햇빛: 기존 `OvercastDirectional` 회전 `(5,88,0)`, 색 `(1,.60,.32)`, 강도1.12. 이름과 오브젝트를 유지했다.
- 정적 반사8개를 석양으로 다시 구웠다. 1F의 RenderSettings에만 적용했다.
- Transform2,107개·Collider165개 유지. 태양 회전 외 배치·스케일·활성·충돌 변경0. 메시·재질·스크립트 누락0, 셰이더 오류0.
- 보호 게임 코드·다른 씬·ProjectSettings {checks['files']}개 해시 일치.
- 실제 Play3시점에서 {p['framesAdvanced']}프레임 진행, 새 경고·오류0. 중앙값{p['medianMs']:.2f}ms, 95백분위{p['p95Ms']:.2f}ms. 짧은 에디터 관측이며 빌드 성능 수치가 아니다.

실측 HDRI가 아닌 직접 제작한 정적 아트 하늘이다. 시간에 따라 해가 움직이는 기능은 추가하지 않았다. 승강기 운행·문 제어·엔딩 스크립트와 Player/Input·Animator는 변경하지 않았다. 구조가 바뀌지 않아 통행 테스트는 중복 실행하지 않았다.

현재 저장된1F 편집 상태, 석양 재질 선택과 서쪽 황야 시야. 커밋·push 미실시. 백업은 `%LOCALAPPDATA%/Temp/AfterSeconds_SunsetSky_20261113/before`에 있으며 첫 Apply는 현재 씬에 재실행하지 않는다.

변경 기록: V0.01 — 석양 스카이박스·조명/반사 연결·보존/Play 검수. 송예찬.
''';(O/'Review.md').write_text(report,encoding='utf8')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>1F 석양 하늘 V0.01</title><style>body{margin:0;background:#1d1922;color:#eee1d6;font:16px/1.7 system-ui}main{max-width:1500px;margin:auto;padding:32px}section{margin:40px 0}h1{font-size:30px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{width:100%;display:block}a{color:#efb58c}figure{margin:0}figcaption{margin-bottom:6px;color:#cbb9ad}@media(max-width:850px){.pair{grid-template-columns:1fr}}</style><main><h1>1F 석양 하늘 V0.01</h1><p>서쪽 출구를 나서면 낮은 태양과 주황빛 황야가 보입니다. 상공은 보랏빛으로 이어지고 공장에는 긴 그림자와 따뜻한 햇빛이 들어옵니다.</p><p>송예찬 · 2026-11-13 · <a href="Review.md">검수 기록</a></p>'''
for key,title in [('Wilderness','황야 진행 방향'),('Exit','공장 출구'),('Sky','석양과 얇은 구름'),('Factory','생산동 안의 빛'),('Facade','외벽'),('Lift','승강기 내부 가시성')]:
 html+=f'<section><h2>{title}</h2><div class="pair">'
 for phase,label in [('before','변경 전'),('after','석양 적용')]:
  assert (O/phase/(key+'.jpg')).exists();html+=f'<figure><figcaption>{label}</figcaption><a href="{phase}/{key}.jpg"><img src="{phase}/{key}.jpg" alt="{title} {label}"></a></figure>'
 html+='</div></section>'
html+='</main>';(O/'review.html').write_text(html,encoding='utf8')
intro=f'2026-11-13 최신 하늘: HDRI 없이1F 전용 절차적 석양을 제작했다. 서쪽 황야 진행 방향의 고도5°태양·주황/보라 하늘·얇은 구름, 햇빛·안개·실내 보조광7개·반사8개를 맞췄다. Transform2,107·Collider165유지, 태양 회전 외 배치 변경0. 실제Play3시점{p["framesAdvanced"]}프레임·새 경고/오류0. 코드/다른씬/설정53개 해시 일치. FS_SunsetSky 재질 선택과 황야 시야, 저장된1F 편집 상태. 기존 하늘 에셋과 승강기/구조/게임 코드 보존, 커밋/push 미실시. 정적인 석양이며 시간 진행·엔딩 기능은 사용자 후속 구현. 첫 Apply와 이전 전체 제작기는 재실행하지 않는다. 작성자 송예찬. '
for file,old,new,prefix in [('AGENTS.md','V1.12','V1.13',''),('CLAUDE.md','V1.12','V1.13',''),('Docs/이어하기_2026-11-12.md','V0.11','V0.12','../')]:
 f=R/file;s=f.read_text(encoding='utf-8-sig');title,rest=s.split('\n',1);assert old in title;review=('Review/' if prefix else 'Docs/Review/')+'2026-11-13_1F_SunsetSky/'
 f.write_text(title.replace(old,new)+'\n\n'+intro+f'[검수]({review}Review.md) · [전후 화면]({review}review.html) · [제작 원본]({prefix}SourceAssets/F1_SunsetSky/README.md).\n\n이전 단계 기록:\n'+rest+f'\n- {new} (2026-11-13): 1F 석양·조명·반사와 보존/Play 검수. 송예찬.\n',encoding='utf8')
f=H/'README.md';s=f.read_text(encoding='utf8').replace('V0.01\n','V0.02\n',1);s+='''

최종 재질은 `Assets/Afrer_Seconds/05.Model/Environment/1F/Materials/FS_SunsetSky.mat`, 셰이더는 같은 층의 `FS_SunsetSky.shader`다. 원래 `FW_WildernessSky.mat`는 보관했다. 태양 위치는 고도5°·Y회전88°이며 재질의 `_SunDirection`을 기존 주광 방향과 맞췄다. 정적 하늘이므로 향후 태양 회전을 바꿀 때 이 방향도 함께 맞춘다. 재질의 색·노출·구름 양·태양 크기는 직접 조절할 수 있다.

[검수](../../Docs/Review/2026-11-13_1F_SunsetSky/Review.md)와 [전후 화면](../../Docs/Review/2026-11-13_1F_SunsetSky/review.html)을 따른다. 첫 Apply·Before 캡처는 후속 변경과 백업을 덮어쓸 수 있으므로 재실행하지 않는다.

변경 기록: V0.02 — 최종 에셋·조절 항목·정적 태양 방향·검수 경로. 송예찬.
''';f.write_text(s,encoding='utf8');print('SUNSET_REPORT_READY',p['framesAdvanced'])
