"""저장 씬의 기존 객체와 에셋 보존 여부를 읽기 전용으로 검사한다. 작성자 송예찬."""
from pathlib import Path
import hashlib, json, re

R=Path(__file__).resolve().parents[2]
b=json.loads((Path(__file__).parent/'baseline.json').read_text(encoding='utf-8'))
out=R/'Docs/검수/2026-11-07_C01_Wayfinding'
def objects(p):
    parts=re.split(r'(?m)^--- !u!(\d+) &(\d+)(?: stripped)?\n',p.read_text(encoding='utf-8'))
    return {parts[i+1]:(parts[i],parts[i+2]) for i in range(1,len(parts),3)}

old=objects(Path(b['backup'])/'Level_B5_Circular.unity')
new=objects(R/b['scene'])
changed=[k for k in old if k in new and old[k]!=new[k]]
expected_parent='1718033888'
assert changed == [expected_parent]
# The sole old object difference is the room parent's reference to the new group.
after_lines=new[expected_parent][1].splitlines()
before_lines=old[expected_parent][1].splitlines()
extras=[line for line in after_lines if line not in before_lines]
assert len(extras)==1 and re.fullmatch(r'  - \{fileID: \d+\}',extras[0])
assert [line for line in after_lines if line!=extras[0]]==before_lines
asset_changes=[name for name,h in b['protected'].items() if hashlib.sha256((R/name).read_bytes()).hexdigest()!=h]
assert asset_changes == [b['scene']]
result=dict(beforeObjects=len(old),afterObjects=len(new),removedExistingObjects=sorted(set(old)-set(new)),addedObjects=len(set(new)-set(old)),changedExistingObjects=changed,soleChange='Room Transform gains one child reference; all other existing serialized objects unchanged.',protectedFiles=len(b['protected']),changedFiles=asset_changes)
assert not result['removedExistingObjects']
(out/'scene_preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
