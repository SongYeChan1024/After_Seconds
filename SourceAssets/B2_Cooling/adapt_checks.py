from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/Diagnostics/OnLook_20261109/Test.cs').read_text(encoding='utf8').replace('OnLookTest','B2Look').replace('SourceAssets/Diagnostics/OnLook_20261109/','Docs/Review/2026-11-09_B2_Cooling/').replace('OnLookDiag.Background','B2Look.Background');(H/'Look.cs').write_text(s,encoding='utf8')
s=(R/'SourceAssets/B3_FullFloor/LiveFrame.cs').read_text(encoding='utf8').replace('B3LiveFrame','B2LiveFrame').replace('2026-11-09_B3_FullFloor','2026-11-09_B2_Cooling');(H/'LiveFrame.cs').write_text(s,encoding='utf8')
