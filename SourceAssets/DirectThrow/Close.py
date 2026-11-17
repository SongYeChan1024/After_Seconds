from pathlib import Path
root=Path(__file__).resolve().parents[2]
assert 'TOTAL passed=34, failed=0' in (root/'Docs/Review/2026-11-17_DirectThrow/validation.txt').read_text(encoding='utf-8-sig')
summary='2026-11-17 최신: 사용자 요청으로 E 선행 없이 좌클릭 누름→자동 준비/조준→해제 즉시 투척으로 바꿨다. R은 준비 전에도 선택, E는 취소만, 우클릭은 조준 중 취소/그 외 확대다. 취소와 입력 맵 해제는 발사보다 우선한다. 실제 PlayerInput34/34·컴파일/콘솔 오류·경고0. 속도·VARCO 동작·짧고 흐린 선·선이 닿을 때만 원 표시 유지. [최신 입력/검수](Docs/Review/2026-11-17_DirectThrow/Review.md). B5 변경 없는 편집·로컬 저장, 이번 커밋/push 없음. 이전 E 필수/좌클릭 사용 분기는 과거 규칙이며 복원하지 않는다. 미구현 총/손전등/문서 사용 입력은 기능 구현 시 정한다. 작성자 송예찬.'
for name in ('AGENTS.md','CLAUDE.md'):
    p=root/name;s=p.read_text(encoding='utf-8-sig');first,rest=s.split('\n',1)
    if summary not in s:p.write_text(first.replace('V1.22','V1.23')+'\n\n'+summary+'\n\n이전 단계 기록:\n'+rest,encoding='utf-8')
p=root/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8-sig')
s=s.replace('바인딩의 존재가 사격·획득·투척 기능의 구현을 뜻하지는 않는다.', '현재 좌클릭 직접 투척은 구현되어 있다. 사격·획득·물건 사용은 별도 후속 구현이며 바인딩의 존재만으로 구현 완료를 뜻하지 않는다.')
s=s.replace('기존 이동/시선·클립·속도·표시선/접촉 원은 유지한다.', '기존 이동/시선·클립·속도·표시선/접촉 원은 유지한다. 구현 후 실제 PlayerInput34/34·컴파일/콘솔 오류·경고0을 확인했다. [직접 투척 입력과 검수](Review/2026-11-17_DirectThrow/Review.md)를 따른다.',1)
p.write_text(s,encoding='utf-8')
print('Direct throw handoff updated.')
