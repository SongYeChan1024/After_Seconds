from pathlib import Path
import shutil
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_T02_StairA'
p=D/'play_inside.json'
if p.exists() and not (D/'play_inside_unfocused.json').exists():shutil.copy2(p,D/'play_inside_unfocused.json')
p=H/'Play.cs';s=p.read_text(encoding='utf-8')
s=s.replace('static InputSettings.BackgroundBehavior background;','static InputSettings.BackgroundBehavior background;static InputSettings.EditorInputBehaviorInPlayMode editorBehavior;')
s=s.replace('background=InputSystem.settings.backgroundBehavior;', 'editorBehavior=InputSystem.settings.editorInputBehaviorInPlayMode;InputSystem.settings.editorInputBehaviorInPlayMode=InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;var view=typeof(Editor).Assembly.GetType("UnityEditor.GameView");EditorWindow.GetWindow(view).Focus();background=InputSystem.settings.backgroundBehavior;')
s=s.replace('InputSystem.settings.backgroundBehavior=background;', 'InputSystem.settings.backgroundBehavior=background;InputSystem.settings.editorInputBehaviorInPlayMode=editorBehavior;')
p.write_text(s,encoding='utf-8')
