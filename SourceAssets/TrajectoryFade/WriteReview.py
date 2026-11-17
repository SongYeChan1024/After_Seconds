from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'Docs/Review/2026-11-17_TrajectoryFade'
assert 'TOTAL passed=34, failed=0' in (out/'validation_visible_contact.txt').read_text(encoding='utf-8-sig')
cards=[('b5_underhand.png','이전 ·선 너머 원 표시'),('visible_b5_underhand.png','현재 ·선이 닿지 않아 원 없음'),('visible_b5_near_floor.png','가까운 바닥 ·선이 닿을 때 원 표시'),('visible_zoom_reaches_wall.png','확대 후 벽에 닿으면 원 표시'),('visible_near_wall.png','가까운 벽 ·접촉면 연결'),('visible_no_hit.png','빈 공간 ·원 없음')]
body=''.join(f'<figure><img src="{path}" alt="{label}"><figcaption>{label}</figcaption></figure>' for path,label in cards)
(out/'review.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>투척선 거리 제한과 페이드 V0.02</title><style>body{background:#10171e;color:#e4edf4;margin:0;font:16px/1.6 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:28px}h1{font-size:28px}p{color:#bcd0da;max-width:1000px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:18px}figure{margin:0;background:#1d2934;border-radius:8px;overflow:hidden}img{display:block;width:100%}figcaption{padding:12px 16px}@media(max-width:500px){main{padding:15px}.grid{grid-template-columns:1fr}}a{color:#9bd5e8}</style><main><h1>짧고 흐린 투척선 ·충돌면에만 원 표시</h1><p>2026-11-17 · 송예찬. 선은 일반2.5m·확대4m, 불투명도30%, 끝으로 갈수록0%까지 사라집니다. 원은 표시선이 실제 표면까지 닿을 때만 나옵니다. 선 너머에는 원을 표시하지 않습니다. 실제 투척 속도·위/아래 동작은 유지했습니다. <a href="Review.md">검수34/34와 설정 안내</a></p><div class="grid">'''+body+'</div></main></html>',encoding='utf-8')
summary='2026-11-17 최신 정정: 사용자 지시로 접촉 원도 표시선이 닿는 범위에만 표시한다. 선이 중간에 끊기면 먼 바닥/벽의 원도 숨긴다. 일반2.5m·확대4m·30%와 끝0% 페이드는 유지. 표면까지 연결할 길이 검사·선 끝 접촉면 연결, 실제 Play34/34·컴파일/콘솔 오류·경고0. [검수 V0.02](Docs/Review/2026-11-17_TrajectoryFade/Review.md) · [화면](Docs/Review/2026-11-17_TrajectoryFade/review.html). B5 변경 없는 편집·로컬 저장, 이번 커밋/push 없음. 아래 V1.21의 선 너머 원 허용은 이전 해석이며 복원하지 않는다. 작성자 송예찬.'
for name in ('AGENTS.md','CLAUDE.md'):
    p=root/name;s=p.read_text(encoding='utf-8-sig');first,rest=s.split('\n',1)
    if summary not in s:p.write_text(first.replace('V1.21','V1.22')+'\n\n'+summary+'\n\n이전 단계 기록:\n'+rest,encoding='utf-8')
p=root/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8-sig')
s=s.replace('가까운 충돌·표시 거리 밖 충돌·공중/시간 한도·예측 거리 한도를 각각 확인한다. 아래 전체선 기록은 이전 단계다.', '가까운 충돌·표시 거리 밖 충돌·빈 공간/시간 한도·예측 거리 한도 등 실제 Play29/29를 통과했다. 컴파일/콘솔 오류·경고0, B5 편집 상태로 복원했다. [검수와 조절값](Review/2026-11-17_TrajectoryFade/Review.md)을 따른다. 아래 전체선 기록은 이전 단계다.')
p.write_text(s,encoding='utf-8')
assert all((out/p).exists() for p,label in cards)
print('Review images and handoff written.')
