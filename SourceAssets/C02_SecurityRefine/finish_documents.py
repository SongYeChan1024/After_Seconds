from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_C02_Refine'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
a=read(D/'audit.json');detail=read(D/'detail_audit.json');walk=read(D/'controller_walk.json');play=read(D/'play_inside.json');files=read(D/'file_preservation.json');state=read(D/'final_state.json');models=read(H/'model_manifest.json')
assert not any([a['degenerateTriangles'],a['missingMaterials'],a['blocked'],a['missingFloor'],a['protectedTransformChanges'],a['lightChanges'],a['newLights'],a['newBehaviours'],detail['collisionPairs'],detail['blocked'],files['missing'],files['unexpected'],state['playing'],state['dirty'],state['runInBackground']])
assert all(w['passed'] for w in walk) and play['complete'] and play['framesAdvanced']>10 and play['displacement']>.2 and not play['errors']
assert len(models)==6 and len(detail['map'])==15 and all(m['found'] for m in detail['map']) and detail['links']==19
report=f'''# C02 보안관제동 밀도·모니터 보강 검수 V0.01

작성자 송예찬 · 2026-11-08

사용자가 지적한 빈 벽면, 6분할 감시 화면의 두 번째 지도, 모니터 제작 디테일을 보강했다. 씬과 현재 미커밋 모델 원본을 각각 백업하고 기존 가구·출입구·Light187개의 배치를 보존했다. 로컬 저장을 완료했으며 커밋·push는 하지 않았다.

## 반영 내용

- 상단 가운데 `SC_Display_05`의 이전7거점 지도를 현재 B5 **15목적지·19복도**로 교체했다. 실제 도면의 중심/반경/통로 끝점/폭을 동일 축척으로 그렸다. C02를 강조하고 5섹터·북쪽·축척을 표기했다. 실제 씬에15돔이 존재함을 확인했다. 문을 뚫은 셸의 렌더러 Bounds 중심은 설계 원의 중심과 최대19.15cm 차이가 있으므로 지도 좌표의 기준은 제작 도면이다.
- 감시 피드01–04도 현재 저장 씬에서 다시 캡처했다. 모두 정적 화면이며 실시간 영상이나 출입 로그 기능은 추가하지 않았다.
- 기존 모델8종의 모니터15곳에 분리 베젤/실링, 안쪽 광학 면, 후면 덮개/통풍구/나사, 단자·상태등을 보강했다. 책상 모니터는 VESA판·틸트 관절·리프트 지지대와 책상 글랜드/하부 채널까지 이어진 케이블을 추가했다. 소형 랙 LCD에는 큰 모니터용 지지대를 달지 않았다.
- 새 모델6종: 영상 분배/점검 랙, 열쇠·출입증 인계함, 봉인 케이스 보관함, 헤드셋·배터리 교대 거치대, 3연 환기 그릴/돔 연결 덕트, 벽 배선/지지대. 용도를 인쇄 아틀라스로 구분하며 구역명 명판은 추가하지 않았다. 유리 보관함 내부에 불투명 뒤판과 실제 내용물이 있다.
- 기존14종+새6종=20종, 배치22곳, Renderer26개, 간단한 BoxCollider17개. 고유 검수 메시22개 **{a['uniqueTriangles']:,}tri**. 새 텍스처1장·재질1개, 기존 화면 텍스처5장 갱신. TC 공용 PBR 원본은 그대로 공유한다.

## 검증

| 검사 | 결과 |
| --- | --- |
| 메시 퇴화·재질 누락 | 0 / 0 |
| 기존 주요 통행로 | {a['samples']:,}표본, 막힘·바닥 누락0 |
| 새 장비 접근 | {detail['accessSamples']}표본, 막힘0 |
| 신규/기존 가구 Collider 관통 | 0쌍 |
| CharacterController 통행 | 세 출입구 간6회·T05 전체1회, 7/7통과 |
| 바닥 글자·기존 안내선 | 겹침0, 최소 여백{a['labelGuideMinClearance']*100:.2f}cm |
| 기존 Transform / Light187개 | 변경0 / 변경0 |
| 기존 파일 보존 | {files['baselineFiles']:,}개 중 대상22개만 변경, 나머지{files['preservedFiles']:,}개 SHA256동일 |
| Play 내부 재검사 | {play['framesAdvanced']}프레임 진행, W 입력으로 {play['displacement']:.3f}m 이동, 새 경고/오류0 |
| 최종 상태 | Edit, 저장 완료, 원래 플레이어 위치/방향·백그라운드 설정복구 |

Play 첫 시도는428프레임이 진행됐지만 이동0으로 통과 처리하지 않았다. 이후 편집 모드로 돌아온 것을 확인해 현재 편집 상태를 백업/보존하고 재시도했다. 재시도에서 입력·프레임·실제 이동과 Game 화면을 확인했다. 추가 T02 Play 시도 전에 다시 편집 모드가 되어 해당 구간의 새 Play 결과는 없다. T02를 포함한 통행은 위 Controller검사로 확인했다. 편집 모드 전환 원인을 사용자 조작이나 게임 오류로 단정하지 않는다.

재검사1920×1080 Editor 중앙값{play['medianMs']:.2f}ms, p95 {play['p95Ms']:.2f}ms는 해당 관측 구간의 값이다. 빌드 성능·전체 B5 최적화 완료를 뜻하지 않는다. 신설 벽 거치대의 벽 고정 앵커는 돔 벽 안에 일부 들어가며 본체/출입 통로를 막지 않는다. Light 추가0, 게임 C#/Animator변경0. 최종 조명·색감은 전체 B5 제작 후다.

## 보기

- [진입 전](Before_FromLab.png) / [진입 후](After_FromLab.png)
- [남쪽 설비 전](Before_SouthServices.png) / [남쪽 설비 후](After_SouthServices.png)
- [모니터 앞](After_MonitorFront.png) / [모니터 뒤](After_MonitorBack.png)
- [6분할 화면·최신 지도](After_WallDetail.png)
- [열쇠/출입증 보관](After_CredentialDetail.png) / [봉인 케이스 보관](After_EvidenceDetail.png)
- [실제 Play 화면](Play_Operations.png)

## 이어서 할 일

사용자가 각 돔에 안내선이 필요하다고 다시 짚었다. 이번 보강에서는 기존 R1·바닥 목적지 표기를 보존했으며 **내부 R1/M1 연장이나 돔별 새 노선은 아직 반영하지 않았다**. 기존 전체 안내체계 문서의 용도별 방식은 가안이므로 돔별 목적지 노선/용도별 내부 연장의 구분을 확인해 전체 연결·색·패턴·글자 겹침을 재검토한다. C02 외형의 사용자 확인, 이후 T02/계단A 연결부, 전체 B5 조명 검수도 남는다. 전체 아트 최종 판정0/34 유지.

검수 원문은 `audit.json`, `detail_audit.json`, `controller_walk.json`, `play_inside_attempt1.json`, `play_inside.json`, `file_preservation.json`, `final_state.json`이다. [제작 원본](../../../SourceAssets/C02_SecurityRefine/README.md)을 따른다.
'''
(D/'검수결과.md').write_text(report,encoding='utf-8')
note=f'''2026-11-08 C02 후속 보강 완료: 사용자 피드백에 따라 상단 두 번째 지도 화면을 현재15목적지·19복도 기준으로 교체하고 감시 피드4장을 새로 캡처했다. 기존 모델8종의 모니터15곳에 베젤/후면 통풍·단자·VESA/틸트 지지대·연결 배선을 보강하고, 영상 분배/키 인계/봉인 보관/교대 거치/환기/벽 배선6종을 추가했다. 기존14종+새6종, 고유 메시366,964tri. 주요/설비 접근1,927표본 막힘0, 가구 관통0, Controller7/7, Play 재검사429프레임/0.431m·새 로그0. 기존 Transform/Light187개와 대상 외 기존 파일3,906개 보존. 화면은 정적·게임 코드 변경0. 사용자 추가 의견은 각 돔의 안내선 연결이며 기존 R1/S1/M1 방식은 가안이므로 노선 구분을 확인 중이다. 이번에 새 안내선은 아직 추가하지 않았다. 다음은 안내체계 확인/반영·C02 외형 확인, 이후 T02/계단A 연결부. 전체 B5 후 조명 조정·아트 판정0/34 유지. 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'''
for rel,version in [('AGENTS.md','V0.51'),('CLAUDE.md','V0.51'),('Docs/이어하기_2026-11-06.md','V0.35'),('Docs/회사_작업목록_2026-11-06.md','V0.33'),('Docs/AfterSeconds_메인기획서.md','V0.40')]:
 p=R/rel;s=p.read_text(encoding='utf-8');head,rest=s.split('\n',1);head=re.sub(r'V0\.\d+',version,head);prefix='Docs/' if '/' not in rel else ''
 if note not in s:s=head+'\n\n'+note+f' [최신 검수]({prefix}검수/2026-11-08_C02_Refine/검수결과.md).\n\n이전 단계 기록:\n'+rest.lstrip()
 if rel.endswith('메인기획서.md') and '| V0.40 |' not in s:s=s.replace('| V0.39 |','| V0.40 | 2026-11-08 | 송예찬 | C02 밀도·모니터 디테일·현재 구조 지도 보강과 통행/Play검수, 각 돔 안내체계 후속 의견. |\n| V0.39 |',1)
 p.write_text(s,encoding='utf-8')
p=R/'SourceAssets/C02_Security/README.md';s=p.read_text(encoding='utf-8');head,rest=s.split('\n',1)
if '후속 보강 우선' not in s:p.write_text(head.replace('V0.02','V0.03')+'\n\n2026-11-08 후속 보강 우선: 현재 모델 디테일/지도/추가6종은 [C02_SecurityRefine](../C02_SecurityRefine/README.md)와 [후속 검수](../../Docs/검수/2026-11-08_C02_Refine/검수결과.md)를 따른다. 아래14종/239,928tri는 초기 본체 단계 기록이다. 현재 기존8종의 원본도 갱신했으며 이전 Apply 전체 재실행은 금지한다. 작성자 송예찬.\n'+rest,encoding='utf-8')
print(json.dumps({'report':str(D/'검수결과.md'),'validated':True,'next':'wayfinding interpretation'},ensure_ascii=True))
