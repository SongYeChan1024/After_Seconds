from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];m=json.loads((H/'name_map.json').read_text(encoding='utf8'));pairs=sorted(((k,v[0]) for k,v in m.items() if len(v)==1),key=lambda p:-len(p[0]))
def replace(s):
 for old,new in pairs:s=s.replace(old,new)
 return s
changed=[]
# Current review tools and layout must resolve the renamed objects. Historical
# before snapshots, older reports and one-shot generators remain immutable evidence.
for folder,files in {
 'B4_ExperimentOperations':['Review.cs','Audit.cs','FinalState.cs','layout.json','README.md'],
 'B4_FullFloor':['Review.cs','FinalState.cs','layout.json'],
 'B4_Observation':['Review.cs'],
 'B5_CeilingLighting':['Review.cs','Audit.cs','FinalState.cs'],
}.items():
 for name in files:
  p=R/'SourceAssets'/folder/name
  if not p.exists():continue
  s=p.read_text(encoding='utf8');updated=replace(s).replace('_관측석내부','_OperatorPosition').replace('_실험체계측위치','_SubjectPosition')
  if updated!=s:p.write_text(updated,encoding='utf8');changed.append(p.relative_to(R).as_posix())
o=R/'Docs/검수/2026-11-08_B4_ExperimentOperations'
for name in ['role_views.json','review.html']:
 p=o/name;p.write_text(replace(p.read_text(encoding='utf8')),encoding='utf8')
p=o/'검수결과.md';s=p.read_text(encoding='utf8');s=replace(s).replace('V0.01','V0.02',1);s=s.replace('작성자 송예찬 · 2026-11-08','작성자 송예찬 · 2026-11-08\n\n후속 이름 정리: 현재 Unity 이름은 간결한 영어다. B4 하이라키1,556개를 영문화했고 이름 이외 직렬화 속성은 동일하다. 아래 배치/Play 검수는 명칭 정리 전후 외형이 같은 설비 작업의 기록이다. [이름 변경 검수](../2026-11-08_EnglishNaming/review.md).',1);s+='\n- V0.02 (2026-11-08): 영문 하이라키 이름과 후속 변경 검수 링크 반영. 송예찬.\n';p.write_text(s,encoding='utf8')
for folder in ['B4_ExperimentOperations','B4_FullFloor','B4_Observation','B5_CeilingLighting']:
 p=R/'SourceAssets'/folder/'README.md'
 if not p.exists():continue
 s=p.read_text(encoding='utf8');title,body=s.split('\n',1)
 p.write_text(title+'\n\n2026-11-08 영문 이름 전환: 현재 씬은 SourceAssets/EnglishNaming/name_map.json 기준이다. 이전 일회성 생성·Apply 도구는 당시 이름을 담은 제작 이력으로, 현재 씬에 그대로 재실행하지 않는다. 최신 Review/Audit 도구는 영문 경로에 맞췄다. 새 제작은 처음부터 영어 이름을 사용한다.\n'+body,encoding='utf8')
(H/'updated_tools.json').write_text(json.dumps(changed,ensure_ascii=False,indent=2),encoding='utf8');print('Updated review/layout files',len(changed))
