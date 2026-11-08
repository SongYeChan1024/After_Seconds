from pathlib import Path
from html.parser import HTMLParser
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_ExperimentOperations'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,tag,attrs):self.refs.extend(v for k,v in attrs if k in ['href','src'])
links=Links();links.feed((O/'review.html').read_text(encoding='utf8'));assert all((O/v).is_file() for v in links.refs)
provenance=json.loads((P/'Assets/Afrer_Seconds/06.Data/AssetSources/B4_ExperimentOperations_20261108.json').read_text(encoding='utf8'))
for m in provenance['newModels']:assert (P/m['asset']).is_file() and (R/m['source']).is_file(),m['name']
assert (H/'B4_before.unity').exists()
assert not (P/'Assets/Temp/B4_ExperimentOperations').exists()
state=json.loads((O/'final_state.json').read_text(encoding='utf8'));assert not state['isDirty'] and not state['isPlaying'] and not state['runInBackground']
print(json.dumps({'galleryFiles':len(set(links.refs)),'modelSources':len(provenance['newModels']),'sceneSaved':True,'playTemporaryFilesRemoved':True},ensure_ascii=False))
