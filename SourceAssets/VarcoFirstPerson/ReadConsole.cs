var asm=typeof(Editor).Assembly;var logs=asm.GetType("UnityEditor.LogEntries");var entryType=asm.GetType("UnityEditor.LogEntry");
var flags=System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Static;
var results=new List<object>();var fields=entryType.GetFields(System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance);
logs.GetMethod("StartGettingEntries",flags).Invoke(null,null);
try
{
    int count=(int)logs.GetMethod("GetCount",flags).Invoke(null,null);
    for(int i=0;i<count;i++)
    {
        var entry=System.Activator.CreateInstance(entryType);logs.GetMethod("GetEntryInternal",flags).Invoke(null,new object[]{i,entry});
        int mode=(int)fields.First(f=>f.Name=="mode").GetValue(entry);
        // Warning/ScriptingWarning. Keep errors too; ordinary logs have bit1024.
        if((mode&1024)!=0&&(mode&512)==0)continue;
        string message=(string)fields.First(f=>f.Name=="message").GetValue(entry);
        results.Add(new{mode,message});
    }
}
finally{logs.GetMethod("EndGettingEntries",flags).Invoke(null,null);}
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_VarcoFirstPerson/console.json")),Newtonsoft.Json.JsonConvert.SerializeObject(results,Newtonsoft.Json.Formatting.Indented));return results;
