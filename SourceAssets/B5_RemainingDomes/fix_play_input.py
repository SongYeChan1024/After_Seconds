from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'Play.cs';s=p.read_text(encoding='utf-8')
s=s.replace('static double start;', 'static Mouse mouse;static bool mouseWasEnabled;static double start;')
s=s.replace('label=id;frameTimes.Clear();','mouse=Mouse.current;mouseWasEnabled=mouse!=null&&mouse.enabled;if(mouseWasEnabled)InputSystem.DisableDevice(mouse);label=id;frameTimes.Clear();')
s=s.replace('InputSystem.settings.backgroundBehavior=background;', 'if(mouseWasEnabled&&mouse!=null)InputSystem.EnableDevice(mouse);InputSystem.settings.backgroundBehavior=background;')
s=s.replace('device="Existing keyboard through Input System; W down/up; focus override restored"','device="Existing keyboard W down/up; mouse disabled during sample then restored; focus override restored"')
p.write_text(s,encoding='utf-8')
p=H/'run_play.py';s=p.read_text(encoding='utf-8');s=s.replace("for method,label in [('Living', 'living'), ('Control', 'control'), ('Meal', 'meal'), ('Cooling', 'cooling'), ('Lift', 'lift'), ('Stairs', 'stairs'), ('Corridor', 'corridor')]:", "for method,label in [('Stairs','stairs'),('Corridor','corridor'),('Living','living')]:")
p.write_text(s,encoding='utf-8')
