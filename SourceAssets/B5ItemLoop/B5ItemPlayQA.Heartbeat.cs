using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Cinemachine;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

public static partial class B5ItemPlayQA
{
    static bool recording, captureFrames;
    static int sampledFrame=-1, firstFrame;
    static double began, shotTime;
    static readonly List<double> beats=new List<double>();
    static readonly List<float> gains=new List<float>();
    static readonly List<float> kicks=new List<float>();
    static readonly JArray frames=new JArray();
    static CinemachineVirtualCamera lens;
    static AudioSource speaker;

    static void StartHeartbeat()
    {
        var effect=inventory.transform.root.GetComponentInChildren<SwapPulseEffect>(true);
        lens=effect.GetComponent<CinemachineVirtualCamera>();
        speaker=effect.GetComponent<AudioSource>();
        beats.Clear();gains.Clear();kicks.Clear();frames.Clear();
        began=Time.timeAsDouble;firstFrame=Time.frameCount;sampledFrame=-1;
        captureFrames=Environment.GetEnvironmentVariable("AS_PULSE_CAPTURE")=="1";
        if(captureFrames)Directory.CreateDirectory(Path.Combine(Output,"PulseFrames"));
        inventory.GetComponent<PlayerSwap>().Pulse+=OnHeartbeat;
        recording=true;
    }
    static void OnHeartbeat(float strength)
    {
        beats.Add(Time.timeAsDouble-began);
        gains.Add(speaker.volume);
        kicks.Add(0f);
    }
    static void SampleHeartbeat()
    {
        sampledFrame=Time.frameCount;
        double now=Time.timeAsDouble-began;
        if(beats.Count>0 && now-beats[beats.Count-1]<.16)
        {
            int i=beats.Count-1;
            kicks[i]=Mathf.Max(kicks[i],lens.m_Lens.FieldOfView-Camera.main.fieldOfView);
        }
        if(captureFrames && (sampledFrame-firstFrame)%2==0)
        {
            string name="frame_"+frames.Count.ToString("D4");
            Capture("PulseFrames/"+name);
            frames.Add(new JObject{["file"]=name+".jpg",["t"]=now});
        }
    }
    static void EndHeartbeat()
    {
        recording=false;
        inventory.GetComponent<PlayerSwap>().Pulse-=OnHeartbeat;
        File.WriteAllText(Path.Combine(Output,"heartbeat.json"),new JObject{
            ["shot"]=shotTime-began,["beatTimes"]=JArray.FromObject(beats),["audioGain"]=JArray.FromObject(gains),
            ["fovKickDegrees"]=JArray.FromObject(kicks),["frames"]=frames}.ToString());
        Check(beats.Count==3 && Enumerable.Range(0,3).All(i=>Math.Abs(beats[i]-(shotTime-began)-(i+1))<.085),
            "three beats at one, two and three game seconds");
        Check(speaker.clip && speaker.clip.name=="SwapHeartbeatBuk" && gains[0]<gains[1] && gains[1]<gains[2],"three increasing heartbeat and drum accents");
        Check(kicks[0]>.65f && kicks[1]>kicks[0] && kicks[2]>kicks[1],"increasing FOV kicks on the actual output camera");
        Check(Math.Abs(Camera.main.fieldOfView-lens.m_Lens.FieldOfView)<.12f,"FOV returns to the active lens without accumulating");
    }

    static IEnumerator ShootCampaignGuard(GuardLoadout target,WorldItem dropped)
    {
        Vector3 behind=-target.transform.forward;
        MoveFeet(target.transform.position+behind*2.65f+Vector3.up*.025f);
        yield return 8;
        LookAt(target.GetComponent<CharacterController>().bounds.center);
        Buttons(2);yield return 18;
        StartHeartbeat();yield return 22;
        var guardBody=target.GetComponent<CharacterController>();
        LookAt(guardBody.bounds.center);shotTime=Time.timeAsDouble;Buttons(3);yield return 3;
        Buttons(2);yield return 4;Buttons(0);
        Check(target.IsDown && !guardBody.enabled && !target.GetComponent<GuardPresenter>().enabled && !dropped.IsStored,"B5 guard falls and drops on the input hit");
        Vector3 hitPosition=target.transform.position;
        var ownFeet=Feet();
        yield return 115;
        Check(Vector3.Distance(Flat(Feet()),Flat(ownFeet))<.2f && Vector3.Distance(Flat(target.transform.position),Flat(hitPosition))<.2f,"fallen guard and player wait for the countdown");
        var droppedAt=dropped.transform.position;
        yield return 113;
        EndHeartbeat();
        Check(target.IsDown && Vector3.Distance(Flat(target.transform.position),Flat(ownFeet))<.22f &&
            Vector3.Distance(Flat(Feet()),Flat(hitPosition))<.22f && Vector3.Distance(Flat(droppedAt),Flat(dropped.transform.position))<.16f,
            "B5 swaps the fallen body and player only");
        MoveFeet(dropped.transform.position+behind*.92f+Vector3.up*.02f);
        yield return 5;
    }

