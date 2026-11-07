from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/B5_RemainingDomes/Verify.cs').read_text(encoding='utf8').replace('RemainingVerify','SpatialVerify').replace('Remaining_Domes_Art','B5_Spatial_Refinement').replace('Remaining_DestinationGuidance','Spatial_DestinationGuidance').replace('B5_RemainingDomes','B5_SpatialRefinement').replace('sqrMagnitude<1e-15f','sqrMagnitude<1e-22f')
(H/'Verify.cs').write_text(s,encoding='utf8')
s=(H/'Audit.cs').read_text(encoding='utf8').replace('sqrMagnitude<1e-15f','sqrMagnitude<1e-22f');(H/'Audit.cs').write_text(s,encoding='utf8')
