# B4 실험 시설·근접 디테일 제작 V0.01

작성자 송예찬 · 2026-11-09

현재 씬의 기존 50개 프랍 MeshFilter/재질을 전용 모델 16종으로 교체했다. E02 연구 책상 두 곳·중앙 섬·준비대 외에 C01/C03/C04/W01/W02/W03/S01의 주요 측정·시험기와 공용 계측 카트/전극대/기록물을 보강했다. `changes.json`이 정확한 대상과 비활성 보존 목록이다. 원래 에셋/메타와 Transform을 보존했다.

1인칭에서 보는 인쇄 문자는 실제 제목·표·그래프·메모를 사용한다. 보고서/화면 수치는 환경 아트 예시이며 확정 게임 규칙이 아니다. 게임 내부 스크립트는 작성하지 않았다. 이 폴더의 C#은 Unity 네이티브 편집·검수 도구이며 Assets에 반입하지 않는다.

제작 순서:

1. `textures.py`: 기록지 6종, 계측 LCD 8종, 기술 라벨 아틀라스. Python/Pillow로 직접 조판했다.
2. `build.py` / `common.py`: Blender의 베벨·가중 노멀, 단자·체결부·슬라이드·보호 커버·센서·패드·정리된 케이블·회수 소품. `LB_*.blend`는 조립 파트가 살아 있는 원본이다.
3. `refine_electrodes.py`: 집게, 접힌 포장, 포장 인쇄·회수 단자와 헤드박스 연결. build 직후에만 한 번 실행한다.
4. `refine_legends.py`: 기록대 키 인쇄면을 위로 향하게 보수한다. 그 뒤 `refine_desk_cables.py`로 책상 위의 수평 접선과 후면의 둥근 서비스 루프를 적용한다.
5. `aim_sensors.py`: 피험체·광학 통과 축·교정 치구를 향하도록 센서를 조정한다.
6. `plan.py`: 원본 백업 조사에서 교체 목록을 생성한다. 현재 Walk.cs의 발판 높이 대응 및 Targeted 검사는 후속 보수이므로 plan.py 재생성 시 덮어쓰지 않는다.
7. Unity `LabApply.Import` → `LabApply.Run`: 네이티브 임포트·재질 remap·씬 저장. 새 모델은 `05.Model/Props/B4`, 이미지와 재질은 해당 Textures/Materials다. 반복 실행은 사용자 수동 편집을 확인한 뒤 필요한 대상에만 한다.
8. `LabWalk.Walk/Targeted`, `LabVerify.Run`, `LabIdentityCapture.After/Details`, `LabPlay`: 통행·상태 보존·실제 Play·전후/근접 화면을 검수한다.
9. `audit.py` → `report.py`: 기존 파일 해시, 보고서·갤러리·provenance·최신 안내를 남긴다.

`LC_*.fbx` 14종은 베벨 전 실제 파트 기반 충돌 전용 메시다. 인쇄면·가는 선·미세 체결부는 충돌에서 제외하고, 본체·프레임·발판·가림판을 남긴다. 큰 박스 하나로 빈 공간을 막지 않는다. 정적 설비용 비볼록 MeshCollider이며 향후 동적 Rigidbody를 붙일 때 재검토한다. 기록대/작은 클립보드는 원래 충돌을 유지했다.

`before.unity`와 `state_before.json`, `props_before.json`, `protected_before.json`은 작업 전 기준이다. 다시 조사해서 덮어쓰지 않는다. `finish_record.py`는 첫 제작의 마지막 모델 재개용 기록이며 일반 제작 단계가 아니다. 이전 전체 제작기, B4_LayoutPolish 전체 Apply, B4_DeskAndCollision 전체 Apply를 현재 씬에 다시 실행하지 않는다.

최종 검수·이미지: [Review.md](../../Docs/Review/2026-11-09_B4_LabIdentity/Review.md), [review.html](../../Docs/Review/2026-11-09_B4_LabIdentity/review.html). 저장된 B4 편집 모드이며 E03 전극 준비대를 선택했다. 사용자 근접 검수와 전체 층 성능/최종 조명 마감은 후속이다. 커밋·push 미실시.
