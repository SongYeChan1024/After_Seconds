from pathlib import Path
H=Path(__file__).resolve().parent;S=H.parent
s=(S/'C01_Lighting/PlayC01.cs').read_text(encoding='utf-8').replace('PlayC01','PlayC02').replace('2026-11-07_C01_Lighting','2026-11-08_C02_Security').replace('new Vector3(-9.3f,-81.32f,-10f),0','new Vector3(-21.6f,-81.32f,16.2f),0').replace('new Vector3(-65f,-81.32f,-20.76f),77.85f','new Vector3(-28.1908f,-81.32f,20.814f),114.444f')
(H/'Play.cs').write_text(s,encoding='utf-8')
s=(S/'T01_CorridorFinish/PlayCapture.cs').read_text(encoding='utf-8').replace('T01PlayCapture','C02PlayCapture').replace('2026-11-07_T01_Corridor','2026-11-08_C02_Security').replace('Play_Threshold.png','Play_Operations.png');(H/'PlayCapture.cs').write_text(s,encoding='utf-8')
print('C02 Play checks prepared')
