from pathlib import Path
import json,hashlib,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_Observation';O.mkdir(parents=True,exist_ok=True)
if (H/'baseline.json').exists():raise RuntimeError('Baseline already exists')
baseline={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Assets','Packages','ProjectSettings'] for p in (P/folder).rglob('*') if p.is_file() and not p.relative_to(P).as_posix().startswith('Assets/Temp/')}
(H/'baseline.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
d=json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text(encoding='utf-8'));f=next(x for x in d['floors'] if x['id']=='B4')
plan={'author':'송예찬','floor':'B4','height':-66,'scene':'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity','room':next(x for x in f['rooms'] if x['id']=='C01'),'tunnels':[t for t in f['tunnels'] if 'C01' in (t['a'],t['b'])],'rooms':f['rooms'],'art':d['floor_art_direction']['B4'],'scope':'대표 구역 C01 중앙 관찰동과 T02 접근 복도. 다른 돔과 B5/B3 실제 연결은 다음 단계.','deck':{'height':2.5,'innerRadius':7.2,'outerRadius':10.6,'angleStart':50,'angleEnd':130,'stairsX':[-5.8,5.8],'stairsZ0':2.8,'stairsZ1':7.0,'width':1.6,'risers':15},'notes':['중앙 측정 영역과 상부 관찰석, 지상 준비/기록 공간을 구분한다.','B5 1차 외형 승인 상태 보존. 기존 전체 파일 해시 보호.','새 하이라키는 층_구역_한글용도_번호. 안내선은 복도에만 둔다.','게임 코드·Animator·문 동작·감지·실험 기믹은 추가하지 않는다.']}
(H/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8');title,body=s.split('\n',1)
assert 'V0.48' in title
note='2026-11-08 B4 제작 시작: 사용자가 B5의 현재 외형·조명을 1차 기준으로 수용하고 다음 층 진행을 요청했다. B5는 보존하고 Decision의 B4 능력 측정·관찰층을 새 Level_B4_Circular 씬으로 시작한다. 대표 구역 C01(반지름12m, 바닥-66m)에 높이2.5m 관찰 데크와 두 계단, 중앙 측정 바닥, 관측·준비·기록 장비를 상세 제작한다. 무채색 회색/흑연색과 중성 국부 작업광을 사용한다. 먼저 C01 및 T02 접근부를 검수한 뒤 나머지12돔·3코어·21복도로 확장한다. 이 단계의 계단 상세·장비 배치는 제작 가안이며 실제 이동과 간섭으로 검수한다. B5↔B4 층간 연결과 게임 기능은 별도다. 작성자 송예찬.'
p.write_text(title.replace('V0.48','V0.49')+'\n\n'+note+'\n\n'+body.lstrip()+'\n- V0.49 (2026-11-08): B5 1차 확인 수용, B4 중앙 관찰동 대표 구역 제작과 확장 순서. 송예찬.\n',encoding='utf-8')
(H/'README.md').write_text('''# B4 중앙 관찰동 제작 V0.01

작성자 송예찬 · 2026-11-08

Decision `facility_layout.json`의 B4-C01 반지름12m, Y=-66m와 네 출입 방향을 유지한다. B5 현재 외형은 사용자 1차 수용 상태로 보존한다. 기존 Old B4 씬을 재사용해 덮어쓰지 않고 별도 `Level_B4_Circular.unity`를 만든다.

이번 단위는 중앙 관찰동과 T02 접근 복도다. 2.5m 관찰 데크, 양쪽15단 계단과 난간, 시험 바닥, 관측석·준비/기록 설비를 구분한다. 데크 북측50~130도, 계단 폭1.6m·단높이1/6m·단깊이0.28m는 제작 가안이다. 데크 장비는 원 명세의 용도를 유지하고 계단·의자 통행에 맞춰 조정한다. 나머지 층은 후속 제작이며 문은 정적 외형이다.

아트 원본·제작/검수 C#은 이 폴더, 모델/프리팹은 `05.Model/{Environment,Props}/B4`, 맵은 해당 Materials/Textures, 제작 출처는06.Data/AssetSources에 둔다. 기존 모델·재질·씬·게임 코드·Animator를 수정하지 않는다. 새 오브젝트 이름은 `B4_C01_한글용도_번호`로 읽기 쉽게 한다.

검수는 메시/재질·돔/계단/문 충돌·통행 여유·실제 키보드 Play·화면 확인·보호 파일 해시 비교를 포함한다. 초기 `prepare.py`와 씬 Build를 재실행해 후속 작업을 덮어쓰지 않는다.
''',encoding='utf-8')
print(json.dumps({'protectedFiles':len(baseline),'room':plan['room'],'scope':plan['scope']},ensure_ascii=True))
