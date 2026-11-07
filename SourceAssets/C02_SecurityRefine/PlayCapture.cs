using System;using System.IO;using UnityEngine;
public static class C02RefinePlayCapture {public static object Run(){if(!Application.isPlaying)throw new Exception("Play mode required");string p=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-08_C02_Refine/Play_Operations.png"));ScreenCapture.CaptureScreenshot(p);return new{requested=p,frame=Time.frameCount};}}
