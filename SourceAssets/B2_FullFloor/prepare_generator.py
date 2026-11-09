from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/B3_FullFloor/varco_import.py').read_text(encoding='utf8')
s=s.replace("Props/B3","Props/B2").replace("[('B3_CryogenicDewar',1.20),('B3_SealedSampleCarrier',.43)]","[('B2_EmergencyGenerator',1.80)]").replace("cam.data.ortho_scale=height*1.55","cam.data.ortho_scale=max((high-low)*scale)*1.45").replace("B3_VARCO_READY","B2_VARCO_READY")
(H/'varco_import.py').write_text(s,encoding='utf8')
