# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
"""의사코드: 승인된 기존 출력 URL을 읽고, 원본을 병렬 저장한 뒤 glTF 헤더와 해시를 검증한다."""
import concurrent.futures, hashlib, json, struct, urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1]
raw=R/'raw'; raw.mkdir(parents=True,exist_ok=True)
records=json.loads((R/'downloads.json').read_text(encoding='utf-8-sig'))
def download(record):
    name=record['name']; d=record['downloads'][0]; path=raw/(name+'.glb')
    if not path.exists():
        with urllib.request.urlopen(d['url'],timeout=180) as source, path.open('wb') as target:
            while block:=source.read(1024*1024):target.write(block)
    blob=path.read_bytes(); magic,version,length=struct.unpack('<4sII',blob[:12])
    if magic!=b'glTF' or version!=2 or length!=len(blob):raise ValueError(name+' invalid GLB')
    result={'name':name,'nodeId':record['nodeId'],'taskId':d['taskId'],'path':str(path),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()}
    print(name,len(blob),flush=True); return result
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results=list(executor.map(download,records))
(raw/'source_manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('VERIFIED',len(results),flush=True)

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
