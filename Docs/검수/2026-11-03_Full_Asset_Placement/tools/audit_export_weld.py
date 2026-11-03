# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
import ast,bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
module=ast.parse((R/'tools'/'prepare_models.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'helpers','exec'))
manifest=json.loads((R/'prepared'/'Props_GasCylinderRack'/'manifest.json').read_text())
for tolerance in [1e-7,1e-8,1e-9,1e-10]:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=manifest['fbx'],use_image_search=False)
    for obj in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        bm=bmesh.new();bm.from_mesh(obj.data);lo=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);hi=Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=(hi-lo).length*tolerance);bm.to_mesh(obj.data);bm.free();result=audit(obj.data,strict=True)
        print('WELD',tolerance,{k:v for k,v in result.items() if k not in ['crossingPairs','crossingPairsSample']},flush=True)

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
