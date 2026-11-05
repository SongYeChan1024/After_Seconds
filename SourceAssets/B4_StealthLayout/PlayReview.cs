using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using Newtonsoft.Json;

public static class PlayReview
{
    public static object Begin()
    {
        if(!EditorApplication.isPlaying) throw new InvalidOperationException("Play Mode required");
        var player=UnityEngine.Object.FindFirstObjectByType<CharacterController>();
        var keyboard=Keyboard.current;
        if(!player || keyboard==null) throw new InvalidOperationException("Player or keyboard unavailable");
        var before=player.transform.position;
        var startFrame=Time.frameCount;
        var stopwatch=System.Diagnostics.Stopwatch.StartNew();
        var frameSamples=new List<int>();
        bool pressed=false;
        bool released=false;
        EditorApplication.CallbackFunction callback=null;
        callback=()=>{
            try {
                if(!EditorApplication.isPlaying || !player) throw new InvalidOperationException("Play session ended during verification");
                if(!pressed) {InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.W));pressed=true;}
                if(stopwatch.Elapsed.TotalSeconds>=0.8 && !released) {InputSystem.QueueStateEvent(keyboard,new KeyboardState());released=true;}
                if(frameSamples.Count==0 || frameSamples[frameSamples.Count-1]!=Time.frameCount) frameSamples.Add(Time.frameCount);
                if(stopwatch.Elapsed.TotalSeconds<1.8) return;
                var after=player.transform.position;
                var output=new {mode="Play Mode; Input System keyboard W for 0.8 seconds",startFrame,endFrame=Time.frameCount,distinctFrames=frameSamples.Count,before=new[]{before.x,before.y,before.z},after=new[]{after.x,after.y,after.z},distance=Vector3.Distance(before,after),isPlaying=EditorApplication.isPlaying,isFocused=Application.isFocused,runInBackground=Application.runInBackground,grounded=player.isGrounded};
                File.WriteAllText("C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4/play_input.json",JsonConvert.SerializeObject(output,Formatting.Indented));
                EditorApplication.update-=callback;
            }
            catch(Exception exception) {
                InputSystem.QueueStateEvent(keyboard,new KeyboardState());
                EditorApplication.update-=callback;
                File.WriteAllText("C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4/play_input.json",JsonConvert.SerializeObject(new{error=exception.ToString()},Formatting.Indented));
            }
        };
        EditorApplication.update+=callback;
        return new{started=true,startFrame,before=before.ToString()};
    }
}
