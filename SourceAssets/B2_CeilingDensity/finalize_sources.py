from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'Capture.cs';s=p.read_text(encoding='utf8').replace('l.intensity=6;','l.intensity=20;')
needle='} }finally{player.SetActive(on);'
replacement='''} if(prefix!="before"){
 Shot(prefix+"_focus_C02",new Vector3(19,-32.35f,-8.7f),new Vector3(19,-29.8f,3),inspect);
 Shot(prefix+"_focus_S01",new Vector3(0,-32.35f,-72.5f),new Vector3(0,-31.4f,-78.5f),inspect);
 Shot(prefix+"_focus_N01",new Vector3(0,-32.35f,71.8f),new Vector3(0,-30.8f,79),inspect);
 } }finally{player.SetActive(on);'''
if 'focus_C02' not in s:s=s.replace(needle,replacement)
s=s.replace('images=12,temporaryInspectionLight','images=prefix=="before"?12:15,temporaryInspectionLight')
p.write_text(s,encoding='utf8')
print('Diagnostic photos use temporary 20-intensity spot; actual-light focus views added.')
