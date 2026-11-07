# C02 밀도·모니터 보강 V0.01

작성자 송예찬 · 2026-11-08

사용자 요청: 빈 벽면을 보강하고 6분할 화면 중 두 번째 화면의 이전 구조를 갱신하며 모니터의 제작 디테일을 높인다. 현재 C02 배치와 사용자 조명 설정을 먼저 백업했다.

`C02_Security/build.py`의 기존 모델8종을 선택 재제작했다. 화면의 기존 UV 방향을 유지하면서 분리된 베젤/실링, 17mm 안쪽 LCD, 후면 서비스 커버/통풍구/체결구, 단자와 VESA/틸트 지지대, 책상 글랜드까지 이어진 배선을 추가한다. 기존 Transform과 모델 GUID를 유지한다. 제작 시 `C02_MODELS`를 쉼표 구분으로 지정하면 해당 파일만 출력한다. 전체 초기 `C02_Security/Apply.cs`는 기존 사용자 편집을 덮어쓸 수 있으므로 현재 씬에 재실행하지 않는다.

새 모델6종은 `build.py`로 만든다. `SR_AVServiceRack` 영상 분배 장비, `SR_CredentialStation` 열쇠/출입증 인계함, `SR_EvidenceCabinet` 봉인 케이스 보관함, `SR_ShiftEquipment` 헤드셋/충전 배터리 벽 거치대, `SR_NorthAirReturn` 3연 환기 그릴과 실제 돔까지 연결된 덕트, `SR_WallServices` 벽 배선/지지대다. 배치는 `C02_Security_Art/C02_Equipment_Infill`에만 추가한다. 기존 가구·문·바닥 표기는 유지한다.

`map_texture.py`는 실제 `facility_layout.json`의 B5 15목적지·19복도와 방 반경/터널 단면을 동일 축척으로 그린다. 상단 가운데 `SC_Display_05`에 사용한다. 수동 7거점 지도는 제거했다. `Feeds.cs`로 현재 씬의 감시 시점4개를 캡처하고 `refresh_feeds.py`로 정적 화면01–04를 갱신한다. 원래 텍스처 생성기도 최신 피드가 있으면 이를 사용하며 05번은 새 지도 생성기를 호출한다. 화면은 모두 정적이고 실시간 감시/로그 기능은 없다.

모델은 05.Model/{Props,Environment}/B5 직하, 공용 재질은 기존 SC_/TC_를 사용한다. 추가 인쇄 아틀라스1장과 재질1개는 Props/B5/Textures·Materials에 둔다. 모델 원본 `.blend`와 제작 스크립트는 SourceAssets, 반입 기록은 06.Data/AssetSources다.

`prepare.py`의 현재 에셋 SHA256 기준과 외부 임시 백업은 이번 단계의 원본이다. `Prepare.cs`는 씬을 별도로 백업한다. `Audit.cs`는 기존 Transform/Light, 메시, 주 통행로를 검사하고 `DetailAudit.cs`는 새 장비의 충돌·접근과 실제15돔을 확인한다. `Walk.cs`는 기존 CharacterController로 통행한다. `Play.cs`는 기존 키보드 입력으로 실제 프레임·이동·새 로그를 기록하며 게임 코드는 수정하지 않는다. `Restore.cs`는 Play 후 편집 상태를 다시 백업/보존한다.

[최종 검수와 전후 이미지](../../Docs/검수/2026-11-08_C02_Refine/검수결과.md)를 따른다. 이번은 로컬 저장 범위다. 사용자 외형 확인과 전체 B5 완성 후 조명 조정은 남아 있다.
