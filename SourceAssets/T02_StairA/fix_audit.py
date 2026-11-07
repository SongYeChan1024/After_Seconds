from pathlib import Path
p=Path(__file__).with_name('Audit.cs');s=p.read_text(encoding='utf-8')
old='var now=lights.Single(k=>(string)k["path"]==(string)b["path"]);var aa=(JObject)b.DeepClone();var bb=(JObject)now.DeepClone();aa.Remove("position");bb.Remove("position");if(!JToken.DeepEquals(aa,bb))badLightSettings.Add((string)b["path"]);'
new='var aa=(JObject)b.DeepClone();aa.Remove("position");if(!lights.Any(k=>{var bb=(JObject)k.DeepClone();bb.Remove("position");return JToken.DeepEquals(aa,bb);}))badLightSettings.Add((string)b["path"]);'
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
