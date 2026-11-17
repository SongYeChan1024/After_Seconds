// Unity CLI script eval_file용. 독립 물리 씬에서 실제 PhysX와 공유 적분을 비교한다.
if (!Application.dataPath.Contains("After_Seconds_Build")) throw new System.Exception("Wrong project");
var prefab = UnityEditor.AssetDatabase.LoadAssetAtPath<ThrownObject>("Assets/Afrer_Seconds/04.Prefabs/Test/ThrowTestItem.prefab");
var report = new System.Text.StringBuilder();
int passed = 0, failed = 0;
foreach (float damping in new[] { 0f, 0.5f })
foreach (float dt in new[] { 0.01f, 0.02f, 0.0333333f })
{
    var scene = UnityEngine.SceneManagement.SceneManager.CreateScene("ThrowFlightCheck_" + System.Guid.NewGuid(), new UnityEngine.SceneManagement.CreateSceneParameters(UnityEngine.SceneManagement.LocalPhysicsMode.Physics3D));
    try
    {
        var item = UnityEngine.Object.Instantiate(prefab);
        UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(item.gameObject, scene);
        var rb = item.GetComponent<Rigidbody>(); rb.linearDamping = damping;
        Vector3 predicted = new Vector3(0f, 10f, 0f), velocity = new Vector3(1.2f, 3f, 11.8f);
        rb.position = predicted; rb.linearVelocity = velocity;
        float maximum = 0f;
        var physics = scene.GetPhysicsScene();
        int steps = Mathf.RoundToInt(1f / dt);
        for (int i = 0; i < steps; i++)
        {
            ThrowFlight.Step(ref predicted, ref velocity, Physics.gravity, damping, dt);
            physics.Simulate(dt);
            maximum = Mathf.Max(maximum, Vector3.Distance(predicted, rb.position));
        }
        bool ok = maximum < 0.001f; if (ok) passed++; else failed++;
        report.AppendLine($"free dt={dt:F5} damping={damping:F1}: max position error={maximum:F7}m {(ok ? "PASS" : "FAIL")}");
    }
    finally { UnityEngine.SceneManagement.SceneManager.UnloadSceneAsync(scene); }
}
foreach (string scenario in new[] { "flat", "high", "slope", "ceiling", "close_wall", "door_frame", "narrow_window", "open_window" })
{
    var scene = UnityEngine.SceneManagement.SceneManager.CreateScene("ThrowCollisionCheck_" + System.Guid.NewGuid(), new UnityEngine.SceneManagement.CreateSceneParameters(UnityEngine.SceneManagement.LocalPhysicsMode.Physics3D));
    try
    {
        void Box(Vector3 pos, Vector3 scale, float tilt = 0f)
        {
            var go = new GameObject("check_" + scenario); go.layer = 31;
            UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(go, scene);
            go.transform.position = pos; go.transform.localScale = scale; go.transform.rotation = Quaternion.Euler(tilt,0,0);
            go.AddComponent<BoxCollider>();
        }
        Vector3 start = new Vector3(0f, 1.6f, 0f), initial = new Vector3(0f, 1.67f, 11.88f);
        if (scenario == "flat") Box(new Vector3(0,-0.2f,5),new Vector3(20,0.4f,30));
        if (scenario == "high") Box(new Vector3(0,-5.2f,5),new Vector3(20,0.4f,40));
        if (scenario == "slope") Box(new Vector3(0,0,5),new Vector3(20,0.4f,30),-12f);
        if (scenario == "ceiling") Box(new Vector3(0,1.82f,5),new Vector3(20,0.1f,20));
        if (scenario == "close_wall") Box(new Vector3(0,1.5f,0.2f),new Vector3(3,4,0.1f));
        if (scenario == "door_frame") { Box(new Vector3(0.11f,1.5f,2),new Vector3(0.12f,3,0.3f)); Box(new Vector3(-1,1.5f,2),new Vector3(0.12f,3,0.3f)); }
        if (scenario.Contains("window"))
        {
            float gap=scenario=="narrow_window"?0.08f:0.6f;
            Box(new Vector3(-gap/2-0.5f,1.5f,2),new Vector3(1,3,0.3f));
            Box(new Vector3(gap/2+0.5f,1.5f,2),new Vector3(1,3,0.3f));
            Box(new Vector3(0,-0.2f,5),new Vector3(20,0.4f,30));
        }
        var item = UnityEngine.Object.Instantiate(prefab);
        UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(item.gameObject,scene);
        var rb=item.GetComponent<Rigidbody>(); rb.position=start;rb.linearVelocity=initial;
        var collider=item.GetComponent<SphereCollider>();float radius=0.06f;
        var physics=scene.GetPhysicsScene();Vector3 p=start,v=initial;
        int predictedStep=-1,actualStep=-1;Vector3 predictedCenter=Vector3.zero,actualCenter=Vector3.zero;
        float maxBefore=0f;
        for(int i=1;i<=150;i++)
        {
            Vector3 previous=p;ThrowFlight.Step(ref p,ref v,Physics.gravity,0f,0.02f);
            Vector3 delta=p-previous;
            if(physics.SphereCast(previous,radius,delta.normalized,out var predictedHit,delta.magnitude,1<<31,QueryTriggerInteraction.Ignore))
            {predictedStep=i;predictedCenter=previous+delta.normalized*predictedHit.distance;break;}
        }
        p=start;v=initial;
        for(int i=1;i<=150;i++)
        {
            ThrowFlight.Step(ref p,ref v,Physics.gravity,0f,0.02f);
            physics.Simulate(0.02f);
            float error=Vector3.Distance(p,rb.position);
            if(Vector3.Distance(v,rb.linearVelocity)>0.001f || error>0.002f)
            {actualStep=i;actualCenter=rb.position;break;}
            maxBefore=Mathf.Max(maxBefore,error);
        }
        float contactError=Vector3.Distance(predictedCenter,actualCenter);
        bool ok=predictedStep>0 && actualStep>0 && Mathf.Abs(actualStep-predictedStep)<=1 && contactError<0.26f;
        if(ok)passed++;else failed++;
        report.AppendLine($"{scenario}: predicted tick={predictedStep}, actual tick={actualStep}, post-solver center difference={contactError:F5}m, pre-contact max={maxBefore:F7}m {(ok?"PASS":"FAIL")}");
    }
    finally { UnityEngine.SceneManagement.SceneManager.UnloadSceneAsync(scene); }
}
report.AppendLine($"TOTAL passed={passed}, failed={failed}. Collision positions include remaining fixed-step solver motion, not sub-frame impact time.");
var output=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_FirstPersonThrow/physics_validation.txt"));
System.IO.File.WriteAllText(output,report.ToString());
return report.ToString();
