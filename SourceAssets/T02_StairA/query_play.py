from pathlib import Path
import subprocess,json,sys
H=Path(__file__).resolve().parent;R=H.parents[1];CLI='C:/Users/Administrator/AppData/Local/Unity/bin/unity.exe'
query=sys.argv[1] if len(sys.argv)>1 else 'editor'
cmd=[CLI,'command','--query',query,'--caller','plugin','--skill','unity-cli','--project-path',str(R/'Unity/After_Seconds_Build_V0.01'),'--format','json']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');d=json.loads(r.stdout)
(H/(query+'_commands.json')).write_text(r.stdout,encoding='utf-8')
print(json.dumps([dict(command=c['command'],parameters=c['parameters']) for c in d['data']['commands'] if c['group'] in ['editor','play','playmode','wait','capture']],ensure_ascii=True,indent=2))
