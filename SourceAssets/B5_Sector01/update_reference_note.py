from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[2];p=R/'Docs/도면/Decision/원형공동/README.md';text=p.read_text('utf-8')
archive=R/'Docs/도면/Old/원형공동/자료안내/V0.06/README.md';archive.parent.mkdir(parents=True,exist_ok=True)
if not archive.exists():shutil.copy2(p,archive)
text=text.replace('원형 공동 제작 자료 V0.06','원형 공동 제작 자료 V0.07',1)
head,body=text.split('\n',1)
note='2026-11-06 최신 제작: 사용자 확인에 따라 새 전체 조감도는 참고용으로 사용한다. B5 C01의 생활 가구는 포드 안, 관찰·진료·보급은 바깥에 둔 현재 Unity 배치를 유지한다. [1섹터 검수](../../../검수/2026-11-06_B5_Sector01/검수결과.md)와 [실제 배치](../../../검수/2026-11-06_B5_Sector01/final_state.json)를 C01의 최신 기준으로 한다. 전체 배치 JSON V0.03·제작목록 V0.03·조감도 V0.01은 그대로 보존하며, C01의 종전 가구 좌표보다 위 사용자 확인과 실제 배치를 우선한다. [섹터도 V0.02](B5_섹터/B5_섹터구분도.png)는 1/14단위 레벨·아트 검수 완료, 다음 T01을 표시한다. 아래 제작 시작 안내는 이전 이력이다.'
p.write_text(head+'\n\n'+note+'\n'+body,encoding='utf-8')
print('Decision reference note V0.07 saved; geometry and workbook unchanged')
