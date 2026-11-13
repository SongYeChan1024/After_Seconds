# 1F 첫 햇빛 표현 보수 V0.02

작성자 송예찬 · 2026-11-13

태양의 크기와 빛번짐을 강조해 공장 밖에서 처음 햇빛을 마주하는 인상을 보강한다. 기존 석양의 위치·색 흐름을 유지하고 태양 원반, 가까운 광륜, 넓은 대기 산란과 1F 전용 URP Bloom을 조정한다. 공장 실내·출구·황야에서 길과 구조의 윤곽을 확인한다.

기존 셰이더·재질의 GUID를 보존한다. VolumeProfile은 `06.Data/Rendering/1F`에 분류하며 다른 층의 설정과 공유하지 않는다. 게임 코드·Player/Input·승강기 가동부·구조·충돌체는 보존한다. SourceAssets C#은 외부 제작/검수 도구이며 게임 실행 코드가 아니다. 동적 눈 적응이나 시간 진행은 포함하지 않는다.

이번 Before·첫 Apply와 과거 전체 제작기는 후속 편집 뒤 다시 실행하지 않는다. 백업은 `%LOCALAPPDATA%/Temp/AfterSeconds_FirstLight_20261113/before`이며 이번 검수만 `Docs/Review/2026-11-13_1F_FirstLight`에 기록한다.

변경 기록: V0.01 — 요청 범위·표현 방향·보존 기준. 송예찬.


최종 태양 반지름0.026, HDR 색(7.5,5.2,2.8), 가까운 광륜1.2, 넓은 광륜0.6/폭0.16이다. `FS_SunsetSky.mat`에서 크기와 광륜을 조절한다. `FL_FirstLightBloom.asset`에서 Threshold1.2·Intensity0.7·Scatter0.78을 조절한다. Bloom 전용 Global Volume이며 원래1F 카메라의 HDR/후처리/Default 레이어를 이용한다. 기존 공용 URP 설정은 변경하지 않았다.

[검수 결과](../../Docs/Review/2026-11-13_1F_FirstLight/Review.md) · [전후 화면](../../Docs/Review/2026-11-13_1F_FirstLight/review.html). 기존 셰이더 최신 원본은 이 폴더의 `FS_SunsetSky.shader`이며 이전 F1_SunsetSky 원본은 최초 제작 당시 자료다.

변경 기록: V0.02 — 최종 조절값·프로필·검수·최신 원본 안내. 송예찬.
