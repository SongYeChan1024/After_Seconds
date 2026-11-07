from pathlib import Path
import re,json
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_TwoDomeGuidance'
read=lambda n:json.loads((D/n).read_text(encoding='utf-8'))
a=read('audit.json');p=read('probe.json');w=read('route_walk.json');f=read('file_preservation.json');s=read('final_state.json')
assert not any([a['protectedTransformChanges'],a['lightChanges'],a['degenerate'],a['downward'],a['missingMaterials'],p['blocked'],p['missingFloor'],f['missing'],f['unexpected'],s['dirty'],s['playing']])
assert len(w['routes'])==2 and all(t['passed'] for t in w['routes']) and a['triangles']==1630
note='2026-11-08 사용자 안내선 방식 확정: 각 돔에서 갈 수 있는 목적지를 기준으로 선을 연결한다. 지금은 C01 실험동과 C02 보안관제동만 대상으로 C01행 청록·C02행 파랑 두 선을 T01에 연결했다. 앞서 추가한 계단A/유틸리티동의 녹색·보라색 경로와 바닥 목적지 표기는 현재 씬에서 제외했으며, 해당 돔을 제작·연결할 때 추가한다. 바닥 색상 안내2곳·정적 감시 화면4장을 갱신했다. 통행674표본 막힘0·Controller왕복2/2, 선 여백21.67cm, 기존 Transform/Light187개와 대상 외 기존 파일3,988개 보존. 실험동 내부 R1 순환선·S1/M1 국소 작업 표기는 유지한다. 현재 제작 기준은 B5_TwoDomeGuidance이며 이전 네 색/여섯 경로 기록을 현재 상태로 적용하지 않는다. 다음은 T02/계단A 연결부 제작과 그에 따른 목적지 안내 확장이다. 최종 조명은 B5 전체 후, 게임 C#/Animator변경0·아트 판정0/34 유지. 로컬 저장, 이번 변경 커밋·push 미실시. 작성자 송예찬.'
for rel,version in [('AGENTS.md','V0.53'),('CLAUDE.md','V0.53'),('Docs/이어하기_2026-11-06.md','V0.37'),('Docs/회사_작업목록_2026-11-06.md','V0.35'),('Docs/AfterSeconds_메인기획서.md','V0.42')]:
    path=R/rel;t=path.read_text(encoding='utf-8')
    if note not in t:
        head,rest=t.split('\n',1);prefix='Docs/' if '/' not in rel else ''
        t=re.sub(r'V0\.\d+',version,head)+'\n\n'+note+f' [최신 검수]({prefix}검수/2026-11-08_B5_TwoDomeGuidance/검수결과.md).\n\n이전 단계 기록:\n'+rest.lstrip()
    if rel.endswith('메인기획서.md') and '| V0.42 |' not in t:
        assert '| V0.41 |' in t
        t=t.replace('| V0.41 |','| V0.42 | 2026-11-08 | 송예찬 | 각 돔의 도달 목적지별 안내 확정. 현재 C01/C02 두 선만 반영하고 다른 돔 안내는 해당 구역 제작 시 확장. |\n| V0.41 |',1)
    path.write_text(t,encoding='utf-8')
for rel,version,target in [('SourceAssets/B5_DestinationColors/README.md','V0.02','../B5_TwoDomeGuidance/README.md'),('SourceAssets/B5_WayfindingNetwork/README.md','V0.03','../B5_TwoDomeGuidance/README.md'),('Docs/도면/Decision/원형공동/B5_안내체계/README.md','V0.05','../../../../../SourceAssets/B5_TwoDomeGuidance/README.md')]:
    path=R/rel;t=path.read_text(encoding='utf-8');marker='2026-11-08 두 돔 안내만 적용'
    if marker not in t:
        head,rest=t.split('\n',1)
        t=re.sub(r'V0\.\d+',version,head)+f'\n\n{marker}: 사용자는 각 돔에서 갈 수 있는 목적지를 기준으로 안내하며 현재 C01/C02 사이의 두 선만 유지한다고 확정했다. [현재 제작 기준]({target})을 우선한다. 아래 네 색/여섯 경로 및 전체 용도별 노선안은 이전 기록이며 현재 씬에 그대로 재적용하지 않는다. 다른 돔이 제작·연결되면 해당 목적지 선을 추가한다. 작성자 송예찬.\n\n이전 단계 기록:\n'+rest.lstrip()
        if '## Revision History' in t:t+='\n| V0.05 | 2026-11-08 | 송예찬 | 도달 목적지별 안내 확정과 현재 C01/C02 두 선으로 범위 정리. |\n'
        path.write_text(t,encoding='utf-8')
print(json.dumps({'validated':True,'routes':len(w['routes']),'preserved':f['preservedFiles']},ensure_ascii=True))
