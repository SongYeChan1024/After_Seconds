from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/B4_ExperimentOperations/Review.cs').read_text(encoding='utf8')
s=s.replace('BEOReview','B4PolishReview').replace('SourceAssets/B4_ExperimentOperations/layout.json','SourceAssets/B4_LayoutPolish/layout.json')
start=s.index('static string O=>');end=s.index(';',start)
s=s[:start]+'static string O=>R+"/Docs/Review/2026-11-09_B4_LayoutPolish/"'+s[end:]
s=s.replace('return result;','return new{tested=results.Count,planningFailures=failures,failed=results.Count(x=>!(bool)x.GetType().GetProperty("passed").GetValue(x))};')
(H/'Review.cs').write_text(s,encoding='utf8')
s=(R/'SourceAssets/B4_ExperimentOperations/Play.cs').read_text(encoding='utf8').replace('BEOPlay','B4PolishPlay')
start=s.index('static string O=>');end=s.index(';',start)
s=s[:start]+'static string O=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-09_B4_LayoutPolish/"))'+s[end:]
(H/'Play.cs').write_text(s,encoding='utf8')
