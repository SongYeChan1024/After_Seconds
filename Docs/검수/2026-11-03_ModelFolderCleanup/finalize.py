from pathlib import Path,PurePosixPath
import json,re,collections,shutil,os,hashlib
R=Path(__file__).parent;P=R.parent.parent;U=P/'Unity/After_Seconds_Build_V0.01';D=P/'Docs/검수/2026-11-03_ModelFolderCleanup';D.mkdir(parents=True,exist_ok=True);plan=json.loads((R/'move_plan.json').read_text());moves=[a for a in plan if a['move']];mapping={a['path']:a['destination'] for a in moves}
def rewrite(s):
 for old,new in sorted(mapping.items(),key=lambda x:-len(x[0])):s=s.replace(old,new).replace(old.replace('/','\\'),new.replace('/','\\'))
 return s
metadata=[]
for a in plan:
 f=U/a['destination']
 if f.suffix in ['.json','.md']:
  raw=f.read_text(encoding='utf-8-sig');new=rewrite(raw)
  if f.suffix=='.json':
   obj=json.loads(new)
   if isinstance(obj,dict):obj['folderCleanup20261103']={'previousPath':a['path'],'currentPath':a['destination'],'mapping':'Docs/検修/2026-11-03_ModelFolderCleanup/move_plan.json'.replace('検修','검수')}
   new=json.dumps(obj,ensure_ascii=False,indent=2)
  f.write_text(new,encoding='utf-8');metadata.append(a['destination'])
