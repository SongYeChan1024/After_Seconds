raise RuntimeError('이 도구는 폐기된 11개 통합안 기록용입니다. 최신 확정 기준은 12공동 + 3코어 + 19복도입니다.')
from pathlib import Path
import json,re,shutil
R=Path(__file__).resolve().parents[2];D=R/'Docs/도면/Decision/원형공동';S=R/'SourceAssets/B5_Sector01'
decision='2026-11-06 최신 사용자 변경: 층별조감도의 외형·공간 구성을 제작 기준으로 삼는다. C01 피험체 격리 공동은 실험·일시 격리 공간이며 생활실이 아니다. 침상·개인 책상·수납·세면 등 생활시설은 별도의 격리 생활 공동에 둔다. 전체 돔은 11개로 재편하되 계단 A/B·승강기 코어의 포함 여부는 확인 중이다. 조감도의 공간 코드를 섹터 코드로 쓰고, 이전 Unity 기준 1~7 번호는 이력으로 보관한다. C01의 완료 보고는 철회한다. 현재는 기존 생활 배치 초안과 기술 검사만 있는 상태이며 아트·실험실 배치 재작업이 필요하다.'
def prepend(p,version,paragraph):
 text=p.read_text('utf-8');head,body=text.split('\n',1);head=re.sub(r'V\d+\.\d+',version,head);p.write_text(head+'\n\n'+paragraph+'\n\n아래는 이전 작업 기록이다. 최신 범위·완료 상태는 위 문단을 우선한다.\n'+body,encoding='utf-8')
for file,ver in [('AGENTS.md','V0.35'),('CLAUDE.md','V0.35'),('Docs/이어하기_2026-11-06.md','V0.19')]:prepend(R/file,ver,decision)
mp=R/'Docs/AfterSeconds_메인기획서.md';prepend(mp,'V0.32',decision)
with mp.open('a',encoding='utf-8') as f:f.write('\n- V0.32 (2026-11-06): C01 실험용 격리·별도 생활 공동 역할 구분, 조감도 기준 섹터와 전체 돔11개 개편 논의. C01 완료 보고 철회 및 아트 재작업. 송예찬.\n')
wl=R/'Docs/회사_작업목록_2026-11-06.md';prepend(wl,'V0.17',decision)
text=wl.read_text('utf-8').replace('| 1섹터 | C01 피험체 격리 | 포드·침상·생활 구획·배식·위생·관찰 시야 | 레벨·아트 검수 완료 |','| C01 | 피험체 격리 공동 | 실험 포드·관찰·계측·제염·안전 설비 | 실험실 배치·아트 재작업 |',1);wl.write_text(text,encoding='utf-8')
ar=R/'Docs/도면/Old/원형공동/자료안내/V0.07/README.md';ar.parent.mkdir(parents=True,exist_ok=True)
if not ar.exists():shutil.copy2(D/'README.md',ar)
prepend(D/'README.md','V0.08',decision)
report=R/'Docs/검수/2026-11-06_B5_Sector01/검수결과.md';prepend(report,'V0.02','완료 판정을 철회한다. 가구 배치와 기술 검사를 시각적 마감 완료로 잘못 판단했다. 아래 수치는 이전 생활 배치 초안의 검사 이력이며 새 실험용 C01의 완료 증거가 아니다. 벽·바닥 마감, 장비와 배선의 연결, 공간 밀도, 조명 및 실험실 역할에 맞춘 재제작이 남는다. '+decision)
prepend(S/'README.md','V0.02',decision+' 기존 자동 Apply·finalize 도구를 재실행해 이전 완료 상태를 복구하지 않는다.')
p=D/'B5_섹터/sector_plan.json';plan=json.loads(p.read_text('utf-8'));ar=R/'Docs/도면/Old/원형공동/B5_섹터/V0.02';ar.mkdir(parents=True,exist_ok=True)
for name in ['sector_plan.json','B5_섹터구분도.svg','B5_섹터구분도.png']:
 if not (ar/name).exists():shutil.copy2(p.parent/name,ar/name)
one=plan['sectors'][0];one['complete']=False;one['status']='실험용 격리 공동으로 재설계·아트 재작업';one['checks']={k:False for k in one['checks']};one['review_note']='이전 기술 검사 결과는 생활시설 배치 초안의 이력이며 완성도 미달로 완료 판정을 철회함.'
plan['title']='B5 기존 Unity 구역과 재편 상태 V0.03';plan['next']='B5-C01';plan['latest_decision']=decision;plan['pending_revision']={'target_domes':11,'includes_vertical_cores':None,'reference':'층별조감도/B5_실내조감도.png','status':'코어 포함 여부 확인 후 상세 통합안 작성','previous_numbering_obsolete':True};p.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
(S/'latest_scope.json').write_text(json.dumps({'version':'V0.02','decision':decision,'C01_role':'실험·일시 격리','living_facility':'별도 공동','dome_target':11,'includes_cores':None,'complete':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Completion retracted; C01 experiment role and 11-dome revision recorded. Unity layout unchanged pending plan.')
