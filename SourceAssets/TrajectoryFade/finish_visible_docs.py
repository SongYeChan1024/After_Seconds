from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[2]
out=root/'Docs/Review/2026-11-17_TrajectoryFade'
assert 'TOTAL passed=34, failed=0' in (out/'validation_visible_contact.txt').read_text(encoding='utf-8-sig')
p=out/'Review.md';s=p.read_text(encoding='utf-8-sig').replace('페이드 V0.01','페이드 V0.02',1)
start=s.index('표시선은 일반');end=s.index('\n\n| 항목',start)
s=s[:start]+'표시선은 일반2.5m·확대4m에서 끝나고, 불투명도30%·끝0% 페이드를 유지한다. **사용자 정정에 따라 선이 실제 표면까지 닿는 경우에만 원을 표시한다.** 선이 중간에서 끊기면 그 너머 바닥/벽의 원도 숨긴다. 물체 반지름 때문에 중심이 먼저 멈추는 거리뿐 아니라 실제 접촉면까지 연결하는 길이도 표시 한도에 포함한다.'+s[end:]
s=s.replace('| 접촉 원 |전체선 끝의 접촉 표면|표시 길이와 독립된 첫 접촉 표면|','| 접촉 원 |짧은 선 너머에도 표시|표시선이 닿는 표면에만 표시|')
s=s.replace('짧은 선의 마지막 점을 먼 접촉점으로 연결하지 않도록, 표시용 끝점과 물리 예측의 끝점을 분리했다.', '범위 밖 접촉은 내부 예측값에만 남고 원을 표시하지 않는다. 범위 안이면 선의 끝점을 접촉면에 연결한다.')
start=s.index('실제 Play29/29');end=s.index('\n\n첫 검사',start)
s=s[:start]+'최신 실제 Play34/34 통과. 선 너머 원 숨김, 가까운 B5 바닥/벽 접촉 원, 확대하면 닿고 확대 해제하면 닿지 않는 같은 벽, 거리/시간 한도, 막힘·취소·방출을 확인했다. 실제 첫 충돌 오차0.0456m, 컴파일/콘솔 오류·경고0. [최신 원시 결과](validation_visible_contact.txt) · [최종 상태](audit.json) · [화면 비교](review.html). 이전29개 결과는 정정 전 기록이다.'+s[end:]
s=s.replace('Show Full Trajectory를 켜면 전체선으로 바뀌며, 꺼도 첫 접촉 원의 예측은 계속한다.', 'Show Full Trajectory를 켜면 전체선으로 바뀐다. 원의 표시 조건은 언제나 선이 실제 표면까지 닿는지 여부다.')
s+='\nV0.02 — 사용자 정정: 선이 닿지 않으면 원도 숨김. 범위 내 접촉점 연결·확대 전환 포함34/34 재검수. 송예찬.\n'
p.write_text(s,encoding='utf-8')
p=root/'SourceAssets/TrajectoryFade/README.md';s=p.read_text(encoding='utf-8-sig').replace('보수 V0.01','보수 V0.02',1)
s=s.replace('미리보기 원은 표시선과 독립적으로 실제 표면을 찾았을 때만 나온다.', '현재 미리보기 원은 표시선이 실제 접촉면까지 닿을 때만 나온다. 선 너머 원은 숨긴다.')
s+='\n최신 검수는 `ValidateVisibleContact.cs`다(34/34). `Validate.cs`의29개 검사는 선 너머 원이 있던 이전 단계다. `prepare_visible_validation.py`는 이전 검사에서 최신 조건을 생성하며, 현재 검수·화면·문서는 V0.02를 따른다.\n\nV0.02 — 표시선 범위에 접촉 원 종속·최신 검수 연결. 송예찬.\n'
p.write_text(s,encoding='utf-8')
p=root/'SourceAssets/TrajectoryFade/WriteReview.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace("TOTAL passed=29, failed=0' in (out/'validation.txt'", "TOTAL passed=34, failed=0' in (out/'validation_visible_contact.txt'")
start=s.index('cards=');end=s.index('\nbody=',start)
s=s[:start]+"cards=[('b5_underhand.png','이전 ·선 너머 원 표시'),('visible_b5_underhand.png','현재 ·선이 닿지 않아 원 없음'),('visible_b5_near_floor.png','가까운 바닥 ·선이 닿을 때 원 표시'),('visible_zoom_reaches_wall.png','확대 후 벽에 닿으면 원 표시'),('visible_near_wall.png','가까운 벽 ·접촉면 연결'),('visible_no_hit.png','빈 공간 ·원 없음')]"+s[end:]
s=s.replace('페이드 V0.01','페이드 V0.02').replace('첫 예상 접촉 원은 선 표시 길이와 독립적입니다.','원은 표시선이 실제 표면까지 닿을 때만 나옵니다. 선 너머에는 원을 표시하지 않습니다.').replace('검수29/29','검수34/34')
start=s.index('summary=');end=s.index('\nfor name',start)
summary='2026-11-17 최신 정정: 사용자 지시로 접촉 원도 표시선이 닿는 범위에만 표시한다. 선이 중간에 끊기면 먼 바닥/벽의 원도 숨긴다. 일반2.5m·확대4m·30%와 끝0% 페이드는 유지. 표면까지 연결할 길이 검사·선 끝 접촉면 연결, 실제 Play34/34·컴파일/콘솔 오류·경고0. [검수 V0.02](Docs/Review/2026-11-17_TrajectoryFade/Review.md) · [화면](Docs/Review/2026-11-17_TrajectoryFade/review.html). B5 변경 없는 편집·로컬 저장, 이번 커밋/push 없음. 아래 V1.21의 선 너머 원 허용은 이전 해석이며 복원하지 않는다. 작성자 송예찬.'
s=s[:start]+'summary='+repr(summary)+s[end:]
s=s.replace("first.replace('V1.20','V1.21')", "first.replace('V1.21','V1.22')")
p.write_text(s,encoding='utf-8');runpy.run_path(str(p))
p=root/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8-sig')
s=s.replace('V0.91의29개 검사는 원을 선 너머에도 표시하던 이전 단계이며 현행 원 표시 조건의 검수가 아니다.', '현행 조건은 실제 Play34/34·컴파일/콘솔 오류·경고0으로 재검수했다. V0.91의29개 검사는 원을 선 너머에도 표시하던 이전 단계다.')
p.write_text(s,encoding='utf-8')
print('Updated visible-contact documents and comparison.')
