# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
"""의사코드: 원본 출처와 저장 FBX 검사 결과를 합쳐 최종 반입 명세를 만든다."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sources={x['name']:x for x in json.loads((R/'raw'/'source_manifest.json').read_text(encoding='utf-8'))}
records=[];checks=[]
for name,source in sources.items():
    directory=R/'prepared'/name;path=directory/'manifest.json';verification=directory/'fbx_verification.json'
    if not path.exists():continue
    record=json.loads(path.read_text(encoding='utf-8'));record['sourceNodeId']=source['nodeId'];record['sourceTaskId']=source['taskId'];record['sourceSha256']=source['sha256']
    for mat in record['materials']:mat['baseColorFactor']=[1,1,1,1]
    record['fbxSha256']=hashlib.sha256(Path(record['fbx']).read_bytes()).hexdigest()
    check=json.loads(verification.read_text(encoding='utf-8')) if verification.exists() else {'name':name,'accepted':False,'reason':'FBX verification pending'}
    record['accepted']=check['accepted'];record['fbxVerificationPath']=str(verification)
    path.write_text(json.dumps(record,indent=2),encoding='utf-8');records.append(record);checks.append(check)
(R/'prepared'/'prepared_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(R/'prepared'/'fbx_verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print('PREPARED',len(records),'ACCEPTED',sum(c['accepted'] for c in checks),'PENDING',[c['name'] for c in checks if not c['accepted']],flush=True)

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
