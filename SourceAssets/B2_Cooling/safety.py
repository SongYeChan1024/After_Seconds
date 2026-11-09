import sys,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
src=(R/'SourceAssets/B4_LayoutPolish/build.py').read_text(encoding='utf8');tree=ast.parse(src)
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['bolt','ring','mount']:exec(compile(ast.Module(body=[n],type_ignores=[]),'safety_helpers','exec'))
class Label:
 def label(self,x,y,z,w,h,kind):b.print_panel('SafetyInstructions',x,y,z,w,h,10)
c=Label();reset();m=bpy.data.materials.new('B4O_Display_10');b.mats['Display_10']=m
a=src.index(' reset(); face=');end=src.index(" save('WallSafety_R'+str(rad))",a)
rad=11;exec('\n'.join(line[1:] for line in src[a:end].splitlines()))
save('WallSafety_R11','Props')
