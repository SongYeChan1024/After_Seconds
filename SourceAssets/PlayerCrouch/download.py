from pathlib import Path
import json, urllib.request, hashlib
from concurrent.futures import ThreadPoolExecutor
p=Path(__file__).parent
source=json.loads((p/'source.json').read_text(encoding='utf-8'))
(p/'Original').mkdir(exist_ok=True)
def fetch(c):
    dest=p/'Original'/('Crouch_'+c['name']+'.fbx')
    with urllib.request.urlopen(c['url'],timeout=120) as response:
        data=response.read()
    if not data.startswith(b'Kaydara FBX Binary'):
        raise ValueError('Not a binary FBX: '+c['name'])
    dest.write_bytes(data)
    return dict(name=c['name'],bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
with ThreadPoolExecutor(max_workers=6) as pool:
    results=list(pool.map(fetch,source['clips']))
(p/'download_validation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results))
