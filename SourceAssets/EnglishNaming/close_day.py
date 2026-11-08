from pathlib import Path

R=Path(__file__).resolve().parents[2]
note='2026-11-08 저녁 작업 마감: B5 천장·복도 조명과 B4 전체13돔·3코어·22복도 및 실험 운용 설비를 로컬 저장했다. B5는 생활·격리/기본 관리, B4는 정밀 측정·발달·강화 연구층이다. 사용자 요청으로 한글 이름1,778개와 특수기호가 있던 복도 이름21개, 총1,799개를 간결한 영어로 변경했다. 현재 루트 `B4_ResearchFloor_V0.03`, 설비 그룹 `B4_ExperimentEquipment`. 전체13씬 이름 ASCII, 직렬화22,473개 비교에서 이름 외 차이0, 대표 B4/B5 실제 Play 새 게임 경고/오류0. **다음은 B4 사용자 전체 검수 → 지적 설비/배치 보수 → 전체 조명·성능 마감**이다. 안내선은 복도 전용이며 화면·장비는 정적이다. 11월8일 저녁 데일리로그/일일개발일지를 블로그 저장소에 작성했다. **이번 저녁 변경과 새 글은 로컬 상태이며 커밋·push·게시 미실시**다. 새벽에 게시된 B5 글과 구분한다. 작성자 송예찬.'
for rel,old,new,link in [
 ('Docs/이어하기_2026-11-06.md','V0.48','V0.49','WorkClose_2026-11-08_Evening.md'),
 ('Docs/회사_작업목록_2026-11-06.md','V0.46','V0.47','WorkClose_2026-11-08_Evening.md'),
 ('Unity/README.md','V0.49','V0.50','../Docs/WorkClose_2026-11-08_Evening.md')]:
 p=R/rel;s=p.read_text(encoding='utf8');title,body=s.split('\n',1);assert old in title
 p.write_text(title.replace(old,new)+'\n\n'+note+f' [저녁 마감·다음 작업]({link}).\n\n이전 단계 기록:\n'+body.lstrip()+f'\n- {new} (2026-11-08): 저녁 마감, 영문 이름과 블로그 로컬 원고·다음 검수 순서 반영. 송예찬.\n',encoding='utf8')
for rel in ['AGENTS.md','CLAUDE.md','Docs/AfterSeconds_메인기획서.md']:
 p=R/rel;s=p.read_text(encoding='utf8')
 old='기존 한글 하이라키1,778개를 네이티브 편집으로 변경하며 위치·재질·충돌·직렬화 참조는 보존한다.'
 new='한글 이름1,778개와 특수기호가 있던 복도 이름21개를 네이티브 편집으로 변경 완료했다. 전체13씬 이름은 ASCII이며 위치·재질·충돌·직렬화 참조가 보존됐다. 이후 새 제작에도 영어 이름을 적용한다.'
 assert old in s;s=s.replace(old,new,1)
 link='Docs/WorkClose_2026-11-08_Evening.md' if '/' not in rel else 'WorkClose_2026-11-08_Evening.md'
 title,body=s.split('\n',1)
 p.write_text(title+f'\n\n최신 마감: [2026-11-08 저녁 작업·블로그 원고]({link}). 이번 저녁 작업은 로컬 저장 상태이며 커밋·push·게시 미실시다. 아래의 이전 단계 이름보다 최신 영문 이름을 우선한다.\n'+body,encoding='utf8')
replacements={
 'B5_CeilingLighting':('새 씬 그룹과 등기구 이름에는 `구역코드_한글용도_번호`를 사용한다. 기존 전체 하이라키의 일괄 이름 변경은 이번 범위에 포함하지 않는다.','현재 씬의 그룹과 등기구 이름은 `C01_CeilingLights`, `C01_CeilingLight_01`처럼 간결한 영어로 통일했다. 이 폴더의 초기 생성 코드는 당시 제작 이력이므로 최신 씬에 그대로 재적용하지 않는다.'),
 'B4_Observation':('새 오브젝트 이름은 `B4_C01_한글용도_번호`로 읽기 쉽게 한다.','새 오브젝트 이름은 `B4_C01_ObservationBooth_01`처럼 구역·기능·번호를 간결한 영어로 작성한다.')}
for folder,(old,new) in replacements.items():
 p=R/'SourceAssets'/folder/'README.md';s=p.read_text(encoding='utf8');assert old in s;p.write_text(s.replace(old,new),encoding='utf8')
p=R/'Docs/개발_일지/README.md';s=p.read_text(encoding='utf8');assert s.startswith('# 개발 일지 V0.04')
s=s.replace('# 개발 일지 V0.04','# 개발 일지 V0.05',1)+'''

## 2026-11-08 저녁 B4·영문 이름 작업 — 로컬 원고

블로그 `Kasil_DevLog`의 `docs/2026-11-08-b4-experiment-operations` 브랜치에 작성했다. 아래 두 글은 아직 커밋·push·게시하지 않았다. 새벽의 기존 공개 글을 덮어쓰지 않는다.

- 데일리로그: `_posts/2026-11-08-daily-log-living-floor-and-experiment-floor.md` — 생활층/실험층 구분, 세 역할의 동선과 설비 접근, 영문 이름 규칙.
- 일일개발일지: `_posts/2026-11-08-after-seconds-b4-experiment-operations.md` — B5 조명, B4 전체 제작·실험 설비, 검수와 이름 전환. 스크린샷5장.
- [저녁 인수인계](../WorkClose_2026-11-08_Evening.md). 본문은 블로그에만 보관한다.

- V0.05 (2026-11-08): B4 작업과 영문 이름 변경을 담은 저녁 원고 위치·로컬 상태 기록. 송예찬.
'''
p.write_text(s,encoding='utf8')
print('Updated latest handoff, naming policy, source READMEs and blog index.')
