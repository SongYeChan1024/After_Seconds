# 층간 단면·후속 검수 원본 V0.01

작성자 송예찬 · 2026-11-06

B5–B4 계단A와 B4–B3 계단B의 도착문, 상부참, 아래층으로 이어지는 계단을 정합한 파생 모델이다. [층간 단면](../../Docs/도면/잠입_탐색/층간_단면.md), [검수 결과](../../Docs/검수/2026-11-06_LevelContinuation/검수결과.md)를 따른다. 기존 LP/B5/B4 모델은 보존했다.

`LC_B5_Architecture.blend`, `LC_B4_Architecture.blend`는 베벨·가중 노멀을 유지한 편집 원본이다. 신규 파트 베벨은 보통4mm/2분할, 작은 렌즈·디딤판 띠는1–2mm다. 기존 파트의 베벨 폭은 유지한다. 출력본은 재질과8m 구역별로 합치고 퇴화 면을 정리한 뒤 명시적으로 삼각화했다. 원본 미세 조인트를 다시 돌출시키지 않는다.

| 파일 | 역할 |
| --- | --- |
| `build_sections.py` | LP 편집 원본에서 B5/B4 단면·문 개구·추락 방지 난간·계단 조명 제작. FBX와 신규/대체 충돌 JSON 출력 |
| `finalize_models.py` | 최초 출력 뒤 계단B 상부 조명 렌즈의 안쪽 방향을 바로잡은 일회성 이력. 최신 생성기에는 수정 반영됨 |
| `ApplyContinuation.cs` | 외부 Editor 제작. Import → Sections → B3. B3 최종 밝기는 JSON/생성기에 반영. 완료 씬에 재실행 금지 |
| `ValidateContinuation.cs` | 경로 캡슐·문 앵커/통행·추가 프랍 겹침·재질/스크립트 참조, 정적 반사25개 |
| `WalkContinuation.cs` | 임시 CharacterController로 A/B/C, 계단·데크 왕복 검사. 실제 플레이 기능 아님 |
| `ReviewContinuation.cs` | 임시 카메라의 후처리 포함 Edit Mode 렌더 |
| `PlayPerformance.cs` | Play Mode에서24초·3시점·W 입력 및 프레임/CPU/GPU/로그 측정. Editor 이벤트만 사용 |

Unity CLI에는 대상 프로젝트와 `--caller plugin --skill unity-cli`를 명시한다. C# 파일은 게임 Assets 밖에 있으며 게임 동작을 추가하지 않는다. `ReloadB5`는 도구 실패 직후 본인이 만든 미저장 변경을 버릴 때만 사용했던 복구 이력이다. 일반 작업에서 실행하지 않는다.

씬 전환 출입문은 닫힌 정적 충돌이다. 자동 로딩·문 작동·키패드 입력·적 AI는 사용자 코딩 단계다. B4 시작점은 정합한 상부참 `(u41, h0, v28.25)`로 이동했다. B5 포드와 기존 인물/소품은 유지하며 새 LP 프랍4개만 앞면 방향을 보정했다.

B5 기존 `StairA_LampUpper`는 새 문 위로 옮긴 씬 Transform override다. 중심높이10.8m, 연결 Point Light10.65m이며 원본 조명 모델은 보존했다. `Sections()`와 `MoveUpperLamp()`에 최종 배치가 반영되어 있다.
