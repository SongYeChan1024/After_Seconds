if(Application.isPlaying)throw new System.Exception("Edit mode required");
// TMP 기본 리소스는 Unity 표준 경로를 유지한다. 폴더 이동은 이 환경에서 접근 거부가 발생했다.
// 프로젝트 전용 폰트와 UI 데이터만 Assets/Afrer_Seconds/06.Data/UI 아래에 분류한다.
foreach(var window in Resources.FindObjectsOfTypeAll<EditorWindow>())if(window.GetType().Name=="TMP_PackageResourceImporterWindow")window.Close();
AssetDatabase.SaveAssets();return "TMP standard resource location retained; project UI data classified separately";
