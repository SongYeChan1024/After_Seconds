"""기존 포드 작업광의 실제 천장 등기구. 작성자: 송예찬."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];lib=R/'SourceAssets/B5_Sector01/build_details.py';e={'__file__':str(lib),'__name__':'fixture_library'}
exec(compile(lib.read_text('utf-8').split('# Structural ribs')[0],str(lib),'exec'),e);e['H']=H;e['reset']();box=e['box'];cyl=e['cyl']
box('Ceiling_Gasket',0,.108,0,1.32,.025,.48,'Dark',.008)
box('Sealed_Housing',0,.061,0,1.28,.086,.44,'Coat',.018)
box('Diffuser_Gasket',0,.012,0,1.20,.018,.37,'Dark',.009)
box('Downlight_Diffuser',0,0,0,1.15,.024,.325,'Lamp',.010)
for x in [-.58,.58]:
 for z in [-.17,.17]:cyl('Captive_Fastener',(x,.011,z),(x,.019,z),.012,'Steel',8)
e['export']('CL_PodCeilingLight')
(H/'geometry.json').write_text(json.dumps(e['manifest'],ensure_ascii=False,indent=2),encoding='utf-8')
