from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];old=R/'SourceAssets/C01_Perimeter'
for n in ['FinalAudit','VerifyC01Routes','PlayC01']:
 s=(old/(n+'.cs')).read_text('utf-8').replace('2026-11-07_C01_Perimeter','2026-11-07_C01_InstrumentDetail')
 if n=='FinalAudit':
  s=s.replace('CP_ t:Model','t:Model').replace('.Select(AssetDatabase.GUIDToAssetPath).OrderBy(p=>p)', '.Select(AssetDatabase.GUIDToAssetPath).Where(p=>Path.GetFileName(p).StartsWith("CP_")||Path.GetFileName(p).StartsWith("ID_")).OrderBy(p=>p)')
 if n=='PlayC01':
  s=s.replace('static bool released;','static bool released,keyboardWasEnabled;').replace('InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.W));','keyboardWasEnabled=keyboard.enabled;if(!keyboardWasEnabled)InputSystem.EnableDevice(keyboard);InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.W));').replace('if(!released&&elapsed>.50)','if(elapsed<.50)InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.W));if(!released&&elapsed>.50)').replace('InputSystem.settings.backgroundBehavior=background;var sorted=','if(keyboard!=null&&!keyboardWasEnabled)InputSystem.DisableDevice(keyboard);InputSystem.settings.backgroundBehavior=background;var sorted=')
 (H/(n+'.cs')).write_text(s,encoding='utf-8')
s=(old/'Audit.cs').read_text('utf-8').replace('SourceAssets/C01_Perimeter/','SourceAssets/C01_InstrumentDetail/')
(H/'Audit.cs').write_text(s,encoding='utf-8')
print('Prepared final validation tools')
