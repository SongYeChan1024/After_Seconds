from pathlib import Path
import json,hashlib,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B4_LabIdentity'
base=json.loads((H/'protected_before.json').read_text(encoding='utf8'));diff=[]
for name,old in base.items():
 p=R/name
 if not p.exists():diff.append({'path':name,'status':'missing'});continue
 with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 if old!=h:diff.append({'path':name,'status':'changed'})
(O/'protected_files.json').write_text(json.dumps(dict(total=len(base),unchanged=len(base)-len(diff),changes=diff),indent=2),encoding='utf8')
check=subprocess.run(['git','diff','--check'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out=check.stdout.decode('utf8',errors='replace');(H/'git_diffcheck.txt').write_text(out,encoding='utf8')
print('Protected',len(base),'differences',diff)
print('Git diff check exit',check.returncode,'issue headers',sum('trailing whitespace' in l for l in out.splitlines()))
