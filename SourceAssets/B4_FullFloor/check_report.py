from pathlib import Path
from html.parser import HTMLParser
import json
R=Path(__file__).resolve().parents[2];O=R/'Docs/검수/2026-11-08_B4_FullFloor'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=0
 def handle_starttag(self,tag,attrs):
  if tag=='img':self.images+=1
  self.links.extend(v for k,v in attrs if k in ['src','href'])
p=Links();p.feed((O/'review.html').read_text(encoding='utf8'));missing=sorted({v for v in p.links if not (O/v).exists()});walk=json.loads((O/'walk.json').read_text(encoding='utf8'));s=json.loads((O/'final_state.json').read_text(encoding='utf8'));result={'galleryImages':p.images,'missingLinks':missing,'walkPassed':sum(x['passed'] for x in walk['results']),'planningFailures':walk['planningFailures'],'sceneSaved':not s['isDirty'],'playStopped':not s['isPlaying']};print(result);assert not missing and result['walkPassed']==104 and result['sceneSaved']
