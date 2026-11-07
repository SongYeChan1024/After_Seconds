from pathlib import Path
R=Path(__file__).resolve().parents[2]
for name,old,new in [('AGENTS.md','V0.45','V0.46'),('CLAUDE.md','V0.45','V0.46'),('Docs/이어하기_2026-11-06.md','V0.29','V0.30'),('Docs/회사_작업목록_2026-11-06.md','V0.27','V0.28')]:
 p=R/name;raw=p.read_bytes();t=raw.decode('utf-8-sig').replace('\r\n','\n');first,rest=t.split('\n',1)
 if new in first:continue
 assert old in first
 prefix='' if name.startswith('Docs/') else 'Docs/'
 note=f'2026-11-07 재개 결정: 사용자가 실험동 타일·조명 확인(이전 목록1번)을 완료했다. **조명·색감의 최종 조정은 B5 전체 제작 후 일괄 진행**한다. 현재는2번 바닥 안내선·출입구 표식 제작이며, 이후 T01 → C02 순서를 유지한다. [이번 제작 원본]({"../" if name.startswith("Docs/") else ""}SourceAssets/C01_Wayfinding/README.md)을 따른다. 게임 C#·Animator는 사용자 직접 구현, 전체 아트 완료 판정0/34는 유지한다. 작성자 송예찬.'
 t=first.replace(old,new)+'\n\n'+note+'\n\n이전 단계 기록:\n'+rest.lstrip('\n')
 if name.endswith('회사_작업목록_2026-11-06.md'):
  t=t.replace('- [ ] C01 사용자 시야에서 최종 타일/조명 확인, 바닥 안내선·출입구 표식 마감.', '- [x] C01 사용자 시야에서 타일/조명 확인.\n- [ ] C01 바닥 안내선·출입구 표식 마감.\n- [ ] B5 전체 제작 후 조명·색감 최종 조정.')
 p.write_bytes(t.replace('\n','\r\n' if b'\r\n' in raw else '\n').encode('utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'))
p=R/'Docs/AfterSeconds_메인기획서.md';raw=p.read_bytes();t=raw.decode('utf-8-sig').replace('\r\n','\n');t=t.replace('— 메인 기획서 V0.34','— 메인 기획서 V0.35',1)
note='2026-11-07 사용자 결정: 실험동 타일·조명 시야 확인은 완료했다. B5를 구역별로 제작한 뒤 조명·색감의 최종 조정을 한 번에 진행한다. 이번 제작은 Decision 원형공동 설계의 R1 흰 이중선·S1 청록 선/사각·M1 황토 점선 규칙을 C01 바닥과 작은 출입 표식에 반영하는 범위다. T11 직원 접근을 기존 R1에 합류시키고 S1은 포드 북동쪽을 돌아 T03에 연결하며, M1은 점검함 전면 국소 표식만 둔다. 실제 경로 좌표는 SourceAssets/C01_Wayfinding/plan.json의 구현 가안이며 다른 공동 경로·게임 규칙은 바꾸지 않는다.'
first,rest=t.split('\n',1);t=first+'\n\n'+note+'\n'+rest
idx=t.index('\n',t.index('\n',t.index('| 버전',t.index('## 변경 기록')))+1)+1;t=t[:idx]+'| V0.35 | 2026-11-07 | 송예찬 | 실험동 확인 완료 및 B5 전체 제작 후 조명·색감 일괄 조정 결정. C01 업무 안내선과 소형 출입 표식 제작 범위·기존 Decision 코드 사용·국소 경로 가안 기록. 게임 규칙 유지. |\n'+t[idx:]
p.write_bytes(t.replace('\n','\r\n' if b'\r\n' in raw else '\n').encode('utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'))
print('Decision and handoff updated')
