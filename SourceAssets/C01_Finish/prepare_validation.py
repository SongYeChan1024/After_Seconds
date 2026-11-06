from pathlib import Path
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
for name,new in [('VerifyFullLayout','VerifyC01Routes'),('WalkFullLayout','WalkC01Routes'),('DetailAudit','C01DoorAudit'),('PlayFullLayout','PlayC01')]:
    s=(R/'SourceAssets/B5_FullLayout'/(name+'.cs')).read_text('utf-8').replace(name,new).replace('2026-11-06_B5_FullLayout','2026-11-07_C01_Finish')
    if name=='WalkFullLayout':
        s=s.replace('foreach(var t in floor["tunnels"])','foreach(var t in floor["tunnels"].Where(t=>new[]{"B5-T01","B5-T03","B5-T11"}.Contains((string)t["id"])))')
    (H/(new+'.cs')).write_text(s,encoding='utf-8')
print('Prepared current-report validation tools; original tools and evidence preserved.')
