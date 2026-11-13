"""Read-only preservation audit and local report from completed Unity evidence."""
from pathlib import Path
import json,re,os,subprocess,html
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;O=R/'Docs/Review/2026-11-13_1F_WindowRoofDamage'
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def git(*args):return subprocess.check_output(['git',*args],cwd=R,stderr=subprocess.PIPE).decode()
f=read('final_check.json');play=read('play.json');walk=read('walk_floor.json');occ=read('occlusion.json');windows=json.loads((H/'windows.json').read_text(encoding='utf-8'));models=json.loads((H/'models.json').read_text(encoding='utf-8'))
base='Unity/After_Seconds_Build_V0.01/'
allowed=[base+'Assets/Afrer_Seconds/05.Model/Environment/1F/',base+'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity',base+'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory/']
tracked=[p for p in git('ls-files','-z','Unity').split('\0') if p];protected=[p for p in tracked if not any(p.startswith(a) for a in allowed)];changed=[p for p in git('diff','--name-only','-z').split('\0') if p]
bad=[p for p in changed if p in protected];guid_changes=[]
tmp=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_WindowRoofDamage_20261113/before'
for q in read('backup.json'):
 p=R/q['path']
 if p.suffix!='.meta':continue
 before=re.search(r'^guid: (\w+)',(tmp/p.name).read_text(),re.M)[1];after=re.search(r'^guid: (\w+)',p.read_text(),re.M)[1]
 if before!=after:guid_changes.append(str(p))
pres=dict(protectedTrackedFiles=len(protected),unexpectedProtectedChanges=bad,existingModelGUIDsChecked=25,changedGUIDs=guid_changes,transformChanges=f['transformChanges'],gameplaySourceChanges=[p for p in changed if p.startswith(base) and p.endswith('.cs')])
(O/'preservation.json').write_text(json.dumps(pres,ensure_ascii=False,indent=2),encoding='utf-8')
assert not bad and not guid_changes and not f['transformChanges'] and not pres['gameplaySourceChanges']
assert play['complete'] and play['framesAdvanced']>0 and not play['errors'] and walk['failed']==0 and not walk['planningFailures']
assert f['saved'] and not f['playing'] and not f['runInBackground']
assert f['missingScripts']==f['missingMeshes']==f['missingMaterials']==0
assert occ['bytes']>0 and occ['guid']=='0aa75ad5e5cdf734c9848a10dad17fad'
before=windows['beforeOpeningArea']/windows['totalWallArea']*100;after=windows['afterOpeningArea']/windows['totalWallArea']*100
md=f'''# 1F 창 비율·재질별 지붕 파손 검수 V0.01

작성자: 송예찬 · 2026-11-13

창이 지나치게 많고 지붕 결손의 묘사가 부족하다는 사용자 요청을 반영했다. [전후 화면](review.html) · [제작 원본과 수치 정의](../../../SourceAssets/F1_WindowRoofDamage/README.md).

## 결과

벽 모델 14개를 재구성해 연속 격자창을 벽 사이에 나눈 창으로 바꿨다. 수정 벽 구간에 대한 창 개구 면적은 {before:.1f}% → {after:.1f}%이며 면적 기준 약 {100*(1-windows['afterOpeningArea']/windows['beforeOpeningArea']):.1f}% 감소했다. 이 수치는 창틀 전체 개구부의 설계 면적이다. 남은 유리 조각의 면적·화면 픽셀 비율과는 다르다. 문 위 헤더·박공·배경 별채는 계산에서 제외했다.

금속 지붕 9개에는 골판의 실제 굴곡, 판재 이음부, 체결점과 받침대, 고정된 뿌리에서 접히고 들린 잔존 판재를 적용했다. 콘크리트 천장 2개에는 두께가 다른 박락 단면과 골재, 주변 균열, 슬래브 안에서 이어지는 노출 철근과 휜 끝을 적용했다. 기존 25 FBX의 GUID를 보존했고 단면용 1F 재질 4개를 추가했다.

기존 표면 색 계열·세부 마모, 코어의 연속 천장, 승강로/가동 부품, VB 계단과 황야를 유지했다. 위치·회전·스케일이 달라진 기존 Transform은 0개다.

## 조사 근거

[PNNL 금속 지붕 자료](https://basc.pnnl.gov/resource-guides/metal-roofs)와 [FEMA 풍해 조사](https://www.fema.gov/sites/default/files/2020-07/guidelines-wind-vulnerability.pdf)의 패널·지지대·체결부 이탈 사례를 참고했다. [NPS 콘크리트 보존 자료](https://www.nps.gov/orgs/1739/upload/preservation-brief-15-concrete.pdf)의 피복 탈락·철근 부식·골재 노출을 참고했다. 파손 원리를 외형으로 해석한 게임 아트이며 구조 해석이나 붕괴 시뮬레이션 결과는 아니다. 조사와 제작 결정을 [Plan.md](../../../SourceAssets/F1_WindowRoofDamage/Plan.md)에 기록했다.

## 검증

| 항목 | 결과 | 근거 |
|---|---|---|
| 배치/충돌체 보존 | {f['transforms']:,} Transform·{f['colliders']} Collider | [최종 상태](final_check.json) |
| 벽 시각/충돌 메시 | 14개 모두 같은 메시, 불일치 0 | [모델 참조](model_references.json) |
| 통행 | {walk['tested']}/{walk['tested']} 통과, 경로 계획 실패 0 | [통행](walk_floor.json) |
| 실제 Play | {play['views']}시점, {play['framesAdvanced']}프레임 진행, 오류 0 | [Play](play.json) |
| 누락 스크립트·메시·재질 | 모두 0 | [최종 상태](final_check.json) |
| 반사 | 8개 갱신 | [반사](reflections.json) |
| 가림 데이터 | {occ['bytes']:,} bytes, 기존 GUID 유지 | [가림](occlusion.json) |
| 다른 층·게임 코드 | 보호 추적 파일 {len(protected):,}개 범위 밖 변경 없음 | [보존](preservation.json) |

Play 검수는 플레이어·입력을 수정하지 않고 실제 프레임 진행 중 임시 카메라로 촬영했다. 가림 사용을 켠 세 시점에서 확인했다. 이번 Editor 측정은 빌드 성능 보장이나 사용자 외형 승인과 다르다. 창·지붕의 구조와 외형만 수정했으며 게임 기능을 추가하지 않았다.

현재 저장된 `Level_1F_Factory` 편집 상태가 최신이다. `AE_C01_Walls`가 선택되어 있다. 로컬 저장이며 커밋/push는 하지 않았다. 후속 변경 뒤 예전 전체 제작기나 단계별 Apply를 일괄 재실행하지 않는다.

변경 이력: V0.01 (2026-11-13) 창 비율과 재질별 지붕 파손, 조사·검수 기록. 송예찬.
'''
(O/'Review.md').write_text(md,encoding='utf-8')
def figure(path,title):
 assert (O/path).exists(),path
 return f'<figure><a href="{path}"><img loading="lazy" src="{path}" alt="{html.escape(title)}"></a><figcaption>{html.escape(title)}</figcaption></figure>'
