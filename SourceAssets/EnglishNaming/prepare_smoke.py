from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-08_EnglishNaming';O.mkdir(exist_ok=True)
s=(R/'SourceAssets/B4_ExperimentOperations/Play.cs').read_text(encoding='utf8').replace('BEOPlay','ENPlay').replace('2026-11-08_B4_ExperimentOperations','2026-11-08_EnglishNaming')
s=s.replace('if(!SceneManager.GetActiveScene().path.EndsWith("Level_B4_Circular.unity"))throw new Exception("B4 required");','')
s=s.replace(' static object Start(', ' public static object B5()=>Start("B5",new Vector3(-9.2f,-81.32f,-10),270,.55f);\n static object Start(')
(H/'Play.cs').write_text(s,encoding='utf8')
for folder in ['B4_ExperimentOperations','B4_FullFloor','B4_Observation','B5_CeilingLighting']:
 p=R/'SourceAssets'/folder/'README.md';s=p.read_text(encoding='utf8');title,body=s.split('\n',1);assert 'V0.01' in title
 p.write_text(title.replace('V0.01','V0.02')+'\n'+body+'\n- V0.02 (2026-11-08): 영문 이름 전환과 최신 검수 도구/이전 생성기 구분. 송예찬.\n',encoding='utf8')
