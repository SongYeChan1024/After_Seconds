from pathlib import Path,PurePosixPath
import json,re,collections,shutil,hashlib
R=Path(__file__).parent;P=R.parent.parent;U=P/'Unity/After_Seconds_Build_V0.01';ROOT='Assets/Afrer_Seconds/05.Model';DATA='Assets/Afrer_Seconds/06.Data/AssetSources';d=json.loads((R/'asset_inventory.json').read_text(encoding='utf-8-sig'));assets=d['assets']
def category(path):
 if '/AS01_Crate/' in path:return 'Props'
 if '/AS05_PlayerDummy/' in path:return 'Player'
 if '/AS06_GuardDummy/' in path:return 'Enemy'
 if path.startswith(ROOT+'/'):return path[len(ROOT)+1:].split('/')[0]
 return 'Common'
def family(path):
 for marker in ['/Batch02/','/VARCO/','/VARCO_V002/','/Architecture_Rebuilt/']:
  if marker in path:
   tail=path.split(marker,1)[1].split('/')
   if tail[0] not in ['Materials','Textures','Models','Prefabs'] and len(tail)>1:return marker+tail[0]
 return str(PurePosixPath(path).parent)
family_floors=collections.defaultdict(set)
for a in assets:family_floors[(category(a['path']),family(a['path']))].update(a['floors'])
def floor(a):
 p=a['path'];cat=category(p)
 if cat in ['Player','Enemy']:return None
 if 'Crate' in p or 'P05_SampleCanister' in p or 'P13_LogisticsTote' in p:return 'Common'
 if '/Shared/' in p and PurePosixPath(p).suffix in ['.mat','.png','.json']:return 'Common'
 if len(a['floors'])>1:return 'Common'
 if len(a['floors'])==1:return a['floors'][0]
 fs=family_floors[(cat,family(p))]
 if len(fs)>1:return 'Common'
 if len(fs)==1:return next(iter(fs))
 m=re.search(r'/(B[1-5]|1F)(?:[_/])',p)
 return m.group(1) if m else 'Common'
def owner(path):
 parts=path.split('/');skip={'Models','Textures','Materials','Prefabs','Repaired','Meshes','Labels','Modules','Shaders'}
 i=len(parts)-2
 while i>=0 and parts[i] in skip:i-=1
 return re.sub(r'[^A-Za-z0-9_-]','_',parts[i])
plan=[];used={}
for a in sorted(assets,key=lambda a:a['path']):
 src=a['path'];ext=PurePosixPath(src).suffix.lower();cat=category(src);fl=floor(a);name=PurePosixPath(src).name;stem=PurePosixPath(src).stem;own=owner(src)
 if ext in ['.json','.md']:
  token='_'.join(src.split('/')[3:-1]);token=re.sub(r'[^A-Za-z0-9_-]','_',token)
  dst=DATA+'/'+token+'_'+name
 else:
  folder=ROOT+'/'+cat+('/'+fl if fl else '')
  if ext=='.mat':folder+='/Materials'
  if ext in ['.png','.jpg','.jpeg','.tga','.exr','.psd','.tif','.tiff']:folder+='/Textures'
  generic=ext in ['.png','.mat'] and not (stem.startswith(own+'_') or re.match(r'^(B[1-5]|1F|AS0[156])_',stem) or stem.startswith('FacilityWall_'))
  if generic:
   if stem=='material_0_URP':name=own+'_URP'+ext
   else:name=own+'_'+name
  dst=folder+'/'+name
 key=dst.lower()
 if key in used:
  dst=str(PurePosixPath(dst).with_name(own+'_'+PurePosixPath(dst).name));key=dst.lower()
 if key in used:
  dst=str(PurePosixPath(dst).with_name(PurePosixPath(dst).stem+'_'+a['guid'][:8]+ext));key=dst.lower()
 assert key not in used,(src,dst)
 used[key]=src;plan.append({**a,'category':cat,'floor':fl,'destination':dst,'move':src!=dst})
for a in plan:
 if a['move'] and (U/a['destination']).exists():raise RuntimeError('Existing destination '+a['destination'])
backup=R/'AssetBackup'
for a in plan:
 src=U/a['path'];dst=backup/a['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 if src.with_name(src.name+'.meta').exists():shutil.copy2(str(src)+'.meta',str(dst)+'.meta')
 a['beforeSha256']=hashlib.sha256(src.read_bytes()).hexdigest()
(R/'move_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'assets':len(plan),'moves':sum(a['move'] for a in plan),'destinations':dict(collections.Counter((a['category']+'/'+str(a['floor'])) for a in plan if not a['destination'].startswith(DATA)))},indent=2))
