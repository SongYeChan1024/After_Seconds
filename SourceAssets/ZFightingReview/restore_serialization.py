"""Undo only this review's incidental reserialization outside its 14 scene edits.
The repository was clean at baseline and the pre-pack diff contained only these
scene paths (preservation.json). No user edits are staged or reset.
"""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[2];H=Path(__file__).parent
allowed={'Unity/After_Seconds_Build_V0.01/'+json.loads(p.read_text())['scene'] for p in H.glob('applied_*.json')}
p=subprocess.run(['git','-c','core.quotepath=false','diff','--name-only','-z'],cwd=ROOT,capture_output=True,check=True)
paths=[s.decode('utf-8') for s in p.stdout.split(b'\0') if s]
restore=[p for p in paths if p not in allowed]
(H/'serialization_restored.json').write_text(json.dumps(restore,ensure_ascii=False,indent=2),encoding='utf-8')
for i in range(0,len(restore),25):
 subprocess.run(['git','restore','--source=HEAD','--worktree','--',*restore[i:i+25]],cwd=ROOT,check=True,capture_output=True)
print('Restored incidental changes:',len(restore))
