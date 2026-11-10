from pathlib import Path
import json,hashlib,re,html
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-10_B2_CeilingDensity';D=R/'Docs/도면/Decision/원형공동'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(H/'plan.json');ground=read(O/'ground.json');upper=read(O/'upper.json');play=read(O/'play.json');retry=read(O/'play_generator.json');state=read(O/'final_state.json');geo=read(O/'geometry.json');models=read(H/'models.json')
targets=[t for r in ground for t in r['targets']];moves=[m for r in upper for m in r['moves']]
assert all(t['reachable'] and (not t.get('move') or t['move']['passed']) for t in targets)
assert all(m['passed'] for m in moves)
assert play['complete'] and retry['complete'] and not play['errors'] and not retry['errors']
assert all(t['passed'] for t in play['results'] if not t['name'].startswith('W02')) and all(t['passed'] for t in retry['results'])
assert len([t for t in play['results'] if not t['passed']])==1
assert not any(x['outside'] for x in geo['shell'])
assert state['saved'] and not state['missingOriginal'] and not state['missingMeshes'] and not state['missingMats'] and not state['activeGuidance']
assert not any(m['degenerate'] for m in state['newModels'])
assert all(f['verticesUnchanged'] and f['trianglesUnchanged'] for f in state['floors'])
protected=read(R/'SourceAssets/B2_SurfaceRefinement/protected_before.json');changed=[p for p,sha in protected.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=sha];assert not changed,changed
write(O/'protected.json',dict(files=len(protected),changed=changed))
frames=sum(t['frames'] for t in play['results'] if t['passed'])+sum(t['frames'] for t in retry['results'])
scaled=[p for p in plan['placements'] if p.get('relative_scale')]
write(D/'B2_운영동선_재설계/as_built_ceiling_density.json',dict(version='V0.01',author='송예찬',date='2026-11-10',placements=plan['placements'],reference_images=plan['reference_images'],models=models,ceiling_rooms=12,new_work_frames=['S01','E03'],ground_targets=len(targets),upper_moves=len(moves),play_verified_frames=frames,lighting='Existing 158 lights, dark red mood. No added permanent lights.',runtime_added=False))
facility=read(D/'facility_layout.json');facility['version']='V0.12';facility['floor_art_direction']['B2'].update(dict(reference_images=plan['reference_images'],density_direction='큰 설비의 작업열과 굵은 배관, 계장 분기, 케이블 트레이, 지지 철골을 바닥부터 돔 천장까지 연결한다. 어둡고 붉은 조명과 철색, 관리된 조작부/사용감 있는 바닥·계단을 함께 유지한다.'))
facility['production_status']['B2']='운영 배치194개, 설비27개 확대, 12공동 천장 배관/케이블 트레이, S01 정비 프레임·E03 처리 프레임. 바닥/콘솔 보수 유지, 하부226·상부34·실제 Play8경로 검수. 사용자 근접 외형 검수 단계.'
facility['production_status']['B2_CeilingDensity']=dict(date='2026-11-10',as_built='B2_운영동선_재설계/as_built_ceiling_density.json',review='../../../Review/2026-11-10_B2_CeilingDensity/Review.md',runtime_added=False)
if not any(isinstance(x,dict) and x.get('version')=='V0.12' for x in facility['revision_history']):facility['revision_history'].append(dict(version='V0.12',date='2026-11-10',author='송예찬',change='B2 레퍼런스9장에 맞춘 설비 크기·천장 밀도와 S01/E03 구조 보강, 통행/배관 간섭 보수.'))
write(D/'facility_layout.json',facility)
write(R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B2_CeilingDensity.json',dict(version='V0.01',author='송예찬',source='SourceAssets/B2_CeilingDensity',reference_images=plan['reference_images'],models=models,method='Blender purpose-built beveled steel frames and continuous pipe circuits; 26 detailed models plus 26 far LODs. Six additional placements reuse existing authored props. No new VARCO job.',runtime_added=False))
review=f'''# B2 설비 크기·천장 밀도 보강 V0.01

작성자 송예찬 · 2026-11-10

사용자 B2 레퍼런스9장을 확인하고 `Level_B2_Circular.unity`에 적용했다. 큰 설비가 작업열을 이루고, 굵은 주 배관·가는 계장 배관·케이블 트레이·철골이 바닥부터 천장까지 이어지는 구성을 반영했다. 기존 어두운 붉은 광원158개를 유지했다.

- C02 펌프5개는2배(높이 약0.8→1.6m), E01/E03 펌프5개는1.5배. C01 원심분리기2·C01/C02 열교환기4·W02 발전기3·N01 HVAC2는1.5배, W01 변압기4는1.35배, C01 수처리2는1.2배로 조정했다. 전체27개다. 사람용 콘솔/작업대와 기존4.75m 탱크는 무리하게 확대하지 않았다.
- `Visual_L0`만 변경하지 않고 상위 설비 루트를 확대하여 LOD와 충돌도 함께 반영했다. 사용자가 조정한 하위 시각 메시 회전은 보존했다.
- C02 펌프 열, 열교환기 정면, 탱크·헤더·모터 받침/카트를 재배치했다. C01 정비면과 W01 변압기 작업면, W02 연료 밸브 간격, E01 펌프/탱크 간섭을 보수했다. 받침 크기/방향과 연결 배관도 새 치수에 맞췄다.
- 12공동 모두에 공급/회수 주 배관, 계장 분기, 케이블 트레이, 플랜지·가스켓·볼트·천장 앵커/행거를 추가했다. 물/공조/전력 구역별로 관경과 연결을 달리했다. 새 배관망은 돔 내부 곡률에 맞췄다.
- S01에는 두 정비 작업열을 감싸는 인양 프레임·호이스트·전력 트레이와 교정 전원/정비 부품 설비4개를 넣었다. E03에는 탱크 처리 프레임·통기 집합관과 완충 탱크/필터 보관 설비2개를 추가했다. 운영 배치목록은188→194개다.
- 앞 단계의 콘솔8개, 윤활 설비, 산업용 콘크리트와 닳은 계단/그레이팅, B2 안내선 미표시를 유지했다. [앞 단계 검수](../2026-11-10_B2_SurfaceRefinement/Review.md).

하부 출입/작업면 {len(targets)}/{len(targets)}, 상부 경로 왕복 {len(moves)}/{len(moves)}를 통과했다. 실제 PlayerMotor/입력으로8경로, 통과 구간 총{frames}프레임을 확인했다. 최초 W02 직선 검사는 기존 계단과 겹쳐 상부로 올라갔으므로 실패 기록을 남기고, 실제 발전기 서쪽 연료 점검 통로를 별도로 재검사해 통과했다. 경비/AI 동작이나 최종 성능 벤치마크를 검사했다는 의미는 아니다.

원본 Transform {state['originalTransforms']}개 누락0, 메시/재질 누락0, 신규52 FBX의 퇴화 삼각형0. 신규26개 조립체의 돔 경계 검사에서0.12m 초과 침범0. 기존 바닥15개의 꼭짓점/삼각형 보존, 보호 파일{len(protected)}개(Player 씬/게임 코드/Animator/다른 층 등) 변경0. 광원158개, 영구 신규 조명0. 마우스/키보드 활성, runInBackground 복원. 반사37개와 가림 데이터를 갱신했다.

비교 화면은 [review.html](review.html). `before_*`/`after_*`와 `play_view`는 실제 조명이다. `inspection_*`는 형상 확인을 위한 임시 점검등 사진으로, 해당 등은 촬영 즉시 제거했다. 어두운 분위기의 최종 판단은 실제 조명 화면과 Unity에서 한다.

현재 단계는 정적 레벨/아트 보강 완료와 사용자 외형 검수다. 플레이어·에너미 로직, 문/설비 기능을 새로 작성하지 않았다. 로컬 저장, 이번 커밋/push 미요청.

다음 확인 순서: C02 확대 펌프/작업면 → S01 정비 프레임/천장 → E03 처리 설비/천장 → W02 연료 점검 통로 → N01 공조 규모. 지적된 구역만 후속 보수한다.
'''
(O/'Review.md').write_text(review,encoding='utf8')
cards=[]
for id,label in [('C02','확대 펌프와 중앙 점검로'),('S01','정비 작업열과 인양 프레임'),('N01','공조 장비와 상부 설비')]:
 cards.append(f'<h2>{id} · {label}</h2><div class="pair"><figure><img src="after_focus_{id}.png"><figcaption>주요 변경 · 실제 붉은 조명</figcaption></figure><figure><img src="inspection_focus_{id}.png"><figcaption>형상 확인 · 임시 점검등</figcaption></figure></div>')
for r in plan['rooms']:
 id=r['id'];cards.append(f'<h2>{id} · {html.escape(r["name"])}</h2><div class="pair"><figure><img loading="lazy" src="before_{id}.png"><figcaption>변경 전 · 실제 조명</figcaption></figure><figure><img loading="lazy" src="after_{id}.png"><figcaption>변경 후 · 실제 조명</figcaption></figure></div><div class="pair"><figure><img loading="lazy" src="after_roof_{id}.png"><figcaption>천장 · 실제 조명</figcaption></figure><figure><img loading="lazy" src="inspection_roof_{id}.png"><figcaption>형상 점검 · 임시 점검등, 씬에 저장하지 않음</figcaption></figure></div>')
(O/'review.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>B2 설비·천장 보강 V0.01</title><style>body{margin:0;background:#151515;color:#ddd;font:16px/1.7 sans-serif;padding:28px}h1,h2{color:#e9c7b8}p{max-width:1000px}a{color:#efad93}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0 0 18px}img{width:100%;border:1px solid #444}figcaption{font-size:14px;color:#bbb}h2{margin-top:45px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>B2 설비 크기·천장 밀도 보강 V0.01</h1><p>송예찬 · 2026-11-10. 사용자 레퍼런스9장: 큰 설비, 연결된 주/분기 배관과 철골, 천장까지 이어지는 밀도. 어둡고 붉은 조명 유지. 27설비 확대 · 12공동 천장 · S01/E03 프레임 · 프랍6배치 추가. <a href="Review.md">검수 기록</a></p><p>실제 조명과 임시 점검등 사진을 구분했다. 점검등은 형상 확인용이며 씬에 저장하지 않았다.</p>'+''.join(cards)+'</html>',encoding='utf8')
(H/'README.md').write_text('''# B2 설비 규모·천장 밀도 제작 원본 V0.01

작성자 송예찬 · 2026-11-10

`plan.json`194배치와 `changes.json`, `models.json`이 이 단계의 원본이다. 사용자 레퍼런스9장은 Docs/Reference/B2에 있다. 이전 B2_SurfaceRefinement188배치에서 이어진다. 현재 씬에 과거 Apply나 prepare를 무작정 재실행하지 않는다.

`prepare.py`는 기준 배치로부터 확대/재배치안과 서비스 제작 코드를 만든다. `services.py`는 치수·회전·돔 곡률에 맞는 공정 배관/받침, `build.py`는 천장 회로12종과 S01/E03 프레임2종을 만든다. 모두 새 CD_ 접두어로 보관하며 원본 .meta/GUID는 보존했다. 제조 모서리 베벨, 플랜지/볼트, 편집용 .blend, Far LOD를 포함한다. 신규 VARCO 요청 없이 Blender로 연결 구조를 직접 제작했다.

`Apply.Import` 반입 → `Apply.Run` 최초1회 배치 → 필요한 경우 `Apply.Reposition`만 사용한다. Run 재실행은 중복 적용을 막는다. Reposition은 위치/방향만 갱신해 확대 배율을 중복 적용하지 않는다. 기존 Visual_L0 하위 회전은 보존한다. 기존 BO 배관은 비활성 보관했다.

`Audit.Ground/Upper`, `Quality`, `Verify`는 콜라이더 통행/돔 경계/참조/모델 검수다. `Play` 최초 W02 경로는 계단을 올라가는 잘못된 바닥 경로여서 실패했고 `PlayGenerator`로 발전기 서쪽 점검 통로를 재검증했다. 실패 기록도 유지했다. Mouse/Keyboard는 비활성화하지 않으며 검사 후 설정을 복원한다. 이 C#은 Assets 밖의 일시 실행 제작/검수 도구이며 런타임 게임 코드가 아니다.

`Finish.Reflections/Occlusion/Complete`는 반사/가림 마감, `Capture`와 `Audit.After`는 비교 사진, `record.py`는 검사 통과 후 문서/출처 기록이다. `inspection_*`만 임시 점검등 사진이다.

백업: C:/Users/503-26/Documents/Codex/Backups/AfterSeconds_B2_Ceiling_20261110. 작업 중 사용자 미저장 상태도 별도 사본으로 저장했다.

[검수 기록](../../Docs/Review/2026-11-10_B2_CeilingDensity/Review.md) · [비교 화면](../../Docs/Review/2026-11-10_B2_CeilingDensity/review.html)
''',encoding='utf8')
note='2026-11-10 B2 설비·천장 후속: 사용자 B2 레퍼런스9장에 맞춰 설비27개를1.2~2배로 조정하고 배치/점검 면·받침·연결 배관을 보수했다. 12공동 천장 배관/케이블 트레이, S01 정비 인양 프레임·E03 탱크 처리 프레임과 프랍6배치를 추가했다. 최신 배치194개. 하부226/226·상부34/34·실제 Play8경로 검수, 광원158개와 붉고 어두운 분위기 유지. 기존 콘솔/바닥 보수와 B2 안내선 미표시 유지. [최신 검수](Docs/Review/2026-11-10_B2_CeilingDensity/Review.md) · [제작 원본](SourceAssets/B2_CeilingDensity/README.md)을 우선한다. 다음은 C02→S01→E03→W02→N01 사용자 근접 검수다. 이전 전체 Apply 재실행 금지. 게임 코드/Player/Animator/다른 층 보존, 로컬 저장, 이번 커밋·push 미요청. 작성자 송예찬.'
for filename in ['AGENTS.md','CLAUDE.md']:
 p=R/filename;s=p.read_text(encoding='utf8');lines=s.splitlines();lines[0]=re.sub(r'V0\.\d+','V0.91',lines[0]);s='\n'.join(lines)+'\n'
 if note not in s:s=s.replace('\n\n','\n\n'+note+'\n\n이전 단계 기록:\n\n',1);s+='\n- V0.91 (2026-11-10): B2 레퍼런스 기반 설비 확대·천장/정비 구조·통행 보수. 송예찬.\n'
 p.write_text(s,encoding='utf8')
p=D/'B2_운영동선_재설계/README.md';s=p.read_text(encoding='utf8');msg='최신 후속: `as_built_ceiling_density.json`194배치와 [B2 설비·천장 보강 검수](../../../Review/2026-11-10_B2_CeilingDensity/Review.md)를 우선한다. 27설비 확대, 12공동 천장 연결과 S01/E03 구조가 반영됐다.'
if msg not in s:p.write_text(s.replace('\n\n','\n\n'+msg+'\n\n',1),encoding='utf8')
old=D/'B2_운영동선_재설계/as_built_surface_refinement.json';j=read(old);j['next_revision']='as_built_ceiling_density.json';write(old,j)
print(json.dumps(dict(ground=len(targets),upper=len(moves),play_frames=frames,protected=len(protected),scaled=len(scaled),models=len(models))))
