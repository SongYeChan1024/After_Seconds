from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
if (H/'baseline.json').exists():raise SystemExit('Baseline exists')
(H/'baseline.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8').replace('메인 기획서 V0.38','메인 기획서 V0.39',1);head,tail=s.split('\n',1)
note='2026-11-08 C02 보안관제동 제작 시작: 사용자 T01 외형 확인 후 C02 본체를 요청했다. 기존 돔/출입3곳을 기준으로 북측 관제석2곳·다중 감시 화면, 전산/녹화/UPS, 교대 무전/장비/기록 구역을 제작한다. 문 접합·건축 마감·배선과 바닥 목적지 표기를 함께 검수한다. 화면은 정적, Light 설정과 게임 코드 보존, 전체 B5 후 조명 조정 방침 유지. SourceAssets/C02_Security/README.md를 따른다. 작성자 송예찬.'
s=head+'\n\n'+note+'\n'+tail
key='| V0.38 |';i=s.index(key);s=s[:i]+'| V0.39 | 2026-11-08 | 송예찬 | T01 사용자 확인 및 C02 관제동 본체 제작 범위·관제/교대 역할·통행/조명 보존 기준. |\n'+s[i:];p.write_text(s,encoding='utf-8')
print('C02 asset baseline and design note saved')