(R/'metadata_updates.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
# Exact current file paths, plus old folder aliases where the resulting location is unambiguous.
aliases=dict(mapping)
for a in moves:
 for old,new in [(a['path'],a['destination']),(a['path'].removeprefix('Assets/Afrer_Seconds/'),a['destination'].removeprefix('Assets/Afrer_Seconds/'))]:aliases[old]=new
folders=collections.defaultdict(list)
for a in plan:
 if '/05.Model/' not in a['path']:continue
 parent=PurePosixPath(a['path']).parent
 while str(parent).startswith('Assets/Afrer_Seconds/05.Model/'):
  folders[str(parent)].append(str(PurePosixPath(a['destination']).parent));parent=parent.parent
for old,paths in folders.items():
 if old.startswith('Assets/Afrer_Seconds/05.Model/Player/Rigged') or '/Materials' in old or '/Textures' in old or '/Models' in old or '/Meshes' in old or '/Labels' in old:continue
 modelpaths=[x for x in paths if '/05.Model/' in x]
 if modelpaths:
  new=os.path.commonpath(modelpaths).replace('\\','/')
  if old!=new:aliases[old]=new;aliases[old.removeprefix('Assets/Afrer_Seconds/')]=new.removeprefix('Assets/Afrer_Seconds/')
def docpaths(s):
 for old,new in sorted(aliases.items(),key=lambda x:-len(x[0])):s=s.replace(old,new)
 return s
tree='''  05.Model/
    Player/                         # 기준 모델·모델 단계 프리팹
      Materials/
      Textures/
    Enemy/
      Materials/
      Textures/
    Props/
      Common/                       # 상자·시료 용기·공용 설비
      B5/                           # 각 폴더에 모델·프리팹을 바로 보관
      B4/
      B3/
      B2/
      B1/
      1F/
    Environment/
      Common/                       # 여러 층에서 쓰는 배관·덕트·공용 재질
      B5/
      B4/
      B3/
      B2/
      B1/
      1F/
    # Props·Environment의 층/Common 폴더에도 Materials·Textures만 하위 분리
'''
for f,old,new in [(P/'Unity/README.md','V0.20','V0.21'),(P/'Docs/이어하기_2026-10-26.md','V0.15','V0.16')]:
 s=f.read_text(encoding='utf-8-sig');s=docpaths(s).replace(old,new,1)
 if f.name=='README.md':
  start=s.index('  05.Model/\n');end=s.index('  06.Data/\n',start);s=s[:start]+tree+s[end:];s=s.replace('  06.Data/\n','  06.Data/\n    AssetSources/                   # 제작 출처·반입·검수 JSON/안내\n',1)
  start=s.find('    Candidates/VARCO/\n')
  if start>=0:
   end=s.index('  04.Prefabs/',start);s=s[:start]+'''    Environment/                    # 2D 표지·아틀라스 등
'''+s[end:]
  s=s.replace('Player·Enemy·Props·Environment로 분류하며 플레이어 기준 모델과 반입 기록은 Player/Rigged에 보관함','Player·Enemy는 직접 분류, Props·Environment는 층별/Common으로 분류. 하위는 Materials·Textures만 사용하고 제작 기록은 06.Data/AssetSources에 보관함')
 i=s.index('\n');s=s[:i]+'''

## 2026-11-03 모델 폴더 단순화 완료

사용자 요청에 따라 `05.Model`은 Player·Enemy·Props·Environment 네 분류로 정리했다. Props와 Environment는 B5/B4/B3/B2/B1/1F/Common으로 나누고, 각 분류/층 폴더에 모델·프리팹·메시를 바로 보관한다. 하위 폴더는 Materials와 Textures만 사용한다. 여러 층에서 쓰는 에셋은 Common 한 곳을 참조하며 복제하지 않는다. 기존 VARCO·Batch02·Models·Prefabs·Meshes·Repaired 중간 폴더는 제거했다.

상자·시료 용기·물류 용기는 `Props/Common`, 플레이어 모델은 `Player`, 경비 모델은 `Enemy`에 있다. 기존 03.Art/Candidates의 3D 모델 3종도 해당 분류로 이동했다. 제작 출처·반입 기록은 `06.Data/AssetSources`에 모았고 동작 FBX·Animator 자료는 기존 `07.Animator`에 유지했다. 414개 파일을 AssetDatabase로 이동해 대상 443개 GUID, 6개 층 의존 참조, 53개 FBX 내부 ID와 40개 프리팹 참조를 확인했다. 이동 전후 경로표와 검수는 `Docs/검수/2026-11-03_ModelFolderCleanup/정리결과.md`를 따른다. 과거 검수 스크립트의 반입 경로를 그대로 재실행하면 옛 폴더가 생길 수 있으므로 새 경로표를 적용한다.
'''+s[i:];f.write_text(s,encoding='utf-8')
f=P/'CLAUDE.md';s=f.read_text(encoding='utf-8-sig').replace('V0.04','V0.05',1);anchor='  - `04.Prefabs`에는';idx=s.index(anchor);s=s[:idx]+'''  - **모델 폴더는 단순하게 유지한다.** `05.Model/{Player,Enemy,Props,Environment}` 네 분류를 사용한다. Props·Environment는 `{B5,B4,B3,B2,B1,1F,Common}`으로 나눈다. 모델·프리팹·메시·필요한 셰이더는 해당 분류/층 폴더에 바로 두고, 하위 폴더는 `Materials/`, `Textures/`만 사용한다. VARCO·Batch·에셋명별·Models·Prefabs·Meshes·Repaired 중간 폴더를 다시 만들지 않는다. 여러 층 공용 에셋은 Common 한 곳에 보관한다. 출처·반입 JSON과 안내는 `06.Data/AssetSources/`에 저장한다.
'''+s[idx:];s=s.replace('`03.Art/Candidates/VARCO`의 과거 파일은 신규 분류 규칙과 구분하며 별도 정리 요청 없이 일괄 이동하지 않습니다.','기존 `03.Art/Candidates/VARCO`의 3D 모델 3종은 2026-11-03 사용자 폴더 정리 요청으로 새 모델 분류에 이동했습니다.');f.write_text(s,encoding='utf-8')
f=P/'AGENTS.md';s=f.read_text(encoding='utf-8-sig').replace('V0.04','V0.05',1);s+='''
모델 폴더는 `05.Model/{Player,Enemy,Props,Environment}` 네 분류를 사용합니다. Props·Environment만 층별 `B5/B4/B3/B2/B1/1F/Common`으로 나누며, 각 분류/층 폴더에는 모델·프리팹·메시를 바로 둡니다. 하위 폴더는 Materials·Textures만 사용하고, 제작/반입 기록은 06.Data/AssetSources에 둡니다. 공용 파일은 복제하지 않습니다. 동작/Animator 리소스는 기존 07.Animator 규칙을 유지합니다.
''';f.write_text(s,encoding='utf-8')
for f in R.iterdir():
 if f.suffix in ['.json','.cs','.py']:shutil.copy2(f,D/f.name)
shutil.copytree(R/'AssetBackup',D/'AssetMetadataBackup',dirs_exist_ok=True,ignore=lambda path,names:[n for n in names if Path(path,n).is_file() and Path(n).suffix not in ['.json','.md','.meta']])
(D/'정리결과.md').write_text('''# 모델 폴더 단순화 검수 V0.01

2026-11-03 · 작성자 송예찬

05.Model 아래를 Player·Enemy·Props·Environment 네 분류로 정리했다. Props·Environment는 층별과 Common으로 나누고, 모델/프리팹/메시 파일을 그 위치에 바로 두었다. 하위 폴더는 Materials·Textures만 남겼다. 다층 사용은 6개 Stage 씬의 AssetDatabase 의존 관계로 판별하고, 상자·시료 용기·물류 용기도 공용 분류로 배치했다. 사용되지 않는 원본·복구 FBX도 같은 계열 파일의 층 분류에 따라 보존했다.

414개 파일 이동, 대상 443개 GUID 유지. 6개 층의 GUID 의존 관계 동일, 53개 FBX의 서브에셋 파일 ID 유지, 프리팹 40개에서 missing script/mesh/material 0개를 확인했다. 머티리얼은 새로 만들거나 복제하지 않았다. 03.Art/Candidates/VARCO에 있던 상자·플레이어·경비의 모델/텍스처/재질도 각각 Props/Common·Player·Enemy로 옮겼다. 게임 코드·씬 내용·Animator·ProjectSettings는 이 정리에서 편집하지 않았다. 열려 있는 씬의 사용자 편집을 저장하거나 되돌리지 않았다.

제작 출처·반입 JSON/안내는 06.Data/AssetSources에 모으고 그 안의 에셋 경로 문자열도 갱신했다. Unity README·이어하기·프로젝트 작업 규칙을 새 구조로 갱신했다. move_plan.json이 전체 이전/현재 경로와 GUID 대응표다. 과거 Docs/검수의 원시 기록·재현 스크립트는 당시 증거를 보존하기 위해 일괄 수정하지 않았다. 해당 스크립트를 재실행할 때는 새 경로표를 적용해야 한다.

## 던질 소품 후속 후보

현재 외형 에셋으로는 AS01_Crate 상자, P05_SampleCanister 시료 용기, P13_LogisticsTote 물류 용기가 있다. 시료 용기는 작은 투척 소품의 우선 후보, 물류 용기는 크기와 취급 방식을 검토할 후보다. 총 모델은 이번 모델 목록에서 확인되지 않았다. 추가 제작 후보는 빈 금속통·작은 비파손 시료병·손전등·소형 공구 케이스이며, 실제 투척 기능/무게 규칙은 아직 연결하지 않았다. 폭발물이나 산산이 깨지는 유리병을 전제로 새 게임 규칙을 추가하지 않았다.
''',encoding='utf-8')
M=P.parent/'Management/ModelFolderCleanup-20261103';M.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'move_plan.json',M/'AfterSeconds_asset_moves.json');shutil.copy2(R/'move_verification.json',M/'AfterSeconds_asset_validation.json');(M/'README.md').write_text('''# After Seconds 모델 폴더 이동 검증 V0.01

2026-11-03 · 작성자 송예찬

대상 프로젝트: 04.After_Seconds/Unity/After_Seconds_Build_V0.01. 프로젝트 루트 이동 없이 모델 하위 폴더만 단순화했다. 414개 파일 이동, 대상 443개 GUID와 6개 Stage 씬 의존 관계, 53개 FBX 내부 ID, 40개 프리팹 참조를 검증했다. 상세 기록은 프로젝트 Docs/검수/2026-11-03_ModelFolderCleanup/정리결과.md와 이 폴더의 경로표를 따른다.
''',encoding='utf-8')
print(json.dumps({'metadataUpdated':len(metadata),'docsUpdated':4,'managementRecord':str(M)},ensure_ascii=False))
