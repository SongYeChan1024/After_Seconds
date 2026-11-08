from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_ExperimentOperations';O.mkdir(parents=True,exist_ok=True)
assert not (H/'baseline.json').exists(),'Already prepared'
b={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Assets','Packages','ProjectSettings'] for p in (P/folder).rglob('*') if p.is_file() and not p.relative_to(P).as_posix().startswith('Assets/Temp/')}
(H/'baseline.json').write_text(json.dumps(b,indent=2),encoding='utf8')
plan=json.loads((R/'SourceAssets/B4_FullFloor/layout.json').read_text(encoding='utf8'));plan['name']='능력 측정·발달·강화층';plan['role_decision']='B5 생활·격리 및 기본 관리 / B4 본격적인 정밀 측정·능력 발달·강화 실험';(H/'base_layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf8');title,body=s.split('\n',1);assert 'V0.53' in title
note='2026-11-08 B4 실험 운용 설비 제작 시작: 사용자는 B5를 생활·격리 중심, B4를 본격적인 실험 공간으로 확정하고 각 돔의 역할을 구분해 프랍·설비를 채우도록 요청했다. 실험체의 이송/접수·대기·준비·시험·회복, 경비의 인계·감시·통제, 연구원의 교정·조작·분석·기록·장비 회수 동선을 고려한다. 기존13돔·3코어·22복도의 연결을 유지하며 시험 구획/관측 구획, 전용 계측/반복 훈련 장비, 수납·교정·회수·응급·보안 지원을 보강한다. 설비 위치·치수·세부 운용은 제작 가안이며 충돌·통행·시야로 검수한다. 구체적인 능력 강화 수단·약물·게임 수치는 확정하지 않고, 현재는 정적 아트로 제작한다. 안내선은 복도 전용이다. 작성자 송예찬.'
p.write_text(title.replace('V0.53','V0.54')+'\n\n'+note+'\n\n이전 단계 기록:\n'+body.lstrip()+'\n- V0.54 (2026-11-08): B5 생활 중심/B4 본격 실험의 역할 확정과 실험체·경비·연구원 관점의 설비 보강 착수. 송예찬.\n',encoding='utf8')
print('baseline',len(b))
