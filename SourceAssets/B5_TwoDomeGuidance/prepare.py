from pathlib import Path
import json, hashlib, shutil

H=Path(__file__).resolve().parent; R=H.parents[1]; S=H.parent/'B5_DestinationColors'
D=R/'Docs/검수/2026-11-08_B5_TwoDomeGuidance'; D.mkdir(parents=True,exist_ok=True)
if (H/'baseline.json').exists(): raise SystemExit('Baseline already exists')
A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
(H/'baseline.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
for name in ['Prepare.cs','Inspect.cs','Apply.cs','Audit.cs','Probe.cs','RouteWalk.cs','Capture.cs','LabCapture.cs','T01Capture.cs','Feeds.cs','RecordSource.cs','verify_plan.py','refresh_feeds.py']:
    t=(S/name).read_text(encoding='utf-8').replace('B5_DestinationColors','B5_TwoDomeGuidance').replace('AfterSeconds_DestinationColors_','AfterSeconds_TwoDomeGuidance_').replace('class Destination','class TwoDome')
    if name=='Apply.cs':
        t=t.replace('"C01_FromVA"','"C01_FromC02"').replace('destinations=4','destinations=2')
        t=t.replace('foreach(string code in new[]{"C01","C04","VA"})Assign(c02.Find("SC_Destination_"+code).GetComponent<Renderer>(),labels[code]);','Assign(c02.Find("SC_Destination_C01").GetComponent<Renderer>(),labels["C01"]);foreach(string code in new[]{"C04","VA"}){var rr=c02.Find("SC_Destination_"+code).GetComponent<Renderer>();rr.enabled=false;changedRenderers.Add(PathOf(rr.transform));}')
        t=t.replace('foreach(var f in Directory.GetFiles', 'foreach(var f in Directory.GetFiles')
    if name=='Audit.cs':
        t=t.replace('before["hierarchy"].Where(j=>!current.Any', 'before["hierarchy"].Where(j=>!((string)j["path"]).Contains("/Destination_Colour_Guidance/")).Where(j=>!current.Any')
    if name=='RecordSource.cs':
        t=t.replace('Four destination colours', 'Two destination colours')
    (H/name).write_text(t,encoding='utf-8')
shutil.copy2(S/'survey.json',H/'survey.json')
t=(S/'build_plan.py').read_text(encoding='utf-8')
start=t.index("route('C01_FromVA'"); end=t.index('destinations=')
t=t[:start]+'''# Exactly two destination lanes between the currently authored domes.
blue=offset(trim(base,start=1.4,end=2),.16);joinpoint=origin+np.array([.16,1.50]);ops=origin+np.array([.16,2.20])
route('C02_FromC01','C02',join(blue,quad(blue[-1],origin+np.array([.16,-.1]),joinpoint),resample([joinpoint,ops])))
cyan=offset(trim(base,end=2),-.16,True);cyanjoin=origin+np.array([-.16,1.50]);cyanops=origin+np.array([-.16,2.20])
route('C01_FromC02','C01',join(cyan,quad(cyan[-1],origin+np.array([-.16,-.1]),cyanjoin),resample([cyanjoin,cyanops])),True)
'''+t[end:]
t=t.replace("plan=dict(title='B5 목적지 색 안내선 V0.01'", "destinations={k:destinations[k] for k in ['C01','C02']}\nplan=dict(title='B5 두 돔 목적지 안내선 V0.01'")
t=t.replace("scope='C01 north approach, T01, C02, T02 to VA, T05 to inside C04; other B5 destinations pending'", "scope='C01 to C02 through T01 only; all other destinations deferred until their dome is authored'")
t=t.replace('width=1.30,length=1.80','width=1.30,length=1.10').replace('width=1.0,length=1.38','width=1.0,length=.846')
(H/'build_plan.py').write_text(t,encoding='utf-8')
t=(S/'textures.py').read_text(encoding='utf-8').replace('(1040,1440)','(1040,880)').replace('4 destination stencils and 2 four-colour floor legends','2 destination stencils and 2 two-colour floor legends')
(H/'textures.py').write_text(t,encoding='utf-8')
print('Prepared isolated two-dome authoring sources and asset baseline')
