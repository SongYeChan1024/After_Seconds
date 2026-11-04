"""새로 만든 Blender 원본의 보기 방향과 외부 텍스처 보관을 마무리한다."""
import bpy,json,sys,math
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]);repo=root.parents[1];source=repo/'SourceAssets/PropEdgeFinish'
bpy.ops.wm.open_mainfile(filepath=str(source/'WorkbenchColorRebake.blend'))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source/'WorkbenchColorRebake.blend'))
bpy.ops.wm.open_mainfile(filepath=str(source/'PropEdgeFinish.blend'))
bpy.context.preferences.filepaths.save_version=0
records=json.loads((root/'finish_manifest.json').read_text(encoding='utf-8'))
for r in records:
 obj=bpy.data.objects.get(r['id'])
 if obj:
  obj.rotation_euler=(math.pi/2,0,0);obj.scale=(r['metersPerLocalUnit'],)*3
bpy.ops.wm.save_as_mainfile(filepath=str(source/'PropEdgeFinish.blend'))
print('SOURCES_PACKED_AND_UPRIGHT',flush=True)
