"""Keep authoring files portable and remove only generated local backup files."""
import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
for path in sorted(HERE.glob('SD_*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 bpy.ops.file.pack_all()
 bpy.ops.file.make_paths_relative()
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(path))
 print('PORTABLE_SOURCE',path.name,flush=True)
