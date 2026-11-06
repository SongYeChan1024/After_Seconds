from pathlib import Path
import json,hashlib,re
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-06_CircularDressing'
archive=json.loads((O/'scene_archive.json').read_text('utf-8'));mapping={m['from']:m['to'] for m in archive['moved']}
before=json.loads((H/'protected_before.json').read_text('utf-8'));dif=[]
allowed={'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity','ProjectSettings/EditorBuildSettings.asset'}
for old,digest in before.items():
 p=old.replace('\\','/');actual=mapping.get(p,p)
 if p.endswith('.meta'):actual=mapping.get(p[:-5],p[:-5])+'.meta'
 q=U/actual
 if not q.exists() or hashlib.sha256(q.read_bytes()).hexdigest()!=digest:
  if p not in allowed:dif.append(p)
check=json.loads((O/'validation.json').read_text('utf-8'))
assert not dif,dif
assert not check['blocked'] and not check['propOverlaps'] and not check['missingMeshes'] and not check['missingMaterials']
proof={'protectedFiles':len(before),'unexpectedChanges':dif,'authorizedChanges':sorted(allowed),'sceneMoves':len(mapping),'oldSceneCount':len(list((U/'Assets/Afrer_Seconds/01.Scenes/Stage/Old').glob('*.unity'))),'newScenes':[p.name for p in (U/'Assets/Afrer_Seconds/01.Scenes/Stage').glob('*.unity')],'runtimeCodeChanged':False}
(O/'preservation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),'utf-8')
plan=json.loads((H/'production_plan.json').read_text('utf-8'));env=json.loads((H/'environment_manifest.json').read_text('utf-8'));vr=json.loads((H/'varco_record.json').read_text('utf-8'))
source=dict(version='V0.01',author='송예찬',date='2026-11-06',scope=plan['scope'],environmentModels=list(env),props=['CFD_TransferCabinet','CFD_LinenHamper','CFD_EmergencyCabinet'],varco=vr,placementCount=check['placements'],checks=check,sceneArchive=archive,sourceFolder='SourceAssets/CircularDressing',workbook='Docs/도면/원형공동/AfterSeconds_프랍환경_제작목록.xlsx')
(U/'Assets/Afrer_Seconds/06.Data/AssetSources/CircularDressing_20261106.json').write_text(json.dumps(source,ensure_ascii=False,indent=2),'utf-8')

intro='2026-11-06 프랍·환경 목록 및 기준 구간 제작: [제작 목록 V0.03](도면/원형공동/AfterSeconds_프랍환경_제작목록.xlsx)에 기존145종을 유지하고 바닥형 보급장2종과 환경32종을 추가했다. B5 C01·T01에 환경 모델11개·프랍3개를 사용해42개를 배치했다. VARCO2종 생성·리메시와 Blender 후처리, 생성 실패1종은 Blender 직접 제작이다. [검수 기록](검수/2026-11-06_CircularDressing/검수결과.md)을 따른다. 현재 제작 씬2개는 Stage에, 구버전10개는 Stage/Old에 있다. 제작 원본은 SourceAssets/CircularDressing이다. 전체층·전체 프랍 완성은 아니며 다음은 B5 내부 생활 구획과 나머지 핵심실, 이후 B4 연결이다. 게임 C#은 추가하지 않았고 커밋/push하지 않았다.'
for f in ['Docs/이어하기_2026-11-06.md','Docs/회사_작업목록_2026-11-06.md','Docs/AfterSeconds_메인기획서.md','AGENTS.md','CLAUDE.md','Unity/README.md']:
 p=R/f;s=p.read_text('utf-8');lines=s.splitlines();lines[0]=re.sub(r'V(\d+)\.(\d+)',lambda m:f'V{m[1]}.{int(m[2])+1:02}',lines[0]);body=intro
 if f in ['AGENTS.md','CLAUDE.md']:body='2026-11-06 최신: 프랍·환경 제작 목록 V0.03과 B5 기준 구간 아트를 반영했다. 최신은 [이어하기](Docs/이어하기_2026-11-06.md), [제작 목록](Docs/도면/원형공동/AfterSeconds_프랍환경_제작목록.xlsx), [검수](Docs/검수/2026-11-06_CircularDressing/검수결과.md)다. 현재 Stage에는 Level_B5_Circular와 Level_B2_MezzaninePreview만 남기고 구버전10개는 Stage/Old에 보관한다. 에셋 GUID와 게임 C#을 보존했다. SourceAssets/CircularDressing/README.md를 읽고 재개한다. 이전 제작기는 현재 씬에 자동 재실행하지 않는다.'
 if f=='Unity/README.md':body='2026-11-06 최신: Stage의 현재 레벨은 Level_B5_Circular와 Level_B2_MezzaninePreview다. 이전9개 레벨과 Player 테스트 씬은 Stage/Old에 보관하며 GUID·내용을 보존했다. 빌드 설정의 Player 참조 경로도 Old로 갱신했고 활성 여부는 유지했다. B5 C01·T01에는 CFD_ 환경11개 모델·프랍3개 모델로42개를 배치했다. 모델은 05.Model/Environment/Common 및 Props/Common, 출처는 06.Data/AssetSources/CircularDressing_20261106.json이다. [최신 검수](../Docs/검수/2026-11-06_CircularDressing/검수결과.md)를 따른다.'
 s=lines[0]+'\n\n'+body+'\n\n'+'\n'.join(lines[1:]).lstrip()+'\n'
 if f.endswith('메인기획서.md'):s+='\n- V0.28 (2026-11-06): 프랍·환경 제작 목록 V0.03, 환경32종과 바닥형 보급장2종 추가. B5 기준 구간42배치 및 구버전 씬 Old 정리. 송예찬.\n'
 p.write_text(s,'utf-8')

p=R/'SourceAssets/CircularFacility/BuildCircular.cs';s=p.read_text('utf-8')
for old,new in [('01.Scenes/Stage/Level_B5_Stealth.unity','01.Scenes/Stage/Old/Level_B5_Stealth.unity'),('01.Scenes/Stage/Level_B2_Machinery.unity','01.Scenes/Stage/Old/Level_B2_Machinery.unity')]:s=s.replace(old,new)
p.write_text(s,'utf-8')
p=R/'SourceAssets/CircularFacility/README.md';s=p.read_text('utf-8');s=s.replace('V0.01','V0.02',1);s+='\n2026-11-06: 구버전 씬은 Stage/Old로 이동했다. BuildCircular의 원본 씬 참조만 이동 경로로 보정했다. 현재 B5 후속 CFD 아트는 SourceAssets/CircularDressing 소유이므로 BuildB5 재실행 시 손실될 수 있다.\n';p.write_text(s,'utf-8')
print(json.dumps(proof,ensure_ascii=False))
