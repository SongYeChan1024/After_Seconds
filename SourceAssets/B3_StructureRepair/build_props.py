import runpy,ast,json,random,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
base=runpy.run_path(str(R/'SourceAssets/B3_FullFloor/common.py'))
for k,v in base.items():
 if not k.startswith('_') and k not in ['H','R','save']:globals()[k]=v
b.H=H;b.manifest=json.loads((H/'models.json').read_text())
tree=ast.parse((R/'SourceAssets/B3_FullFloor/props.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'existing_detailed_case_parts','exec'))
def save(name):
 b.OUT=b.A/'Props'/'B3';b.raw_export('BR_B3_'+name);b.manifest['BR_B3_'+name]['category']='Props'
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf-8')
for variant in range(3):
 init();rng=random.Random(1940+variant)
 for x in [-.48,0,.48]:box('Pallet_Load_Beam',x,.085,0,.12,.17,1.04,'Steel',.008)
 for z in [-.42,-.21,0,.21,.42]:box('Pallet_Deck_Slat',0,.19,z,1.20,.045,.16,'Steel',.008)
 for layer in range(2 if variant==2 else 3):
  for col in range(2):
   for row in range(2):
    if variant==1 and layer==2 and col==1:continue
    crate(-.29+col*.58,.218+layer*.34,-.26+row*.52,.53,.32,.47,(layer*3+col+row+variant)%6)
 for x in [-.51,.51]:
  for z in [-.46,.46]:box('Pallet_Corner_Block',x,.24,z,.08,.10,.08,'Rubber',.008)
 label(0,.14,.533,.32,.07,12+variant);save('SamplePallet_'+str(variant+1))
init();w=2.65;d=1.12
box('Archive_Island_Frame',0,.77,0,w,1.46,d,'Steel',.016)
for side in [-1,1]:
 for col in range(4):
  for row in range(5):
   x=-.96+col*.64;y=.22+row*.25;z=side*.574
   box('Sample_Drawer_Face',x,y,z,.60,.226,.035,'Case'+str((col+row)%4),.006)
   tube('Recessed_Pull',[(x-.10,y,side*.598),(x-.10,y,side*.624),(x+.10,y,side*.624),(x+.10,y,side*.598)],.008,'Steel')
   if side==1:label(x,y+.064,.596,.17,.036,(col*5+row)%32)
box('Stainless_Island_Top',0,1.53,0,w+.04,.045,d+.04,'Steel',.009)
for x in [-1.10,1.10]:
 for z in [-.44,.44]:box('Island_Adjustable_Foot',x,.035,z,.14,.07,.14,'Dark',.008)
for i in range(3):crate(-.78+i*.78,1.553,-.05,.60,.24,.46,2+i)
save('SampleDrawerIsland')
init();w=.82;d=.60
for x in [-.36,.36]:
 for z in [-.25,.25]:
  cyl('Caster_Axle',(x-.035,.065,z),(x+.035,.065,z),.06,'Rubber',16)
  box('Caster_Fork',x,.12,z,.08,.09,.09,'Steel',.006)
  box('Tubular_Frame',x,.63,z,.035,1.0,.035,'Steel',.005)
for y in [.19,.60,1.01]:
 box('Transfer_Tray',0,y,0,w,.035,d,'Steel',.006)
 for i in [-1,1]:crate(i*.19,y+.025,0,.32,.24,.39,2 if i<0 else 4)
tube('Push_Handle',[(-.36,1.03,-.25),(-.36,1.20,-.34),(.36,1.20,-.34),(.36,1.03,-.25)],.018,'Steel')
save('LoadedTransferCart')
init()
for x in [-.47,.47]:
 for z in [-.32,.32]:box('Sterile_Rack_Upright',x,1.04,z,.04,2.04,.04,'Steel',.004)
for i in range(6):
 y=.20+i*.32;box('Perforated_Shelf',0,y,0,.96,.025,.66,'Steel',.005)
 for j in range(2):
  x=-.23+j*.46;box('Sterile_Tray',x,y+.045,0,.41,.055,.54,'Steel',.009)
  for k in range(4):box('Wrapped_Instrument_Pouch',x,y+.077+k*.012,-.03,.36,.018,.43,'Paper',.005)
  label(x,y+.087,.279,.24,.045,26+j)
for x in [-.43,.43]:
 for z in [-.28,.28]:cyl('Rack_Caster',(x-.03,.05,z),(x+.03,.05,z),.05,'Rubber',16)
save('SterileTrayRack')
init();box('Packaging_Tray',0,.015,0,.53,.03,.34,'Steel',.008)
for i in range(3):
 box('Sealed_Pouch',-.15+i*.14,.038+i*.006,.02,.12,.012,.25,'Paper',.003)
 label(-.15+i*.14,.046+i*.006,.149,.08,.025,25+i)
cyl('Seal_Roll',(.18,.075,-.085),(.18,.075,.035),.055,'Paper',32)
cyl('Roll_Core',(.18,.075,.036),(.18,.075,.039),.018,'Dark',24)
save('SealingKit')
print('Detailed storage and processing assemblies complete',flush=True)
