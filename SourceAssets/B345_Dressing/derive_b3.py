"""B3 dressing V0.01: remove only the old monolithic shelf cases, preserve rack/architecture."""
import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPOSITORY=HERE.parents[1]
helper=REPOSITORY/'SourceAssets/LevelContinuation/build_sections.py'
code=helper.read_text(encoding='utf-8').split("for floor in ('B5','B4'):")[0]
code=code.replace("'LC_'+floor+'_Architecture.blend'","'SD_'+floor+'_Architecture.blend'").replace("'LC_'+floor+'_Architecture.fbx'","'SD_'+floor+'_Architecture.fbx'")
exec(compile(code,str(helper),'exec'))
SRC=HERE;REPO=REPOSITORY
bpy.ops.wm.open_mainfile(filepath=str(REPO/'SourceAssets/B3_StealthLayout/LC_B3_Architecture.blend'))
removed=remove_where(lambda o:o.name.startswith(('SealedSpecimenCrate','SpecimenCrateLid','SpecimenCrateLatch')))
assert len(removed)==864, len(removed)
export('B3',removed)
(HERE/'removed_case_objects.json').write_text(json.dumps(removed,indent=2))
print('DRESSING_ARCH_DONE',len(removed),flush=True)
