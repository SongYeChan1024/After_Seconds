import re
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
assert (R/'Docs/Review/2026-11-10_B2_Operations/Review.md').exists()
note='2026-11-10 B2 운영 동선 재구성: 사용자 승인으로 **12공동 내부를186배치·부분 데크4개·공정 연결12개**로 다시 구성했다. C02 펌프 점검로, E02 필터 교체/모터 정비면, W03 입고→보관→수리→출고, C03/C04 건식 전기/관제, S01 진단 정비를 구분한다. C02·E01·E02·W02의 기존 상부7끝, 공동12·코어3·통로21은 유지한다. 기존 설비/데크 비활성 보존. 광원158개 유지·흰 직접광0, 베벨·LOD·정비대 겹침 보수·반사/가림 갱신. [최신 검수](Docs/Review/2026-11-10_B2_Operations/Review.md)와 [제작 원본](SourceAssets/B2_OperationsRebuild/README.md)을 우선한다. 하부 접근·상부 왕복34/34·기존 복층 통로4910표본/76왕복·실제 Play6경로 통과. **다음은 사용자 C02→E02→W03→E01/W02의 1인칭 구조·정비면·숨는 길 검수 후 지적 구역 보수**다. 정적 레벨이며 경비 AI/설비 기능은 미구현, 게임 코드/Player 씬/Animator 보존. 현재 씬과 과거 Apply를 혼용하지 않는다. 로컬 저장, 이번 커밋·push 미요청. 작성자 송예찬.'
for name in ['AGENTS.md','CLAUDE.md']:
 p=R/name;s=p.read_text(encoding='utf8');first,rest=s.split('\n',1)
 if 'B2 운영 동선 재구성:' in rest:continue
 m=re.search(r'V(\d+)\.(\d+)',first);v=f'V{int(m[1])}.{int(m[2])+1:02}' if m else 'V0.01'
 first=re.sub(r'V\d+\.\d+',v,first)
 p.write_text(first+'\n\n'+note+'\n\n이전 단계 기록:\n'+rest+f'\n- {v} (2026-11-10): B2 12공동 운영 동선과 부분 데크, 근접·보행 검수. 송예찬.\n',encoding='utf8')
D=R/'Docs/도면/Decision/원형공동'
p=D/'B2_운영동선_재설계/README.md';s=p.read_text(encoding='utf8')
s=s.replace('재설계 V0.01','재설계 V0.02',1)
s=s.replace('**💡 B2 기계층의 12개 공동을 사람이 점검하고 운영하는 작업장으로 재구성하는 제안이다.**','**사용자 승인 후 B2 기계층의 12개 공동에 운영 동선 재구성을 적용했다.**',1)
s=s.replace('최근 제작한 B2를 우선 대상으로 삼았으며, 아래 내부 배치와 동선은 Unity 적용 전 설계안이다.','현재 Unity 내부는 [검수 화면](../../../../Review/2026-11-10_B2_Operations/review.html)과 [실배치 데이터](as_built_operations.json)를 따른다. 아래 기존 그림은 제작 방향을 정했던 초기 설계도이며, 최종 계단 참·난간 개구·탱크 위치는 통행 검수에 맞춰 조정했다.',1)
s=s.replace('내부 설비 위치는 새 제안이며 기존 실배치의 측량도가 아니다.','아래 초기 그림과 현행 실배치를 구분하며, 현재 치수·위치는 `as_built_operations.json`을 우선한다.',1)
s=s.replace('높이별 구조의 충돌·계단 단면·최종 이동 가능 판정은 Unity에 옮긴 뒤 검수한다.','높이별 충돌·계단 단면·이동 검수 결과는 [Unity 검수 기록](../../../../Review/2026-11-10_B2_Operations/Review.md)에 정리했다.',1)
s+='\n| V0.02 | 2026-11-10 | 송예찬 | 사용자 승인 후 12공동 Unity 적용·부분 데크4·공정 연결·186배치·근접/보행 검수. 초기 제안 그림과 현행 실배치 참조 구분. |\n';p.write_text(s,encoding='utf8')
p=D/'B2_배관통로/README.md';s=p.read_text(encoding='utf8');first,rest=s.split('\n',1);first=re.sub(r'V(\d+)\.(\d+)',lambda m:f'V{int(m[1])}.{int(m[2])+1:02}',first)
p.write_text(first+'\n\n2026-11-10 내부 배치 최신: [운영 동선 실배치](../B2_운영동선_재설계/as_built_operations.json)와 [Unity 검수](../../../../Review/2026-11-10_B2_Operations/Review.md)를 우선한다. 공동12·코어3·통로21 및 상부7끝은 유지했고 내부 설비186배치와 부분 데크4개를 재구성했다. 아래 원형 데크/97개 증설 설명은 이전 제작 이력이다. 작성자 송예찬.\n'+rest+'\n변경 기록: 2026-11-10 운영 동선 재구성의 최신 실배치 참조 추가. 송예찬.\n',encoding='utf8')
print('Context updated')
