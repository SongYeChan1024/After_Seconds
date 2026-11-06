from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;O=R/'Docs/검수/2026-11-07_C01_InstrumentDetail';B=R/'SourceAssets/C01_Perimeter';OLD=R/'Docs/검수/2026-11-07_C01_Perimeter'
def read(p):return json.loads(p.read_text('utf-8'))
play=read(O/'play_inside.json');audit=read(O/'audit.json');asset=read(O/'final_assets.json');local=read(H/'audit.json');placement=read(H/'placement.json');protected=read(B/'baseline.json')['protected']
changed=[p for p,d in protected.items() if hashlib.sha256((R/p).read_bytes()).hexdigest()!=d]
assert not changed
assert play['complete'] and play['framesAdvanced']>0 and play['displacement']>.1 and not play['errors']
assert not audit['blocked'] and not audit['groundMissing'] and not audit['missingMesh'] and not audit['missingMats']
assert asset['modelCount']==37 and asset['badTriangles']==0 and not asset['missingMaterials']
assert not local['overlaps'] and not local['circleBlocked'] and placement['acceptedStationLayoutPreserved']
assert asset['playerPosition']=='(-9.200, -81.360, -10.000)' and asset['playerRotation']=='(0.000, 0.000, 0.000)'
(O/'protected_files.json').write_text(json.dumps({'checked':len(protected),'changed':changed},indent=2),encoding='utf-8')

report=f'''# C01 외곽 장비 다양화·디스플레이 검수 V0.01

작성자 송예찬 · 2026-11-07

`Level_B5_Circular`의 C01에서 사용자가 승인한 **외곽 30개 작업대의 위치와 회전을 그대로 유지**했다. 반복되는 탁상 장비 16자리를 서로 다른 장비로 교체하고 수납 형식도 나눴다. 이번 변경은 로컬 저장 상태이며 커밋·push하지 않았다.

## 외형 변경

신규 모델은 **장비 16종과 수납 변형 5종, 총21종**이다. 현미경, PCR 열순환기, 피펫 작업대, 유세포 분석기, 정밀저울, 이중 교반기, 크로마토그래피 스택, 초음파 세척기, 유리기구 건조대, 탁상 멸균기, 슬라이드 스캐너, 이중 믹서, 마이크로플레이트 핸들러, 튜브 회전기, 멸균 포장 실러, 라벨 프린터를 배치했다. 같은 기구를 각 구역에 반복하는 구성을 줄이고 시료 준비·분석·세척·보관에 맞춰 구분했다.

수납에는 냉동 서랍장, 유리 시료장, 혼합 물품 선반, 위로 여는 상부장, 인덱스 서랍장을 추가했다. 건축 작업대 규격은 유지하고 눈높이의 장비 실루엣과 수납 패턴을 바꿨다. 큰 장비 위의 낮은 선반은 상부장으로 교체해 간섭을 피했다.

베벨·패널 이음·고정 나사·방진발·슬롯·통풍구·시료 홀더·힌지·연결 호스·명판을 추가했다. 크로마토그래피 호스는 장비 포트와 시약병 뚜껑까지 연결했다. 기존 바이탈 모니터는 둥근 외함을 유지하고 앞 단계에서 받침대·바퀴·케이블·조작부를 보수했다.

## 모니터

- 판 위에 입체 선으로 만들었던 그래프를 제거하고 **장비별 화면 13종**을 제작했다. 환자 생체 신호와 환경 모니터, 분석 결과, 회전수, 온도, PCR, 저울, 멸균, 라벨 출력 등을 구분한다.
- LCD 평면에 전용 UV와 화면 텍스처를 넣고 약한 자체 발광을 적용했다. 베젤 앞면보다 안쪽에 표시 면을 두고 별도 투명 커버와 홈을 만들었다.
- 화면 텍스처는1024×640, 밉맵·Trilinear·Clamp를 사용한다. 기구 명판6종은 별도 텍스처다.
- 화면은 **정적 외형**이다. 실시간 파형·측정·장비 조작·게임 UI를 구현하지 않았다.

## 검사 결과

- 신규/보수 모델37종: 퇴화 삼각형0, 누락 재질0, 강제 반입 경고/오류0. 면적5e-9㎡ 미만의 삼각형을 검사했다. 원본 바이탈의 중복 정점을 용접한 뒤 남은 미세 퇴화 면은 정리했다.
- 신규 바닥 충돌체29개: 기존 구조와35mm 초과 관통0. 모든 메시 간 정밀 교차 판정이라는 뜻은 아니다.
- C01 반경5.0/5.7/6.4m 순환 동선540 capsule 표본: 막힘0.
- 전체 복도4854 capsule 표본: 막힘·바닥 누락0. 문38세트와 T01/T03/T11 왕복6회는 직전 외곽 배치 단계에서 통과했고, 이후 작업대 위치와 문·복도 구조는 변경하지 않았다.
- 최종1920×1080 Editor Play5초: **{play['framesAdvanced']}프레임**, 실제 W 입력 **{play['displacement']:.3f}m 이동**, 새 경고/오류0. median {play['medianMs']:.2f}ms, p95 {play['p95Ms']:.2f}ms. 전체 빌드 성능이나 최종 게임 완성을 뜻하지 않는다.
- 첫 입력 검사는 비활성 키보드 포커스로 이동0m였다. 검수 도구에서 기존 키보드 장치를 일시 활성화하고 입력을 다시 전달해 위 이동을 확인했다. 장치 상태와 백그라운드 실행 override는 복원했다.
- 게임 C#·Animator·다른 씬·기존 리브를 포함한 보호 파일23개의 해시 동일. 저장된 플레이어 위치(-9.2,-81.36,-10), 회전(0,0,0) 유지.

## 시각 자료

- [콘솔 수정 전](Before_Close_Observation_Console_A.png) → [수정 후](After_Close_Observation_Console_A.png)
- [바이탈 모니터](After_Close_S1_VitalMonitor_18.png), [광학 분석기](After_Close_OpticalAnalyzer.png)
- [현미경](After_Close_ID_BinocularMicroscope.png), [정밀저울](After_Close_ID_PrecisionBalance.png), [크로마토그래피](After_Close_ID_ChromatographyStack.png)
- [마이크로플레이트 장비](After_Close_ID_MicroplateHandler.png), [실험 구역](After_Zone_50.png), [보관·관찰 구역](After_Zone_325.png)

앞 단계의 캐비닛·PPE·점검함·서비스 패널 수정은 [외곽 재구성 기록](../2026-11-07_C01_Perimeter/검수결과.md)에 있다. 전체 아트0/34는 유지하며 C01 출입구 곡면·문 포켓·벽/광원·바닥 안내선의 최종 마감, 다른 공동24배치와 층간 구조는 별도 남은 작업이다. 현재 범위를 B5 전체 완성으로 해석하지 않는다.

원본과 반입/검수 도구는 [SourceAssets/C01_InstrumentDetail](../../../SourceAssets/C01_InstrumentDetail/README.md)에 있다.
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')
oldreport='''# C01 외곽 실험 설비 재구성 V0.01

