from pathlib import Path
H=Path(__file__).resolve().parent;old=H.parent/'C01_InstrumentDetail'
for file in ['Capture.cs','FinalAudit.cs','Audit.cs','VerifyC01Routes.cs','PlayC01.cs']:
    txt=(old/file).read_text('utf-8').replace('2026-11-07_C01_InstrumentDetail','2026-11-07_C01_PropFinish').replace('SourceAssets/C01_InstrumentDetail/','SourceAssets/C01_PropFinish/')
    if file=='Capture.cs':
        txt=txt.replace('"ID_BenchAutoclave","ID_MicroplateHandler"','"ID_BenchAutoclave","ID_MicroplateHandler","CP_Centrifuge","ID_UltrasonicBath","ID_DualMagneticStirrer","ID_PipetteWorkstation","ID_GlasswareDryingRack","ID_LabelPrinter","ID_SterileSealer"')
        txt=txt.replace('target3+t.forward*1.4f+t.right*.6f+Vector3.up*.50f','target3+t.forward*1.10f+t.right*.42f+Vector3.up*.60f').replace('images=prefix=="After"?17:7','images=prefix=="After"?24:7')
        txt=txt.replace('Single(x=>x.name==n);var target3','First(x=>x.name==n);var target3')
    (H/file).write_text(txt,encoding='utf-8')
