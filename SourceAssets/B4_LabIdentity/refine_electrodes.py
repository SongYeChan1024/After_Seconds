"""Near-camera handling details, connected headbox and returned consumables."""
import sys,json,bpy,math
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import common as m
from common import *
m.manifest.update(json.loads((H/'models.json').read_text(encoding='utf8')))
bpy.ops.wm.open_mainfile(filepath=str(H/'LB_ElectrodePrepBench.blend'))
b.mats={x.name.replace('B4O_','').replace('BX_','').replace('LB_',''):x for x in bpy.data.materials}
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('Forceps_Arm','Opened_Peel_Pack')):bpy.data.objects.remove(o,do_unlink=True)
# Spring forceps, joined heel, tapering jaws and grip grooves, resting on the mat.
for side in [-1,1]:
 x=.17
 vs=[(x+side*.010,.926,.19),(x+side*.008,.933,.20),(x+side*.018,.933,.29),(x+side*.007,.926,.36),(x+side*.003,.926,.36),(x+side*.012,.929,.29),(x+side*.002,.929,.20),(x+side*.004,.923,.19)]
 mesh('Spring_Forceps_Jaw',vs,[(0,1,2,3,4,5,6,7)],'Steel',.001)
 for j in range(5):box('Forceps_Grip_Groove',x+side*.012,.934,.225+j*.010,.008,.001,.002,'Dark',.0002)
box('Joined_Forceps_Heel',.17,.926,.19,.024,.007,.012,'Steel',.002)
# Opened peel pouch has an actually folded film flap and printed lot panel.
for i in range(2):
 x=.88+i*.09;z=.22
 box('Opened_Pouch_Base',x,.952,z,.074,.002,.095,'Paper',.001)
 mesh('Folded_Peel_Flap',[(x-.035,.954,z-.04),(x+.035,.954,z-.04),(x+.030,.968,z+.005),(x+.029,.978,z+.030),(x-.030,.980,z+.028),(x-.032,.967,z+.003)],[(0,1,2,5),(5,2,3,4)],'Paper',.0004)
 printed('Pouch_Lot_Print',[(x-.032,.954,z+.005),(x+.032,.954,z+.005),(x+.032,.954,z+.044),(x-.032,.954,z+.044)],[(.50,.75),(.75,.75),(.75,.50),(.50,.50)],'Labels')
for i in range(3):
 x=-.25+i*.10;z=-.11+i*.055
 printed('Sealed_Pouch_Print',[(x-.040,.9555,z+.022),(x+.040,.9555,z+.022),(x+.040,.9555,z+.060),(x-.040,.9555,z+.060)],[(.50,1),(.75,1),(.75,.75),(.50,.75)],'Labels')
# The displayed signal comes from a plugged cable, not from an unexplained screen.
port(.58,1.22,-.26,.012);port(-.82,1.03,-.34,.012)
cable('Headbox_To_Analyzer',[(.58,1.22,-.24),(.65,1.15,-.19),(.65,.96,-.24),(.07,.94,-.28),(-.38,.94,-.29),(-.82,1.03,-.32)],.0035)
# Used lead has terminal hardware at both ends.
cyl('Return_Lead_Plug',(.83,.955,-.145),(.83,.955,-.115),.007,'Steel',16)
save('LB_ElectrodePrepBench')
