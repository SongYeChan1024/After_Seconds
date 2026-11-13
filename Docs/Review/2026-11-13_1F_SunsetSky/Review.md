# 1F 석양 하늘 검수 V0.01

작성자 송예찬 · 2026-11-13

HDRI 없이 1F 전용 절차적 석양 스카이박스를 제작해 저장했다. 서쪽 출구·황야 진행 방향에 고도5°의 태양을 두고 주황빛 수평선, 분홍·보랏빛 상공, 얇은 구름과 해 주변 광륜을 표현했다. 햇빛 방향·색과 거리 안개를 맞추고 실내 보조광7개와 환경광을 조정해 공장 구조가 읽히도록 했다. 기존 하늘 재질 `FW_WildernessSky`는 보존한다.

[전후 비교](review.html) · [황야 화면](after/Wilderness.jpg) · [출구 화면](after/Exit.jpg)

- 새 에셋: `Environment/1F/FS_SunsetSky.shader`, `Environment/1F/Materials/FS_SunsetSky.mat`.
- 하늘: `AfterSeconds/1F/WildernessSunset`. 상공·수평선·반대편 색, 태양 크기, 구름 양, 노출을 재질에서 조절할 수 있다.
- 햇빛: 기존 `OvercastDirectional` 회전 `(5,88,0)`, 색 `(1,.60,.32)`, 강도1.12. 이름과 오브젝트를 유지했다.
- 정적 반사8개를 석양으로 다시 구웠다. 1F의 RenderSettings에만 적용했다.
- Transform2,107개·Collider165개 유지. 태양 회전 외 배치·스케일·활성·충돌 변경0. 메시·재질·스크립트 누락0, 셰이더 오류0.
- 보호 게임 코드·다른 씬·ProjectSettings 53개 해시 일치.
- 실제 Play3시점에서 330프레임 진행, 새 경고·오류0. 중앙값16.72ms, 95백분위38.54ms. 짧은 에디터 관측이며 빌드 성능 수치가 아니다.

실측 HDRI가 아닌 직접 제작한 정적 아트 하늘이다. 시간에 따라 해가 움직이는 기능은 추가하지 않았다. 승강기 운행·문 제어·엔딩 스크립트와 Player/Input·Animator는 변경하지 않았다. 구조가 바뀌지 않아 통행 테스트는 중복 실행하지 않았다.

현재 저장된1F 편집 상태, 석양 재질 선택과 서쪽 황야 시야. 커밋·push 미실시. 백업은 `%LOCALAPPDATA%/Temp/AfterSeconds_SunsetSky_20261113/before`에 있으며 첫 Apply는 현재 씬에 재실행하지 않는다.

변경 기록: V0.01 — 석양 스카이박스·조명/반사 연결·보존/Play 검수. 송예찬.
