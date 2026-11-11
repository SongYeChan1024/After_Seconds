from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs'
rule='**2026-11-11 사용자 정정.** 실험체의 정상 생활·시험 범위는 B5·B4이며, B4→B3 상행 경계부터 실험체 진입을 막는다. B3·B2·B1·1F는 실험체의 정상 활동 구역이 아니다. 플레이어가 상층으로 올라가는 것은 이 경계를 뚫는 탈출 상황이다. B1은 연구 데이터 업무·기록 보관과 직원 생활 공간이다. 여기서 통제는 실험체의 상층 진입을 막는 출입 보안을 뜻하며, 직원 통제나 B1 현장 능력 실험을 뜻하지 않는다. 세 코어의 자유 선택은 탈출 경로 선택 규칙이고 무조건 개방된 문이나 보안 부재를 뜻하지 않는다. 구체적인 보안문 작동·AI·층간 전환은 후속 구현이다.'
def update(rel,old,new,fn,note=rule):
 p=R/rel;s=p.read_text(encoding='utf8');assert old in s.splitlines()[0],rel;s=s.replace(old,new,1);s=fn(s)
 if note:s=s.replace('\n\n','\n\n'+note+'\n\n',1)
 s+='\n\n- '+new+' (2026-11-11): 실험체 B5/B4 활동 경계와 B1 연구 데이터·직원 생활 용도 정정. 송예찬.\n';p.write_text(s,encoding='utf8')
def main(s):
 s=s.replace('B5·B4·B3·B2에 각각','B5·B4·B3·B2·B1에 각각').replace('네 층의 보행과 공간','다섯 층의 보행과 공간').replace('B1과 1F는 최신 도면으로 설명한다.','1F는 최신 도면으로 설명한다.')
 s=s.replace('| B1 실험층 | 중앙 피험 챔버·관찰 구역과 연구원 작업실·숙소·책임자 기록실이 이어진다. 중앙을 건너거나 직원의 외곽 동선을 이용하는 설계다. | 세 코어 중 선택 → 1F | 현행 평면 설계 · 원형 씬 제작 전 |','| B1 연구 데이터·직원 생활층 | 연구 자료 인계·열람·분석·보관과 사무·회의·숙소·식당·위생 공간이 이어진다. 실험체와 현장 능력 시험은 없다. | 세 코어 중 선택 → 1F | 원형 씬 제작 · 용도 정정 후 검수 |')
 s=s.replace('B1 실험 준비','B1 연구 기록 인계').replace('B1 의료 지원','B1 직원 의무실').replace('B1 관찰','B1 직원 회의')
 s=s.replace('계단 A에서 실험 준비 공동으로 진입하고, 중앙 피험 챔버나 기록 공동을 거쳐 의료 지원 공동에서 합류할 수 있다.','계단 A에서 연구 기록 인계 공동으로 진입하고, 중앙 자료 열람·대조실이나 기록 보관실을 거쳐 직원 의무실에서 합류할 수 있다.')
 s=s.replace('직원 생활부의 따뜻한 회색·아이보리와 시험 구역의 중성 작업광','직원 생활부의 따뜻한 회색·아이보리와 데이터 업무 구역의 작업광')
 s=s.replace('B1은 실험 카트리지·녹음기·연구 자료','B1은 녹음기·연구 수첩·서류·데이터 매체')
 s=s.replace('**2026-11-11 B1 제작 현황.**','**2026-11-11 B1 최초 제작 이력 — 이후 용도 정정으로 대체.**')
 s=s.replace('## 변경 기록\n','## 변경 기록\n\n| V0.78 | 2026-11-11 | 송예찬 | 사용자 정정: 실험체는 B5/B4에 한정, B4→B3 상행 통제. B1은 연구 데이터·직원 생활층이며 현장 시험 장비 제거 방향 반영. |\n',1)
 return s
update('Docs/AfterSeconds_메인기획서.md','V0.77','V0.78',main)
for rel in ['AGENTS.md','CLAUDE.md']:
 update(rel,'V0.98','V0.99',lambda s:s,rule+' 현재 B1 용도 보수는 `SourceAssets/B1_StaffDataRevision/`를 따른다. 이전 B1 전체 제작 및 시험 설비 배치 설명은 이력이다.')
update('Docs/층간_코어_연결_대조.md','V0.07','V0.08',lambda s:s.replace('세 코어는 모든 층에서 열려 있다.','세 코어는 모든 층에서 탈출 경로로 자유롭게 선택한다. 정상 운영의 출입 허가나 문 개방 상태를 뜻하지 않는다.').replace('C02 실험 준비 11.2m','C02 기록 인계 11.2m').replace('N01 미래시 시험','N01 데이터 분석').replace('C04 의료 지원 11.1m','C04 직원 의무실 11.1m').replace('C05 관찰 13.7m','C05 직원 회의 13.7m').replace('| B1 → 1F | 18m | 씬 제작 전 |','| B1 → 1F | 18m | VA·VB 18m 계단과 정적 VL 캐빈, 실제 층 전환 미구현 |'))
update('Docs/에너미_AI_기획과_로직.md','V0.05','V0.06',lambda s:s.replace('기획서](AfterSeconds_메인기획서.md) V0.76','기획서](AfterSeconds_메인기획서.md) V0.78').replace('| B1 연구 통제층 | 연구원 업무와 경비/CCTV 보고를 연결한 관찰·통제 구역 |','| B1 연구 데이터·직원 생활층 | 연구 데이터 업무·직원 생활과 출입 보안. 실험체 현장 관찰·시험 공간 없음 |'))
def pickup(s):
 s=s.replace('### B1 실험층','### B1 연구 데이터·직원 생활층').replace('**외형 기준:** 연구 기록과 실험 장비 중심. 개인 작업물과 연구소 전용 데이터 매체의 차이.','**외형 기준:** 연구 기록·서류·데이터 매체와 직원 일상 물건 중심. 현장 능력 실험 도구는 두지 않는다.').replace('연구원 작업실·기록실·실험 준비대','연구원 사무실·기록실·자료 인계대')
 a=s.index('### B1 ');b=s.index('### ',a+6);section=s[a:b]
 section='\n'.join(line for line in section.split('\n') if not any(line.startswith('| '+id+' |') for id in ['ExperimentCartridge','HandAnalyzer','SampleCase']))
 s=s[:a]+section+s[b:];s=s.replace('58개 층별 등장 항목','55개 층별 등장 항목');return s
