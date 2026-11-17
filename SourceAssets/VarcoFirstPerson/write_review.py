from pathlib import Path
import re, html
root=Path(__file__).resolve().parents[2]
out=root/'Docs/Review/2026-11-17_VarcoFirstPerson'
logs={name:(out/name).read_text(encoding='utf-8-sig') for name in ('play_validation.txt','mode_validation.txt')}
for name,text in logs.items():
    assert re.search(r'TOTAL passed=\d+, failed=0,',text), f'Unresolved test: {name}'
total=sum(int(re.search(r'TOTAL passed=(\d+)',s).group(1)) for s in logs.values())
review=f'''# VARCO 동작 연결과 R 투척 보정 V0.01

2026-11-17 · 작성자 송예찬

VARCO의 `throw_baseball` 클립을 현재 리그에 맞춰 반입하고, 기존 걷기·달리기와 함께1인칭 손 동작에 연결했다. 사용자 후속 요청으로 R 아래 던지기의 손을 낮추고 상승 궤적과 위/아래 힘 차이를 보완했다. 로컬 저장 완료, 이번 커밋·push 없음.

## 반영한 동작

- 걷기·달리기: 기존 사용자 선택 VARCO 클립의 손목 경로를 추출해 화면용 진폭으로 재생한다. 기존 하체 Animator의 normalizedTime을 공유하며 정지·조준·확대에 따라 진폭을 줄인다.
- 위에서 던지기: 새 Humanoid 클립3.333초 중 실제 투척 구간을 사용한다. 준비0.18초·방출 후 팔 동작0.42초. 물체는 버튼을 놓은 같은 프레임에 출발한다.
- 아래에서 던지기: 전용 VARCO 동작이 없어 기존 절차적 동작을 보완했다. 준비점을 낮추고 방출 후 팔을 위로 따라 올린다. 카탈로그에 없는 전용 클립을 반입했다고 표시하지 않는다.
- 발/하체: 기존 본을 공유하는4,486삼각형 표시 메시와 전신 Controller를 유지한다. 점프/착지 전용 클립의 새 연결은 이번 항목이 아니다.

## 현재 조절값

| 항목 | 위에서 던지기 | 아래에서 띄워 던지기 |
|---|---:|---:|
| 초기 속도 |12m/s|6m/s|
| 시선 대비 상승 각도 |8°|35°|
| 눈 기준 손 위치(X,Y,Z)m |(0.30,-0.15,0.45)|(0.26,-0.34,0.68)|
| 평평한 시험 바닥의 수평 거리 |약8.99m|약4.80m|

거리 수치는 정면 조준·정지·현재 시험용 공·평평한 바닥에서 측정한 값이다. 높이/시선/장애물에 따라 바뀐다. 아래 궤적은 시작점에서 약0.567m 상승했다. 아래쪽을 의도적으로 조준하면 조준 방향을 유지한다. 확대할 때는 아래 손에만8cm 위쪽 보정을 더해 화면 잘림을 막는다. 이 값은 플레이 조정용이며 질량별 힘 모델이나 홀드 충전 기능을 추가한 것은 아니다.

## 검수

- 실제 Play 동작47개와 R 투척20개, 총{total}개 통과. 원시 결과는 [동작](play_validation.txt)·[R/힘/궤적](mode_validation.txt)에 있다.
- 이동 중 손의 반대 박자, 발 애니메이션, 조준 흔들림 감소, 점프/착지 기존 반응, 확대 시 손 표시, 취소·중복 방출 방지·첫 접촉 원을 확인했다.
- R 입력으로 조준 중 방식 전환, 낮은 실제 손에서 시작하는 상승 곡선, 속도2:1, 거리 차이, 실제 물리 출발 속도, 같은 프레임 방출을 확인했다. 아래 던지기의 첫 접촉 예측 오차는 약2cm 이내였다.
- 실제 B5 이동/투척 화면을 [review.html](review.html)에 정리했다. 이동 캡처의 프레임·속도 기록은 [final_visual.txt](final_visual.txt)다.
- 첫 자동 입력 시험은 키가 전달되지 않아 실패했다. 임시 InputSettings와 장치 활성화를 보완해 재검수했으며 실패 기록은 [input_harness_attempt.txt](input_harness_attempt.txt)에 남겼다.
- 컴파일·콘솔·참조 및 편집 상태는 [audit.json](audit.json), 기존 파일 해시는 [preservation.json](preservation.json)을 확인한다. 기존 전신 Controller·클립·입력·Presenter·Motor를 보존했다. 이번 프리팹 변경은 손 컴포넌트의 새 참조2개다.
- 컴파일 실패·콘솔 오류·누락 스크립트0. 콘솔 경고1종은 이미 편집 모드인 상태에서 CLI 정지 명령을 호출한 기록이며 게임 동작 경고가 아니다([원문](console.json)). B5 씬은 변경 없는 편집 상태, 입력 설정과 ProjectSettings 해시는 시작 상태로 복원했다. 보호한 기존 소스/Animator/.meta131개 중 지정 C#3개 외128개는 해시가 같다.

## 조절 및 남은 아트 범위

`Assets/Afrer_Seconds/06.Data/PlayerHandAnimations.asset`에서 소스 클립/손 곡선/방출 후 시간을, `PlayerThrowSettings.asset`에서 두 방식의 속도·각도·손 위치를 조절한다. `PlayerHandSettings.asset`의 underhandZoomLift는 확대 시 아래 손 높이다. 기존 수리 리그의 메시와 손가락을 계속 사용하므로 최종 전용 손 모델·물건별 쥐기 포즈·전용 아래 던지기 클립은 남아 있다.

원본·출처·제작 방법은 [SourceAssets/VarcoFirstPerson](../../../SourceAssets/VarcoFirstPerson/README.md)에 있다. 이전 제작기나 첫 반입기를 일괄 재실행하지 않는다.

V0.01 — VARCO 동작 연결과 사용자 후속 투척 방식 보정·검수 기록. 송예찬.
'''
(out/'Review.md').write_text(review,encoding='utf-8')
cards=[('mode_overhand_b5','위에서 강하게 던지기 ·12m/s'),('mode_underhand_b5','낮은 손에서 띄워 던지기 ·6m/s'),('mode_underhand_zoom','아래 던지기 확대 ·손 위치 보정'),('underhand_release','아래 던지기 방출 후 팔 상승'),('b5_walk_a','VARCO 걷기와 양손'),('b5_run_a','VARCO 달리기와 양손'),('b5_walk_down_a','아래를 볼 때 기존 보행 발 표시'),('overhand_release_16','VARCO 위 던지기 후속 동작')]
body=''.join(f'<figure><a href="{n}.png"><img src="{n}.png" alt="{html.escape(label)}" loading="lazy"></a><figcaption>{label}</figcaption></figure>' for n,label in cards)
(out/'review.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>After Seconds · VARCO 동작과 R 투척 V0.01</title><style>body{margin:0;background:#10171e;color:#e4eef4;font:16px/1.65 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:32px}h1{font-size:28px}p{max-width:1000px;color:#bed0da}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(410px,1fr));gap:20px}figure{margin:0;background:#1a2631;border-radius:10px;overflow:hidden}img{display:block;width:100%}figcaption{padding:12px 18px}a{color:#94d6ee}@media(max-width:500px){main{padding:16px}.grid{grid-template-columns:1fr}}</style><main><h1>VARCO 동작과 R 투척 보정</h1><p>2026-11-17 · 송예찬 · 실제 B5 플레이 화면. 위 던지기12m/s, 아래 던지기6m/s·35°. 아래 손에서 시작하는 상승 궤적과 확대 시 손 표시를 보완했습니다. 걷기·달리기는 기존 VARCO 클립에서 추출한 손 경로를 하체 위상에 맞춥니다.</p><p>전용 아래 던지기 클립은 없어 절차적 동작을 보완했습니다. 손 모델과 물건별 쥐기 자세는 임시 아트입니다. <a href="Review.md">상세 기록</a></p><div class="grid">'''+body+'</div></main></html>',encoding='utf-8')
summary=f'2026-11-17 최신: VARCO throw_baseball을 메시 없는 Humanoid 클립으로 반입하고 기존 VARCO 걷기·달리기 손 경로를1인칭 진폭/하체 위상에 연결했다. 사용자 후속 요청으로 R 아래 던지기 손을 낮추고 속도6m/s·상승각35도, 위 던지기12m/s·8도와 구분했다. 아래 손 확대 보정8cm, 즉시 방출 유지. Play 동작47+투척20={total}개 통과. 기존 전신 Controller·클립·Presenter·Motor·입력 보존. 전용 underhand 클립/최종 손·물건별 쥐기는 남아 있다. [최신 검수](Docs/Review/2026-11-17_VarcoFirstPerson/Review.md) · [화면](Docs/Review/2026-11-17_VarcoFirstPerson/review.html). 로컬 저장, 이번 커밋·push 없음. 이전 제작기 일괄 재실행 금지. 작성자 송예찬.'
for name in ('AGENTS.md','CLAUDE.md'):
    p=root/name;s=p.read_text(encoding='utf-8-sig');first,rest=s.split('\n',1)
    first=first.replace('V1.19','V1.20')
    if summary not in s:p.write_text(first+'\n\n'+summary+'\n\n이전 단계 기록:\n'+rest,encoding='utf-8')
p=root/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8-sig')
s=s.replace('위로 던지기(멀리, 높은 궤적)와 아래로 던지기(가까이, 낮은 궤적)','위에서 강하게 던지기(멀리)와 아래에서 약하게 띄워 던지기(가까이)')
s=s.replace('새 아래 던지기의 시야 안 손 위치·상승 구간·거리 차이·즉시 방출·취소를 실제 Play에서 확인한다.', '구현 후 일반 동작47개·아래 던지기20개를 모두 통과했다. 평평한 바닥 정면 시험에서 위 약8.99m·아래 약4.80m, 아래 상승 높이 약0.567m를 확인했다. [최신 연결·검수 기록](Review/2026-11-17_VarcoFirstPerson/Review.md)을 따른다.')
p.write_text(s,encoding='utf-8')
print(f'Wrote review and handoff: {total} checks.')
