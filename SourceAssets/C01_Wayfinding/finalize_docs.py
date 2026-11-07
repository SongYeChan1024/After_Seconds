"""이번 제작의 완료 상태와 인수인계를 기록한다. 작성자 송예찬."""
from pathlib import Path
import json

R = Path(__file__).resolve().parents[2]
for rel in ['AGENTS.md', 'CLAUDE.md', 'Docs/이어하기_2026-11-06.md', 'Docs/회사_작업목록_2026-11-06.md']:
    p = R / rel
    s = p.read_text(encoding='utf-8')
    start = s.index('2026-11-07 재개 결정:')
    end = s.index('\n\n', start)
    prefix = 'Docs/' if '/' not in rel else ''
    source = '' if '/' not in rel else '../'
    s = s[:start] + (
        '2026-11-07 재개 작업 완료: 사용자가 실험동 타일·조명 확인(이전 목록 1번)을 완료했다. '
        '**조명·색감의 최종 조정은 B5 전체 제작 후 일괄 진행**한다. '
        '2번 바닥 안내선·출입 표식은 R1 흰 이중선, S1 청록 선/사각, M1 점검함 앞 국소 점선, 바닥 코드 5곳·출입 명판 3곳으로 반영했다. '
        '경로 358표본 막힘 0·복도 왕복 6/6·Play 두 구간 실제 입력 이동을 확인했다. '
        '기존 프랍 Transform·187 Light·대상 씬 외 기존 에셋을 보존했다. '
        f'[최신 검수]({prefix}검수/2026-11-07_C01_Wayfinding/검수결과.md)와 '
        f'[제작 원본]({source}SourceAssets/C01_Wayfinding/README.md)을 따른다. '
        '**다음 제작은 T01 복도 세부 마감 → C02**다. '
        '이번 변경은 로컬 저장, 커밋·push 미실시. 게임 C#·Animator는 사용자 직접 구현하며 전체 아트 최종 판정 0/34는 유지한다. 작성자 송예찬.'
    ) + s[end:]
    if rel.endswith('회사_작업목록_2026-11-06.md'):
        s = s.replace('- [ ] C01 바닥 안내선·출입구 표식 마감.', '- [x] C01 바닥 안내선·출입구 표식 제작 및 통행·Play 검수.\n- [ ] T01 복도 배선·단자·문 접합부·표면 사용 흔적 세부 마감 후 C02 제작.')
        s = s.replace('프랍37종·30작업대·문3세트·타일·조명 보수 / 최종 시야 검수·안내선 남음', '프랍37종·30작업대·문3세트·타일 확인 완료 / 안내선·출입 표식 제작·검수 완료 / B5 전체 후 광원·색감 최종 조정')
    p.write_text(s, encoding='utf-8')

p = R / 'Docs/AfterSeconds_메인기획서.md'
s = p.read_text(encoding='utf-8')
s = s.replace('실제 경로 좌표는 SourceAssets/C01_Wayfinding/plan.json의 구현 가안이며 다른 공동 경로·게임 규칙은 바꾸지 않는다.', '실제 경로 좌표는 SourceAssets/C01_Wayfinding/plan.json에 보관한 현 배치용 제작 경로이며 다른 공동 경로·게임 규칙은 바꾸지 않는다. 2026-11-07 C01 안내선·바닥 코드 5곳·출입 명판 3곳 반영과 통행·Play 검수를 완료했다. 전체 조명·색감 최종 조정은 보류한다.')
s = s.replace('안내선 팔레트는 아직 미정이다.', '현재 Decision 설계의 R1 흰 이중선(#DEE6E9), S1 청록 단선·사각(#5E9C9A), M1 황토 점선(#BC9B5A)을 C01에 적용했다. 다른 공동·층의 실제 경로 좌표는 해당 구역 제작 때 검수한다.')
s = s.replace('기존 Decision 코드 사용·국소 경로 가안 기록. 게임 규칙 유지.', '기존 Decision 코드 사용·국소 경로 제작 및 검수 완료 기록. 게임 규칙 유지.')
p.write_text(s, encoding='utf-8')

out = R / 'Docs/검수/2026-11-07_C01_Wayfinding'
p = out / 'preservation.json'
j = json.loads(p.read_text(encoding='utf-8'))
j['afterPlaySceneDirtyBeforeRestore'] = j.pop('dirty')
a = json.loads((out/'geometry_audit.json').read_text(encoding='utf-8'))
j['finalSceneDirty'] = a['dirty']
j['finalPlaying'] = a['playing']
j['runInBackgroundRestored'] = not a['runInBackground']
p.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding='utf-8')
print('Completed documents and final restoration state recorded.')
