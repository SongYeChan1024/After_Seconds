from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;p=H/'Play.cs';s=p.read_text(encoding='utf8')
rooms=json.loads((H/'layout.json').read_text(encoding='utf8'))['rooms'];lines=[]
for r in rooms:
 if r['id'] not in ['C01','C03','C05','VB']:continue
 d=r['doors'][0];length=math.hypot(d['x'],d['z']);x=r['x']+(r['r']-.9)*d['x']/length;z=-r['v']+(r['r']-.9)*d['z']/length;yaw=math.degrees(math.atan2(-d['x'],-d['z']))
 lines.append(f' public static object {r["id"]}()=>Start("{r["id"]}",new Vector3({x:.5f}f,-65.32f,{z:.5f}f),{yaw:.5f}f,.55f);')
assert 'public static object C01()' not in s
s=s.replace(' static object Start(', '\n'.join(lines)+'\n static object Start(');p.write_text(s,encoding='utf8')
