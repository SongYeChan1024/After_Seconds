if(!Application.isPlaying)throw new System.Exception("Play required");
var inv=UnityEngine.Object.FindAnyObjectByType<PlayerInventory>();var t=inv.GetComponent<PlayerThrow>();var h=inv.GetComponent<PlayerFirstPersonHands>();var cc=inv.GetComponent<CharacterController>();var look=inv.GetComponent<PlayerLook>();var pi=inv.GetComponent<UnityEngine.InputSystem.PlayerInput>();
var ball=GameObject.Find("PickupLoop_TestBall").GetComponent<WorldItem>();var definition=ball.Definition;int originalId=ball.GetInstanceID();
var flags=System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic;var pitchField=typeof(PlayerLook).GetField("pitchAngle",flags);
var throwSettings=(PlayerThrowSettings)typeof(PlayerThrow).GetField("settings",flags).GetValue(t);
var originalPosition=inv.transform.position;var originalRotation=inv.transform.rotation;var originalEye=t.Origin.localRotation;float originalPitch=(float)pitchField.GetValue(look);
var keyboard=UnityEngine.InputSystem.Keyboard.current;var mouse=UnityEngine.InputSystem.Mouse.current;var originalInput=UnityEngine.InputSystem.InputSystem.settings;var input=UnityEngine.Object.Instantiate(originalInput);
int fps=Application.targetFrameRate,vsync=QualitySettings.vSyncCount,passed=0,failed=0,first=Time.frameCount;bool completed=false;
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_PickupLoop"));System.IO.Directory.CreateDirectory(dir);var log=new System.Text.StringBuilder();
GameObject floor=null,block=null;var clones=new System.Collections.Generic.List<GameObject>();
void Check(string name,bool ok){if(ok)passed++;else failed++;log.AppendLine((ok?"PASS ":"FAIL ")+name);System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"validation.txt"),log.ToString());}
void Mouse(ushort buttons=0,float scroll=0)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(mouse,new UnityEngine.InputSystem.LowLevel.MouseState{buttons=buttons,scroll=new Vector2(0,scroll)});
void Keys(params UnityEngine.InputSystem.Key[] keys)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(keys));
System.Collections.IEnumerator Frames(int count){for(int i=0;i<count;i++)yield return null;}
System.Collections.IEnumerator Key(UnityEngine.InputSystem.Key key){Keys(key);yield return Frames(2);Keys();yield return Frames(3);}
System.Collections.IEnumerator Scroll(float delta){Mouse(0,delta);yield return Frames(2);Mouse();yield return Frames(3);}
void Pitch(float angle){pitchField.SetValue(look,angle);t.Origin.localRotation=Quaternion.Euler(angle,0,0);}
void Aim(Vector3 position){var d=position-t.Origin.position;var flat=Vector3.ProjectOnPlane(d,Vector3.up);if(flat.sqrMagnitude>.001f)inv.transform.rotation=Quaternion.LookRotation(flat);d=position-t.Origin.position;Pitch(-Mathf.Atan2(d.y,new Vector2(d.x,d.z).magnitude)*Mathf.Rad2Deg);}
void Move(Vector3 pos){cc.enabled=false;inv.transform.SetPositionAndRotation(pos,Quaternion.identity);cc.enabled=true;Physics.SyncTransforms();}
void Place(WorldItem item,Vector3 position){item.transform.position=position;var rb=item.GetComponent<Rigidbody>();rb.linearVelocity=rb.angularVelocity=Vector3.zero;Physics.SyncTransforms();}
System.Collections.IEnumerator Capture(string name){yield return new WaitForEndOfFrame();var tex=ScreenCapture.CaptureScreenshotAsTexture();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());UnityEngine.Object.Destroy(tex);}
System.Collections.IEnumerator Run()
{
    try
    {
        input.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;input.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;UnityEngine.InputSystem.InputSystem.settings=input;
        UnityEngine.InputSystem.InputSystem.EnableDevice(keyboard);UnityEngine.InputSystem.InputSystem.EnableDevice(mouse);EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();Application.targetFrameRate=60;QualitySettings.vSyncCount=0;
        Mouse();Keys();yield return Frames(5);
        Check("start empty without automatic test supply",inv.Count==0&&!t.HasHeldItem);Check("one real B5 ball is available",ball.CanPickup);
        Aim(ball.transform.position);yield return Frames(5);Check("looking at nearby B5 ball offers pickup",inv.Candidate==ball);yield return Capture("01_pickup_prompt");
        yield return Key(UnityEngine.InputSystem.Key.F);Check("F stores the same world object",inv.Count==1&&inv.Selected==ball&&ball.IsStored&&!ball.gameObject.activeSelf);Check("pickup connects to held visual",t.HeldItem==definition&&h.ItemVisible);
        yield return Key(UnityEngine.InputSystem.Key.F);Check("repeated F cannot duplicate a held object",inv.Count==1);yield return Capture("02_held_item");
        if(!t.IsUnderhand)yield return Key(UnityEngine.InputSystem.Key.R);Pitch(65);Mouse(1);yield return new WaitForSeconds(.4f);int release=t.ReleaseCount;float firstReleasedAt=Time.time;Mouse();yield return Frames(3);
        Check("left click throws and removes exactly one slot",t.ReleaseCount==release+1&&inv.Count==0&&!t.HasHeldItem);Check("throw reuses original world instance",t.LastThrown.GetComponent<WorldItem>().GetInstanceID()==originalId&&ball.gameObject.activeSelf&&!ball.IsStored);
        Check("underhand settings remain active",Mathf.Abs(t.LastLaunch.Velocity.magnitude-throwSettings.UnderhandSpeed)<.01f&&t.LastLaunch.Velocity.y<0);yield return new WaitForSeconds(2.5f);yield return Capture("03_released_ball");
        var ballPosition=ball.transform.position;Move(new Vector3(ballPosition.x,originalPosition.y,ballPosition.z-.9f));Aim(ball.transform.position);yield return Frames(2);yield return Key(UnityEngine.InputSystem.Key.F);
        Check("thrown ball can be picked up again",inv.Count==1&&inv.Selected==ball&&ball.GetInstanceID()==originalId);
        floor=GameObject.CreatePrimitive(PrimitiveType.Cube);floor.name="TemporaryPickupFloor";floor.transform.position=new Vector3(1000,199.5f,1000);floor.transform.localScale=new Vector3(100,1,100);
        Move(new Vector3(1000,200+cc.height*.5f-cc.center.y+.02f,1000));Pitch(0);yield return new WaitForSeconds(.4f);
        block=GameObject.CreatePrimitive(PrimitiveType.Cube);block.name="TemporaryPickupBlock";block.transform.position=h.ItemPosition;block.transform.localScale=Vector3.one*.3f;Physics.SyncTransforms();yield return Frames(4);yield return Key(UnityEngine.InputSystem.Key.Q);
        Check("blocked drop preserves inventory and world ownership",inv.Count==1&&ball.IsStored);block.SetActive(false);yield return new WaitForSeconds(.4f);
        int dropHits=0;ball.GetComponent<ThrownObject>().Hit+=(obj,collision)=>dropHits++;
        release=t.ReleaseCount;yield return Key(UnityEngine.InputSystem.Key.Q);Check("Q drops same object without throwing",inv.Count==0&&ball.gameObject.activeSelf&&t.ReleaseCount==release);Check("drop restores original physics after underhand",ball.GetComponent<Rigidbody>().linearDamping==0&&Mathf.Abs(ball.GetComponent<Rigidbody>().angularDamping-.05f)<.001f&&ball.GetComponent<Collider>().sharedMaterial==null);
        Check("freshly dropped object has pickup grace period",!ball.CanPickup);yield return new WaitForSeconds(.7f);Check("drop contact does not emit throw hit",dropHits==0);
        Place(ball,new Vector3(1000,200.065f,1001.1f));Aim(ball.transform.position);yield return Frames(4);
        block.SetActive(true);block.transform.position=Vector3.Lerp(t.Origin.position,ball.transform.position,.5f);block.transform.localScale=new Vector3(1,1,.08f);Physics.SyncTransforms();yield return Frames(4);yield return Key(UnityEngine.InputSystem.Key.F);Check("wall blocks pickup",inv.Count==0&&inv.Candidate==null);
        block.SetActive(false);Place(ball,new Vector3(1000,200.065f,1005));Aim(ball.transform.position);yield return Frames(4);yield return Key(UnityEngine.InputSystem.Key.F);Check("distant object cannot be picked up",inv.Count==0);
        Place(ball,new Vector3(1000,200.065f,1001.1f));Aim(ball.transform.position);yield return Frames(4);yield return Key(UnityEngine.InputSystem.Key.F);Check("F works again after wall and distance rejection",inv.Count==1&&inv.Selected==ball);
        for(int i=0;i<4;i++)
        {
            var go=UnityEngine.Object.Instantiate(definition.WorldPrefab.gameObject,new Vector3(1000,200.065f,1001.1f),Quaternion.identity);clones.Add(go);Aim(go.transform.position);yield return Frames(5);yield return Key(UnityEngine.InputSystem.Key.F);
        }
        Check("five identical types remain five separate instances",inv.Count==5&&System.Linq.Enumerable.Distinct(System.Linq.Enumerable.Select(inv.Items,x=>x.GetInstanceID())).Count()==5);
        var sixth=UnityEngine.Object.Instantiate(definition.WorldPrefab.gameObject,new Vector3(1000,200.065f,1001.1f),Quaternion.identity);clones.Add(sixth);Aim(sixth.transform.position);yield return Frames(5);yield return Key(UnityEngine.InputSystem.Key.F);
        Check("sixth pickup is rejected and stays in world",inv.Count==5&&sixth.activeSelf&&!sixth.GetComponent<WorldItem>().IsStored);Check("full inventory reports reason",inv.Message=="공간이 없어");yield return Capture("04_inventory_full");
        int selected=inv.SelectedIndex;yield return Scroll(120);Check("wheel up selects previous individual object",inv.SelectedIndex==(selected+4)%5);yield return Scroll(-120);Check("wheel down selects next individual object",inv.SelectedIndex==selected);yield return Scroll(-120);Check("wheel wraps selection",inv.SelectedIndex==0);
        Mouse(1);yield return Frames(3);release=t.ReleaseCount;yield return Scroll(-120);Mouse();yield return Frames(3);Check("selection cancels held aim without throwing",t.ReleaseCount==release&&!t.IsAiming&&inv.Count==5);
        int before=inv.Count;Mouse(1);yield return Frames(3);Keys(UnityEngine.InputSystem.Key.Q);Mouse();yield return Frames(3);Keys();yield return Frames(3);Check("same-frame Q and release drops only once",inv.Count==before-1&&t.ReleaseCount==release);
        Pitch(0);yield return new WaitForSeconds(.4f);block.SetActive(true);block.transform.position=h.ItemPosition;block.transform.localScale=Vector3.one*.3f;Physics.SyncTransforms();yield return Frames(3);Mouse(1);Mouse();yield return Frames(3);Check("blocked throw never consumes inventory",inv.Count==4&&t.ReleaseCount==release);block.SetActive(false);
        yield return new WaitForSeconds(.4f);inv.enabled=false;Mouse(1);Mouse();yield return Frames(3);Check("disabled inventory cannot release stored items",t.ReleaseCount==release&&inv.Count==4&&!t.HasHeldItem);inv.enabled=true;yield return Frames(3);Check("inventory enable restores selection",t.HasHeldItem&&inv.Selected!=null);
        while(inv.Selected!=ball){yield return Scroll(-120);}
        if(t.IsUnderhand)yield return Key(UnityEngine.InputSystem.Key.R);Pitch(0);Mouse(1);yield return new WaitForSeconds(.4f);Mouse();yield return Frames(3);
        var rb=ball.GetComponent<Rigidbody>();Check("reacquired ball retains overhand profile on next release",t.LastThrown.GetComponent<WorldItem>()==ball&&Mathf.Abs(t.LastLaunch.Velocity.magnitude-throwSettings.OverhandSpeed)<.01f&&rb.linearDamping==0&&Mathf.Abs(rb.angularDamping-.05f)<.001f&&rb.angularVelocity.magnitude<.01f&&ball.GetComponent<Collider>().sharedMaterial==null);
        Check("remaining items stay held after throw",inv.Count==3&&inv.Selected!=ball&&t.HeldItem==definition);
        var otherWorld=inv.Selected;yield return new WaitForSeconds(.35f);yield return Key(UnityEngine.InputSystem.Key.Q);
        Check("second item drops before collision check",!otherWorld.IsStored&&otherWorld.gameObject.activeInHierarchy&&inv.Count==2);
        Check("separately released items still collide with each other",!Physics.GetIgnoreCollision(ball.GetComponent<Collider>(),otherWorld.GetComponent<Collider>()));
        int oldCount=inv.Count;pi.DeactivateInput();Keys(UnityEngine.InputSystem.Key.Q);Mouse(1);Mouse();yield return Frames(4);Keys();pi.ActivateInput();yield return Frames(4);Check("disabled input map cannot drop or throw",inv.Count==oldCount);
        while(Time.time-firstReleasedAt<21f)yield return null;
        Check("world item survives beyond old 20-second test lifetime",ball!=null&&ball.gameObject.activeSelf);
        Check("game frames advanced during validation",Time.frameCount-first>700);completed=true;log.AppendLine($"TOTAL passed={passed}, failed={failed}, frames={first}→{Time.frameCount}, ballId={originalId}, elapsed={Time.time-firstReleasedAt:F2}s");
    }
    finally
    {
        Mouse();Keys();inv.enabled=true;pi.ActivateInput();t.ExitStance();foreach(var go in clones)if(go)UnityEngine.Object.Destroy(go);if(block)UnityEngine.Object.Destroy(block);if(floor)UnityEngine.Object.Destroy(floor);
        Move(originalPosition);inv.transform.rotation=originalRotation;pitchField.SetValue(look,originalPitch);t.Origin.localRotation=originalEye;
        UnityEngine.InputSystem.InputSystem.settings=originalInput;UnityEngine.Object.Destroy(input);Application.targetFrameRate=fps;QualitySettings.vSyncCount=vsync;
        if(!completed)log.AppendLine("INCOMPLETE: inspect Unity console");System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"validation.txt"),log.ToString());
    }
}
inv.StartCoroutine(Run());return "Pickup loop validation running";
