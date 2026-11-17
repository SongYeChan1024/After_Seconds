from pathlib import Path
import json, hashlib

root = Path(__file__).resolve().parents[2]
review = root / 'Docs/Review/2026-11-17_UnderhandRoll'
assert 'TOTAL passed=29, failed=0' in (review / 'validation.txt').read_text(encoding='utf-8-sig')
backup = Path('C:/Users/503-26/AppData/Local/Temp/AfterSeconds_UnderhandRoll_20261117_161400')
protected = json.loads((backup / 'protected.json').read_text(encoding='utf-8-sig'))
changed = [x['Path'] for x in protected if hashlib.sha256((root / x['Path']).read_bytes()).hexdigest().upper() != x['Hash']]
assert len(changed) == 4
summary = {'protected': len(protected), 'unchanged': len(protected)-len(changed), 'changed': changed}
(review / 'preservation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
latest = '2026-11-17 최신: 사용자 정정으로 아래 투척을 낮게 밀어 바닥에서 굴리는 형태로 보수했다. 아래4.5m/s·-12도·상향 제한, 전진 회전/감쇠와 전용 마찰 재질을 적용하고 손의 앞·아래 후속 동작 및 자기 투척물로 양팔이 순간 숨는 현상을 수정했다. 실제 입력/물리29/29, 평지 접촉 후2.568m·약7회 회전, 접촉 예측 오차4.38cm. 위 투척12m/s·8도·VARCO와 좌클릭 직접 투척·짧고 흐린 선/접촉 원 규칙 유지. 컴파일/게임 예외0, Unity AI Assistant 성능 로그 공유 잠금 오류1건은 별도 기록. 보호140개 중 대상 C#4개 외136개와 .meta 보존. B5 변경 없는 편집 상태·설정 복원·로컬 저장, 이번 커밋/push 없음. [최신 구현과 검수](Docs/Review/2026-11-17_UnderhandRoll/Review.md). 아래35도·6m/s는 이전 단계이므로 복원하지 않는다. 작성자 송예찬.'
for name in ['AGENTS.md','CLAUDE.md']:
    path = root / name
    body = path.read_text(encoding='utf-8-sig')
    first, rest = body.split('\n', 1)
    assert 'V1.23' in first
    body = first.replace('V1.23','V1.24') + '\n\n' + latest + '\n\n이전 단계 기록:\n' + rest
    body += '\n- V1.24 (2026-11-17): 아래 투척 굴림·손 후속 동작과 자기 투척물 가림 보수, 실제 입력/물리29/29 및 보존 검수. 송예찬.\n'
    path.write_text(body, encoding='utf-8')
main = root / 'Docs/AfterSeconds_메인기획서.md'
body = main.read_text(encoding='utf-8-sig')
needle = '방출 직후 손을 미는 동안 자기 투척물이 손 가림 검사에 걸려 양팔이 사라지는 현상도 보수한다. 후속 동작 중 시각적인 손 가림 검사에서만 방금 방출한 물체를 제외한다. 벽/지형 가림, 실제 물리 충돌, 새 투척의 막힘 및 예측 검사는 그대로 적용한다.'
body = body.replace(needle, needle + '\n\n구현 후 실제 입력/물리29/29를 통과했다. 평지에서 첫 접촉 약0.48초, 접촉 뒤2.568m·7.01회 회전, 6초 후0.0249m/s로 감속했다. 접촉 예측 오차4.38cm, 손은 아래3.8cm·앞11.5cm 이동하며 사라지지 않는다. [최종 검수](Review/2026-11-17_UnderhandRoll/Review.md). 이 수치는 구체 시험값이며 전용 모션 캡처 클립이나 비구체 투척 지원 완료를 뜻하지 않는다.')
main.write_text(body, encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False))
