from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];S=R/'SourceAssets/B2_Cooling'
for name in ['LodExport.cs','LodImport.cs','LodApply.cs','lods.py','Look.cs']:
 s=(S/name).read_text(encoding='utf8').replace('B2_Cooling','B2_FullFloor').replace('class B2','class BM')
 (H/name).write_text(s,encoding='utf8')
s=(S/'Review.cs').read_text(encoding='utf8');s=s[:s.index(' static void Shot')]+s[s.index(' public static object Audit()'):];s=s.replace('B2_Cooling','B2_FullFloor').replace('class B2Review','class BMAudit')
(H/'Audit.cs').write_text(s,encoding='utf8')
s=(S/'Play.cs').read_text(encoding='utf8').replace('B2_Cooling','B2_FullFloor').replace('B2Play','BMPlay')
start=s.index(' static void Next()');end=s.index(' static void Log',start)
s=s[:start]+''' static void Next(){var cc=player.GetComponent<CharacterController>();var starts=new[]{new Vector3(35.5f,-34,17.5f),new Vector3(-18,-34,4.3f),new Vector3(-124,-34,-8f),new Vector3(-44-2.55f,-34,-(-28)+.8f)};var yaws=new[]{-140f,90f,90f,0f};cc.enabled=false;player.transform.SetPositionAndRotation(starts[stage]+Vector3.up*(cc.height*.5f-cc.center.y+.05f),Quaternion.Euler(0,yaws[stage],0));cc.enabled=true;Physics.SyncTransforms();from=player.transform.position;first=last=Time.frameCount;start=EditorApplication.timeSinceStartup;frameTimes.Clear();}
'''+s[end:]
s=s.replace('new[]{"ground","west_stairs","east_stairs","upper_walkway"}','new[]{"pipe_tunnel","centrifuge_bypass","backup_power","stair_lobby"}')
(H/'Play.cs').write_text(s,encoding='utf8')
# Independent names keep existing C02 helpers and artifacts intact.
print('B2 full-floor review tools prepared')
