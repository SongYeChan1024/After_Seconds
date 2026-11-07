from pathlib import Path
import shutil
H=Path(__file__).resolve().parent;R=H.parents[1];S=H.parent/'B5_DestinationColors'
shutil.copy2(S/'survey.json',H/'survey_guides.json')
s=(S/'build_plan.py').read_text(encoding='utf-8').replace("H/'survey.json'","H/'survey_guides.json'")
s=s.replace("west=resample([origin,np.array([-44.,28.])])", "west=join(resample([origin,np.array([-40.4,26.364])]),np.array([(1-t)**3*np.array([-40.4,26.364])+3*(1-t)**2*t*np.array([-41.765,26.985])+3*(1-t)*t*t*np.array([-41.9,25.45])+t**3*np.array([-43.3,25.45]) for t in np.linspace(0,1,61)]),resample([np.array([-43.3,25.45]),np.array([-44.96,25.45])]))")
s=s.replace("offset(main,-.48,True)","offset(main,-.32,True)").replace("offset(trim(main,start=1.4),-.16)","offset(trim(main,start=1.4),0)")
s=s.replace("blue=offset(trim(base,start=1.4,end=2),.16)","blue=offset(trim(base,start=1.4,end=2),.32)").replace("np.array([.16,", "np.array([.32,")
s=s.replace("fromwest=offset(trim(west,start=2),.16)","fromwest=offset(trim(west,start=2),.32)")
s=s.replace("plan=dict(title='B5 목적지 색 안내선 V0.01'", "routes=[r for r in routes if r['code']!='C04' and r['id']!='C02_FromC04']\ndestinations={k:destinations[k] for k in ['C01','C02','VA']}\nplan=dict(title='T02 계단A 연결 목적지 안내선 V0.01'")
s=s.replace("scope='C01 north approach, T01, C02, T02 to VA, T05 to inside C04; other B5 destinations pending'", "scope='C01/T01/C02/T02/VA stair foot only; other destinations deferred'")
s=s.replace('width=1.30,length=1.80','width=1.30,length=1.45').replace('width=1.0,length=1.38','width=1.0,length=1.115')
s=s.replace("(H/'plan.json').write_text", "plan['coreLegend']=dict(position=(-43.2,24.0),forward=(0,1),width=1.0,length=1.115)\n(H/'plan.json').write_text")
(H/'build_guides.py').write_text(s,encoding='utf-8')
for name in ['Apply.cs','Probe.cs','RouteWalk.cs','verify_plan.py','textures.py','Feeds.cs','refresh_feeds.py','RecordSource.cs']:
    s=(S/name).read_text(encoding='utf-8').replace('B5_DestinationColors','T02_StairA').replace('class Destination','class StairAGuide')
    if name=='Apply.cs':
        s=s.replace('destinations=4','destinations=3').replace('foreach(string code in new[]{"C01","C04","VA"})Assign', 'foreach(string code in new[]{"C01","VA"})Assign')
        s=s.replace('var legend=plan["legend"];','c02.Find("SC_Destination_VA").GetComponent<Renderer>().enabled=true;\n var core=plan["coreLegend"];var coreGeo=new Geo();coreGeo.Rect(V(core["position"]),Vector3.forward,(float)core["width"],(float)core["length"]);Add("ND_Core_Destinations",coreGeo,Mat("ND_Legend_VA",Color.white,"ND_Legend_VA"));\n var legend=plan["legend"];')
        s=s.replace('p.y=y+.0035f;', 'if(Vector2.Distance(new Vector2(p.x,p.z),new Vector2(-44,28))<4.94f)y=Mathf.Max(y,-81.99f);var t2=root.Find("T02_StairA_Art/T02_Corridor");var local2=t2.InverseTransformPoint(p);if(Mathf.Abs(local2.x)<2.02f&&local2.z>.3f&&local2.z<13.4661f)y=Mathf.Max(y,-81.99f);p.y=y+.0035f;')
        s=s.replace('/apply.json','/guide_apply.json')
    if name=='textures.py':
        s=s.replace('(1040,1440)','(1040,1160)').replace("print('4 destination stencils and 2 four-colour floor legends')", "d.rectangle((0,130,1040,224),fill=(0,0,0,0));centered(d,'VA / 계단 A',145,46,1040,col);im.save(O/'ND_Legend_VA.png')\nprint('3 destination stencils and 3 legends')")
    if name=='verify_plan.py':
        s=s.replace("H/'survey.json'","H/'survey_guides.json'")
        s=s.replace('labelchecks=[]', "x,z=p['coreLegend']['position'];w=p['coreLegend']['width']/2;h=p['coreLegend']['length']/2\nlabels.append(('CoreLegend',np.array([[x-w,z-h],[x+w,z-h],[x+w,z+h],[x-w,z+h],[x-w,z-h]])))\nlabelchecks=[]")
    if name=='RecordSource.cs':
        s=s.replace('plan["legend"],plan["labLegend"]','plan["legend"],plan["labLegend"],plan["coreLegend"]').replace('C01/T01/C02/T02/VA/T05/C04 only; remaining B5 destinations pending','C01/T01/C02/T02/VA; actual 16m stairs to B4 landing, B4 scene connection pending')
    newname={'Apply.cs':'GuideApply.cs','Probe.cs':'GuideProbe.cs','RouteWalk.cs':'GuideWalk.cs','RecordSource.cs':'RecordSource.cs'}.get(name,name)
    (H/newname).write_text(s,encoding='utf-8')
print('Prepared three destination route extension')
