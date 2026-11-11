"""Only B1 tunnel ends and stair riser seams; preserves all other models."""
from pathlib import Path
import sys,json
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import common
common.manifest=json.loads((H/'models_environment.json').read_text())
source=(H/'architecture.py').read_text(encoding='utf8');preamble=source[:source.index("for r in plan['rooms']:")];body=source[source.index("for t in plan['tunnels']:\n reset();o=sweep"):]
exec(compile(preamble+body,'B1_targeted_seams','exec'))
