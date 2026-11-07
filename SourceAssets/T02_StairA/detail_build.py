from pathlib import Path
import json
H=Path(__file__).resolve().parent;s=(H/'build.py').read_text(encoding='utf-8')
exec(compile(s[:s.index('\nreset()\nfor i in range')],str(H/'build.py'),'exec'))
manifest=json.loads((H/'model_manifest.json').read_text(encoding='utf-8'))
for start,end in [('\nreset()\n# Vertical','\nreset()\n# Eight'),('\nreset()\n# B4 level',"\nreset();cylinder_object('CoreResinFloor'")]:
    exec(compile(s[s.index(start):s.index(end)],str(H/'build.py'),'exec'))
(H/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
