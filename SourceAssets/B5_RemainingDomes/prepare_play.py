from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;R=H.parents[1];S=R/'SourceAssets/T02_StairA'
s=(S/'Play.cs').read_text(encoding='utf-8').replace('StairAPlay','RemainingPlay').replace('2026-11-08_T02_StairA','2026-11-08_B5_RemainingDomes')
a=s.index(' public static object Inside()');b=s.index(' static object Start(',a)
points=[('Living','living',[-88,-81.32,39.5],90),('Control','control',[0,-81.32,73.5],90),('Meal','meal',[124,-81.32,5.8],90),('Cooling','cooling',[17,-81.32,-7],90),('Lift','lift',[44,-81.32,25.2],90),('Stairs','stairs',[43.04,-81.32,-30],0)]
t=json.loads((H/'plan.json').read_text(encoding='utf-8'))['tunnels'][-1];dx=t['q'][0]-t['p'][0];dz=-t['q'][1]+t['p'][1];L=math.hypot(dx,dz);points.append(('Corridor','corridor',[t['p'][0]+dx/L*3,-81.32,-t['p'][1]+dz/L*3],math.degrees(math.atan2(dx,dz))))
s=s[:a]+''.join(' public static object '+m+'()=>Start("'+label+'",new Vector3('+','.join(f'{v:.6f}f' for v in p)+'),'+f'{yaw:.6f}f'+');\n' for m,label,p,yaw in points)+s[b:];(H/'Play.cs').write_text(s,encoding='utf-8')
s=(S/'run_play.py').read_text(encoding='utf-8').replace('2026-11-08_T02_StairA','2026-11-08_B5_RemainingDomes').replace('StairAPlay.','RemainingPlay.').replace('StairA_Play_','Remaining_Play_').replace("[('Inside','inside'),('Stairs','stairs')]",repr([(p[0],p[1]) for p in points]));(H/'run_play.py').write_text(s,encoding='utf-8')
