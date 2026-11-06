# C01 장비 다양화와 디스플레이 마감 V0.03

최신 병·라벨·간섭 보수는 [C01_PropRepair](../C01_PropRepair/README.md)를 따른다. 현재 제작기는 refine_components.py도 참조하며 새 PR_ 재질은 ImportRepair를 마지막에 반입한다.

최신 제작은 [프랍 디테일/PBR 마감](../C01_PropFinish/README.md)을 따른다. 현재 생성기는 finish_geometry.py도 참조한다. 이전 Import만 실행하면 새 재질 설정을 덮어쓸 수 있으므로 최신 ImportFinish를 우선한다.

작성자 송예찬 · 2026-11-07

사용자가 승인한 외곽 30개 작업대의 위치·회전·순환 동선을 유지하고, 반복되던 탁상 장비 16자리와 수납 형태를 다양화했다. 앞 단계는 [C01_Perimeter](../C01_Perimeter/README.md), 현재 결과는 [검수 기록](../../Docs/검수/2026-11-07_C01_InstrumentDetail/검수결과.md)을 따른다.

## 제작물

- 신규 `ID_` 모델 21종: 장비 16종, 냉동 서랍장·유리 시료장·혼합 선반·상부 개폐장·인덱스 서랍장 5종. Unity `05.Model/Props/B5`에 직접 둔다.
- 장비 LCD 13종과 명판 6종은 같은 분류의 `Textures`, 재질은 `Materials`에 둔다. 실제 게임 HUD나 조작 기능이 아닌 정적 장비 외형이다.
- 화면은 입체 그래프 선 대신 개별 UV를 가진 발광 LCD 평면, 별도 투명 커버, 안쪽 홈과 베젤로 구성한다. 생체 신호·환경 관찰·분석 결과·RPM·온도·PCR·저울·라벨 출력 등의 표시를 구분한다.
- 베벨, 패널 이음, 나사, 방진발, 조작부, 슬롯, 통풍구, 시료 홀더, 실제 끝단을 연결한 호스, 기구 명판을 추가했다. 기존 바이탈 모니터의 둥근 본체 형상은 보존했다.

## 원본과 실행

`build_displays.py`는 Pillow로 정적 화면 PNG를 만든다. 제작 때 사용한 별도 환경은 `%TEMP%/as_art_tools`이며 프로젝트 런타임 의존성이 아니다. `build_instruments.py`는 Blender 5.2의 배치 제작기다. `display_geometry.py`는 이전 단계의 `build_assets.py`와 `repair_vital.py`도 참조한다. 따라서 두 SourceAssets 폴더를 함께 보존한다.

재제작 순서는 화면 PNG → C01_Perimeter/build_assets.py → C01_Perimeter/repair_vital.py → build_instruments.py → `InstrumentDetailApply.Import`다. 기존 에셋의 meta/GUID를 유지한다. 이미 배치된 현재 씬에서 `Apply`를 재실행하지 않는다. `ImportGeometry`는 재제작한 동일 이름 FBX만 반입한다. 소스의 명시적 화면 노멀과 LCD/명판 양면 설정을 유지한다.

URP의 `_EMISSION` 키워드만 켜서는 재질 재검증 때 발광이 꺼질 수 있다. LCD의 `globalIlluminationFlags=BakedEmissive`와 EmissionMap/Color를 함께 보존한다. 화면은 1024×640, 밉맵·Trilinear·Clamp·비압축이다. 유리는 불투명 몸체와 별도 재질이며 깊이를 기록하지 않는다.

`placement.json`에 승인된 30개 작업대의 전후 Transform과 장비 교체 대응을 남겼다. 비활성 원본 프랍을 삭제하지 않는다. `backup.json`은 승인 배치의 작업 전 로컬 사본 위치다. 외부 생성·업로드·커밋·push는 하지 않았다. 게임 C#·Animator·다른 씬·기존 리브·플레이어 시작 위치는 보호했다.
