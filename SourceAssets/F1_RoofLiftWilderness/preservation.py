"""Read-only Git/metadata audit; writes only the review evidence JSON."""
import subprocess,pathlib,re,json
root=pathlib.Path(__file__).resolve().parents[2]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.PIPE)
changed=[p for p in git('diff','--name-only','-z').decode().split('\0') if p]
tracked=[p for p in git('ls-files','-z','Unity').decode().split('\0') if p]
base='Unity/After_Seconds_Build_V0.01/'
allowed=[base+'Assets/Afrer_Seconds/05.Model/Environment/1F/',base+'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity',base+'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory/']
protected=[p for p in tracked if not any(p.startswith(a) for a in allowed)]
unexpected=[p for p in changed if p in protected]
guid_changes=[];checked=0
for p in changed:
 if not p.endswith('.meta'):continue
 old=git('show','HEAD:'+p).decode();new=(root/p).read_text();a=re.search(r'^guid: (\w+)',old,re.M);b=re.search(r'^guid: (\w+)',new,re.M)
 if a and b:
  checked+=1
  if a[1]!=b[1]:guid_changes.append(p)
new=[p for p in git('ls-files','--others','--exclude-standard','-z','Unity').decode().split('\0') if p]
missing_meta=[p for p in new if not p.endswith('.meta') and not (root/(p+'.meta')).exists()]
occ=base+'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory/OcclusionCullingData.asset.meta'
occ_same=git('show','HEAD:'+occ).decode().replace('\r\n','\n')==(root/occ).read_text()
before=json.loads((root/'Docs/Review/2026-11-13_1F_RoofLiftWilderness/before_transforms.json').read_text())
after=json.loads((root/'Docs/Review/2026-11-13_1F_RoofLiftWilderness/after_transforms.json').read_text())
ad={t['path']:t for t in after};changes=[]
for t in before:
 p=t['path']
 if any(k in p for k in ['F1_VL_LiftCabin_01','F1_VB_ArrivalFireDoor_01','OvercastDirectional']):continue
 if p not in ad:changes.append(dict(path=p,change='removed'))
 elif any(t[k]!=ad[p][k] for k in ['position','local','rotation','scale','active']):changes.append(dict(path=p,change='transform'))
result=dict(protectedTrackedFiles=len(protected),unexpectedProtectedChanges=unexpected,changedMetadataGUIDChecks=checked,changedGUIDs=guid_changes,newUnityFiles=len(new),newAssetsMissingMeta=missing_meta,occlusionMetadataPreserved=occ_same,unrelatedTransformChanges=changes,gameplaySourceChanges=[p for p in changed if p.startswith(base) and p.endswith('.cs')])
dest=root/'Docs/Review/2026-11-13_1F_RoofLiftWilderness/preservation.json';dest.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
assert not unexpected and not guid_changes and not missing_meta and not changes and occ_same
