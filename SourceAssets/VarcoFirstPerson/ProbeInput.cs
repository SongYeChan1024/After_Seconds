var t=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();
var pi=t.GetComponent<UnityEngine.InputSystem.PlayerInput>();
var original=UnityEngine.InputSystem.InputSystem.settings;var temp=UnityEngine.Object.Instantiate(original);
var rows=new List<object>();
System.Collections.IEnumerator Run()
{
    try
    {
        temp.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;
        temp.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
        UnityEngine.InputSystem.InputSystem.settings=temp;
        EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();
        UnityEngine.InputSystem.InputSystem.EnableDevice(UnityEngine.InputSystem.Keyboard.current);
        UnityEngine.InputSystem.InputSystem.EnableDevice(UnityEngine.InputSystem.Mouse.current);
        yield return new WaitForSeconds(.3f);
        for(int i=0;i<30;i++)
        {
            UnityEngine.InputSystem.InputSystem.QueueStateEvent(UnityEngine.InputSystem.Keyboard.current,new UnityEngine.InputSystem.LowLevel.KeyboardState(UnityEngine.InputSystem.Key.W));
            UnityEngine.InputSystem.InputSystem.Update();
            bool immediate=UnityEngine.InputSystem.Keyboard.current.wKey.isPressed;
            yield return null;
            rows.Add(new{Time.frameCount,immediate,enabled=UnityEngine.InputSystem.Keyboard.current.enabled,sameSettings=UnityEngine.InputSystem.InputSystem.settings==temp,pressed=UnityEngine.InputSystem.Keyboard.current.wKey.isPressed,move=pi.actions.FindAction("Move").ReadValue<Vector2>().ToString(),speed=t.GetComponent<CharacterController>().velocity.magnitude,devices=pi.devices.Select(d=>d.name+":"+d.deviceId).ToArray(),background=UnityEngine.InputSystem.InputSystem.settings.backgroundBehavior.ToString(),input=UnityEngine.InputSystem.InputSystem.settings.editorInputBehaviorInPlayMode.ToString()});
        }
    }
    finally
    {
        UnityEngine.InputSystem.InputSystem.QueueStateEvent(UnityEngine.InputSystem.Keyboard.current,new UnityEngine.InputSystem.LowLevel.KeyboardState());
        UnityEngine.InputSystem.InputSystem.settings=original;UnityEngine.Object.Destroy(temp);
        System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../SourceAssets/VarcoFirstPerson/input_probe.json")),Newtonsoft.Json.JsonConvert.SerializeObject(rows,Newtonsoft.Json.Formatting.Indented));
    }
}
t.StartCoroutine(Run());return "probe running";
