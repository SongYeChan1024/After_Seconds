if(Application.isPlaying)throw new System.Exception("Edit mode required");
var package=System.IO.Directory.GetFiles("Library/PackageCache","TMP Essential Resources.unitypackage",System.IO.SearchOption.AllDirectories);
if(package.Length!=1)throw new System.Exception("Expected TMP Essentials package");
AssetDatabase.ImportPackage(package[0],false);return "Imported TMP Essentials for first uGUI HUD";
