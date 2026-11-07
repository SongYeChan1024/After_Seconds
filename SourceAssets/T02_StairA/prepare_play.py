from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];S=H.parent/'T01_CorridorFinish'
s=(S/'Play.cs').read_text(encoding='utf-8').replace('class PlayT01','class StairAPlay').replace('2026-11-07_T01_Corridor','2026-11-08_T02_StairA')
s=s.replace('new Vector3(-18.20f,-81.32f,2.81f),345.9637f','new Vector3(-30.0f,-81.32f,21.64f),294.44397f').replace('public static object Tunnel()=>Start("tunnel",new Vector3(-20.6418f,-81.32f,12.5672f),165.9637f);','public static object Stairs()=>Start("stairs",new Vector3(-44.96f,-81.32f,26.0f),0);')
s=s.replace('displacement=delta.magnitude,','displacement=delta.magnitude,rise=player.transform.position.y-from.y,')
(H/'Play.cs').write_text(s,encoding='utf-8')
print('Prepared two actual-input Play checks')
