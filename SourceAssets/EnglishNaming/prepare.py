from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';assert not (H/'baseline.json').exists()
b={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in ['Assets','Packages','ProjectSettings'] for p in (P/base).rglob('*') if p.is_file() and not p.relative_to(P).as_posix().startswith('Assets/Temp/')}
(H/'baseline.json').write_text(json.dumps(b,indent=2),encoding='utf8')
note='2026-11-08 이름 규칙 변경: 사용자 요청에 따라 Unity 오브젝트·에셋·폴더 이름은 간결한 영어(ASCII)로 통일한다. 구역 코드는 유지하고 `B4_W01_ObservationBooth_01`, `C01_CeilingLight_01`처럼 용도와 번호를 붙인다. 기존 한글 하이라키1,778개를 네이티브 편집으로 변경하며 위치·재질·충돌·직렬화 참조는 보존한다. 문서 본문과 사용자 대화는 한국어다. 작성자 송예찬.'
for rel,old,new in [('AGENTS.md','V0.64','V0.65'),('CLAUDE.md','V0.64','V0.65'),('Docs/AfterSeconds_메인기획서.md','V0.55','V0.56')]:
 p=R/rel;s=p.read_text(encoding='utf8');title,body=s.split('\n',1);assert old in title
 p.write_text(title.replace(old,new)+'\n\n'+note+'\n\n이전 단계 기록:\n'+body.lstrip()+f'\n- {new} (2026-11-08): 프로젝트 내부 이름의 간결한 영어 표기 규칙과 기존 이름 마이그레이션. 송예찬.\n',encoding='utf8')
print('Protected files',len(b))
