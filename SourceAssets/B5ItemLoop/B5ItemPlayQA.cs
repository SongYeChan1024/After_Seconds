using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

[InitializeOnLoad]
public static partial class B5ItemPlayQA
{
    static readonly JArray checks=new JArray();
    static string Mode=>SessionState.GetString("AS_ItemCycle","");
    static string Output=>Environment.GetEnvironmentVariable("AS_CYCLE_WORK");
    static IEnumerator sequence;
    static int next,previous=-1;
    static double waitingSince;
    static Keyboard keyboard;
    static Mouse mouse;
    static PlayerInventory inventory;
    static PlayerThrow thrower;
    static CharacterController body;
    static PlayerLook look;
    static PlayerLookSettings lookSettings;
    static B5ItemPlayQA(){EditorApplication.update+=Tick;}
    public static void Review()=>Start("review",B5ItemAuthoring.Review);
    public static void WorldTargets()=>Start("world-targets",B5ItemAuthoring.Review);
    public static void Health()=>Start("health",B5ItemAuthoring.B5);
    public static void Campaign()=>Start("campaign",B5ItemAuthoring.B5);
    static void Start(string mode,string path)
    {
        EditorSceneManager.OpenScene(path);
        SessionState.SetString("AS_ItemCycle",mode);
        EditorApplication.EnterPlaymode();
    }
    static void Tick()
    {
        if (Mode!="")
        {
            if(waitingSince==0) waitingSince=EditorApplication.timeSinceStartup;
            if(EditorApplication.timeSinceStartup-waitingSince>240){Finish("Play verification timeout");return;}
        }
        if (recording && Application.isPlaying && Time.frameCount != sampledFrame)
            SampleHeartbeat();
        if(Mode=="" || !Application.isPlaying || !EditorApplication.isPlaying || Time.frameCount<6 || Time.frameCount==previous || Time.frameCount<next)return;
        previous=Time.frameCount;
        try
        {
            if(sequence==null)
            {
                inventory=Object.FindAnyObjectByType<PlayerInventory>();
                if(!inventory || !inventory.GetComponent<PlayerFirstPersonHands>().Ready || !inventory.GetComponent<PlayerPresenter>().isActiveAndEnabled)return;
                thrower=inventory.GetComponent<PlayerThrow>();body=inventory.GetComponent<CharacterController>();look=inventory.GetComponent<PlayerLook>();
                lookSettings=(PlayerLookSettings)new SerializedObject(look).FindProperty("settings").objectReferenceValue;
                keyboard=InputSystem.AddDevice<Keyboard>();mouse=InputSystem.AddDevice<Mouse>();
                var cfg=Object.Instantiate(InputSystem.settings);
                cfg.backgroundBehavior=InputSettings.BackgroundBehavior.IgnoreFocus;
                cfg.editorInputBehaviorInPlayMode=InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
                InputSystem.settings=cfg;
                var input=inventory.GetComponent<PlayerInput>();input.enabled=false;input.enabled=true;input.ActivateInput();
                input.SwitchCurrentControlScheme("Keyboard&Mouse",keyboard,mouse);input.ActivateInput();
                Time.captureDeltaTime=1f/60;Keys();Buttons(0);
                sequence=Mode switch
                {
                    "world-targets" => CheckWorldTargets(),
                    "health" => CheckHealthAndRetry(),
                    "campaign" => InCampaign(),
                    _ => InReview()
                };
            }
            if(!sequence.MoveNext()){Finish(null);return;}
            next=Time.frameCount+Mathf.Max(1,(int)sequence.Current);
        }
        catch(Exception ex){Finish(ex.ToString());}
    }
    static void Check(bool ok,string description)
    {
        Debug.Log("B5_ITEM_QA "+ok+" "+description);
        checks.Add(new JObject{["check"]=description,["pass"]=ok});
        if(!ok)throw new InvalidOperationException(description+"; camera "+thrower.Origin.position+" forward "+thrower.Origin.forward+
            " candidate "+inventory.Candidate+" guard "+inventory.GuardCandidate+" selection "+inventory.Selected+" message "+inventory.Message);
    }
    static void Finish(string error)
    {
        string mode=Mode;SessionState.EraseString("AS_ItemCycle");
        File.WriteAllText(Path.Combine(Output,mode+".json"),new JObject{["unity"]=Application.unityVersion,["checks"]=checks,["error"]=error}.ToString());
        if(error!=null)Debug.LogError(error);
        EditorApplication.Exit(error==null?0:7);
    }
    static void Keys(params Key[] keys)=>InputSystem.QueueStateEvent(keyboard,new KeyboardState(keys));
    static void Buttons(ushort mask)=>InputSystem.QueueStateEvent(mouse,new MouseState{buttons=mask});
    static Vector3 Feet(){var b=body.bounds;return new Vector3(b.center.x,b.min.y,b.center.z);}
    static void MoveFeet(Vector3 point)
    {
        Vector3 delta=point-Feet();body.enabled=false;inventory.transform.position+=delta;body.enabled=true;Physics.SyncTransforms();
    }
    static void LookAt(Vector3 point)
    {
        for(int i=0;i<3;i++)
        {
            Vector3 direction=(point-thrower.Origin.position).normalized;
            var forward=thrower.Origin.forward;
            float yaw=Vector3.SignedAngle(Vector3.ProjectOnPlane(forward,Vector3.up),Vector3.ProjectOnPlane(direction,Vector3.up),Vector3.up);
            float pitch=(Mathf.Asin(direction.y)-Mathf.Asin(forward.y))*Mathf.Rad2Deg;
            look.Rotate(new Vector2(yaw/lookSettings.HorizontalSensitivity,pitch/lookSettings.VerticalSensitivity));
        }
        Physics.SyncTransforms();
    }
    static void Capture(string filename)
    {
        var camera=Camera.main;
        if(!camera || SystemInfo.graphicsDeviceType==UnityEngine.Rendering.GraphicsDeviceType.Null)return;
        var target=RenderTexture.GetTemporary(960,540,24);
        var previousTarget=RenderTexture.active;
        var pixels=new Texture2D(960,540,TextureFormat.RGB24,false);
        try
        {
            var request=new UnityEngine.Rendering.RenderPipeline.StandardRequest{destination=target};
            if(!UnityEngine.Rendering.RenderPipeline.SupportsRenderRequest(camera,request))return;
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera,request);
            RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,960,540),0,0);pixels.Apply();
            File.WriteAllBytes(Path.Combine(Output,filename+".jpg"),pixels.EncodeToJPG(90));
        }
        finally{RenderTexture.active=previousTarget;RenderTexture.ReleaseTemporary(target);Object.Destroy(pixels);}
    }

    static Vector3 Flat(Vector3 p)=>new Vector3(p.x,0,p.z);

    static IEnumerator InReview()
    {
        yield return 35;
        Check(inventory.GetComponent<IDamageable>()!=null,"player implements IDamageable");
        Check(GameObject.Find("소품 받침대").GetComponent<IInteractable>()==null,"decorative stand offers no interaction");
        var first=inventory.Candidate;Check(first && first.Definition.HasIronSights,"review stand offers the pistol");
        Keys(Key.F);yield return 4;Keys();yield return 12;
        Check(first is IInteractable && first.Ability is SwapShotAbility,"world pickup and held ability are independent contracts");
        Check(inventory.Selected==first && first.GetComponent<SwapShotAbility>().RemainingRounds==3,"F picks up one instance with three starting uses");
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(B5ItemAuthoring.Root+"04.Prefabs/B5_MealGuard.prefab");
        var guard=Object.Instantiate(prefab,new Vector3(-2,0,2),Quaternion.identity);
        var marker=guard.GetComponent<CharacterController>();
        var equipment=guard.GetComponent<GuardLoadout>();
        var dropped=guard.GetComponentInChildren<WorldItem>();
        var start=new Vector3(-2,.008f,-1.4f);MoveFeet(start);LookAt(marker.bounds.center);yield return 10;
        var wall=GameObject.CreatePrimitive(PrimitiveType.Cube);
        wall.transform.position=(thrower.Origin.position+marker.bounds.center)*.5f;wall.transform.localScale=new Vector3(1.2f,1.8f,.2f);
        Physics.SyncTransforms();Buttons(2);yield return 16;Buttons(3);yield return 7;
        Check(first.GetComponent<SwapShotAbility>().RemainingRounds==2 && inventory.Selected==first && inventory.Message=="교환 대상 없음","wall blocks reservation and a held click spends only one use");
        Buttons(2);yield return 190;
        Check(Vector3.Distance(Flat(Feet()),Flat(start))<.12f,"blocked hit leaves both actors in place after three seconds");
        Check(!equipment.IsDown && dropped.IsStored,"cover also blocks immediate damage");
        Object.Destroy(wall);yield return 3;LookAt(marker.bounds.center);Buttons(3);yield return 6;Buttons(2);
        Check(first.GetComponent<SwapShotAbility>().RemainingRounds==1 && inventory.Message=="위치 교환 예약","valid game target schedules the shared swap");
        Check(equipment.IsDown && !marker.enabled && !guard.GetComponent<GuardPresenter>().enabled &&
            !dropped.IsStored && !dropped.transform.IsChildOf(guard.transform),"first shot immediately disables the guard and drops its gun");
        Check(!equipment.TakeDamage(1),"a fallen guard rejects additional damage and drops");
        yield return 44;var moved=start+Vector3.right*.72f;MoveFeet(moved);yield return 90;
        var gunAtRest=dropped.transform.position;
        Check(Vector3.Distance(Flat(Feet()),Flat(moved))<.15f,"no exchange before the three-second delay");
        yield return 85;
        Check(Vector3.Distance(Flat(Feet()),new Vector3(-2,0,2))<.18f && Vector3.Distance(Flat(guard.transform.position),Flat(moved))<.18f,
            "exchange uses current positions at execution");
        Check(equipment.IsDown && !marker.enabled && Vector3.Distance(Flat(gunAtRest),Flat(dropped.transform.position))<.12f,
            "only the fallen guard moves; its pistol stays behind");
        LookAt(thrower.Origin.position+Vector3.forward*5);Buttons(3);yield return 4;Buttons(2);yield return 5;
        Check(first.GetComponent<SwapShotAbility>().RemainingRounds==0 && inventory.Selected==first,"last use leaves the empty pistol selected");
        Buttons(3);yield return 3;Buttons(0);yield return 10;
        Check(first.GetComponent<SwapShotAbility>().RemainingRounds==0 && first.IsStored,"empty aimed click keeps the item");
        Buttons(1);yield return 10;Buttons(0);yield return 7;
        Check(!first.IsStored && !inventory.Items.Contains(first),"ordinary left release throws the empty instance");
        var rb=first.GetComponent<Rigidbody>();rb.useGravity=false;rb.linearVelocity=rb.angularVelocity=Vector3.zero;
        rb.position=thrower.Origin.position+thrower.Origin.forward*.8f;Physics.SyncTransforms();yield return 28;
        Keys(Key.F);yield return 4;Keys();yield return 6;
        Check(inventory.Selected==first && first.GetComponent<SwapShotAbility>().RemainingRounds==0,"F reacquires the same empty instance");
        var lamp=Object.FindObjectsByType<WorldItem>(FindObjectsSortMode.None).Single(x=>x.Definition && x.Definition.name=="Item_Flashlight");
        MoveFeet(new Vector3(.94f,.01f,.22f));LookAt(lamp.transform.position);yield return 8;
        Keys(Key.F);yield return 4;Keys();yield return 5;
        Check(inventory.Selected==lamp,"flashlight can be picked up at review stand");
        Buttons(1);yield return 12;Buttons(0);yield return 5;
        Check(!lamp.IsStored && !inventory.Items.Contains(lamp),"flashlight throws through the ordinary item path");
        var damageChecks=CheckGuardFire(prefab);
        while(damageChecks.MoveNext()) yield return damageChecks.Current;
    }

    static IEnumerator InCampaign()
    {
        yield return 75;
        var scene=SceneManager.GetSceneByPath(B5ItemAuthoring.B5);
        var placed=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<GuardLoadout>()).Where(g=>g.gameObject.activeInHierarchy).OrderBy(x=>x.transform.position.z).ToArray();
        Check(placed.Length==2,"B5 loads both on-duty guards through GameRoot ("+placed.Length+")");
        var droppedDutyItems = new List<WorldItem>();
        foreach(var guard in placed)
        {
            var presenter=guard.GetComponent<GuardPresenter>();
            var worn=guard.GetComponentsInChildren<WorldItem>();
            var gun=worn.Single(i=>i.Ability is SwapShotAbility);
            var auxiliary=worn.Single(i=>!(i.Ability is SwapShotAbility));
            Check(auxiliary.IsStored && !auxiliary.CanPickup && !auxiliary.GetComponent<SwapTarget>().Available &&
                auxiliary.GetComponentsInChildren<Renderer>().Any(r=>r.enabled), "visible duty gear stays attached until defeat "+guard.name);
            Check(gun && !gun.CanPickup && gun.Definition.HasIronSights && gun.GetComponent<SwapShotAbility>().RemainingRounds==3,"guard carries its own pistol "+guard.name);
            Vector3 behind=-guard.transform.forward;
            if(inventory.Count==0)
            {
                MoveFeet(guard.transform.position+behind*1.04f+Vector3.up*.02f);
                LookAt(guard.GetComponent<CharacterController>().bounds.center);yield return 4;
                Keys(Key.F);yield return 4;Keys();yield return 52;
                Check(guard.IsDown && guard.CurrentHP==0 && !presenter.enabled && guard.GetComponent<SwapTarget>().Available && !gun.transform.IsChildOf(guard.transform),
                    "F disables one guard and releases one world item "+guard.name);
            }
            else
            {
                var sequence=ShootCampaignGuard(guard,gun);
                while(sequence.MoveNext()) yield return sequence.Current;
            }
            Check(!guard.TryInteract(body),"repeat interaction cannot produce another pistol");
            Check(auxiliary.CanPickup && auxiliary.GetComponent<SwapTarget>().Available && !auxiliary.transform.IsChildOf(guard.transform),
                "same duty item drops alongside the pistol "+guard.name);
            droppedDutyItems.Add(auxiliary);
            LookAt(gun.transform.position);yield return 4;Keys(Key.F);yield return 4;Keys();yield return 5;
            Check(inventory.Selected==gun,"separate F picks up the released world item "+guard.name);
            if(inventory.Count==1)
            {
                // 제압한 몸도 유효 표적이므로 잔탄 소모용 두 발은 빈 천장 쪽으로 보낸다.
                LookAt(thrower.Origin.position + Vector3.up * 8f + guard.transform.forward * .15f);
                Buttons(2);yield return 5;
                for(int i=0;i<2;i++){Buttons(3);yield return 3;Buttons(2);yield return 3;}
                Buttons(0);yield return 5;Check(gun.GetComponent<SwapShotAbility>().RemainingRounds==1,"first guard pistol keeps one use for the next encounter");
            }
        }
        Check(inventory.Items[0].GetComponent<SwapShotAbility>().RemainingRounds==0 && inventory.Items[1].GetComponent<SwapShotAbility>().RemainingRounds==3,"two guard pistols preserve independent remaining uses");
        foreach (var auxiliary in droppedDutyItems)
        {
            var drop = auxiliary.GetComponent<Collider>().bounds.center;
            foreach (var side in new[]{Vector3.forward,Vector3.back,Vector3.right,Vector3.left})
            {
                MoveFeet(drop + side * .75f + Vector3.up * .025f);
                yield return 6; LookAt(auxiliary.GetComponent<Collider>().bounds.center); inventory.RefreshCandidate();
                if (inventory.Candidate == auxiliary) break;
            }
            Keys(Key.F); yield return 4; Keys(); yield return 4;
            Check(inventory.Selected == auxiliary, "F recovers the role-specific drop "+auxiliary.Definition.DisplayName);
            Check(auxiliary.IsStored && !auxiliary.GetComponent<SwapTarget>().Available,
                "recovered duty item is stored with its original identity");
        }
        var levelItems=scene.GetRootGameObjects().Single(x=>x.name=="B5_UsableItems");
        var ordinary=levelItems.GetComponentsInChildren<WorldItem>().Where(x=>!x.Definition.HasIronSights).ToArray();
        Check(ordinary.Length==8,"eight B5 props remain on their carts after physics settles");
        foreach(var item in ordinary)
        {
            var original=item.transform.position;
            var cart=levelItems.GetComponentsInChildren<Transform>().First(x=>x.name.EndsWith("_PickupCart") &&
                Vector3.Distance(Flat(x.position),Flat(original))<.65f);
            Check(original.y-cart.position.y>.35f,"supported shelf item "+item.Definition.DisplayName);
            if(item.Definition.name=="Item_DocumentFolder")
            {
                var box=item.GetComponent<BoxCollider>().bounds;
                Check(Mathf.Abs(box.center.x-cart.position.x)+box.extents.x<.38f &&
                      Mathf.Abs(box.center.z-cart.position.z)+box.extents.z<.23f,"folder fits inside the shelf rim");
            }
            // Approach the nearer long edge, then aim the actual camera at the object's center.
            var side=original.z>=cart.position.z?Vector3.forward:Vector3.back;
            foreach(var offset in new[]{side,-side,Vector3.left,Vector3.right})
            {
                Vector3 feet=cart.position+offset*1.02f;
                if(offset.x==0) feet.x=original.x; else feet.z=original.z;
                MoveFeet(feet+Vector3.up*.025f);yield return 8;
                LookAt(item.transform.position);yield return 6;
                LookAt(item.transform.position);yield return 3;
                if(inventory.Candidate==item) break;
                var eye=thrower.Origin;
                string hits=string.Join(", ",Physics.RaycastAll(eye.position,(item.transform.position-eye.position).normalized,2.2f,~0,QueryTriggerInteraction.Ignore).OrderBy(h=>h.distance).Take(6).Select(h=>h.collider.name+"@"+h.distance.ToString("F3")));
                Debug.Log("ITEM_SIGHT "+item.name+" "+item.transform.position.ToString("F3")+" from "+eye.position.ToString("F3")+" ray "+hits+" candidate "+inventory.Candidate);
            }
            Check(inventory.Candidate==item,"reachable on authored shelf "+item.Definition.DisplayName);
            if(item.Definition.name=="Item_Pen" || item.Definition.name=="Item_DocumentFolder") Capture(item.Definition.name);
            Keys(Key.F);yield return 4;Keys();yield return 7;
            Check(inventory.Selected==item && inventory.GetComponent<PlayerFirstPersonHands>().ItemVisible,"real pickup and hand mesh "+item.Definition.DisplayName);
            // 선반에서 벽 쪽으로 돌아서는 경우는 시작 공간 검사가 맞게 막는다. 실제 관제동의 빈 보행면에서 투척한다.
            MoveFeet(new Vector3(-22f,-81.97f,18f));yield return 7;
            LookAt(thrower.Origin.position+Vector3.back*4+Vector3.up*.4f);yield return 15;
            Buttons(1);yield return 15;
            Check(thrower.IsAiming && thrower.TryGetLaunch(out _),"clear launch space "+item.Definition.DisplayName);
            Buttons(0);yield return 6;
            Check(!item.IsStored && !inventory.Items.Contains(item),"real throw "+item.Definition.DisplayName);
        }
    }
}
