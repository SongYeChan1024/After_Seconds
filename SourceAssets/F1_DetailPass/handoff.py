from pathlib import Path
R=Path(__file__).resolve().parents[2]
body='2026-11-13 최신 근접 디테일: 벽14구역의 금속판 표면·창/하단 마감, 승강기11배치의 기계/카/문 부품, 줄기120개·잎5,554장의 벽 아이비, 내부 프랍24종·49배치를 보강했다. 기존1,778Transform 변경0, 부품296추가→2,074, Collider165유지. 통행75/75·실제Play3시점696프레임·누락참조/셰이더/콘솔 오류0, 보호13,131파일 해시 일치. 창 비율·지붕·황야·다른층과 기존 가동부 피벗 유지. 게임 운행/문 제어는 사용자가 작성한다. 저장된 Level_1F_Factory가 최신이며 승강기 선택, 로컬 저장·커밋/push 미실시. 이전 전체 제작기와 첫 Apply를 일괄 재실행하지 않는다. 작성자 송예찬. '
for file,old,new,prefix in [('AGENTS.md','V1.10','V1.11',''),('CLAUDE.md','V1.10','V1.11',''),('Docs/이어하기_2026-11-12.md','V0.09','V0.10','../')]:
 p=R/file;text=p.read_text(encoding='utf-8-sig');title,rest=text.split('\n',1);assert old in title
 review=('Review/' if prefix else 'Docs/Review/')+'2026-11-13_1F_DetailPass/'
 intro=body+f'[최신 검수]({review}Review.md) · [전후 화면]({review}review.html) · [제작/부품 연결]({prefix}SourceAssets/F1_DetailPass/README.md).'
 text=title.replace(old,new)+'\n\n'+intro+'\n\n이전 단계 기록:\n'+rest
 text+=f'\n- {new} (2026-11-13): 벽·승강기·아이비·프랍 근접 디테일과 보존/통행/Play 검수 기록. 송예찬.\n'
 p.write_text(text,encoding='utf8')
print('HANDOFF_UPDATED')
