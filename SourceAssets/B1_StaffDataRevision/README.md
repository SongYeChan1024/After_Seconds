# B1 직원·연구 데이터 용도 보수 V0.01

작성자 송예찬 · 2026-11-11

사용자 정정의 B5/B4 실험체 구역·B4→B3 상행 경계와 B1 연구 데이터/직원 생활을 반영했다. C05는 후속 요청으로 8인 회의장이 됐다. [검수](../../Docs/Review/2026-11-11_B1_StaffData/Review.md)를 따른다.

현재 씬에 Apply/Conference/prepare/docs/conference_plan을 재실행하지 않는다. 이미 저장됐고 사용자 후속 편집을 덮어쓸 수 있다. 전체 B1_FullFloor 제작기도 재실행 금지다.

- before_layout.json / before_design_B1.json: 정정 전 배치·설계 이력. 현재 기준으로 복원하지 않는다.
- layout.json: 최종198배치. B1_FullFloor/layout.json과 Decision/B1_제작현황/as_built_layout.json에도 동일하게 저장.
- Apply.cs: 38배치 제거·57가구 복제·화면/빛 정정 및 회의장 확장 이력. 기존 보수 메시/LOD를 복제하고136개 잔여 배치 Transform 보존.
- conference_models.py: 회의 테이블/발표 화면 FBX2종 제작. 이전 공용 모델·meta를 덮어쓰지 않음. conference_plan.py는 초기4인 회의석을8인으로 바꾼 일회성 기록.
- Review/Play/ConferenceExport.cs, geometry.py: 외부 검수. Assets에 C# 추가하지 않음. geometry_scan/verified의 전체 결과는 회의장 확장 직전, C05 결과는 최종 확장 뒤. 두 결과를 함께 사용.
- run_play.py: 실제 입력/프레임/새 오류 검사, Play 종료·Run In Background 원상복구. 최종 C05 재검사 결과가 최신.
- finish.py: 검수 증거 확인 후 보고서/현재 배치도 생성 및 현행 문서 연결.

정상 운영의 실험체 출입 금지를 플레이어의 상행 불가로 바꾸지 않는다. 보안문·AI·층 전환·사용 가능한 발표 UI는 미구현. 다음은 사용자 C05 회의장 및 C01/N01 업무 공간 외형 확인. 커밋·push하지 않았다.
