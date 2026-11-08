from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/B4_FullFloor/Review.cs').read_text(encoding='utf8').replace('BFFReview','BEOReview').replace('B4_FullFloor','B4_ExperimentOperations')
a=s.index(' public static object Audit()');b=s.index(' static bool Free(',a);s=s[:a]+s[b:]
needle='var doors=room["doors"].Select(d=>center+new Vector3((float)d["x"],0,(float)d["z"])).ToArray();'
replacement='''var portalDoors=room["doors"].Select(d=>center+new Vector3((float)d["x"],0,(float)d["z"])).ToArray();var access=plan["workspaces"].Where(q=>(string)q["room"]==id).ToArray();var doors=portalDoors.Concat(access.Select(q=>center+new Vector3((float)q["point"][0],0,(float)q["point"][2]))).ToArray();'''
assert needle in s;s=s.replace(needle,replacement)
s=s.replace('int start=Nearest(doors[0]),end=Nearest(doors[d]);','int start=Nearest(doors[0]),end=Nearest(doors[d]);if(d>=portalDoors.Length&&Vector3.Distance(Pos(end),doors[d])>.70f){failures.Add(id+" workspace not accessible "+(string)access[d-portalDoors.Length]["name"]+" delta="+Vector3.Distance(Pos(end),doors[d]));continue;}')
s=s.replace('route.Add(doors[d]);paths.Add','if(d<portalDoors.Length)route.Add(doors[d]);paths.Add')
s=s.replace('results.Add(Travel(cc,player,id+"_door_0_"+d,route));route.Reverse();results.Add(Travel(cc,player,id+"_door_"+d+"_0",route));','results.Add(Travel(cc,player,id+(d<portalDoors.Length?"_door_0_"+d:"_work_"+(string)access[d-portalDoors.Length]["name"]),route));if(d<portalDoors.Length){route.Reverse();results.Add(Travel(cc,player,id+"_door_"+d+"_0",route));}')
(H/'Review.cs').write_text(s,encoding='utf8')
for file,old,new in [('Play.cs','BFFPlay','BEOPlay'),('play_checks.py','BFFPlay','BEOPlay'),('InspectDirty.cs','BFFInspectDirty','BEOInspectDirty')]:
 s=(R/'SourceAssets/B4_FullFloor'/file).read_text(encoding='utf8').replace(old,new).replace('B4_FullFloor','B4_ExperimentOperations');(H/file).write_text(s,encoding='utf8')
