from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'B1_FullFloor'))
import common as c
c.H=HERE
from common import reset,box,cyl,save,b
reset()
box('MeetingTableTop',0,.755,0,4.2,.075,1.45,'Warm',.035)
box('Underframe',0,.685,0,3.6,.065,.70,'Steel',.009)
for x in [-1.30,1.30]:
 box('TrestleFoot',x,.035,0,.62,.055,1.05,'Steel',.015)
 for z in [-.36,.36]:box('TrestlePost',x,.38,z,.065,.635,.065,'Steel',.006)
 for z in [-.44,.44]:box('RubberPad',x,.0075,z,.31,.015,.15,'Rubber',.005)
for x in [-.65,.65]:box('CableLid',x,.796,0,.31,.007,.13,'Dark',.003)
for x in [-1.4,0,1.4]:
 for z in [-.47,.47]:
  box('ReportFolder',x,.803,z,.31,.017,.32,'Teal',.003)
  box('ReportPaper',x,.815,z,.284,.006,.298,'Paper',.001)
  for k in range(5):box('PrintedLine',x,.8188,z-.08+k*.026,.21-.015*(k%2),.0015,.003,'Dark',0)
  cyl('MeetingPen',(x+.18,.800,z-.13),(x+.18,.800,z+.07),.005,'Dark',10)
save('ConferenceTable','Props',True)
reset()
box('PresentationBack',0,2,0,3.08,1.87,.12,'Dark',.022)
box('ScreenSurface',0,2,.063,2.91,1.65,.004,'Paper',.001)
# A single UV mapped optical face, separated from its backplate.
ob=b.print_panel('PresentationContent',0,2,.067,2.90,1.64,1)
for x in [-1.05,1.05]:
 box('StandFoot',x,.045,-.02,.56,.09,.70,'Steel',.018)
 box('StandColumn',x,.61,-.02,.065,1.04,.065,'Steel',.007)
box('CableCover',0,.61,-.08,.09,1.04,.04,'Dark',.007)
save('PresentationBoard','Props',True)
print('CONFERENCE MODELS COMPLETE',flush=True)
