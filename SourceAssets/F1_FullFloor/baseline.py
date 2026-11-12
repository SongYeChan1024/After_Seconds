from pathlib import Path
import sys,json,subprocess,hashlib,time
sys.stdout.reconfigure(encoding='utf8')
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-12_1F_FullFloor';O.mkdir(parents=True,exist_ok=True)
target=H/'protected_before.json'
assert not target.exists(),'Never overwrite the pre-task baseline'
files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard','Unity/After_Seconds_Build_V0.01'],cwd=R).decode('utf8').split('\0')
data={};start=time.time()
for i,p in enumerate(sorted(set(files)-{''})):
 f=R/p
 if not f.is_file():continue
 with f.open('rb') as stream:data[p]=hashlib.file_digest(stream,'sha256').hexdigest()
 if i%2500==0:print('Protected',i,flush=True)
target.write_text(json.dumps(data,indent=2),encoding='utf8');print({'protectedFiles':len(data),'seconds':round(time.time()-start,1)},flush=True)
