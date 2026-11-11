"""Restore only tracked paths Git confirms have no content diff (stat/EOL noise)."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[2];H=Path(__file__).parent
def paths(*args):return set(subprocess.check_output(['git',*args,'-z'],cwd=ROOT,stderr=subprocess.DEVNULL).decode().split('\0'))-{''}
modified=paths('ls-files','-m');changed=paths('diff','--name-only')
candidates=sorted(p for p in modified-changed if p.startswith('Unity/After_Seconds_Build_V0.01/'))
spec=ROOT/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/eol_paths.txt'
spec.write_bytes(b'\0'.join(p.encode() for p in candidates)+b'\0')
if candidates:subprocess.run(['git','restore','--worktree','--pathspec-from-file='+str(spec),'--pathspec-file-nul'],cwd=ROOT,check=True)
(H/'eol_cleanup.json').write_text(json.dumps(dict(count=len(candidates),paths=candidates),indent=2))
print(json.dumps(dict(eolOnlyPathsRestored=len(candidates),remainingModified=len(paths('ls-files','-m')))))
