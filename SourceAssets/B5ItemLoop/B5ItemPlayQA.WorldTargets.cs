using System.Collections;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Object = UnityEngine.Object;

// 의사코드: 같은 월드 아이템을 줍고 내려놓아 사격한다. 직접 제압한 경비와 바닥 물건은 실제 투척 충돌로도 검사한다.
public static partial class B5ItemPlayQA
{
    static WorldItem PutInReach(string prefabPath)
    {
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
        var item = Object.Instantiate(prefab, thrower.Origin.position + thrower.Origin.forward * .85f,
            Quaternion.identity).GetComponent<WorldItem>();
        Physics.SyncTransforms();
        inventory.RefreshCandidate();
        Check(inventory.Candidate == item && inventory.TryPickup(), "pick up " + item.name);
        return item;
    }

    static void PlaceLoose(WorldItem item, Vector3 point)
    {
        var rigid = item.GetComponent<Rigidbody>();
        rigid.position = point;
        rigid.rotation = Quaternion.identity;
        rigid.linearVelocity = rigid.angularVelocity = Vector3.zero;
        Physics.SyncTransforms();
    }

    static IEnumerator ThrowAt(SwapTarget target)
    {
        LookAt(thrower.Origin.position + Vector3.forward * 3f);
        var ball = PutInReach(B5ItemAuthoring.Root + "04.Prefabs/Test/ThrowTestItem.prefab");
        thrower.BeginAim();
        Check(thrower.ReleaseThrow(), "release projectile through normal throw path");
        // 작은 USB도 매번 같은 각도로 맞도록 발사 후 초기 조건을 고정한다. 명중은 PhysX가 판정한다.
        var rigid = ball.GetComponent<Rigidbody>();
        rigid.position = target.Body.bounds.center + Vector3.up * .8f;
        rigid.linearVelocity = Vector3.down * 4f;
        Physics.SyncTransforms();
        int relocations = 0;
        Vector3 source = Feet(), targetStart = target.transform.position;
        target.Relocated += () => relocations++;
        for (int i = 0; i < 45 && inventory.Message != "위치 교환 예약"; i++) yield return 1;
        Check(inventory.Message == "위치 교환 예약", "physical contact reserves " + target.name);
        yield return 90;
        Check(relocations == 0, "impact obeys three-second delay " + target.name);
        yield return 115;
        Check(relocations == 1 && Vector3.Distance(Flat(source), Flat(target.transform.position)) < .25f &&
            Vector3.Distance(Flat(Feet()), Flat(targetStart)) < .55f, "impact exchanges both positions " + target.name);
        Object.Destroy(ball.gameObject);
    }

    static IEnumerator CheckWorldTargets()
    {
        yield return 30;
        var folders = new[] { B5ItemAuthoring.Root+"04.Prefabs/Items", B5ItemAuthoring.Root+"04.Prefabs/Test" };
        var prefabs = AssetDatabase.FindAssets("t:Prefab", folders).Select(id =>
            AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(id))).Where(p => p.GetComponent<WorldItem>()).ToArray();
        Check(prefabs.Length >= 12 && System.Array.TrueForAll(prefabs, p =>
            p.GetComponent<SwapTarget>() && p.GetComponent<SwapTarget>().Body == p.GetComponent<Collider>()),
            "each shipped WorldItem prefab binds its physical hit collider");
        Check(!GameObject.Find("소품 받침대").GetComponent<SwapTarget>(), "decorative prop stays outside swap targets");
        var gun = inventory.Candidate;
        Check(gun && gun.Ability is SwapShotAbility && inventory.TryPickup(), "pick up review pistol");
        var start = new Vector3(-2,.008f,-1.25f);
        var far = new Vector3(-2,.05f,2.2f);
        MoveFeet(start); LookAt(thrower.Origin.position + Vector3.forward*3);
        var usb = PutInReach(B5ItemAuthoring.PrefabPath("UsbDrive"));
        var usbTarget = usb.GetComponent<SwapTarget>();
        Check(!usbTarget.Available, "stored item unavailable");
        Check(inventory.TryDrop() && inventory.Selected == gun && usbTarget.Available, "Q releases the same item into the world");
        PlaceLoose(usb, far); yield return 45;
        var name = usb.Number;
        LookAt(usbTarget.Body.bounds.center); inventory.UseAimedItem();
        Check(inventory.Message == "위치 교환 예약", "aimed shot reserves dropped USB");
        var moved = start + Vector3.right * .65f;
        MoveFeet(moved); yield return 120;
        Check(Vector3.Distance(Flat(Feet()),Flat(moved)) < .18f, "shot waits before exchanging");
        yield return 80;
        Check(Vector3.Distance(Flat(Feet()),Flat(far)) < .18f && Vector3.Distance(Flat(usb.transform.position),Flat(moved)) < .18f &&
            usb.Number == name && usb.CanPickup, "shot exchanges current positions and preserves item identity");

