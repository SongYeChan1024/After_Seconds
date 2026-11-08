from pathlib import Path
import json,hashlib,math
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_FullFloor';O.mkdir(parents=True,exist_ok=True)
if (H/'baseline.json').exists():raise RuntimeError('Already prepared')
baseline={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Assets','Packages','ProjectSettings'] for p in (P/folder).rglob('*') if p.is_file() and not p.relative_to(P).as_posix().startswith('Assets/Temp/')}
(H/'baseline.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
d=json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text(encoding='utf-8'));f=next(x for x in d['floors'] if x['id']=='B4')
for r in f['rooms']:
 r['doors']=[]
 for t in f['tunnels']:
  if r['id'] not in [t['a'],t['b']]:continue
  p=t['p'] if t['a']==r['id'] else t['q'];r['doors'].append({'id':t['id'],'x':p[0]-r['x'],'z':-p[1]+r['v'],'angle':math.degrees(math.atan2(-p[1]+r['v'],p[0]-r['x']))})
f['author']='송예찬';f['scene']='Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity';f['preserve']='Existing C01/T02 art; open four temporary closures only';f['scope']='All16rooms/22corridors, static art. Runtime mechanisms and cross-scene transitions excluded.'
(H/'plan.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8');title,body=s.split('\n',1);assert 'V0.50' in title
note='2026-11-08 B4 전체 일괄 제작 결정: 사용자가 대표 구역 검수에서 멈추지 말고 전체를 먼저 만들도록 요청했다. C01/T02 기존 외형을 보존하면서 남은12돔·3코어·21복도를 일괄 제작하고, 이후 사용자 전체 검수를 받는다. 각 방의 측정/진단/관찰지원/분석/기록/판독/연구/회복 용도를 구조와 대표 장비로 구분한다. VA/VB는 B4→B3 높이17m의 정적 계단과 상부 연결 준비, VL은 화물 승강기 외형을 구성한다. 복도 전용 목적지 안내와 리브 사이 등기구, 각 돔 작업 조명을 유지한다. B5/B3 실제 씬 전환·문/승강기·실험·AI 게임 기능은 별도다. 작성자 송예찬.'
p.write_text(title.replace('V0.50','V0.51')+'\n\n'+note+'\n\n이전 단계 기록:\n'+body.lstrip()+'\n- V0.51 (2026-11-08): 사용자 요청에 따른 B4 전체 일괄 제작 범위와 후속 일괄 검수. 송예찬.\n',encoding='utf-8')
print('protected',len(baseline),'rooms',len(f['rooms']),'corridors',len(f['tunnels']))
