using System.Collections.Generic;
using UnityEngine;

// 의사코드: 한 바퀴를 마친 경비가 짝과 만나면 장비와 역할을 바꾼다. 네 번째 복귀 전에 접근 시간을 빼고 새 조를 호출한다.
// 인계점에 실제로 모인 조만 근무를 넘긴다. 먼저 온 조는 기다리고, 퇴근조는 계단까지 걸어가서 층을 떠난다.
public sealed class DomeShift
{
    private readonly FloorSecurity floor;
    public DomePost Post { get; }
    public StairApproach Stair { get; }
    public GuardPresenter Runner { get; private set; }
    public GuardPresenter Watcher { get; private set; }
    public int Laps { get; private set; }
    public int TeamsRelieved { get; private set; }
    public float LastDispatch { get; private set; }
    public float LastArrival { get; private set; }
    public float LastFourthReturn { get; private set; }
    public float LastArrivalOffset { get; private set; }
    public bool ReliefOnWay => arriving != null;
    private GuardPresenter[] arriving;
    private readonly List<Departure> departures = new();
    private struct Departure { public GuardPresenter guard; public int lane; public bool entered; }
    private readonly float[] tailSeconds;
    private readonly float nominalLap, speed;
    private float pace = 1f, approachPace = 1f, activeSeconds, lastTick;
    private bool gathering, credited;

    public DomeShift(FloorSecurity floor, DomePost post, StairApproach stair, GuardPresenter runner, GuardPresenter watcher)
    {
        this.floor = floor;
        Post = post;
        Stair = stair;
        speed = runner.Settings.patrolSpeed;
        var wait = runner.Settings.patrolWait;
        tailSeconds = new float[post.circuit.Length + 1];
        for (int i = post.circuit.Length - 1; i >= 0; --i)
            tailSeconds[i] = tailSeconds[i + 1] + post.legLengths[i] / speed + post.WaitAt(i, wait);
        nominalLap = tailSeconds[0];
        lastTick = Time.time;
        StartLap(runner, watcher);
    }

    private void StartLap(GuardPresenter runner, GuardPresenter watcher)
    {
        Runner = runner;
        Watcher = watcher;
        Runner.Duty.BeginCircuit(Post.circuit, Post.Entrances, Post.inspectionStops);
        Watcher.Duty.Watch(Post.indoor, Post.watch, Post.watchYaw, Post.chairFeet, Post.Entrances);
        activeSeconds = 0f;
        gathering = credited = false;
    }

    private static bool Free(GuardPresenter guard) => guard && guard.isActiveAndEnabled &&
        !guard.RedAlert && !guard.HasSight && !guard.Duty.Investigating && !guard.Duty.OnStairs;

    private float Remaining()
    {
        int index = Runner.Duty.StopIndex;
        if (Runner.Duty.CircuitDone) return (3 - Laps) * nominalLap * pace;
        var previous = index == 0 ? Post.meeting[0] : Post.circuit[index - 1];
        float fraction = Mathf.Clamp01(Vector3.Distance(Runner.transform.position, Post.circuit[index]) /
            Mathf.Max(.1f, Vector3.Distance(previous, Post.circuit[index])));
        float thisLeg = fraction * Post.legLengths[index] / speed + Post.WaitAt(index, Runner.Settings.patrolWait);
        return (thisLeg + tailSeconds[index + 1] + (3 - Laps) * nominalLap) * pace;
    }

    public void Tick()
    {
        TickDepartures();
        float dt = Time.time - lastTick;
        lastTick = Time.time;
        if (arriving != null && LastArrival == 0f && Together(arriving[0], arriving[1]))
        {
            LastArrival = Time.time;
            approachPace = Mathf.Clamp((LastArrival - LastDispatch) / Mathf.Max(1f, Post.arrivalDistance / speed), .75f, 1.8f);
        }
        if (!Free(Runner) || !Free(Watcher)) return;
        activeSeconds += dt;
        float remaining = Remaining();
        if (arriving == null && remaining <= Post.arrivalDistance / speed * approachPace && floor.BookStair(Post.stairIndex))
            Dispatch();
        // 돔 안쪽에서 보초를 서는 사람도 제때 인계 위치로 걸어온다.
        if (!gathering && Runner.Duty.StopIndex == Post.circuit.Length - 1)
        {
            gathering = true;
            Watcher.Duty.MeetAt(Post.meeting[1]);
        }
        if (!Runner.Duty.CircuitDone) return;
        if (!credited)
        {
            credited = true;
            if (Laps == 3) LastFourthReturn = Time.time;
            pace = Mathf.Clamp(Mathf.Lerp(pace, activeSeconds / Mathf.Max(1f, nominalLap), .65f), .65f, 2f);
            Runner.Duty.MeetAt(Post.meeting[0]);
        }
        if (!Together(Runner, Watcher)) return;
        if (Laps < 3)
        {
            Runner.Equipment.ExchangeDutyItems(Watcher.Equipment);
            Laps++;
            StartLap(Watcher, Runner);
            return;
        }
        if (arriving == null || !Together(arriving[0], arriving[1])) return;
        Depart(Runner, 0);
        Depart(Watcher, 1);
        Laps = 0;
        LastArrivalOffset = LastArrival - LastFourthReturn;
        TeamsRelieved++;
        floor.HandedOver();
        StartLap(arriving[0], arriving[1]);
        arriving = null;
    }

    private static bool Together(GuardPresenter first, GuardPresenter second) =>
        Free(first) && Free(second) && first.Duty.AtHandover && second.Duty.AtHandover;

    private void Dispatch()
    {
        arriving = new GuardPresenter[2];
        LastDispatch = Time.time;
        LastArrival = 0f;
        for (int lane = 0; lane < 2; lane++)
        {
            var actor = floor.SpawnGuard(Post.id + "_Relief_" + lane, Stair.entryFeet[lane], lane == 0 ? 1 : 0);
            actor.Duty.Assign(lane == 0 ? 1 : 0, Post.indoor, 0, Post.Entrances);
            actor.Duty.MeetAt(Post.meeting[lane + 2]);
            actor.Duty.EnterStairs(Stair.threshold[lane], Stair.landings[lane]);
            arriving[lane] = actor;
        }
    }

    private void Depart(GuardPresenter actor, int lane)
    {
        actor.Duty.MeetAt(Stair.landings[lane]);
        departures.Add(new Departure { guard = actor, lane = lane });
    }

    private void TickDepartures()
    {
        for (int i = departures.Count - 1; i >= 0; i--)
        {
            var person = departures[i];
            var actor = person.guard;
            if (!actor || actor.IsDown) { departures.RemoveAt(i); continue; }
            if (!Free(actor)) continue;
            if (person.entered)
            {
                if (actor.Duty.AtStairExit)
                {
                    floor.SendHome(actor);
                    departures.RemoveAt(i);
                }
                else
                {
                    // 퇴근 도중 능력으로 자리가 바뀌면 새 위치에서 계단까지 다시 걸어온다.
                    actor.Duty.MeetAt(Stair.landings[person.lane]);
                    person.entered = false;
                    departures[i] = person;
                }
            }
            else if (actor.Duty.AtHandover && floor.BookStair(Post.stairIndex))
            {
                actor.Duty.EnterStairs(Stair.threshold[person.lane], Stair.entryFeet[person.lane], true);
                person.entered = true;
                departures[i] = person;
            }
        }
    }
}