        MoveFeet(start); PlaceLoose(usb, far); yield return 35;
        var swap = inventory.GetComponent<PlayerSwap>();
        int cancelledMoves = 0; usbTarget.Relocated += () => cancelledMoves++;
        Check(swap.ScheduleSightHit(usbTarget) && usb.TryStore(inventory.transform), "pick up a pending target");
        usb.Release(far,Quaternion.identity,0); yield return 200;
        Check(cancelledMoves == 0 && Vector3.Distance(Flat(Feet()),Flat(start)) < .18f, "dropping it again cannot revive an old reservation");
        MoveFeet(far - Vector3.forward * .75f); LookAt(usbTarget.Body.bounds.center);
        Check(inventory.TryPickup() && inventory.Selected == usb, "retrieve the same USB by interaction");
        MoveFeet(start); LookAt(thrower.Origin.position + Vector3.forward * 3);
        thrower.BeginAim();
        Check(thrower.ReleaseThrow(), "throw the USB before using it as the next target");
        PlaceLoose(usb, far + Vector3.up * .25f); yield return 90;
        var itemImpact = ThrowAt(usbTarget);
        while (itemImpact.MoveNext()) yield return itemImpact.Current;
        Object.Destroy(usb.gameObject); yield return 3;

        MoveFeet(start);
        var guardPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(B5ItemAuthoring.Root+"04.Prefabs/B5_MealGuard.prefab");
        var guard = Object.Instantiate(guardPrefab, new Vector3(-2,.012f,2.0f), Quaternion.identity);
        var loadout = guard.GetComponent<GuardLoadout>();
        var corpse = guard.GetComponent<SwapTarget>();
        var equipment = guard.GetComponentInChildren<WorldItem>();
        MoveFeet(guard.transform.position - guard.transform.forward * .85f);
        Check(loadout.TryInteract(body) && loadout.IsDown && corpse.Available && !corpse.Body.isTrigger, "rear takedown leaves a hittable body");
        MoveFeet(start); yield return 65;
        var gunDrop = equipment.transform.position;
        LookAt(corpse.Body.bounds.center);
        inventory.UseAimedItem();
        Check(inventory.Message == "위치 교환 예약" && loadout.CurrentHP == 0, "aimed shot reserves the already fallen guard");
        yield return 205;
        Check(Vector3.Distance(Flat(guard.transform.position),Flat(start)) < .2f &&
            Vector3.Distance(Flat(Feet()),new Vector3(-2,0,2)) < .2f &&
            Vector3.Distance(Flat(equipment.transform.position),Flat(gunDrop)) < .22f, "only the body exchanges and its dropped gun stays");
        var corpseImpact = ThrowAt(corpse);
        while (corpseImpact.MoveNext()) yield return corpseImpact.Current;
        Check(loadout.CurrentHP == 0 && !guard.GetComponent<GuardPresenter>().enabled &&
            !loadout.TryInteract(body), "repeated exchanges preserve defeat and do not drop another pistol");

        // 떨어뜨린 총을 따로 맞혀도 누운 몸은 따라오지 않는다.
        Vector3 bodyBefore = guard.transform.position;
        Vector3 pickupAt = equipment.transform.position;
        var pickupTarget = equipment.GetComponent<SwapTarget>();
        int gunMoves = 0;
        pickupTarget.Relocated += () => gunMoves++;
        MoveFeet(new Vector3(1.7f, .008f, 1.4f)); yield return 8;
        Vector3 beforeGunSwap = Feet();
        LookAt(pickupTarget.Body.bounds.center);
        var aim = thrower.Origin;
        bool visibleGun = thrower.Sweep(aim.position, aim.forward * 25f, 0f, out var firstHit) && firstHit.collider == pickupTarget.Body;
        Check(visibleGun, "dropped pistol is visible beside the guard: first hit " + firstHit.collider);
        inventory.UseAimedItem();
        Check(inventory.Message == "위치 교환 예약", "released guard pistol accepts its own shot reservation");
        yield return 205;
        Check(gunMoves == 1 && Vector3.Distance(Flat(Feet()), Flat(pickupAt)) < .2f &&
            Vector3.Distance(Flat(equipment.transform.position), Flat(beforeGunSwap)) < .2f &&
            Vector3.Distance(guard.transform.position, bodyBefore) < .02f, "dropped gun moves independently of the corpse: count=" + gunMoves + " player=" + Feet() + " to=" + pickupAt +
            " gun=" + equipment.transform.position + " to=" + beforeGunSwap + " corpseDelta=" + (guard.transform.position - bodyBefore));
    }
}

