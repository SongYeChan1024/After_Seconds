from pathlib import Path
import json,shutil
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_DestinationColors'
for folder,cls,out in [('T01_CorridorFinish','T01CorridorCapture','T01Capture'),('C01_Wayfinding','C01WayfindingCapture','LabCapture')]:
 p=R/'SourceAssets'/folder/'Capture.cs';s=p.read_text(encoding='utf-8').replace(cls,'Destination'+out)
 s=s.replace('2026-11-07_T01_Corridor','2026-11-08_B5_DestinationColors/T01').replace('2026-11-07_C01_Wayfinding','2026-11-08_B5_DestinationColors/C01')
 (H/(out+'.cs')).write_text(s,encoding='utf-8');(D/('T01' if folder.startswith('T01') else 'C01')).mkdir(exist_ok=True)
backup=Path(json.loads((D/'backup.json').read_text(encoding='utf-8'))['backup'])/'camera_textures';backup.mkdir(exist_ok=True)
assets=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures'
for i in range(1,5):
 for suffix in ['.png','.png.meta']:
  p=assets/f'SC_Display_{i:02}{suffix}'
  if not (backup/p.name).exists():shutil.copy2(p,backup/p.name)
for name in ['Feeds.cs','refresh_feeds.py']:
 s=(R/'SourceAssets/C02_SecurityRefine'/name).read_text(encoding='utf-8').replace('2026-11-08_C02_Refine','2026-11-08_B5_DestinationColors').replace('C02RefineFeeds','DestinationFeeds')
 (H/name).write_text(s,encoding='utf-8')
print('Capture tools and current surveillance texture backup ready')
