"""피드백 보수의 실제 결과와 비교 자료. 작성자: 송예찬."""
from pathlib import Path
import json,hashlib,re,shutil
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-07_C01_PropRepair';P=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5'
read=lambda p:json.loads(p.read_text('utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=read(H/'baseline.json');backup=Path(base['backup']);asset=read(O/'final_assets.json');state=read(O/'state.json');play=read(O/'play_inside.json');rows=[read(p) for p in H.glob('*.json') if p.name.startswith(('CP_','ID_'))];bottles=[r for r in rows if r['bottles']]
assert len(bottles)==9 and sum(len(r['bottles']) for r in bottles)==46
assert all(r['oldCubeBottleLabels']==0 for r in rows)
protected={p:sha(R/p)==h for p,h in base['protected'].items()};guids={}
for p in P.glob('*.fbx.meta'):
 if not p.name.startswith(('CP_','ID_')):continue
 get=lambda x:re.search(r'^guid: (\S+)',x.read_text('utf-8'),re.M).group(1)
 guids[p.name]=get(p)==get(backup/p.relative_to(R))
scene=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity';same=sha(scene)==base['sceneHash']
assert all(protected.values()) and all(guids.values()) and same and state['accepted30StationTransformsPreserved'] and not state['sceneDirty'] and not state['playing']
assert asset['badTriangles']==0 and not asset['missingMaterials'] and not play['errors'] and play['displacement']>.4
triangles=sum(m['trianglesIncludingLODs'] for m in asset['models']);gap=read(H/'CP_OpticalAnalyzer.json')['monitorCartridgeClearanceM']
preservation={'protectedFiles':protected,'modelGUIDs':guids,'sceneByteIdentical':same,'bottleModels':len(bottles),'uniqueSourceBottles':46,'oldCubeBottleLabels':0,'monitorCartridgeClearanceM':gap,'preparationPouchesInsideTray':read(H/'CP_PreparationKit.json')['pouchesInsideTray'],'trianglesIncludingLODs':triangles}
(O/'preservation.json').write_text(json.dumps(preservation,indent=2),encoding='utf-8')
# Same camera pairs, without image retouching.
sheet=Image.new('RGB',(1600,1638),(20,28,33));d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
for row,(key,title) in enumerate([('Analyzer_Clearance','분석기 화면 / 카트리지 간섭'),('Preparation_Tray','준비 키트 / 트레이 내부 정리'),('Vial_Detail','병 / 곡면 밀착 라벨')]):
 for col,(prefix,label) in enumerate([('Before','수정 전'),('After','수정 후')]):
  y=row*546;im=Image.open(O/(prefix+'_'+key+'.png')).convert('RGB').resize((800,500),Image.Resampling.LANCZOS);sheet.paste(im,(col*800,y));d.text((col*800+14,y+508),label+' · '+title,font=font,fill=(227,238,237))
sheet.save(O/'BeforeAfter.jpg',quality=94)
for p in P.rglob('PR_*'):
 if p.is_file() and p.suffix!='.meta':assert Path(str(p)+'.meta').exists(),p
prov={'author':'송예찬','date':'2026-11-07','scope':'C01 feedback: analyzer overlap, preparation tray, conformal bottle labels and contact cleanup','source':'SourceAssets/C01_PropRepair','bottleModels':9,'sourceBottleCount':46,'newTextures':4,'newMaterials':7,'monitorGapM':gap,'savedSceneByteIdentical':same,'modelsValidated':37,'modelGUIDsPreserved':37,'runtimeCodeChanged':False,'externalGeneration':False,'committedOrPushed':False,'files':{str(p.relative_to(R)).replace('\\','/'):sha(p) for p in P.rglob('*') if p.is_file() and p.name.startswith('PR_') and p.suffix!='.meta'}}
(R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/C01_PropRepair_20261107.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2),encoding='utf-8')
table='\n'.join('| '+r['asset']+' | '+str(len(r['bottles']))+' |' for r in bottles)
report=f'''# C01 겹침·병 라벨·얇은 소품 보수 V0.01

작성자 송예찬 · 2026-11-07

사용자가 지적한 분석기 화면/소켓 겹침, 준비 키트 카드 돌출, 병의 상자형 라벨을 수정했다. 승인된 방 구성·30작업대 Transform·Collider는 유지하며 기존 FBX를 갱신했다. [전후 비교](BeforeAfter.jpg)는 동일 카메라로 촬영했다.

![수정 전후](BeforeAfter.jpg)

## 고친 부분

- **CP_OpticalAnalyzer**: 화면 중심을7cm 올려 카트리지 상단과 화면 모듈 하단 사이 **{gap*1000:.1f}mm** 여유를 확보했다. 카트리지 도크가 본체 상판에 닿게 만들고 표면 라벨 돌출도 줄였다.
- **CP_PreparationKit**: 트레이 네 변과 바닥을 다시 만들고 포장물3개를 내부에 배치했다. 포장 두께를12mm에서1.8mm로 줄였으며 라벨은0.2mm 정도만 띄웠다. 태블릿/포장 인쇄의 UV 방향도 고쳤다.
- **병 공통**: 큐브 라벨을 없애고 병 곡률을 따르는16면 인쇄 표면으로 교체했다. 표면과의 간격은0.18mm다. 뚜껑24개 파지 홈·병목·밀봉 링·시료 바코드/눈금·유리 내부 시료를 반영했다. 큰 시약병은 불투명 폴리머, 작은 시료병은 유리/시료를 구분한다.
- **추가 점검**: 믹서의 병을 고무 컵 바닥 가까이 내렸다. 피펫 표시도 곡면에 밀착했다. 실러 포장은1.8mm, 프린터 출력지는0.45mm로 만들고 출력 슬롯에서 이어지는 굽은 종이로 바꿨다. 상자 밴드는 얇은 인쇄 표면으로 바꿨다.
- **받침 접점**: 크로마토그래피·유세포 분석기·시약 선반·혼합 선반·응급 캐비닛의 병과 일부 상자가 떠 있던 높이를 보정했다. 병을 내린 기구의 호스 끝점도 함께 맞췄다. 시료장 내부 상자 받침도 보정했다.

공통 병 수정은 다음9종의 원본46개에 적용된다. 씬에서 반복 배치된 수를 뜻하지 않는다.

| 원본 | 병 수 |
| --- | ---: |
{table}

## 검증

- 최종 재반입 경고/오류0. 모델37종 퇴화 삼각형0(면적5e-9㎡ 기준), 누락 재질/셰이더0. 고유 모델 삼각형 {triangles:,}개(바이탈 LOD 합산).
- 원본 검사에서 상자형 병 라벨0, 준비 키트 포장물3개 모두 트레이 내부, 분석기 수직 이격{gap*1000:.1f}mm.
- 승인된30작업대 Transform,37개 모델 GUID,23개 보호파일 해시 유지. 저장 씬은 이번 단계 전후 바이트 단위 동일.
- 바닥 충돌체29개의35mm 초과 관통0, C01 순환540 capsule 표본 막힘0. 전체 복도4854 검사는 직전 단계 결과이며 이번에는 구조·Collider를 변경하지 않았다.
- 새 병/라벨 반입 후1920×1080 Play5초: {play['framesAdvanced']}프레임, W입력 {play['displacement']:.3f}m 이동, 새 경고/오류0. median {play['medianMs']:.2f}ms / p95 {play['p95Ms']:.2f}ms. 이 Play 이후 선반 받침 높이를 미세 보정했으며 최종 메시 반입/시각 검사를 다시 수행했다. 전체 빌드 성능 검사로 해석하지 않는다.
- 편집 모드, scene dirty=false, 플레이어(-9.2,-81.36,-10)/회전0, 백그라운드 override=false 복원.
- 최종 근접13장과 작업 전11장 보관. 전체 프랍의 모든 면 교차가 없다는 보증은 아니며 이번에 지적된 겹침·라벨·소품 접점을 집중 검사했다.

## 직접 확인

- [분석기](After_OpticalAnalyzer.png), [화면 간격](After_Analyzer_Clearance.png)
- [준비 키트](After_PreparationKit.png), [트레이](After_Preparation_Tray.png)
- [믹서](After_ID_DualVortexMixer.png), [병 확대](After_Vial_Detail.png)
- [피펫](After_ID_PipetteWorkstation.png), [크로마토그래피](After_ID_ChromatographyStack.png), [선반](After_ID_MixedSupplyShelf.png), [응급 캐비닛](After_EmergencyCabinet.png)
- [실러](After_ID_SterileSealer.png), [프린터](After_ID_LabelPrinter.png)
- [모델 검사](final_assets.json), [보존/간격](preservation.json), [Play 결과](play_inside.json), [최종 편집 상태](state.json)

로컬 반영 완료. 커밋/push·외부 생성·업로드는 하지 않았다. 장비는 정적 아트이며 게임 C# 추가0. 제작 원본과 재현 순서는 [README](../../../SourceAssets/C01_PropRepair/README.md)를 따른다.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
(H/'README.md').write_text('''# C01 겹침·병 라벨·소품 접점 보수 V0.01

작성자 송예찬 · 2026-11-07

사용자 피드백의 실제 수정 범위와13장 근접 검수는 [검수 기록](../../Docs/검수/2026-11-07_C01_PropRepair/검수결과.md)을 따른다. C01_Perimeter/C01_InstrumentDetail/C01_PropFinish/이 폴더를 함께 보존한다.

`refine_components.py`는 기존 finish_geometry.py 마지막 단계에서 실행된다. 원통 제작 가이드와 큐브 라벨을 최종 병·밀착 라벨·얇은 인쇄물로 교체한다. 원본46병/9종, 분석기 화면 간격과 포장물 내부 배치 근거는 개별 모델 JSON에 남는다. 라벨은32각 병의 각도 샘플과 맞춘16면 반원 표면이며0.18mm만 띄운다. 큰 병은 폴리머, 작은 병은 유리+시료로 구분한다. 인쇄물 UV는 기존 투영 UV로 덮어쓰지 않는다.

재현 순서: `build_labels.py`(Pillow) → Blender의 `C01_Perimeter/build_assets.py` → `C01_InstrumentDetail/build_instruments.py` → `PropRepairImport.Run`. 기반 PBR까지 새로 반입할 때는 `PropFinishImport.Run` 뒤 `PropRepairImport.Run`을 실행한다. 기하만 바꾸면 기존 `InstrumentDetailApply.ImportGeometry`를 사용한다. **현재 씬에 배치 Apply를 다시 실행하지 않는다.** 기존 meta/GUID를 보존한다.

`prepare.py`는 최초 백업 전용이다. 현재 상태에서 기준을 다시 만들지 않는다. `Capture.cs`는 저장된 B5 편집 씬에서 전후 동일 카메라13개를 사용한다. 검수 도구는 Assets 밖의 에디터용 C#이며 게임 코드가 아니다. `FinishAudit.RestoreAfterOwnPlay`는 해당 검수기가 방금 실행한 Play만 복원할 때 사용한다. 사용자 미저장 편집 중에는 호출하지 않는다.

`finalize_records.py`는 최종 검사 JSON과 실제 파일을 대조해 보고서/보존 검사/provenance와 전후 비교 이미지를 기록한다. 이전 단계의 finalize 스크립트를 현재 기록 생성용으로 다시 실행하지 않는다. 임시 백업은 baseline.json의 로컬 경로이며 Git 전달 원본은 생성기·blend·FBX·텍스처·재질이다.

씬/30작업대/Collider/기존 리브/다른 씬/게임 코드 보존. 로컬 수정이며 커밋/push 미실시.
''',encoding='utf-8')
summary='2026-11-07 최신 피드백 보수: CP_OpticalAnalyzer 화면/카트리지 겹침을36.9mm 간격으로 수정하고 CP_PreparationKit 포장물3개를 트레이 안으로 정리했다. 9종 원본46병의 큐브 라벨을0.18mm 곡면 밀착 인쇄로 교체하고 병목·뚜껑 홈·밀봉·시료를 보강했다. 피펫/실러/출력지와 선반·병의 뜬 접점도 보수했다. [최신 검수](검수/2026-11-07_C01_PropRepair/검수결과.md), [제작 도구](../SourceAssets/C01_PropRepair/README.md)를 우선한다. 모델37종 누락/퇴화0,30작업대/37GUID/23보호파일/저장 씬 유지. 로컬 저장, 커밋/push 미실시. 다음은 사용자 시야 확인 후 C01 출입구·문 포켓·벽/광원·바닥 안내선 → T01/C02이며 전체 아트0/34 유지.'
for rel,v1,v2 in [('AGENTS.md','V0.41','V0.42'),('CLAUDE.md','V0.41','V0.42'),('Docs/이어하기_2026-11-06.md','V0.25','V0.26'),('Docs/회사_작업목록_2026-11-06.md','V0.23','V0.24')]:
 p=R/rel;txt=p.read_text('utf-8');dst=backup/'docs_before_repair'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(p,dst)
 if '2026-11-07_C01_PropRepair' not in txt[:1400]:
  head,body=txt.split('\n',1);s=summary if rel.startswith('Docs/') else summary.replace('(검수/','(Docs/검수/').replace('(../SourceAssets/','(SourceAssets/');p.write_text(head.replace(v1,v2)+'\n\n'+s+'\n\n이전 단계 기록:\n'+body.lstrip(),encoding='utf-8')
for folder,v1,v2 in [('C01_Perimeter','V0.03','V0.04'),('C01_InstrumentDetail','V0.02','V0.03'),('C01_PropFinish','V0.01','V0.02')]:
 p=H.parent/folder/'README.md';txt=p.read_text('utf-8')
 if 'C01_PropRepair' not in txt[:700]:
  head,body=txt.split('\n',1);p.write_text(head.replace(v1,v2)+'\n\n최신 병·라벨·간섭 보수는 [C01_PropRepair](../C01_PropRepair/README.md)를 따른다. 현재 제작기는 refine_components.py도 참조하며 새 PR_ 재질은 ImportRepair를 마지막에 반입한다.\n'+body,encoding='utf-8')
print(json.dumps({'bottleModels':9,'bottles':46,'triangles':triangles,'protected':len(protected),'guids':len(guids),'sceneSame':same,'records':'written'}))
