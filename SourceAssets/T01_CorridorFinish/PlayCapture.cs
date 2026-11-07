using System;using System.IO;using UnityEngine;
public static class T01PlayCapture {public static object Run(){if(!Application.isPlaying)throw new Exception("Play mode required");string p=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-07_T01_Corridor/Play_Threshold.png"));ScreenCapture.CaptureScreenshot(p);return new{requested=p,frame=Time.frameCount};}}
