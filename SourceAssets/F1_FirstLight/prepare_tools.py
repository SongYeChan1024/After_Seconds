"""Create scoped review tools; never invoke the previous phase's Apply/Before."""
from pathlib import Path
H=Path(__file__).resolve().parent
P=H.parent/'F1_SunsetSky'
for name in ['Inspect.cs','PlayCheck.cs','Finish.cs','Check.cs']:
    s=(P/name).read_text(encoding='utf8')
    s=s.replace('F1Sunset','F1FirstLight').replace('1F_SunsetSky/','1F_FirstLight/').replace('AfterSeconds_SunsetSky_','AfterSeconds_FirstLight_')
    s=s.replace('renderPostProcessing=false','renderPostProcessing=true')
    if name=='Inspect.cs':
        s=s.replace('File.Copy(s.path,b+"/Level_1F_Factory.unity",false);','File.Copy(s.path,b+"/Level_1F_Factory.unity",false);foreach(string asset in new[]{"FS_SunsetSky.shader","FS_SunsetSky.shader.meta","Materials/FS_SunsetSky.mat","Materials/FS_SunsetSky.mat.meta"})File.Copy("Assets/Afrer_Seconds/05.Model/Environment/1F/"+asset,b+"/"+Path.GetFileName(asset),false);')
    if name=='Check.cs':
        start=s.index(' public static object Refine()')
        end=s.index(' public static object Run()',start)
        s=s[:start]+s[end:]
        s=s.replace('if(path==sun&&q.key=="rotation")continue;','')
        s=s.replace('allowedTransformChange=sun+" rotation",','allowedTransformChange="None",')
    (H/name).write_text(s,encoding='utf8')
assert '1F_SunsetSky/' not in (H/'Inspect.cs').read_text()
print('FirstLight review tools ready')
