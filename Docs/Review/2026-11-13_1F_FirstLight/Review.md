# 1F 태양과 빛번짐 보수 검수 V0.01

작성자 송예찬 · 2026-11-13

태양의 지름을 기존의 약2.9배로 키우고 밝은 중심부, 가까운 광륜, 넓은 주황빛 산란을 겹쳐 출구 너머 햇빛의 존재감을 보강했다. 1F 전용 Bloom으로 밝은 부분의 빛번짐을 더했다. 석양의 위치·기존 조명·안개·공장과 황야 배치는 유지했다.

[전후 화면](review.html) · [황야](after/Wilderness.jpg) · [출구](after/Exit.jpg)

| 조절 항목 | 최종 값 |
| --- | --- |
| 태양 반지름 `_SunRadius` | 0.009 → 0.026 |
| 태양 HDR 색 `_SunColor` | (7.5, 5.2, 2.8) |
| 가까운 광륜 `_CoronaStrength` | 1.2 |
| 넓은 광륜 강도 / 폭 | 0.6 / 0.16 |
| Bloom Threshold / Intensity / Scatter | 1.2 / 0.7 / 0.78 |

기존 `Environment/1F/FS_SunsetSky.shader`와 `Materials/FS_SunsetSky.mat`의 GUID를 보존했다. 새 프로필은 `06.Data/Rendering/1F/FL_FirstLightBloom.asset`이고 Bloom 한 효과만 포함한다. 씬의 `1F_AbandonedFactory/Lighting/FirstLightBloom`에 연결했다. Default 레이어0·Global·Priority10·Weight1이며 기존 Main Camera의 Volume Mask1·후처리·HDR 설정에서 실제 적용을 확인했다. 기존 PC_RPAsset·PC_Renderer·카메라 설정은 변경하지 않았다.

출구·황야·생산동·외벽·승강기 화면을 확인했다. 태양과 광륜을 강조하면서 길과 바위 윤곽, 실내 구조가 읽히는 것을 확인했다. 반사8개는 새 하늘로 다시 구웠다. Bloom 자체는 화면 후처리이며 반사 베이크에 포함되지 않는다.

- 기존2,107 Transform의 위치·회전·스케일·활성 변경0. Volume1개 추가로2,108. Collider165개 유지.
- 셰이더 오류·누락 메시/재질/스크립트0. 콘솔 경고/오류0.
- 게임 코드·프리팹·Animator·입력·다른 씬·설정 등 보호215파일 해시 일치. 하늘 셰이더/재질.meta 보존.
- 실제 Play에서 후처리를 켠 임시 카메라3시점·724프레임 진행·새 경고/오류0. 프레임 중앙값8.40ms, 95백분위15.59ms는 짧은 에디터 관측이다.

정적인 햇빛 표현이다. 출구를 넘을 때 화면이 밝아졌다 적응하는 시간 연출, 엔딩 기능은 추가하지 않았다. Player/Input·승강기 가동부·게임 코드는 유지했다. 구조 변경이 없어 통행 검사를 반복하지 않았다. 검수 카메라는 기존 검수와 같은 시점/FOV와 far8500을 사용했고, 실제 Main Camera의 far1000은 유지했다.

저장된1F 편집 상태이며 석양 재질을 선택했다. 커밋·push 미실시. 백업은 `%LOCALAPPDATA%/Temp/AfterSeconds_FirstLight_20261113/before`. 최신 제작 원본은 [F1_FirstLight](../../../SourceAssets/F1_FirstLight/README.md)이며 이전 전체 제작기와 첫 Apply는 재실행하지 않는다.

변경 기록: V0.01 — 태양·광륜·Bloom·반사 보수와 보존/Play 검수. 송예찬.