    static IEnumerator CheckHealthAndRetry()
    {
        var victim = inventory.GetComponent<PlayerDamageReceiver>();
        var scene = SceneManager.GetSceneByPath(B5ItemAuthoring.B5);
        var guards = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren<GuardLoadout>()).ToArray();
        Check(guards.Length == 2 && guards.All(g => g.CurrentHP == 1 && g.MaxHP == 1), "B5 guards start at their own maximum HP");
        Check(victim.CurrentHP == 3 && victim.MaxHP == 3, "player starts with three HP");
        Check(!victim.TakeDamage(0) && !victim.TakeDamage(-1) && victim.CurrentHP == 3, "nonpositive damage is ignored");
        Check(guards[0].TakeDamage(1) && guards[0].IsDown && guards[0].CurrentHP == 0 && guards[1].CurrentHP == 1, "one guard falling leaves the other guard at full HP");

        var shooter = guards[1];
        var weapon = shooter.GetComponentInChildren<SwapShotAbility>();
        Check(shooter.TryFireAt(victim) && victim.CurrentHP == 2 && weapon.RemainingRounds == 2, "guard shot removes one player HP and one round");
        Check(shooter.TryFireAt(victim) && victim.CurrentHP == 1 && weapon.RemainingRounds == 1, "successive guard hits accumulate");
        yield return 5;
        Check(Time.timeScale > 0f && victim.CurrentHP == 1, "surviving a hit keeps the attempt active");
        int lost = 0;
        victim.Damaged += amount => lost += amount;
        Check(victim.TakeDamage(int.MaxValue) && lost == 1 && victim.CurrentHP == 0, "overkill reports only remaining HP and clamps at zero");
        Check(!victim.TakeDamage(1) && lost == 1 && !shooter.TryFireAt(victim) && weapon.RemainingRounds == 1, "zero HP rejects repeat damage without spending a round");
        yield return 4;
        var hud = victim.transform.root.GetComponentInChildren<PlayerInventoryView>();
        Check(Time.timeScale == 0f && !victim.GetComponent<PlayerPresenter>().enabled && hud.EncounterPrompt.Contains("체력 소진"), "zero HP pauses the attempt and offers retry");
        Keys(Key.Enter); yield return 3; Keys();
        PlayerDamageReceiver nextPlayer = null;
        for (int frame = 0; frame < 1500; frame++)
        {
            nextPlayer = Object.FindAnyObjectByType<PlayerDamageReceiver>();
            if (nextPlayer && nextPlayer != victim && Time.timeScale > 0f) break;
            yield return 1;
        }
        Check(nextPlayer && nextPlayer != victim && nextPlayer.CurrentHP == nextPlayer.MaxHP && Time.timeScale > 0f,
            "Enter starts a new attempt at full player HP");
        var freshGuards = Object.FindObjectsByType<GuardLoadout>();
        Check(freshGuards.Length == 2 && freshGuards.All(g => !g.IsDown && g.CurrentHP == g.MaxHP),
            "retry restores both B5 guards");
    }

    static IEnumerator CheckGuardFire(GameObject prefab)
    {
        var enemy=Object.Instantiate(prefab,new Vector3(2,0,-1.8f),Quaternion.identity);
        var presenter=enemy.GetComponent<GuardPresenter>();
        MoveFeet(new Vector3(2,.015f,2.2f));
        presenter.BindPlayer(inventory.GetComponent<PlayerMotor>());
        var gun=enemy.GetComponentInChildren<SwapShotAbility>();
        var victim=inventory.GetComponent<PlayerDamageReceiver>();
        int hits=0;victim.Damaged+=amount=>hits+=amount;
        int before = victim.CurrentHP;
        for(int i=0;i<320 && !presenter.ShotPending;i++)yield return 1;
        Check(presenter.ShotPending && hits==0 && gun.RemainingRounds==3,"guard gives warning before damage");
        var wall=GameObject.CreatePrimitive(PrimitiveType.Cube);
        wall.transform.position=(enemy.GetComponent<CharacterController>().bounds.center+body.bounds.center)*.5f;
        wall.transform.localScale=new Vector3(2.4f,3f,.22f);
        Physics.SyncTransforms();yield return 105;
        Check(!presenter.ShotPending && hits==0 && gun.RemainingRounds==3,"cover cancels guard shot without spending a round");
        Object.Destroy(wall);yield return 2;
        for(int i=0;i<360 && hits==0;i++)yield return 1;
        Check(hits==1 && victim.CurrentHP==before-1 && gun.RemainingRounds==2 && victim.MovementScale<1f,"guard fires its own round through IDamageable");
        enemy.GetComponent<IDamageable>().TakeDamage(1);yield return 95;
        Check(hits==1 && victim.MovementScale==1f && gun.RemainingRounds==2,"downed guard stops firing and retains its actual remaining uses");
        var testActor = new GameObject("Test guard HP override");
        testActor.SetActive(false);
        var guard = testActor.AddComponent<GuardLoadout>();
        var settings = new UnityEditor.SerializedObject(guard);
        settings.FindProperty("maxHP").intValue = 3;
        settings.ApplyModifiedPropertiesWithoutUndo();
        testActor.SetActive(true);
        Check(guard.MaxHP == 3 && guard.TakeDamage(1) && guard.CurrentHP == 2 && !guard.IsDown,
            "guard prefab HP override survives a partial hit");
        testActor.SetActive(false); testActor.SetActive(true);
        Check(guard.CurrentHP == 2 && guard.TakeDamage(3) && guard.IsDown && guard.CurrentHP == 0 && !guard.TakeDamage(1),
            "guard retains HP on re-enable and falls only once at zero");
        Object.Destroy(testActor);
    }
}
