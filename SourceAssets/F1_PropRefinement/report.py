from pathlib import Path
import json,html
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-13_1F_PropRefinement'
models=json.loads((H/'models.json').read_text());play=json.loads((O/'play.json').read_text());check=json.loads((O/'check.json').read_text());protection=json.loads((O/'protected_check.json').read_text());walk=json.loads((O/'walk_floor.json').read_text());applied=json.loads((O/'applied.json').read_text())
assert play['complete'] and not play['errors'] and not check['missingOrInvalid'] and not check['shaderMessages'] and not protection['unexpectedFileChanges'] and not protection['transformChanges'] and not protection['colliderChanges'] and walk['failed']==0
names={'CableReel':'케이블 릴','OfficeChair':'사무용 의자','ToolCart':'공구 카트','Forklift':'지게차','Press':'유압 프레스'}
descs={'CableReel':'원형 판재·목재 결/끝 갈라짐, 연속 나선 권선과 바닥으로 처지는 곡선 케이블.','OfficeChair':'둥근 쿠션·봉제선·등받이 쉘, 가스 리프트·높이 레버·5발 베이스·캐스터 브래킷.','ToolCart':'접힌 판금과 서랍 틈, 둥근 손잡이·잠금쇠, 바퀴 허브와 회전 브래킷.','Forklift':'둥근 차체/카운터웨이트, 개방형 상부 가드, 마스트 채널·가이드 롤러·풀리를 감는 체인·테이퍼 포크.','Press':'가이드 봉/슈, 램 실린더·글랜드/플랜지, 펌프·매니폴드와 기둥을 돌아 연결되는 유압 호스.'}
rows='\n'.join(f"| {names[m['name'][3:]]} | {sum(x['kind']==m['name'][3:] for x in applied)} | {' / '.join(format(n,',') for n in m['triangles'])} |" for m in models)
text=f'''# 1F 프랍 곡면·기계 연결·표면 보수 V0.01

작성자: 송예찬 · 2026-11-13

사용자가 승인한 순서인 곡면/케이블 → 기계 연결 → 재질별 마모를 5종·11배치에 적용했다. 현재 저장된 `Level_1F_Factory`가 최신이다. [전후 화면](review.html)에서 동일한 석양 아래 앞뒤 모습을 비교할 수 있다.

## 변경 내용

'''+''.join(f"- **{names[k]}**: {v}\n" for k,v in descs.items())+f'''
1F 전용 재질17개와 `PRPropLit.shader`를 사용한다. 도장 금속의 작은 박리·하단 먼지, 손잡이와 축의 닳은 금속, 목재 섬유/단면, 고무 미세 균열/접지 오염, 매트한 직물 짜임을 구분했다. 기존 공장 전체 표면 셰이더는 변경하지 않았다.

| 프랍 | 배치 | LOD0 / LOD1 / LOD2 삼각형 |
|---|---:|---:|
{rows}

## 보존과 적용 방식

- 기존 4,790 Transform의 위치·회전·스케일·활성 상태 변경0. 새 모델 자식44개 → 총4,834.
- 기존 Collider165개 형상 설정/활성 상태 유지. 새 시각 모델에 충돌체를 중복 생성하지 않았다.
- 기존 원본 모델과 GUID/.meta를 보존하고, 대상11개에만 `PR_*` 새 FBX를 연결했다. 이전 본체/FD 디테일 Renderer는 끄고 기존 LODGroup을 새3단계 메시로 연결했다. 카트에는 LODGroup을 추가했다.
- 보호 파일 {protection['protectedFiles']:,}개 가운데 허용된1F 씬/반사 EXR 외 변경0. 승인한 태양·하늘·Bloom, 황야/지형, 벽/지붕/아이비, 승강기/계단, 다른층·Player/Input·게임 C#·Animator·설정 보존.
- 기존 반사8개를 재베이크했다. 가림 데이터는 유지했다.

## 검수

- Unity6000.4.0f1 Native API 반입/저장. 셰이더 오류0·누락 메시/재질/스크립트0·LOD11/11 연결 확인.
- 앞뒤 확대10시점, 실제 Play3시점. 통행75/75, 경로 탐색 실패0.
- 최종 Play {play['framesAdvanced']}프레임 실제 진행, 새 경고/오류0. 짧은 Editor 관측 median {play['medianMs']:.2f}ms / p95 {play['p95Ms']:.2f}ms이며 제품 빌드 성능 보증은 아니다.
- 제작 중 베벨 profile 기본값으로 생긴 오목한 모서리를 `.5` 둥근 단면으로 수정했다. 작은 모서리 세그먼트도 줄였다.
- 첫 Play 검수용 외부 도구가 본체 대신 하위 LOD를 선택해 반복 예외를 냈다. 부모 필터와 실패 시 종료를 추가하고 진단을 저장한 뒤 해당 검수 로그를 정리했다. 최종 재검수는 정상 완료했다. 게임 코드 변경은 없다.
- Collider JSON 비교는 씬 재개방 시 달라지는 Unity instanceID를 제외한다.

## 현재 상태와 범위

저장된1F 편집 상태, `F1_C01_CableReel_05` 선택. 커밋/push 미실시. 정적 외형 보수이며 프랍/승강기 운행이나 엔딩 기능은 구현하지 않았다. 이번5종 외 전체 프랍의 최종 완성도를 보증하는 기록은 아니다.

제작 원본: [SourceAssets/F1_PropRefinement](../../../SourceAssets/F1_PropRefinement/README.md). 첫 `Before`/`Apply`와 이전 전체 제작기를 현행 씬에 재실행하지 않는다.

## 변경 기록

- V0.01 (2026-11-13): 5종·11배치 보수와 통행/Play/보존 검수. 송예찬.
'''
(O/'Review.md').write_text(text,encoding='utf8')
readme='''# 1F 프랍 보수 제작 원본 V0.01

작성자: 송예찬 · 2026-11-13

대상은 CableReel3·OfficeChair5·ToolCart1·Forklift1·Press1, 총11배치다. `models.py`/`mesh.py`가 현재 원본이며 Blender5.2.2 LTS에서 Unity 미터 좌표의3LOD FBX를 만든다. 기존 공용 모델은 수정하지 않았다.

- `PRProp*`: 1F 새 프랍 전용 URP Lit 확장. `Environment/1F/AEWeatheredInput.hlsl`의 기존 재질 선언을 읽지만 수정하지 않는다.
- `Apply.cs`: 최초 Native API 반입·재질17개 생성·11배치 연결. 이미 적용했으므로 재실행 금지.
- `Refresh.cs`: 이번5개 FBX만 GUID 유지 갱신하는 도구. 소스 수정 후 대상/씬 상태를 확인한 경우만 사용한다.
- `Inspect.cs`, `Check.cs`, `Walk.cs`, `PlayCheck.cs`: 외부 검수용. Assets 안의 게임 C#이 아니다. `Before`/`ResumeBefore`/`prepare.py`는 기존 기준 자료를 덮거나 재생성하지 않도록 재실행하지 않는다.
- 최초 씬 백업: `%LOCALAPPDATA%/Temp/AfterSeconds_PropRefinement_20261113/before/Level_1F_Factory.unity`.
- 1F 대상 루트/충돌체 유지. 이전 Renderer를 끄고 새 PR 자식에 LOD0/1/2를 연결했다. 이전 FD 겹침은 비활성 Renderer로 보존한다.

반입 위치: `Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/1F/PR_*`.

[검수 결과](../../Docs/Review/2026-11-13_1F_PropRefinement/Review.md) · [전후 화면](../../Docs/Review/2026-11-13_1F_PropRefinement/review.html)

## 변경 기록

- V0.01 (2026-11-13): 곡면·기계 연결·마모와 검수 원본. 송예찬.
'''
(H/'README.md').write_text(readme,encoding='utf8')
cards=[]
for k in ['CableReel','OfficeChair','ToolCart','Forklift','Press']:
 for suffix,title in [('',names[k]),('_Rear',names[k]+' · 뒤쪽')]:
  cards.append(f'<section><h2>{title}</h2><p>{descs[k]}</p><div class="pair">'+''.join(f'<figure><figcaption>{label}</figcaption><a href="{phase}/{k}{suffix}.jpg"><img loading="lazy" src="{phase}/{k}{suffix}.jpg" alt="{title} {label}"></a></figure>' for phase,label in [('before','보수 전'),('after','보수 후')])+'</div></section>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>1F 프랍 보수 V0.01</title><style>body{margin:0;background:#17191b;color:#e8e6df;font:16px/1.65 system-ui,sans-serif}main{max-width:1600px;margin:auto;padding:30px}h1{font-size:32px}p{color:#bcbdb7}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{display:block;width:100%;border-radius:6px}figcaption{padding:8px 0}section{margin:48px 0}a{color:#e6c58b}@media(max-width:800px){.pair{grid-template-columns:1fr}main{padding:16px}}</style><main><h1>1F 프랍 보수 V0.01</h1><p>송예찬 · 2026-11-13 · 5종 / 11배치<br>곡면과 케이블, 실제 연결되는 기계 부품, 재질별 작은 마모. 승인한 석양·배치 유지.</p><p>75개 통행 경로 통과 · 최종 실제 Play3시점 새 경고/오류0 · <a href="Review.md">검수 기록</a></p>'''+''.join(cards)+'</main></html>'
(O/'review.html').write_text(page,encoding='utf8')
notice='2026-11-13 최신 프랍 보수: 릴·의자·카트·지게차·프레스5종11배치의 곡면/케이블·기계 연결·재질별 마모를 보수했다. 새1F 전용5FBX·17재질·3LOD, 기존4,790Transform 변경0·44추가→4,834·Collider165유지. 통행75/75·최종Play3시점728프레임 새 경고/오류0·기존14,222파일 중 허용 씬/반사 외 변경0. 승인 하늘/Bloom·황야·다른층·게임 코드 보존. 저장된1F 편집, CableReel 선택. 커밋/push 미실시. 첫Apply/Before/이전 제작기 재실행 금지. 작성자 송예찬. [검수](Docs/Review/2026-11-13_1F_PropRefinement/Review.md) · [전후](Docs/Review/2026-11-13_1F_PropRefinement/review.html) · [원본](SourceAssets/F1_PropRefinement/README.md).'
for name,old,new in [('AGENTS.md','V1.15','V1.16'),('CLAUDE.md','V1.15','V1.16'),('Docs/이어하기_2026-11-12.md','V0.14','V0.15')]:
 p=R/name;s=p.read_text(encoding='utf8');first,rest=s.split('\n',1);assert old in first and '최신 프랍 보수' not in s[:1800];first=first.replace(old,new)
 n=notice if not name.startswith('Docs/') else notice.replace('(Docs/Review/','(Review/').replace('(SourceAssets/','(../SourceAssets/')
 s=first+'\n\n'+n+'\n\n이전 단계 기록:\n'+rest+'\n- '+new+' (2026-11-13): 1F 프랍5종·11배치 곡면/연결/마모 보수와 검수. 송예찬.\n';p.write_text(s,encoding='utf8')
print('Wrote review, source README and three handoff headers')
