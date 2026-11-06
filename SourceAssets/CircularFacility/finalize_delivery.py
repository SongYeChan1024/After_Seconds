import json,hashlib,shutil
from pathlib import Path
from PIL import Image
from pypdf import PdfReader
import openpyxl
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
DOC=REPO/'Docs/도면/원형공동';REPORT=REPO/'Docs/검수/2026-11-06_CircularFacility'
UNITY=REPO/'Unity/After_Seconds_Build_V0.01'
SOURCE=Path('C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_multilevel')
DELIVERY=SOURCE.parent/'after_seconds_reviewed';DELIVERY.mkdir(exist_ok=True)
audit=json.loads((HERE/'source_audit.json').read_text(encoding='utf-8'))
wb=openpyxl.load_workbook(next(SOURCE.glob('*.xlsx')),read_only=True,data_only=False)
for s in wb:
 s.calculate_dimension(force=True);audit['workbook'][s.title]={'rows':s.max_row,'columns':s.max_column}
wb.close();(HERE/'source_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
before=json.loads((HERE/'protected_before.json').read_text());changed=[]
for rel,h in before.items():
 p=UNITY/rel
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(rel)
source_changed=[rel for rel,h in audit['source_hashes'].items() if hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()!=h]
validation=json.loads((REPORT/'validation.json').read_text());walk=json.loads((REPORT/'B2_controller_walk.json').read_text());doors=json.loads((REPORT/'door_validation.json').read_text())
proof={'protected_files':len(before),'changed_protected':changed,'source_files_changed':source_changed,'scenes':[str(p.relative_to(UNITY)) for p in (UNITY/'Assets/Afrer_Seconds/01.Scenes/Stage').glob('Level_*Circular.unity')]+['Assets/Afrer_Seconds/01.Scenes/Stage/Level_B2_MezzaninePreview.unity'],'navigation':[{k:v[k] for k in ['floor','samples','triangles']}|{'blocked':len(v['blocked'])} for v in validation],'doors':{'count':len(doors),'failed':sum(not r['openClear'] or not r['closedBlocks'] for r in doors)},'stairs':{'runs':len(walk),'failed':sum(r['remaining']>.12 or r['heightError']>.12 for r in walk)},'scope':'B5 static route capsules; B2 upper deck capsules plus CharacterController stairs. No runtime AI, light switches, complete vertical traversal, keyboard Play or FPS verification.'}
(REPORT/'preservation_and_checks.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
assert not changed,("Protected files changed",changed)
assert not source_changed,("Source changed",source_changed)
assert not any(p['blocked'] for p in proof['navigation'])
assert proof['doors']['failed']==0 and proof['stairs']['failed']==0
data=json.loads((DOC/'facility_layout.json').read_text(encoding='utf-8'))
data['production_status']={'B5':'핵심 공동4·코어3·터널7, 문14세트, 기존 프랍17개 첫 제작','B2':'C02 메자닌 검토 씬: 실제 그레이팅·계단2·작업대·탱크2·펌프2·배관 연결','B4_B3_B1_1F':'설계 데이터 수정 완료 / 새 원형 씬 제작은 후속','B3_switches':'13회로 설계, 이 중5개 보관 구역 기본 소등 / 스위치 동작 미구현','checks':proof['navigation']}
(DOC/'facility_layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
refname='참고원본_시설생활_프랍배치.xlsx'
shutil.copy2(next(SOURCE.glob('*.xlsx')),DOC/refname)
readme='''# After Seconds 원형 공동 제작 설계 V0.03

작성자 송예찬 · 2026-11-06

현재 기준은 `AfterSeconds_원형공동_제작설계.pdf`와 `facility_layout.json`입니다. 원본 V0.02의 생활·업무·소품 명세를 보존하면서 B2 메자닌, 안내선과 기록, 최신 층별 색감, B3 구역별 점등, 회전 분리 CCTV 후보를 반영했습니다.

- PDF 17장: 대조 결과·색감·6층 전체 배치·6층 핵심 예상 이동·B2 메자닌 단면·안내선/기록·층간 제작 순서.
- 도면 폴더: 같은 내용의 SVG와 PNG. 경로선은 도면상의 예상 이동이며 UI·미니맵은 구현하지 않았습니다.
- 참고원본 엑셀: 145종·3,264명세의 원본 그대로입니다. 새 메자닌/안내선/점등 회로는 수정 JSON을 우선하며 원본 엑셀 수량을 새 배치 완료 수량으로 해석하지 않습니다.
- Unity 시작 씬: `Level_B5_Circular.unity`. B5 핵심 원형 공간과 터널·문·기존 프랍을 별도 씬에 제작했습니다.
- B2 구조 검토 씬: `Level_B2_MezzaninePreview.unity`. 기계층 전체가 아닌 냉각·펌프 공동 한 곳의 복층/재질/배관 검토입니다.
- B3는 사람이 적은 보관 구역의 소등·구역 점등 설계를 반영했습니다. 수동 스위치·AI·문 동작은 사용자 직접 코딩 범위입니다.

단면·격자·광량은 게임 제작 가안입니다. 전체 소품 배치, 내부 생활 칸막이, 층간 계단·승강기, 다른 층의 새 원형 레벨과 실제 잠입 플레이/FPS 검수는 후속 작업입니다.

프로젝트 기준 폴더: `C:/Users/503-26/Desktop/Projects/04.After_Seconds/Docs/도면/원형공동`
전달 사본: `C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_reviewed`
이전 `after_seconds_multilevel`의 원본 파일은 변경하지 않았습니다.
'''
(DOC/'README.md').write_text(readme,encoding='utf-8')
for file in DOC.iterdir():
 if file.is_file() and file.name!='contact.png':shutil.copy2(file,DELIVERY/file.name)
shutil.copytree(DOC/'도면',DELIVERY/'도면',dirs_exist_ok=True)
(DELIVERY/'먼저읽기.txt').write_text(readme,encoding='utf-8')
dest=UNITY/'Assets/Afrer_Seconds/06.Data/AssetSources';dest.mkdir(exist_ok=True,parents=True)
(dest/'CircularFacility_Production.json').write_text(json.dumps({'author':'송예찬','source':'SourceAssets/CircularFacility','design':'Docs/도면/원형공동/facility_layout.json','models':json.loads((HERE/'geometry_manifest.json').read_text()),'runtime_code_added':False,'original_models_preserved':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False))
print('DELIVERY',str(DELIVERY))
