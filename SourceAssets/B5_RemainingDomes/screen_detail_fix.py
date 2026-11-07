"""Six distinct control wall feeds. Author 송예찬."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build
build.manifest.update(json.loads((build.H/'models.json').read_text(encoding='utf-8')))
build.reset();build.bigwall();build.export('CentralVideoWall')
