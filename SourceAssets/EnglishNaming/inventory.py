from pathlib import Path
import re,json,collections
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';A=P/'Assets';ko=re.compile('[\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]')
paths=[];names=collections.Counter();byfile={};lookups=[]
for p in A.rglob('*'):
 if ko.search(p.name):paths.append(p.relative_to(P).as_posix())
 if not p.is_file():continue
 if p.suffix in ['.unity','.prefab','.asset','.mat','.controller','.anim']:
  try:s=p.read_text(encoding='utf8')
  except UnicodeError:continue
  hits=[]
  for v in re.findall(r'^  m_Name: (.*)$',s,re.M):
   try:v=json.loads(v) if v.startswith('"') else v
   except ValueError:pass
   if ko.search(v):names[v]+=1;hits.append(v)
  if hits:byfile[p.relative_to(P).as_posix()]=hits
 if p.suffix=='.cs':
  for i,line in enumerate(p.read_text(encoding='utf8').splitlines(),1):
   if ko.search(line) and re.search('Find|Load|CompareTag|\.name|Tag\(|Layer',line):lookups.append({'file':p.relative_to(P).as_posix(),'line':i,'text':line.strip()})
data={'koreanPaths':paths,'names':dict(names),'byFile':byfile,'codeLookups':lookups}
(H/'inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'paths':paths,'nameCount':sum(names.values()),'uniqueNames':len(names),'byFile':{p:len(n) for p,n in byfile.items()},'lookups':lookups},ensure_ascii=False,indent=2))
