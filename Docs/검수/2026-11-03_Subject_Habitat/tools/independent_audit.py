# [의사코드] 현재 저장 파일을 작업 시작 해시와 대조하고 새 모델/프리팹의 출처·치수·GUID를 독립 검사한다.
# [코딩]
from pathlib import Path
import hashlib,json,re,subprocess,collections,sys
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;u=r/'Unity/After_Seconds_Build_V0.01';assets=u/'Assets';base=json.loads((w/'baseline_hashes.json').read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[];removed=[]
for name,h in base.items():
 p=r/name
 if not p.is_file():removed.append(name)
 elif sha(p)!=h:changed.append(name)
allowed_scene='Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Isolation.unity'
protected=[name for name in base if name.startswith('Unity/') and name not in (allowed_scene,'Unity/README.md') or name.startswith('SourceAssets/')]
bad=[n for n in protected if n in changed or n in removed]
asset_new=[p for p in assets.rglob('*') if p.is_file() and p.relative_to(r).as_posix() not in base]
source_new=[p.relative_to(r).as_posix() for p in (r/'SourceAssets').rglob('*') if p.is_file() and p.relative_to(r).as_posix() not in base]
source_allowed={'SourceAssets/SubjectHabitat/SubjectHabitat.blend','SourceAssets/SubjectHabitat/DualFoodHatch.blend'}
source_unexpected=[n for n in source_new if n not in source_allowed]
model=assets/'Afrer_Seconds/05.Model';folder_violations=[]
for category in ['Props','Environment']:
 for floor in (model/category).iterdir():
  if not floor.is_dir():continue
  for d in floor.rglob('*'):
   if d.is_dir() and (len(d.relative_to(floor).parts)>1 or d.name not in ('Materials','Textures')):folder_violations.append(d.relative_to(u).as_posix())
for category in ['Player','Enemy']:
 for d in (model/category).rglob('*'):
  if d.is_dir() and (len(d.relative_to(model/category).parts)>1 or d.name not in ('Materials','Textures')):folder_violations.append(d.relative_to(u).as_posix())
guid_re=re.compile(r'^guid:\s*([a-f0-9]{32})\s*$',re.M);ref_re=re.compile(r'guid:\s*([a-f0-9]{32})')
guid_assets={};dupes=[]
for p in assets.rglob('*.meta'):
 text=p.read_text(encoding='utf-8-sig',errors='replace');m=guid_re.search(text)
 if not m:continue
 g=m.group(1);target=Path(str(p)[:-5]);
 if g in guid_assets:dupes.append({'guid':g,'paths':[str(guid_assets[g].relative_to(u)),str(target.relative_to(u))]})
 guid_assets[g]=target
guid_all=dict(guid_assets)
scene=u/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Isolation.unity';visited=set();pending=[scene];missing={};text_exts={'.unity','.prefab','.mat','.asset','.controller','.overridecontroller','.playable','.shadervariants','.lighting','.rendertexture','.meta','.asmdef','.json'}
def consume():
 while pending:
  p=pending.pop()
  if p in visited or not p.is_file():continue
  visited.add(p)
  if p.suffix.lower() not in text_exts:continue
  for g in ref_re.findall(p.read_text(encoding='utf-8-sig',errors='replace')):
   if g.startswith('0000000000000000'):continue
   if g not in guid_all:missing.setdefault(g,[]).append(p.relative_to(u).as_posix())
   else:pending.append(guid_all[g])
consume()
# Read only package metadata that is actually referenced, instead of walking every package file.
for _ in range(10):
 if not missing:break
 args=['rg','-l','-F','--glob','*.meta']
 for g in missing:args.extend(['-e',g])
 args += [str(p) for p in [u/'Packages',u/'Library/PackageCache'] if p.is_dir()]
 found=subprocess.run(args,capture_output=True,text=True,encoding='utf8');matched=0
 for name in found.stdout.splitlines():
  p=Path(name);m=guid_re.search(p.read_text(encoding='utf-8-sig',errors='replace'))
  if m and m.group(1) in missing:
   g=m.group(1);target=Path(str(p)[:-5]);guid_all[g]=target;del missing[g];pending.append(target);matched+=1
 if not matched:break
 consume()
manifest=json.loads((assets/'Afrer_Seconds/06.Data/AssetSources/SubjectHabitat_LivingModels.json').read_text(encoding='utf8'))
facts=json.loads((w/'living_import_facts.json').read_text(encoding='utf8'));living=[]
for a in manifest:
 p=u/a['fbx'];f=next(x for x in facts if x['name']==a['name']);b=a['unitySizeXYZ'];delta=max(abs(float(f['bounds'][i])-float(b[i])) for i in range(3));prefab=u/f['prefab'];prefab_guid=guid_re.search(Path(str(prefab)+'.meta').read_text()).group(1)
 instance_count=len(re.findall(r'm_SourcePrefab: \{fileID: \d+, guid: '+prefab_guid,scene.read_text(encoding='utf8')))
 living.append({'name':a['name'],'fbxShaMatchesManifest':sha(p)==a['sha256'],'correctedPrefabBoundsMatch':delta<.0001,'maximumBoundsError':delta,'prefabUsedBySavedScene':prefab in visited,'prefabInstancesInSavedScene':instance_count,'prefabDirectSceneGuidReferences':scene.read_text(encoding='utf8').count(prefab_guid),'trianglesMatch':f['triangles']==a['triangles']})
# Locate the original pod prefab instance's root Transform overrides without opening Unity.
pod_prefab=u/'Assets/Afrer_Seconds/04.Prefabs/Environment/ObservationPod.prefab';pod_guid=guid_re.search(Path(str(pod_prefab)+'.meta').read_text()).group(1)
text=pod_prefab.read_text(encoding='utf8');blocks=re.split(r'(?m)^--- !u!',text);go_block=next(b for b in blocks if b.startswith('1 ') and re.search(r'^  m_Name: ObservationPod\s*$',b,re.M));root_transform=re.search(r'component: \{fileID: (\d+)\}',go_block).group(1)
scene_blocks=re.split(r'(?m)^--- !u!',scene.read_text(encoding='utf8'));pod_blocks=[b for b in scene_blocks if b.startswith('1001 ') and re.search(r'm_SourcePrefab: \{fileID: \d+, guid: '+pod_guid,b)]
pose={}
for b in pod_blocks:
 for target,prop,value in re.findall(r'- target: \{fileID: (\d+), guid: [^\n]+\}\s+propertyPath: ([^\n]+)\s+value: ([^\n]*)',b):
  if target==root_transform and prop.startswith(('m_LocalPosition.','m_LocalScale.')):pose[prop]=float(value)
expected={'m_LocalPosition.x':0,'m_LocalPosition.y':0,'m_LocalPosition.z':10.32,'m_LocalScale.x':3,'m_LocalScale.y':2,'m_LocalScale.z':3}
pose_match=all(k in pose and abs(pose[k]-v)<.0001 for k,v in expected.items())
guard_blocks=[b for b in scene_blocks if b.startswith('1001 ') and 'value: Guard_A_' in b];guard_pose={}
for b in guard_blocks:
 source_guid=re.search(r'm_SourcePrefab: \{fileID: \d+, guid: ([a-f0-9]{32})',b).group(1);source=guid_assets[source_guid]
 source_blocks=re.split(r'(?m)^--- !u!',source.read_text(encoding='utf8'));root_block=next(x for x in source_blocks if x.startswith('4 ') and re.search(r'm_Father: \{fileID: 0\}',x));transform_id=re.match(r'4 &(\d+)',root_block).group(1)
 for target,prop,value in re.findall(r'- target: \{fileID: (\d+), guid: [^\n]+\}\s+propertyPath: ([^\n]+)\s+value: ([^\n]*)',b):
  if target==transform_id and prop.startswith('m_LocalPosition.'):guard_pose[prop]=float(value)
guard_radial=((guard_pose.get('m_LocalPosition.x',0))**2+(guard_pose.get('m_LocalPosition.z',0)-10.32)**2)**.5
guard_outside=bool(guard_pose) and guard_radial>4.215+.28
hm_mats=[p.relative_to(u).as_posix() for p in (model/'Props/B5/Materials').glob('HM_*.mat')]
record={'baselineFiles':len(base),'changedExistingFiles':changed,'removedExistingFiles':removed,'protectedFiles':len(protected),'unexpectedProtectedChanges':bad,'newSourceAssets':source_new,'unexpectedNewSourceAssets':source_unexpected,'modelFolderViolations':folder_violations,'duplicateAssetGuids':dupes,'missingReachableGuids':missing,'livingModels':living,'savedPodRootOverrides':pose,'savedUserScaleAndPositionMatch':pose_match,'savedGuardRootOverrides':guard_pose,'guardRootRadialDistanceFromPodCenter':guard_radial,'guardOutsidePod':guard_outside,'hmSharedMaterialCount':len(hm_mats),'hmSharedMaterialPaths':hm_mats,'newAssetFiles':len(asset_new),'temporaryEditorFolderExists':(assets/'Editor').exists()}
hatch=json.loads((assets/'Afrer_Seconds/06.Data/AssetSources/SubjectHabitat_DualFoodHatch.json').read_text(encoding='utf8'))
hatch_sha={k:sha(u/path)==hatch['sha256'][k] for k,path in hatch['exports'].items()}
hardware=json.loads((w/'Hatch/four_face_material_verification.json').read_text(encoding='utf8'))
record['allowedDocumentationUpdates']=[n for n in changed if n=='Unity/README.md']
record['hatchFbxShaMatchesManifest']=hatch_sha
record['hatchFourFaceMaterialAudit']=hardware.get('accepted',False)
record['pass']=not any([bad,removed,source_unexpected,folder_violations,dupes,missing]) and all(all(x[k] for k in ['fbxShaMatchesManifest','correctedPrefabBoundsMatch','prefabUsedBySavedScene','trianglesMatch']) and x['prefabInstancesInSavedScene']==1 for x in living) and pose_match and guard_outside and len(hm_mats)==8 and all(hatch_sha.values()) and record['hatchFourFaceMaterialAudit']
(w/'independent_audit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:record[k] for k in ['baselineFiles','protectedFiles','unexpectedProtectedChanges','removedExistingFiles','newSourceAssets','unexpectedNewSourceAssets','modelFolderViolations','duplicateAssetGuids','missingReachableGuids','livingModels','savedPodRootOverrides','savedUserScaleAndPositionMatch','hmSharedMaterialCount','pass']},ensure_ascii=False,indent=2))
# [주석] 미저장 씬의 값은 이 검사 범위에 없다. 저장 완료 후 재실행해 최종 판정한다.