작성자 송예찬 · 2026-11-07

돔 외곽을30개 설비 자리로 연결했다. 하부 작업대·서랍·세척대·냉장고, 상부 수납·시약 선반, 서비스 패널·배관·콘솔 배선을 배치했다. 세 출입구와 중앙 포드의 순환 동선은 보존했다. 이 배치는 사용자 확인을 받았으며, 최신 장비 다양화/화면 마감은 [후속 검수](../2026-11-07_C01_InstrumentDetail/검수결과.md)를 우선한다.

- CD-040 응급 캐비닛: 실제 불투명 후면·측면·선반·수납물, 유리문과 서랍을 제작했다. 유리 너머로 벽이 보이던 문제를 수정했다.
- CD-029 서비스 백플레이트: 기존 점검함은 한 곳으로 통합했고, 다른 쪽은 통풍구만 유지했다. C01 활성 점검함1개다.
- B5 관찰 콘솔2대: 낡은 기존 외형을 비활성 보존하고 밀폐형 일체식 본체·조작부로 교체했다.
- Clinical_PPE_Station: 수납장·장갑/마스크 디스펜서·손 소독기 구조로 다시 제작했다.
- S1_ServiceBackboard_Support: 별도로 서 있던 판을 보관하고 시계·기록판을 연속 작업대 서비스 패널에 통합했다.
- S1_VitalMonitor_18: 원본 외함을 유지하며 정점 용접·노멀·LOD를 보수하고 녹아 보이던 받침대·바퀴·케이블·조작부를 다시 제작했다. 원본 모델/재질은 보존한다.
- LP_BenchAnalyzer: 반복된 상자형 외관을 시료 캐러셀·광학 헤드·카트리지가 보이는 광학 분석기로 교체했다. 기능은 정적 외형이다.
- 곡면 작업대의 전면 겹침을 줄이고 상판 접합 쐐기로 뒤쪽 틈을 닫았다. 이전 벽 수납장과 새 수납장이 겹치는 문제를 정리했다.

초기 외곽 배치 검사에서 작업대 충돌체29개 관통0, 순환 동선540표본 막힘0, 전체 복도4854표본 막힘/바닥 누락0을 확인했다. T01/T03/T11 왕복6/6, 문38세트 열린 통행/닫힌 충돌38/38을 통과했다. Play395프레임·실제 입력1.217m·새 경고/오류0을 확인했다. 최종 후속 화면/모델 검수와 성능은 위 링크가 최신이다.

