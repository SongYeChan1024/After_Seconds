if(Application.isPlaying)throw new System.Exception("Edit mode required");AssetDatabase.Refresh();
const string root="Assets/Afrer_Seconds/";const string fontPath=root+"06.Data/UI/Pickup_Korean_SDF.asset";
var font=AssetDatabase.LoadAssetAtPath<TMPro.TMP_FontAsset>(fontPath);
if(font==null)
{
    var source=AssetDatabase.LoadAssetAtPath<Font>(root+"06.Data/UI/NotoSansKR.ttf");if(source==null)throw new System.Exception("Font not imported");
    font=TMPro.TMP_FontAsset.CreateFontAsset(source,64,6,UnityEngine.TextCore.LowLevel.GlyphRenderMode.SDFAA,1024,1024,TMPro.AtlasPopulationMode.Dynamic);
    font.name="Pickup_Korean_SDF";font.isMultiAtlasTexturesEnabled=true;AssetDatabase.CreateAsset(font,fontPath);
    AssetDatabase.AddObjectToAsset(font.material,font);foreach(var texture in font.atlasTextures)AssetDatabase.AddObjectToAsset(texture,font);
    string chars="소지품빈손휠선택내려놓기시험용공줍간이없어을▶·[]FQ0123456789/ ";
    if(!font.TryAddCharacters(chars,out string missing))throw new System.Exception("Missing glyphs: "+missing);
    font.material.SetColor("_OutlineColor",new Color(0.015f,.025f,.03f,1));font.material.SetFloat("_OutlineWidth",.15f);EditorUtility.SetDirty(font);EditorUtility.SetDirty(font.material);
}
var current=UnityEngine.Object.FindAnyObjectByType<PlayerInventory>();string path=PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(current.gameObject);var player=PrefabUtility.LoadPrefabContents(path);
try
{
    if(player.transform.Find("InventoryHUD")!=null)throw new System.Exception("HUD already exists; edit incrementally");
    var go=new GameObject("InventoryHUD",typeof(RectTransform),typeof(Canvas),typeof(UnityEngine.UI.CanvasScaler),typeof(UnityEngine.UI.GraphicRaycaster));go.transform.SetParent(player.transform,false);
    var canvas=go.GetComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceOverlay;canvas.sortingOrder=20;
    var scaler=go.GetComponent<UnityEngine.UI.CanvasScaler>();scaler.uiScaleMode=UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);scaler.matchWidthOrHeight=.5f;
    RectTransform Rect(string name,Vector2 anchor,Vector2 pivot,Vector2 pos,Vector2 size)
    {
        var child=new GameObject(name,typeof(RectTransform));var rect=child.GetComponent<RectTransform>();rect.SetParent(go.transform,false);rect.anchorMin=rect.anchorMax=anchor;rect.pivot=pivot;rect.anchoredPosition=pos;rect.sizeDelta=size;return rect;
    }
    TMPro.TextMeshProUGUI Text(RectTransform rect,float size,TMPro.TextAlignmentOptions align)
    {
        var label=rect.gameObject.AddComponent<TMPro.TextMeshProUGUI>();label.font=font;label.fontSize=size;label.color=new Color(.93f,.96f,.97f);label.alignment=align;label.raycastTarget=false;label.text="";return label;
    }
    var panel=Rect("InventoryBacking",new Vector2(1,0),new Vector2(1,0),new Vector2(-32,32),new Vector2(350,260));var image=panel.gameObject.AddComponent<UnityEngine.UI.Image>();image.color=new Color(.025f,.035f,.045f,.66f);image.raycastTarget=false;
    var contents=Text(Rect("Contents",new Vector2(1,0),new Vector2(1,0),new Vector2(-48,48),new Vector2(318,228)),25,TMPro.TextAlignmentOptions.TopLeft);
    var prompt=Text(Rect("PickupPrompt",new Vector2(.5f,.5f),new Vector2(.5f,.5f),new Vector2(0,-78),new Vector2(650,54)),30,TMPro.TextAlignmentOptions.Center);
    var dot=Rect("PickupReticle",new Vector2(.5f,.5f),new Vector2(.5f,.5f),Vector2.zero,new Vector2(4,4)).gameObject.AddComponent<UnityEngine.UI.Image>();dot.color=new Color(.85f,.95f,.95f,.6f);dot.raycastTarget=false;
    var view=go.AddComponent<PlayerInventoryView>();var so=new SerializedObject(view);so.FindProperty("inventory").objectReferenceValue=player.GetComponent<PlayerInventory>();so.FindProperty("prompt").objectReferenceValue=prompt;so.FindProperty("contents").objectReferenceValue=contents;so.ApplyModifiedPropertiesWithoutUndo();
    PrefabUtility.SaveAsPrefabAsset(player,path);
}
finally{PrefabUtility.UnloadPrefabContents(player);}
AssetDatabase.SaveAssets();var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene);
return new{font=AssetDatabase.GetAssetPath(font),glyphs=font.characterTable.Count,canvases=UnityEngine.Object.FindObjectsByType<Canvas>(FindObjectsSortMode.None).Length};