update('Docs/층별_획득오브젝트_명세.md','V0.04','V0.05',pickup,rule+' B1의 실험 카트리지·휴대 분석기·시료 케이스 3종은 현행 배치에서 제외한다. 정의는 제작 이력으로 보관하며 다른 층에 자동 배치하지 않는다.')
p=D/'Objects/pickup_catalog.json';j=json.loads(p.read_text(encoding='utf8'));j['title']=j['title'].replace('V0.04','V0.05');j['version']='V0.05';j['date']='2026-11-11';b=next(x for x in j['floors'] if x['id']=='B1');excluded={'ExperimentCartridge','HandAnalyzer','SampleCase'};b['items']=[x for x in b['items'] if x not in excluded];b['title']='연구 데이터·직원 생활층';b['art_direction']='연구 기록·서류·데이터 매체와 직원 일상. 현장 능력 실험 장비 없음.';b['placement_area_candidates']='연구원 사무실·자료 인계·열람·보관';j['summary']['floor_entries']=sum(len(x['items']) for x in j['floors']);j['summary']['active_item_types']=len(set(x for f in j['floors'] for x in f['items']))
for x in j['items']:
 if x['id'] in excluded:x['floors']=[];x['production_status']='B1 용도 정정으로 배치 제외 / 정의 이력 보관, 다른 층 배치 미정'
j['revision_history'].append(dict(version='V0.05',date='2026-11-11',change='B1 연구 데이터·직원 생활. 현장 시험 소품3종 제외, 55개 층별 항목.'))
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
update('Docs/도면/Decision/원형공동/층별조감도/README.md','V0.02','V0.03',lambda s:s.replace('[직원 생활·통제]','[연구 데이터·직원 생활]'),rule+' 기존 조감도 이미지·PDF는 이전 제작 이력이며 B1 현행 용도/배치는 `../B1_제작현황/`를 우선한다.')
update('Docs/도면/Decision/원형공동/README.md','V0.17','V0.18',lambda s:s,rule+' B1의 현행 배치 기준은 [B1 제작 현황](B1_제작현황/README.md)이다. 기존 PDF/엑셀의 B1 시험 장비 목록은 이전 설계 이력이다.')
# Preserve old design placement lists explicitly as superseded; the current B1 source is the scene plan.
p=D/'도면/Decision/원형공동/facility_layout.json';j=json.loads(p.read_text(encoding='utf8'));changes=json.loads((H/'changes.json').read_text(encoding='utf8'));names={k:v[0] for k,v in changes['roomNames'].items()};b=next(x for x in j['floors'] if x['id']=='B1');before=dict(floor=b,rooms=[x for x in j['rooms'] if x['floor']=='B1'],placements=[x for x in j['placements'] if x['floor']=='B1']);(H/'before_design_B1.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf8')
b.update(name='연구 데이터·직원 생활층',full_role='연구 데이터 분석·보관·직원 업무와 생활',theme='실험체 없는 상층 직원 공간. 자료 인계·열람·분석·보관과 숙소·식당.',placements_source='B1_제작현황/as_built_layout.json')
for r in b['rooms']:
 if r['id'] in names:r['name']=names[r['id']]
for r in j['rooms']:
 if r['floor']=='B1' and r['id'] in names:r['name']=names[r['id']]
for r in j['placements']:
 if r['floor']=='B1':
  if r['room'] in names:r['room_name']=names[r['room']]
  r['state']='이전 설계 이력 / 현재 배치 아님';r['superseded_by']='B1_제작현황/as_built_layout.json'
j['floor_art_direction']['B1'].update(label='연구 데이터와 직원 생활',description='따뜻한 회색·아이보리. 직원 생활의 온화한 빛과 데이터 업무의 중성 작업광. 현장 실험 없음.')
j['gameplay_rules']['subject_access_boundary']=dict(normal_floors=['B5','B4'],upper_forbidden_floors=['B3','B2','B1','1F'],boundary='B4->B3',meaning='실험체 상층 진입 방지. 플레이어 상행은 탈출. 직원 통제나 B1 시험 공간을 뜻하지 않음.',runtime_implemented=False)
j['production_status']['B1_StaffData']=dict(date='2026-11-11',scene='Level_B1_Circular.unity',as_built='B1_제작현황/as_built_layout.json',status='현장 시험설비 제외·직원/연구 데이터 용도 보수',runtime_added=False)
j['title']=j['title'].replace('V0.09','V0.10');j['version']='V0.10';j['date']='2026-11-11';j['revision_history'].append(dict(version='V0.10',date='2026-11-11',change='B5/B4 실험체 활동 경계·B1 연구 데이터/직원 생활. B1 이전 배치목록을 이력으로 명시.'));p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Current planning, boundary, B1 roles, pickup and drawing authority corrected.')
