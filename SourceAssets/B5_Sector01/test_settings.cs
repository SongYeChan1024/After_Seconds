var t=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("Unity.Pipeline.Editor.Commands.AutoTickCommand")).FirstOrDefault(x=>x!=null);
var flags=System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.NonPublic;
var data=new{autoTick=(bool)t.GetProperty("IsEnabled",flags).GetValue(null),interval=(long)t.GetProperty("CurrentIntervalMs",flags).GetValue(null),runInBackground=UnityEngine.Application.runInBackground};
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(UnityEngine.Application.dataPath,"../../../SourceAssets/B5_Sector01/test_settings.json")),Newtonsoft.Json.JsonConvert.SerializeObject(data));
return data;
