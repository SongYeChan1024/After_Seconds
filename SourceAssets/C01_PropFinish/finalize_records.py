"""현재 파일과 검사 결과를 기반으로 제작 기록을 갱신한다. 작성자: 송예찬."""
from pathlib import Path
import hashlib,json,re,shutil
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-07_C01_PropFinish';A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds';P=A/'05.Model/Props/B5'
read=lambda p:json.loads(p.read_text('utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=read(H/'baseline.json');backup=Path(base['backup'])
protected={p:sha(R/p)==h for p,h in base['protected'].items()}
guids={}
for p in base['modelMetaBefore']:
    get=lambda path:re.search(r'^guid: (\S+)',path.read_text('utf-8'),re.M).group(1)
    guids[p]=get(R/p)==get(backup/p)
scene=A/'01.Scenes/Stage/Level_B5_Circular.unity';scene_same=sha(scene)==sha(backup/scene.relative_to(R))
assets=read(O/'final_assets.json');state=read(O/'state.json');play=read(O/'play_inside.json');audit=read(H/'audit.json')
triangles=sum(m['trianglesIncludingLODs'] for m in assets['models'])
assert all(protected.values()) and all(guids.values()) and scene_same
assert assets['badTriangles']==0 and not assets['missingMaterials'] and state['pbrMaterialsValid'] and state['accepted30StationTransformsPreserved']
assert not state['sceneDirty'] and not state['playing'] and play['complete'] and play['displacement']>.4 and not play['errors']
preservation={'protectedFiles':protected,'modelGUIDs':guids,'savedSceneByteIdentical':scene_same,'totalUniqueTrianglesIncludingVitalLODs':triangles}
(O/'preservation.json').write_text(json.dumps(preservation,indent=2),encoding='utf-8')
files=[p for p in P.rglob('*') if p.is_file() and p.suffix in {'.fbx','.mat','.png'} and p.name.startswith(('CP_','ID_','PF_'))]
record={'author':'송예찬','date':'2026-11-07','scope':'C01 accepted layout prop manufacturing detail and PBR finish','source':'SourceAssets/C01_PropFinish','models':37,'newRuntimeTextures':30,'roughnessOriginals':6,'preservedStationTransforms':30,'savedSceneByteIdentical':scene_same,'uniqueTrianglesIncludingLODs':triangles,'hashes':{str(p.relative_to(R)).replace('\\','/'):sha(p) for p in files},'externalGeneration':False,'runtimeCodeChanged':False,'committedOrPushed':False}
(A/'06.Data/AssetSources/C01_PropFinish_20261107.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
tiles=[('ID_ThermalCycler','PCR · 반응 웰과 가열 뚜껑'),('CP_Centrifuge','원심분리기 · 로터와 시료 홀더'),('ID_UltrasonicBath','초음파 세척기 · 수조와 바스켓'),('ID_DualMagneticStirrer','교반기 · 유리 플라스크와 용액')]
sheet=Image.new('RGB',(1600,1080),(20,28,33));draw=ImageDraw.Draw(sheet)
for i,(n,title) in enumerate(tiles):
    x=(i%2)*800;y=(i//2)*540;im=Image.open(O/('After_Close_'+n+'.png')).convert('RGB').resize((800,500),Image.Resampling.LANCZOS);sheet.paste(im,(x,y));draw.text((x+15,y+505),title,font=font,fill=(222,234,235))
sheet.save(O/'Detail_Overview.jpg',quality=92)
report=f'''# C01 프랍 기능 디테일·베벨·PBR 마감 V0.01

작성자 송예찬 · 2026-11-07

사용자가 확인한 구성과 30개 작업대 배치를 유지하면서 CP_/ID_ 모델 37종의 외형 마감을 갱신했다. 이번 단계는 새 방 배치가 아니라 기존 실험 장비와 수납 가구의 제작 디테일을 높이는 작업이다. FBX·재질을 갱신했으며 저장된 씬 파일은 작업 전 백업과 바이트 단위로 동일하다.

![기능 디테일](Detail_Overview.jpg)

## 실제 반영

| 대상 | 형상 보강 |
| --- | --- |
| 공통 하우징·가구 | 3분할 베벨, 곡면/평면 노멀 분리, 가중 노멀 보존 FBX, 문 경첩·분할선 |
| 원심분리기 | 실제 몸체 구멍, 내부 챔버·8개 로터 홀더·잠금부, 투명 덮개와 고무 씰 |
| PCR | 열린 가열 뚜껑·힌지·내부 플레이트, 96개 열린 반응 웰 |
| 초음파 세척기 | 상판을 뚫은 깊이 있는 수조, 내부 벽·바닥·와이어 바스켓·집게 |
| 현미경 | 굽은 주조 지지대, 헤드·회전 대물렌즈부·미세 초점 조절부·스테이지 레일 |
| 교반기·건조대 | 목·어깨·입구 두께가 있는 유리 플라스크, 교반기 용액과 건조대 배수 홈 |
| 정밀저울·플레이트 장비 | 방풍 유리 레일·수평계, 96개 열린 웰·구동 레일 |
| 피펫·회전기·믹서 | 테이퍼 팁·손가락 받침·표시, 베어링·기어박스·시료 마개, 열린 고무 컵 |
| 멸균기·실러 | 잠금 손잡이·원형 압력계·바늘, 금속 열접착부·포장 봉합선 |
| 라벨 프린터·준비 키트 | 스캐너 광학창·용지 가이드·바코드 출력, 시료 기록 화면·밀봉팩 표시 |
| PPE·수납·분석기 | 성형 용기·보호구 표기·마스크 귀끈, 열린 부품함·내용물, 바이알 어깨·캡·렌즈 링 |

기존 바이탈 모니터의 승인된 둥근 본체, LCD 발광/유리 구조와 외곽 밀도는 유지했다. 모든 면에 무조건 베벨을 넣지는 않았다. LCD·라벨 평면, 얇은 밀봉선과 이미 매끄러운 원본 본체는 용도에 맞게 보존했다.

## 텍스처 구성

공유 표면 6종(Coat/Blue/Steel/Dark/Rubber/Paper)에 1024² Base Color·Tangent Normal·Metallic/Smoothness 패킹 맵 **18장**, 기능 라벨/눈금 **12장**을 추가했다. 거칠기 원본 6장은 SourceAssets에 보관한다. 도장 표면, 브러시 스테인리스, 고무와 종이의 반사·표면 질감을 구분했다.

URP Lit용 패킹은 R=Metallic, A=Smoothness(1−Roughness), G=1, B=0이다. Base는 sRGB, Normal/패킹은 선형이며, 공유 재질의 BaseMap·BumpMap·MetallicGlossMap 연결과 키워드를 실제 에디터에서 확인했다. [Unity URP Lit 공식 문서](https://docs.unity.com/en-us/engine/6000.0/manual/materials-and-shaders/built-in/shaders-in-universalrp/reference/lit-shader)의 맵 역할을 따른다.

이번 맵은 로컬에서 제작한 공유 타일 표면과 개별 라벨이다. 개별 프랍의 고해상도 원본에서 AO/노멀을 베이크한 작업으로 기록하지 않는다. 기구의 큰 형상과 홈은 실제 메시다. 화면·표시·바늘·뚜껑 상태는 정적 아트이며 조작/애니메이션 기능은 추가하지 않았다.

## 검증 결과

- 37종 모델, 고유 에셋 삼각형 **{triangles:,}개**(바이탈 3 LOD 합산). 이전235,680개보다 증가했다. 이 값은 전체 씬 렌더 삼각형 수와 다르다.
- 면적5e-9㎡ 미만 퇴화 삼각형0, 재질/셰이더 누락0, 강제 재반입 경고/오류0.
- 6개 공유 PBR 재질 연결·키워드 유효, 모델37개 GUID 보존, 보호파일23개 해시 동일.
- 승인 작업대30개 위치/회전 동일. 바닥 충돌체29개와 기존 구조의35mm 초과 관통0.
- C01 순환 capsule540표본 막힘0. 전체 복도4854표본 막힘·바닥 누락0.
- 최종1920×1080 Editor Play5초: **{play['framesAdvanced']}프레임 진행, 실제 W 이동{play['displacement']:.3f}m, 새 경고/오류0**. median {play['medianMs']:.2f}ms, p95 {play['p95Ms']:.2f}ms. 짧은 에디터 표본이며 빌드 전체 성능 판정은 아니다.
- Play 종료 후 저장 씬으로 복원, 편집 모드/dirty=false, 백그라운드 override=false. 플레이어(-9.2,-81.36,-10), 회전(0,0,0) 유지.
- `git diff --check`는 이전 작업에서 Unity가 직렬화한 빈 `m_Name: `5곳의 후행 공백을 보고했다. 해당 씬은 이번 단계 전후 해시가 같으며 수동 편집하지 않았다.

첫 시각 검수에서 바이알 중심 좌표 계산, 곡면 노멀, 일부 중복 라벨과 미세 Boolean 삼각형을 찾아 고친 후 최종 반입·검수를 수행했다. 최종 근접/구역 캡처는24장이다. Collider 검사는 모든 미세 메시의 교차 검사를 뜻하지 않는다.

## 자료

- [전체 모습](After_Overview.png), [실험 구역](After_Zone_50.png)
- [현미경 이전](Before_Close_ID_BinocularMicroscope.png) / [현재](After_Close_ID_BinocularMicroscope.png)
- [PCR 이전](Before_Close_ID_ThermalCycler.png) / [현재](After_Close_ID_ThermalCycler.png)
- [원심분리기](After_Close_CP_Centrifuge.png), [세척기](After_Close_ID_UltrasonicBath.png), [멸균기](After_Close_ID_BenchAutoclave.png)
- [바이탈](After_Close_S1_VitalMonitor_18.png), [광학 분석기](After_Close_OpticalAnalyzer.png), [PPE](After_Close_Clinical_PPE_Station.png)
- [모델 검사](final_assets.json), [플레이 검사](play_inside.json), [재질/배치/최종 상태](state.json), [보존 해시](preservation.json)

근접 캡처는 내부를 확인하기 위해 이전보다 가까운 각도로 찍었다. Overview/구역 캡처는 이전과 같은 카메라다. 원본·재현 방법은 [제작 README](../../../SourceAssets/C01_PropFinish/README.md)에 있다. 로컬 저장 완료, 커밋·push는 하지 않았다. C01 출입구·문 포켓·벽/광원·바닥 안내선 마감과 다른 공동은 후속이며 전체 아트0/34는 유지한다.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
readme='''# C01 프랍 제조 디테일·PBR 제작 V0.01

작성자 송예찬 · 2026-11-07

승인된 C01 배치의 CP_/ID_ 모델37종을 갱신한다. 결과와 범위는 [검수 기록](../../Docs/검수/2026-11-07_C01_PropFinish/검수결과.md)을 따른다. `C01_Perimeter`, `C01_InstrumentDetail`, 이 폴더를 함께 보존한다.

## 파일과 재제작

1. `build_pbr.py`: Pillow/numpy를 사용하는 로컬 표면 맵 제작기. 별도 제작 환경은 `%TEMP%/as_art_tools`이며 게임 의존성이 아니다. 런타임 맵30장은 Props/B5/Textures, 거칠기 원본6장은 이 폴더에 둔다.
2. `C01_Perimeter/build_assets.py` → `C01_Perimeter/repair_vital.py` → `C01_InstrumentDetail/build_instruments.py`를 Blender5.2에서 실행한다. 세 제작기가 `finish_geometry.py`를 참조한다. 같은 이름 FBX를 교체하므로 meta/GUID를 보존해야 한다. 장면 배치 도구를 다시 실행하지 않는다.
3. `ImportFinish.cs`의 `PropFinishImport.Run`: 재질/텍스처 설정과 CP_/ID_ 모델의 기존 GUID를 유지한 반입. 이후 기하 수정만 있으면 `InstrumentDetailApply.ImportGeometry`를 사용한다.
4. `FinalAudit.cs`, `Audit.cs`, `VerifyC01Routes.cs`, `Capture.cs`, `PlayC01.cs`, `FinishAudit.cs`: Assets 밖에서 실행하는 에디터 검수 도구. 게임 내부 C#이 아니다. Play 전 저장/편집 상태를 확인한다. `RestoreAfterOwnPlay`는 이 검수기가 방금 실행한 Play 잔여 dirty 상태를 복원할 때만 사용하며 사용자 편집 중에는 실행하지 않는다.

`finish_geometry.py`는 기구별 기능 부품을 더한 뒤 노멀을 정리한다. 최종 evaluated mesh를 무조건 BMesh로 왕복하면 custom normal을 잃을 수 있으므로 삼각분할 후 정상 메시의 노멀을 유지한다. Boolean에서 생긴5e-9㎡ 미만 삼각형만 UV·material index·split normal을 복사해 정리한다. display_uv가 있는 LCD/라벨은 투영 UV 재생성에서 제외한다.

PBR은 6종 공용 표면(Base/Normal/MOS)이며 MOS의 R=metallic, A=smoothness, G=1, B=0이다. 고해상도 개별 에셋 AO 베이크로 해석하지 않는다. Normal은 tangent +Y, Base는 sRGB, Normal/MOS는 선형. 공통 타일링5, Normal strength 도장0.25/Steel0.38. URP 키워드와 텍스처 연결은 state.json에 남긴다.

`baseline.json`의 작업 전 백업은 로컬 임시 폴더다. 백업 자체는 Git 전송 대상이 아니며 `.blend`, 생성기, 최종 FBX/텍스처/재질과 검수 기록이 전달 원본이다. `prepare.py`는 최초 백업 전용이므로 현재 상태에서 다시 실행해 기준을 덮어쓰지 않는다. `prepare_checks.py`도 검수 도구 복사 초기화용이다. `finalize_records.py`는 최종 검사 후 로컬 기록과 provenance를 갱신한다.

게임 C#·Animator·다른 씬·리브·플레이어 시작 위치는 보호한다. 이번 단계에서는 씬 저장 파일 자체도 변경하지 않았으며 외부 생성/업로드/커밋/push를 하지 않았다.
'''
(H/'README.md').write_text(readme,encoding='utf-8')
summary=f'2026-11-07 최신: 승인된 C01 배치를 유지하며 프랍37종의 베벨·곡면 노멀·기구 디테일과 공용 PBR18장/기능 라벨12장을 반영했다. 원심분리기 로터, PCR96웰, 세척기 수조, 현미경, 유리 플라스크, 압력계·열접착부 등을 구체화했다. [최신 검수](검수/2026-11-07_C01_PropFinish/검수결과.md), [제작 도구](../SourceAssets/C01_PropFinish/README.md)를 우선한다. 모델 누락/퇴화0, 순환540/복도4854 막힘0, Play{play["framesAdvanced"]}프레임·{play["displacement"]:.3f}m·새 경고/오류0. 30작업대 Transform·37GUID·23보호파일·저장 씬 동일, 게임 코드 추가0. 로컬 저장, 커밋/push 미실시. 다음은 사용자 시야 확인 후 C01 출입구·문 포켓·벽/광원·바닥 안내선 마감 → T01/C02이며 전체 아트0/34 유지.'
for rel,oldver,newver in [('Docs/이어하기_2026-11-06.md','V0.24','V0.25'),('Docs/회사_작업목록_2026-11-06.md','V0.22','V0.23'),('AGENTS.md','V0.40','V0.41'),('CLAUDE.md','V0.40','V0.41')]:
    path=R/rel;txt=path.read_text('utf-8');dst=backup/'docs_before_propfinish'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(path,dst)
    if '2026-11-07_C01_PropFinish' not in txt[:1500]:
        head,body=txt.split('\n',1);text=summary if rel.startswith('Docs/') else summary.replace('(검수/','(Docs/검수/').replace('(../SourceAssets/','(SourceAssets/')
        path.write_text(head.replace(oldver,newver)+'\n\n'+text+'\n\n이전 단계 기록:\n'+body.lstrip(),encoding='utf-8')
for folder,oldver,newver in [('C01_Perimeter','V0.02','V0.03'),('C01_InstrumentDetail','V0.01','V0.02')]:
    p=H.parent/folder/'README.md';txt=p.read_text('utf-8')
    if 'C01_PropFinish' not in txt[:800]:
        head,body=txt.split('\n',1);p.write_text(head.replace(oldver,newver)+'\n\n최신 제작은 [프랍 디테일/PBR 마감](../C01_PropFinish/README.md)을 따른다. 현재 생성기는 finish_geometry.py도 참조한다. 이전 Import만 실행하면 새 재질 설정을 덮어쓸 수 있으므로 최신 ImportFinish를 우선한다.\n'+body,encoding='utf-8')
print(json.dumps({'models':37,'triangles':triangles,'protected':sum(protected.values()),'guids':sum(guids.values()),'sceneIdentical':scene_same,'records':'written'},ensure_ascii=False))
