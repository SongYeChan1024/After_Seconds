var pi=UnityEngine.Object.FindAnyObjectByType<UnityEngine.InputSystem.PlayerInput>();
return new {Application.isFocused,Application.runInBackground,keyboard=UnityEngine.InputSystem.Keyboard.current?.enabled,keyboardId=UnityEngine.InputSystem.Keyboard.current?.deviceId,mouse=UnityEngine.InputSystem.Mouse.current?.enabled,
    pi.inputIsActive,pi.enabled,pi.currentControlScheme,map=pi.currentActionMap?.name,devices=pi.devices.Select(d=>new{d.name,d.deviceId,d.enabled}).ToArray(),
    settings=UnityEngine.InputSystem.InputSystem.settings.name,UnityEngine.InputSystem.InputSystem.settings.backgroundBehavior,UnityEngine.InputSystem.InputSystem.settings.editorInputBehaviorInPlayMode,
    actions=pi.actions.actionMaps.Select(m=>new {m.name,m.enabled}).ToArray(),move=pi.actions.FindAction("Move").ReadValue<Vector2>()};
