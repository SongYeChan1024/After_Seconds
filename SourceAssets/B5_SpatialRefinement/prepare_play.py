from pathlib import Path
import json,math,re
H=Path(__file__).resolve().parent;plan=json.loads((H/'plan.json').read_text(encoding='utf8'))
cases=[('Security','C02',0,.1,0),('Cooling','C03',0,-4.8,0),('Utility','C04',0,-2.5,0),('Living','W01',0,2.2,0),('Isolation','W02',0,2.6,0),('Medical','W03',0,-1.8,0),('Receiving','E01',0,-2,0),('Meal','E02',-1.8,-3,0),('Decon','E03',0,-1.7,0),('Control','N01',4.2,-1.6,0),('TestCell','S01',0,-3.3,0),('StairA','VA',-.96,-2,0),('Stairs','VB',-.96,-2,0),('Lift','VL',0,-2.8,90)]
s=(H/'Play.cs').read_text(encoding='utf8');start=s.index(' public static object Living()');end=s.index(' static object Start',start);lines=[]
for name,room,x,z,yaw in cases:
 r=plan['rooms'][room];xx=r['x']+x;zz=-r['v']+z;lines.append(f' public static object {name}()=>Start("{name.lower()}",new Vector3({xx:.6f}f,-81.32f,{zz:.6f}f),{yaw:.1f}f);')
lines.append(' public static object LivingUnculled()=>Start("living_unculled",new Vector3(-88,-81.32f,40.2f),0,false);')
lines.append(' public static object Corridor()=>Start("corridor",new Vector3(-10.818387f,-81.32f,-70.360628f),-62.468023f);')
(H/'Play.cs').write_text(s[:start]+'\n'.join(lines)+'\n'+s[end:],encoding='utf8')
s=(H/'run_play.py').read_text(encoding='utf8');a=s.index('    for method,label in ');b=s.index(':\n',a);series=[('LivingUnculled','living_unculled')]+[(n,n.lower()) for n,*_ in cases]+[('Corridor','corridor')];s=s[:a]+'    for method,label in '+repr(series)+s[b:];s=s.replace("if '--stairs-only'", "if '--only' in sys.argv and label not in sys.argv[sys.argv.index('--only')+1].split(','):continue\n        if '--stairs-only'")
(H/'run_play.py').write_text(s,encoding='utf8')
p=H/'PostPlay.cs';s=p.read_text(encoding='utf8');s=s.replace('"living_unculled","living","control","meal","cooling","lift","stairs","corridor"',','.join('"'+label+'"' for _,label in series));p.write_text(s,encoding='utf8')
