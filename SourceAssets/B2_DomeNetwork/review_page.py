"""Regenerate the Korean review page from a UTF-8 file, never a shell text pipe."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Docs/Review/2026-11-10_B2_DomeNetwork'
labels={'E01':'E01 급수 공동','E02':'E02 공조 공동','W02':'W02 예비 전력 공동','C01':'C01 원심분리 공동','W03':'W03 정비 공동','N01':'N01 환기 공동','C02':'C02 냉각 공동'}
page=['''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>B2 공동 밀도·상부 연결 V0.02</title>
<style>body{margin:36px auto;max-width:1500px;background:#11191f;color:#dfe8ed;font:17px/1.65 system-ui;padding:0 24px}h1{font-size:32px}h2{margin-top:42px;font-size:24px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{width:100%;height:auto;border:1px solid #37454d}figcaption{padding:8px;color:#afbec5}a{color:#72d6bb}.wide{max-width:1200px;margin:16px auto}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style>
</head><body><h1>B2 공동 설비와 상부 연결 V0.02</h1>
<p>추가 설비 97배치 · 신규 메자닌 3개 · C02 포함 4개 공동 · 6개 통로·7개 접속부 · 광원 158개 유지</p>
<p><a href="Review.md">검수 기록</a> · <a href="../../도면/Decision/원형공동/B2_배관통로/B2_공동상부연결.png">현재 도면</a></p>
<p>동일한 시점의 변경 전후 Unity 렌더입니다. 어두운 철색과 붉은 실물 조명을 유지했습니다.</p>''']
for code,label in labels.items():
    page.append(f'<h2>{label}</h2><div class="pair"><figure><img loading="lazy" src="before_{code}.png" alt="{label} 변경 전"><figcaption>변경 전</figcaption></figure><figure><img loading="lazy" src="after_{code}.png" alt="{label} 변경 후"><figcaption>변경 후</figcaption></figure></div>')
    if code in ['E01','E02','W02']:
        page.append(f'<figure class="wide"><img loading="lazy" src="after_{code}_upper.png" alt="{label} 상부 정비 데크"><figcaption>상부 정비 데크에서 본 설비와 연결 동선</figcaption></figure>')
page.append('''<h2>터널에서 E01로 들어오는 상부 연결부</h2><figure class="wide"><img src="after_E01_portal.png" alt="터널과 E01 상부의 연결부"><figcaption>터널에서는 앉아서, 공동 데크에 올라와서는 서서 이동합니다.</figcaption></figure>
<p>작성자 송예찬 · 2026-11-10 · 정적 레벨·외형 작업 · 설비 작동과 AI는 별도 구현</p></body></html>''')
result='\n'.join(page)
for target in re.findall(r'(?:href|src)="([^"]+)"',result):
    assert (OUT/target).is_file(),target
assert '\ufffd' not in result and '?' not in result
(OUT/'review.html').write_bytes(result.encode('utf-8'))
print('UTF-8 review page regenerated; all 20 local references exist.')