[외곽 전](Before_Zone_280.png) / [외곽 재구성 후](After_Zone_280.png), [유리 캐비닛](After_EmergencyCabinet.png), [PPE](After_Close_Clinical_PPE_Station.png).

이 폴더의 렌더는 장비 다양화 전 단계의 기록이다. Blender 원본·FBX는 후속 단계에서 LCD 등 세부가 갱신되었으며 `SourceAssets/C01_Perimeter`와 `SourceAssets/C01_InstrumentDetail`을 함께 보존한다. 로컬 저장 상태로 커밋/push하지 않았다.
'''
(OLD/'검수결과.md').write_text(oldreport,encoding='utf-8')

note='2026-11-07 최신: C01 외곽30개 작업대 배치를 사용자 확인 후 유지했다. 장비16종·수납변형5종을 추가해 반복을 줄였고,13종 LCD/베젤/유리/발광·명판·호스·세부를 반영했다. 응급 캐비닛 내부, 점검함1곳, 콘솔/PPE/서비스 패널과 바이탈 모니터 보수도 포함한다. [최신 검수](검수/2026-11-07_C01_InstrumentDetail/검수결과.md), [제작 도구](../SourceAssets/C01_InstrumentDetail/README.md)를 따른다. 모델37종 누락/퇴화0, 순환540/복도4854표본 막힘0, 최종 Play401프레임·0.916m·새 경고/오류0. 화면은 정적 외형이며 게임 C#을 추가하지 않았다. 보호23파일/플레이어 시작 위치 유지. 로컬 저장, 커밋/push 미실시. 다음은 사용자 시야 확인 후 C01 출입구·문 포켓·표면/광원 마감 → T01/C02이며 전체 아트0/34 유지.'
for rel,a,b in [('Docs/이어하기_2026-11-06.md','V0.23','V0.24'),('Docs/회사_작업목록_2026-11-06.md','V0.21','V0.22')]:
 p=R/rel;s=p.read_text('utf-8');head,rest=s.split('\n',1);assert a in head;p.write_text(head.replace(a,b)+'\n\n'+note+'\n'+rest,encoding='utf-8')
for rel in ['AGENTS.md','CLAUDE.md']:
 p=R/rel;s=p.read_text('utf-8');head,rest=s.split('\n',1);assert 'V0.39' in head
 lead='2026-11-07 최신: C01 외곽30개 작업대·캐비닛/콘솔/PPE/바이탈 보수 후, 승인된 배치를 유지하며 신규 장비16종+수납변형5종과13종 LCD를 반영했다. [이어하기 V0.24](Docs/이어하기_2026-11-06.md), [최신 검수](Docs/검수/2026-11-07_C01_InstrumentDetail/검수결과.md), [원본](SourceAssets/C01_InstrumentDetail/README.md)을 우선한다. 게임 코드·다른 씬·기존 리브·플레이어 시작 위치 보존. 로컬 저장 상태로 이번 변경은 커밋/push하지 않았다. 전체층이나 전체 아트 완료가 아니며0/34 유지. 이전 전체 Apply를 재실행하지 않는다.'
 p.write_text(head.replace('V0.39','V0.40')+'\n\n'+lead+'\n'+rest,encoding='utf-8')
p=B/'README.md';s=p.read_text('utf-8').replace('V0.01','V0.02',1);head,rest=s.split('\n',1);p.write_text(head+'\n\n최신: 사용자 승인 배치에 장비 다양화와 LCD 마감을 추가했다. [후속 제작 원본](../C01_InstrumentDetail/README.md)을 함께 읽는다. 현재 CP_ 화면 모델 제작기는 후속 display_geometry.py를 참조한다. 기존 Apply를 현재 씬에 재실행하지 않는다.\n'+rest,encoding='utf-8')

provenance={'author':'송예찬','date':'2026-11-07','scene':'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity','sources':['SourceAssets/C01_Perimeter','SourceAssets/C01_InstrumentDetail'],'originalVital':'SourceAssets/B5_Sector01/S1_VitalMonitor.blend','acceptedStations':30,'newInstrumentAndStorageTypes':21,'lcdTextures':13,'labelTextures':6,'staticVisualsOnly':True,'newRuntimeScripts':0,'paidGeneration':False,'models':read(H/'assets_manifest.json'),'perimeterModels':read(B/'assets_manifest.json'),'vitalRepair':read(B/'vital_repair.json')}
p=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/C01_Perimeter_InstrumentDetail_20261107.json';p.write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'protected':len(protected),'changed':changed,'newModels':21,'totalModels':asset['modelCount'],'playMoved':play['displacement'],'reportsWritten':True}))
