"""제작 시작 시점의 원본 파일과 저장된 씬을 읽기 전용으로 대조한다."""
import hashlib,json
from pathlib import Path
REPO=Path(__file__).resolve().parents[4]
TMP=REPO/'tmp/ArchitectureDetail_20261104'
OUT=Path(__file__).resolve().parent.parent
results={}
for name in ('protected_before','input_scenes_before'):
    records=json.loads((TMP/(name+'.json')).read_text(encoding='utf-8-sig'))
    changed=[]
    for item in records:
        file=REPO/item['path']
        actual=hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else None
        if actual!=item['hash']:changed.append({'path':item['path'],'before':item['hash'],'current':actual})
    results[name]={'checked':len(records),'changed':changed}
(OUT/'source_preservation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=True),flush=True)
manifest=OUT/'clean_kit_manifest.json'
data=json.loads(manifest.read_text(encoding='utf-8-sig'))
if 'AD_Manufactured_Emission.png' not in data['textures']:data['textures'].append('AD_Manufactured_Emission.png')
manifest.write_text(json.dumps(data,indent=2),encoding='utf-8')
