from pathlib import Path
H=Path(__file__).resolve().parent;S=H.parent
text=(S/'C01_Wayfinding/Walk.cs').read_text(encoding='utf-8').replace('C01WayfindingWalk','T01CorridorWalk').replace('new[]{"B5-T01","B5-T03","B5-T11"}','new[]{"B5-T01"}').replace('2026-11-07_C01_Wayfinding','2026-11-07_T01_Corridor')
(H/'Walk.cs').write_text(text,encoding='utf-8')
text=(S/'C01_Lighting/PlayC01.cs').read_text(encoding='utf-8').replace('PlayC01','PlayT01').replace('2026-11-07_C01_Lighting','2026-11-07_T01_Corridor').replace('new Vector3(-9.3f,-81.32f,-10f),0','new Vector3(-18.20f,-81.32f,2.81f),345.9637f').replace('new Vector3(-65f,-81.32f,-20.76f),77.85f','new Vector3(-20.6418f,-81.32f,12.5672f),165.9637f')
(H/'Play.cs').write_text(text,encoding='utf-8')
print('T01 corridor and doorway checks prepared')