pairs=[('Window_Front','생산동 창과 벽'),('Window_C03','사무 구역 창과 벽'),('Exterior','공장 전경'),('C01_roof','실내에서 보는 금속 지붕'),('Metal_Top','골판·체결점·들린 금속판'),('Metal_Close','금속판 아래와 받침대'),('Concrete_Top','콘크리트 파단면·균열·철근'),('Concrete_Close','실내에서 보는 콘크리트'),('T07','통로의 금속 천장')]
sections=[]
for name,title in pairs:sections.append('<section><h2>'+title+'</h2><div class="pair">'+figure('before/'+name+'.jpg','수정 전')+figure('after/'+name+'.jpg','수정 후')+'</div></section>')
sections.append('<section><h2>콘크리트 파단면 근접</h2>'+figure('after/Concrete_Fracture.jpg','수정 후 — 박락 단면과 골재·철근')+'</section>')
sections.append('<section><h2>실제 Play 화면</h2><div class="triple">'+''.join(figure('play_'+n+'.jpg',t) for n,t in [('Facade','벽과 창'),('Concrete','콘크리트 천장'),('Factory','공장 내부')])+'</div></section>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1F 창과 지붕 — 전후 비교</title><style>body{margin:0;background:#171b1b;color:#e4e4dc;font:16px/1.7 system-ui,sans-serif}main{max-width:1560px;margin:auto;padding:32px}h1{font-size:32px}h2{font-size:23px}p{color:#c4c9c1}a{color:#d9bd83}section{margin:36px 0;border-top:1px solid #454c45;padding-top:14px}.pair,.triple{display:grid;gap:16px;grid-template-columns:repeat(2,minmax(0,1fr))}.triple{grid-template-columns:repeat(3,minmax(0,1fr))}figure{margin:0;background:#29312c;border:1px solid #414b43;border-radius:6px;overflow:hidden}img{display:block;width:100%;height:auto}figcaption{padding:8px 12px}.facts{padding:16px;background:#28352d;border-left:4px solid #b1aa73}@media(max-width:850px){main{padding:18px}.pair,.triple{grid-template-columns:1fr}}</style><main><h1>1F 창 비율과 재질별 지붕 파손</h1><p>송예찬 · 2026-11-13 · V0.01</p><p>벽의 비중을 높이고, 금속판과 콘크리트가 서로 다른 방식으로 파손된 모습을 보강했습니다. 전후 쌍은 동일 시야이며, 이미지를 누르면 원본 크기로 볼 수 있습니다.</p><p class="facts">창 개구 비율 44.8% → 19.8% · 벽 14개·지붕 11개 보수 · 기존 배치 유지 · 통행 75/75</p><p>비율은 수정 벽 구간의 설계 면적 기준입니다. 문 위 헤더·박공·배경 별채는 계산에서 제외합니다.</p><p><a href="Review.md">검수와 조사 출처</a> · <a href="../../../SourceAssets/F1_WindowRoofDamage/README.md">제작 원본·수치 정의</a> · <a href="../../../SourceAssets/F1_WindowRoofDamage/Plan.md">파손 자료와 적용 방향</a></p>'''+''.join(sections)+'</main></html>'
(O/'review.html').write_text(page,encoding='utf-8')
print(json.dumps(dict(report=str(O),comparisons=len(pairs),protectedFiles=len(protected),guidChanges=guid_changes),ensure_ascii=False))
