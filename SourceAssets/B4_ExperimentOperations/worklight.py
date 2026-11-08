import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
reset();box('Anchored_Lamp_Base',0,.04,-.25,.48,.08,.62,'Steel',.016)
for x in [-.17,.17]:
 for z in [-.45,-.05]:cyl('Base_Anchor',(x,.082,z),(x,.098,z),.018,'Steel',12)
box('Task_Light_Mast',0,1.21,-.38,.06,2.34,.07,'Steel',.009)
cyl('Boom_Hinge',(-.06,2.36,-.38),(.06,2.36,-.38),.065,'Dark',24)
box('Task_Light_Boom',0,2.37,.03,.055,.07,.82,'Steel',.008)
box('Luminaire_Housing',0,2.36,.40,.82,.11,.19,'Coat',.016);box('Recessed_Diffuser',0,2.298,.40,.72,.016,.13,'Lamp',.005)
tube('Protected_Lamp_Cable',[(.04,2.34,.38),(.04,2.31,-.36),(.04,.2,-.36),(.14,.12,-.3)],.006)
box('Lamp_Switch_Housing',0,1.1,-.30,.13,.24,.07,'Dark',.01);buttons(0,1.1,-.26,1)
save('TaskLightPole')
