After Seconds 전체 씬 깊이 충돌 검수 도구 V0.01
작성일: 2026-11-11 / 작성자: 송예찬

최종 결과: ../../Docs/Review/2026-11-11_ZFighting/review.html
검증: saved_validation.json, preservation.json, residual_summary.json

이 폴더는 Unity 프로젝트 밖의 일회성 편집·검수 도구다.
게임 런타임 스크립트가 아니며 Assets에 복사하지 않는다.
Unity 6000.4.0f1의 열린 Editor와 unity-cli를 사용한다.
Python 3 + NumPy, Shapely, Pillow가 필요하다.
메시 바이너리와 Python 보조 의존성은 Unity 프로젝트 Temp/ZFightingReview에 있다.
다른 PC에서 검사할 때에는 Export.cs로 현재 메시를 새로 내보낸다.

results/: 수정 전 기준 조사.
plans/, residual2/, finish_plans/, precision_plans/: 각 단계의 적용 계획.
applied_*.json: 적용 당시 기록. 초기 빈 메시의 복구 이력은 repaired_empty_*.json.
after/, final/: 중간 시점의 전체 재조사이며 최종 무결성 판정 파일은 아니다.
verified_candidates/, verified_residual/: 최종 저장 메시로 다시 검사한 후보.
residual_summary.json: 0.05mm 경계 허용오차로 잔여 영역을 평가한 최종 판정.

이전 계획의 삼각형 인덱스·메시 GUID는 당시 상태에 종속된다.
Apply, batch_apply, second_pass, finish, precision을 현재 씬에 다시 실행하지 않는다.
수정 도구의 기준 SHA 검사를 우회하지 않는다.
새 수정에는 현재 씬을 새로 조사하고 별도 계획·기준 SHA를 만든다.

원본 모델·재질·Collider·Transform·Player·Animator·게임 C#은 보존했다.
새 ZF_*.asset 메시와 .meta, 이를 참조하는 14개 씬을 함께 관리해야 한다.
추가 메시의 Unity 텍스트 에셋 용량은 약 2.3GiB다.
원본 씬 백업은 C:/Users/503-26/Documents/Codex/Backups/AfterSeconds_ZFighting_20261111/.

변경 기록: V0.01 전체 씬 조사·시각 메시 수정·보존 검증 기록. 송예찬.
