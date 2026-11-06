from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/CircularDressing/prepare_varco.py').read_text('utf-8')
s=s.replace("Props/Common'","Props/B5'").replace('2026-11-06_CircularDressing','2026-11-06_B5_Sector01').replace('CFD_','S1_')
s=s.replace("sizes={'LinenHamper':(.65,.65,.95),'EmergencyCabinet':(.75,.45,1.4)}", "sizes={'IsolationBed':(.85,2.05,.80),'SanitaryUnit':(.6,.8,.95),'VitalMonitor':(.55,.55,1.48)}")
s=s.replace("factor=Vector((target[2]/dim.z,)*3)","factor=Vector(((2.05/max(dim.x,dim.y)) if name=='IsolationBed' else (target[2]/dim.z),)*3)")
s=s.replace("target=(dim.x*factor.x,dim.y*factor.y,target[2])","target=(dim.x*factor.x,dim.y*factor.y,dim.z*factor.z)")
s=s.replace("sc.cycles.samples=20","sc.cycles.samples=16")
s=s.replace("bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene", "bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene")
(H/'prepare_varco.py').write_text(s,encoding='utf-8')
