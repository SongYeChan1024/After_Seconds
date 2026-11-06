// Level continuation play/performance review V0.01. External Editor tool only.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using Newtonsoft.Json;
public static class PlayPerformance {
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Output=>Repo+"/Docs/검수/2026-11-06_LevelContinuation/";
 static float[] V(Vector3 p)=>new[]{p.x,p.y,p.z};
 public static object PrepareB5()=>Prepare("B5");
 public static object PrepareB4()=>Prepare("B4");
 public static object PrepareB3()=>Prepare("B3");
 static object Prepare(string floor){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved Edit Mode required");var s=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var p=UnityEngine.Object.FindAnyObjectByType<CharacterController>();Directory.CreateDirectory(Output);return new{scene=s.path,p.name,position=V(p.transform.position),camera=Camera.main.name,quality=QualitySettings.names[QualitySettings.GetQualityLevel()],runInBackground=Application.runInBackground};}
 public static object Begin(){
  if(!EditorApplication.isPlaying)throw new Exception("Play Mode required");
  var p=UnityEngine.Object.FindAnyObjectByType<CharacterController>();var k=Keyboard.current;if(!p||k==null)throw new Exception("Player/input missing");
  EditorWindow.GetWindow(typeof(EditorWindow).Assembly.GetType("UnityEditor.GameView")).Focus();
  string floor=SceneManager.GetActiveScene().name.Contains("B5")?"B5":SceneManager.GetActiveScene().name.Contains("B4")?"B4":"B3";
  var poses=floor=="B5"?new[]{new[]{-3.5f,.89f,-8,0},new[]{5f,.89f,-9,70},new[]{18.25f,.89f,9.4f,180}}:floor=="B4"?new[]{new[]{-3.5f,.89f,-8,0},new[]{10.5f,.89f,-8,270},new[]{0f,.89f,6.8f,135}}:new[]{new[]{-3.5f,.89f,-8,0},new[]{-10f,.89f,-5,0},new[]{9f,.89f,4,270}};
  var log=new List<object>();Application.LogCallback logging=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)log.Add(new{type=t.ToString(),message=m});};Application.logMessageReceived+=logging;
  int stage=-1,frameStart=Time.frameCount,last=-1;var clock=System.Diagnostics.Stopwatch.StartNew();var samples=new List<object>();var stagePositions=new List<object>();var timing=new FrameTiming[1];bool pressed=false,released=false;Vector3 start=p.transform.position;int frames=0;
  EditorApplication.CallbackFunction cb=null;Action cleanup=()=>{InputSystem.QueueStateEvent(k,new KeyboardState());Application.logMessageReceived-=logging;EditorApplication.update-=cb;};
  cb=()=>{try{
   if(!EditorApplication.isPlaying||!p)throw new Exception("Session interrupted");double elapsed=clock.Elapsed.TotalSeconds;int index=(int)(elapsed/8);
   if(index>=3){stagePositions.Add(new{stage,finish=V(p.transform.position)});cleanup();File.WriteAllText(Output+floor+"_play_performance.json",JsonConvert.SerializeObject(new{floor,mode="Editor Play Mode, three 8-second views, 2-second warm-up each; W input during corridor sample",hardware=new{cpu=SystemInfo.processorType,gpu=SystemInfo.graphicsDeviceName,api=SystemInfo.graphicsDeviceType.ToString(),memoryMB=SystemInfo.systemMemorySize},resolution=new{width=Camera.main.pixelWidth,height=Camera.main.pixelHeight,scale=UnityEngine.Rendering.Universal.UniversalRenderPipeline.asset.renderScale},quality=QualitySettings.names[QualitySettings.GetQualityLevel()],vsync=QualitySettings.vSyncCount,targetFPS=Application.targetFrameRate,frameStart,frameEnd=Time.frameCount,observedDistinctFrames=frames,positions=stagePositions,samples,logs=log,limits="Editor diagnostics, not standalone target-hardware benchmark"},Formatting.Indented));return;}
   if(index!=stage){if(stage>=0)stagePositions.Add(new{stage,finish=V(p.transform.position)});stage=index;InputSystem.QueueStateEvent(k,new KeyboardState());var a=poses[stage];p.enabled=false;p.transform.SetPositionAndRotation(new Vector3(a[0],a[1],a[2]),Quaternion.Euler(0,a[3],0));p.enabled=true;Physics.SyncTransforms();start=p.transform.position;stagePositions.Add(new{stage,start=V(start)});}
   double t=elapsed-stage*8;if(stage==0&&t>=2&&!pressed){InputSystem.QueueStateEvent(k,new KeyboardState(Key.W));pressed=true;}if(stage==0&&t>=3&&!released){InputSystem.QueueStateEvent(k,new KeyboardState());released=true;}
   if(Time.frameCount==last)return;last=Time.frameCount;frames++;FrameTimingManager.CaptureFrameTimings();uint count=FrameTimingManager.GetLatestTimings(1,timing);
   if(t>=2)samples.Add(new{stage,frame=Time.frameCount,deltaMs=Time.unscaledDeltaTime*1000,cpuMs=count>0?timing[0].cpuFrameTime:0,mainMs=count>0?timing[0].cpuMainThreadFrameTime:0,gpuMs=count>0?timing[0].gpuFrameTime:0,drawCalls=UnityStats.drawCalls,setPass=UnityStats.setPassCalls,triangles=UnityStats.triangles,focused=Application.isFocused});
  }catch(Exception e){cleanup();File.WriteAllText(Output+floor+"_play_performance.json",JsonConvert.SerializeObject(new{error=e.ToString()},Formatting.Indented));}};
  EditorApplication.update+=cb;return new{started=true,floor,frameStart,durationSeconds=24};
 }
 public static object Status()=>new{playing=EditorApplication.isPlaying,frame=Time.frameCount,focused=Application.isFocused,scene=SceneManager.GetActiveScene().path,dirty=SceneManager.GetActiveScene().isDirty,runInBackground=Application.runInBackground};
}

