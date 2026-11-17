var assembly=typeof(Editor).Assembly;var logs=assembly.GetType("UnityEditor.LogEntries");var entryType=assembly.GetType("UnityEditor.LogEntry");var flags=System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic;
logs.GetMethod("StartGettingEntries",flags).Invoke(null,null);var entries=new System.Collections.Generic.List<object>();
try{int count=(int)logs.GetMethod("GetCount",flags).Invoke(null,null);for(int i=0;i<count;i++){var entry=System.Activator.CreateInstance(entryType);logs.GetMethod("GetEntryInternal",flags).Invoke(null,new object[]{i,entry});entries.Add(new{message=entryType.GetField("message").GetValue(entry),mode=entryType.GetField("mode").GetValue(entry)});}}
finally{logs.GetMethod("EndGettingEntries",flags).Invoke(null,null);}
return entries;
