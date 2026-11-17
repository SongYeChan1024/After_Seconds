from pathlib import Path
root = Path(__file__).resolve().parents[2]
source = root/'SourceAssets/FirstPersonMotion/ValidatePlay.cs'
s = source.read_text(encoding='utf-8-sig').replace('2026-11-17_FirstPersonMotion','2026-11-17_VarcoFirstPerson')
s = s.replace('float until=Time.time+.85f', 'float until=Time.time+1.6f')
s = s.replace('var log=new System.Text.StringBuilder();', '''var originalInputSettings=UnityEngine.InputSystem.InputSystem.settings;
var captureInputSettings=UnityEngine.Object.Instantiate(originalInputSettings);
var motion=AssetDatabase.LoadAssetAtPath<PlayerHandAnimationSet>("Assets/Afrer_Seconds/06.Data/PlayerHandAnimations.asset");
var log=new System.Text.StringBuilder();''')
s = s.replace('t.ExitStance();zoom.SetZoomed(false);motor.TryStandUp();Teleport(testHome', 't.ExitStance();if(t.IsUnderhand){t.ToggleStance();t.ToggleThrowMode();t.ExitStance();}zoom.SetZoomed(false);motor.TryStandUp();Teleport(testHome')
s = s.replace('QualitySettings.vSyncCount=0;Application.targetFrameRate=60;', '''captureInputSettings.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;
        captureInputSettings.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
        UnityEngine.InputSystem.InputSystem.settings=captureInputSettings;
        Check("VARCO animation set connected",h.UsesAnimationClips);
        Check("three humanoid sources",motion.walkSource.isHumanMotion&&motion.runSource.isHumanMotion&&motion.overhandSource.isHumanMotion);
        Check("walk loop continuous",Vector3.Distance(motion.walkRight.Evaluate(0),motion.walkRight.Evaluate(1))<.001f&&Vector3.Distance(motion.walkLeft.Evaluate(0),motion.walkLeft.Evaluate(1))<.001f);
        Check("run loop continuous",Vector3.Distance(motion.runRight.Evaluate(0),motion.runRight.Evaluate(1))<.001f&&Vector3.Distance(motion.runLeft.Evaluate(0),motion.runLeft.Evaluate(1))<.001f);
        Check("follow-through returns smoothly",motion.releaseRight.Evaluate(0).magnitude<.001f&&motion.releaseRight.Evaluate(1).magnitude<.001f&&motion.releaseLeft.Evaluate(1).magnitude<.001f);
        Check("follow-through has motion",Enumerable.Range(0,21).Max(i=>motion.releaseRight.Evaluate(i/20f).magnitude)>.025f);
        QualitySettings.vSyncCount=0;Application.targetFrameRate=60;''')
s = s.replace('Check("release once",t.ReleaseThrow()', 'int releaseFrame=Time.frameCount;Check("release once",t.ReleaseThrow()')
s = s.replace('Check("duplicate release refused",!t.ReleaseThrow());', 'Check("VARCO follow-through starts without delay",Time.frameCount==releaseFrame&&h.Pose=="Recover");Check("duplicate release refused",!t.ReleaseThrow());')
s = s.replace('Application.targetFrameRate=oldFPS;QualitySettings.vSyncCount=oldVSync;', 'Application.targetFrameRate=oldFPS;QualitySettings.vSyncCount=oldVSync;UnityEngine.InputSystem.InputSystem.settings=originalInputSettings;UnityEngine.Object.Destroy(captureInputSettings);')
s = s.replace('UnityEngine.InputSystem.InputSystem.settings=captureInputSettings;', '''UnityEngine.InputSystem.InputSystem.settings=captureInputSettings;
        UnityEngine.InputSystem.InputSystem.EnableDevice(keyboard);UnityEngine.InputSystem.InputSystem.EnableDevice(mouse);
        EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();''')
(root/'SourceAssets/VarcoFirstPerson/ValidatePlay.cs').write_text(s,encoding='utf-8')
c=(root/'SourceAssets/FirstPersonMotion/CaptureFinal.cs').read_text(encoding='utf-8-sig').replace('2026-11-17_FirstPersonMotion','2026-11-17_VarcoFirstPerson')
c=c.replace('t.CancelAim();zoom.SetZoomed(true);', '''t.ExitStance();Home();Pitch(30);t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.35f);Capture("overhand_prepared");
        t.ReleaseThrow();yield return new WaitForSeconds(.08f);Capture("overhand_release_08");yield return new WaitForSeconds(.08f);Capture("overhand_release_16");yield return new WaitForSeconds(.14f);Capture("overhand_release_30");yield return new WaitForSeconds(.4f);Capture("overhand_recovered");
        Home();Pitch(38);t.ToggleStance();t.BeginAim();
        t.CancelAim();zoom.SetZoomed(true);''')
c=c.replace('Home();UnityEngine.InputSystem.InputSystem.settings=originalInputSettings;', 'Home();foreach(var obj in UnityEngine.Object.FindObjectsByType<ThrownObject>(FindObjectsSortMode.None))if(obj.name.Contains("Clone"))UnityEngine.Object.Destroy(obj.gameObject);UnityEngine.InputSystem.InputSystem.settings=originalInputSettings;')
c=c.replace('UnityEngine.InputSystem.InputSystem.settings=captureInputSettings;', '''UnityEngine.InputSystem.InputSystem.settings=captureInputSettings;
        UnityEngine.InputSystem.InputSystem.EnableDevice(keyboard);UnityEngine.InputSystem.InputSystem.EnableDevice(mouse);
        EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();''')
(root/'SourceAssets/VarcoFirstPerson/CaptureFinal.cs').write_text(c,encoding='utf-8')
