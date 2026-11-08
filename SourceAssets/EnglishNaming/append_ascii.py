from pathlib import Path
import json

H = Path(__file__).resolve().parent
plan = json.loads((H/'rename_plan.json').read_text(encoding='utf8'))
assert len(plan) == 1778
scene = 'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity'
rows = json.loads((H/'Level_B4_Circular_before.json').read_text(encoding='utf8'))
extra = [{'scene':scene, 'id':r['id'], 'old':r['name'], 'new':r['name'].replace('↔','_')} for r in rows if '↔' in r['name']]
assert len(extra) == 21 and all(r['new'].isascii() for r in extra)
plan.extend(extra)
mapping = json.loads((H/'name_map.json').read_text(encoding='utf8'))
for r in extra:
    mapping[r['old']] = [r['new']]
(H/'rename_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(H/'name_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for folder in ['B4_ExperimentOperations','B4_FullFloor','B4_Observation']:
    for p in (H.parent/folder).glob('*'):
        if p.name not in ['Review.cs','Audit.cs','FinalState.cs','layout.json']:
            continue
        s=p.read_text(encoding='utf8');updated=s
        for r in extra: updated=updated.replace(r['old'],r['new'])
        if updated!=s:p.write_text(updated,encoding='utf8')
p=H/'report.py';s=p.read_text(encoding='utf8')
s=s.replace("==1778", "==1799").replace('B4 1,556개·B5 222개, 총1,778개 하이라키 이름','B4 1,577개·B5 222개, 총1,799개 하이라키 이름').replace('에셋·폴더 경로의 한글은 처음부터0개였다.','한글 이름1,778개와 화살표 기호가 있던 복도 이름21개를 정리했다. 에셋·폴더 경로의 한글은 처음부터0개였다.').replace('이미 영어인 이름은 유지했다.','영어 이름의 복도 연결 기호 `↔`21개를 밑줄로 바꿨으며 그 외 기존 영어 이름은 유지했다.').replace('plan.py produced1,778 ID-based renames.','plan.py produced1,778 ID-based renames; append_ascii.py added21 corridor names containing arrow symbols, for1,799 total.')
p.write_text(s,encoding='utf8')
print({'total':len(plan),'symbolNames':len(extra)})
