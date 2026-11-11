from pathlib import Path
import json,html
H=Path(__file__).parent;ROOT=H.parents[1];O=ROOT/'Docs/Review/2026-11-11_ZFighting'
saved=json.loads((H/'saved_validation.json').read_text());preserved=json.loads((H/'preservation.json').read_text());residual=json.loads((H/'residual_summary.json').read_text())
rows=[]
for s in saved['scenes']:
    name=Path(s['scene']).stem;b=json.loads((H/'results'/f'{name}.json').read_text())
    rows.append(f"<tr><td>{name}</td><td>{s['activeMeshRenderers']:,}</td><td>{s['changedRenderers']:,}</td><td>{'수정 저장' if s['changedRenderers'] else '변경 없음'}</td></tr>")
def pic(name,label):return f'<figure><a href="{name}.png"><img loading="lazy" src="{name}.png" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>'
shots=json.loads((H/'shots.json').read_text())
gallery=''.join(pic('after_'+s['name'],'수정 후 · '+s['name']) for s in shots)
result=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>After Seconds 전체 씬 깊이 충돌 검수 V0.01</title>
<style>body{{margin:0;background:#12191d;color:#e6ecee;font:16px/1.7 system-ui,sans-serif}}main{{max-width:1240px;margin:auto;padding:40px 24px}}h1{{font-size:32px;line-height:1.3}}h2{{margin-top:48px}}a{{color:#9cd8d3}}p{{max-width:95ch}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;background:#202b31}}img{{width:100%;display:block}}figcaption{{padding:10px 14px}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;padding:10px;border-bottom:1px solid #39474d}}.note{{padding:18px;background:#23343c;border-left:4px solid #8dc8c2}}code{{overflow-wrap:anywhere}}@media(max-width:750px){{.grid{{grid-template-columns:1fr}}h1{{font-size:25px}}}}</style>
<main><h1>After Seconds 전체 씬 깊이 충돌 검수 V0.01</h1><p>2026-11-11 · 작성자 송예찬 · Unity 6000.4.0f1 · 로컬 저장, 커밋·push 미실시</p>
<p class="note">Player와 보관된 Old 씬을 포함한 15개 씬의 활성 메시를 조사하고, 14개 씬의 {saved['changedRenderers']:,}개 렌더러에 겹친 면 보정을 적용했다. 계단·데크·벽 패널·터널 접합부의 중복 표면을 제거했다. Player 씬은 변경하지 않았다.</p>
<h2>B4 VA 계단 전후</h2><p>같은 카메라·조명·후처리로 촬영했다. 계단 전면에 나타났던 검은 삼각형 무늬가 제거됐다.</p><div class="grid">{pic('before_B4_VA_user_view','수정 전')}{pic('after_B4_VA_user_view','수정 후')}</div>
<h2>씬별 범위</h2><table><thead><tr><th>씬</th><th>활성 메시 렌더러</th><th>수정 렌더러</th><th>저장 상태</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>수정과 검증</h2><ul><li>원본 모델의 GUID와 파일을 보존하고, 시각 표시용 MeshFilter에 파생 메시를 연결했다. 동일한 결과는 여러 렌더러가 공유한다.</li><li>같은 방향의 중복 삼각형과 같은 평면 위 겹친 영역을 제거했다. 평면 차이는 모든 삼각형 정점에서 0.05mm 이하인 경우만 허용했다. 새 삼각형의 노멀·탄젠트·색상·UV는 원본에서 보간했다.</li><li>원본 Transform·Collider 상태를 적용 전후 비교해 동일함을 확인했다. 저장 후 렌더러 ID·배치 행렬·재질·LOD 구성·스킨드 메시도 비교했다.</li><li>15개 씬의 참조 메시 {saved['meshCount']:,}개에 빈 정점·무효 좌표·잘못된 삼각형 인덱스 오류가 없다. 보호 대상 {preserved['protectedFiles']}개 파일과 Git 변경 범위를 확인했다. 게임 C#·Player·Animator·원본 모델·재질·프로젝트 설정은 보존했다.</li></ul>
<p>최종 후보 재검사에서 0.05mm 경계 허용오차를 넘는 잔여 내부 겹침은 {residual['nontrivialInteriorOverlaps']}건이다. 원형 씬의 float32 좌표 경계에는 미세한 잔여 조각이 남는다. 잔여 영역을 0.05mm 안쪽으로 축소하면 내부가 사라지는지 판정했으며, 수학적으로 모든 면적이 정확히 0이라고 주장하지 않는다.</p>
<h2>검수 범위와 제한</h2><p>큰 정적 면은 전체 활성 씬 데이터에서 검사했고, 아래 33개 화면은 대표 시점의 정적 렌더다. 일부 근접 사진은 표면 일부만 보이거나 주변 구조에 가려져 있다. 모든 이동 경로·카메라 각도에 대한 플레이 테스트나 성능 측정은 이번 검수에 포함하지 않았다.</p><p>평면 후보 탐색은 삼각형 면적 0.005m² 이상·동일 방향을 기준으로 한다. 투명 표면의 평면 클리핑과 스킨드 메시 수정은 제외했다. 서로 배타적인 하위 LOD는 교차 겹침에서 제외하고, 자체 중복 삼각형만 검사했다. 매우 작은 디테일·반대 방향 면·애니메이션 중 겹침은 이 자동 검사의 보장 범위가 아니다.</p>
<p>파생 메시 {preserved['derivedMeshes']}개가 로컬에 추가됐으며, Unity 텍스트 에셋 기준 합계 {preserved['derivedMiB']:,.2f}MiB다. 원본을 함께 유지하는 방식으로 저장 용량이 늘었다. 빌드 크기나 GPU 메모리 증가량과 같은 수치는 아니며 별도 측정하지 않았다.</p>
<h2>증거와 재검사</h2><p><a href="../../../SourceAssets/ZFightingReview/saved_validation.json">저장 데이터 검증</a> · <a href="../../../SourceAssets/ZFightingReview/preservation.json">보존 검증</a> · <a href="../../../SourceAssets/ZFightingReview/residual_summary.json">잔여 후보 판정</a></p><p>도구는 <code>SourceAssets/ZFightingReview/</code>에 있다. Unity 프로젝트 밖에서 CLI로 실행하며 게임 런타임 코드를 추가하지 않는다. <code>Export.cs → analyze.py → repair_plan.py → Apply.cs</code> 순서로 조사·계획·적용한다. Python에는 NumPy·Shapely·Pillow가 필요하며, 메시 캐시는 Unity 프로젝트의 <code>Temp/ZFightingReview/</code>에 생성한다. 새 환경에서는 다시 내보내야 한다. 기존 계획은 이전 메시 삼각형 인덱스에 종속되므로 현재 씬에 재실행하지 않는다. 수정 도구는 기준 씬 SHA를 검사한다.</p><p>중간 검수 도구에서 발생한 읽기 불가 메시·직렬화 오류는 복구 후 데이터 재검사로 확인했다. 과거 콘솔 로그는 지우지 않았으므로 콘솔 전체 오류 수를 0건으로 보고하지 않는다.</p><p>수정 전 씬 백업: <code>C:/Users/503-26/Documents/Codex/Backups/AfterSeconds_ZFighting_20261111/</code>. 원상 복구할 때는 씬 백업 또는 작업 시작 당시 Git 버전과 원본 메시 참조를 함께 사용한다.</p>
<h2>수정 후 대표 시점</h2><div class="grid">{gallery}</div><p>변경 기록: V0.01 (2026-11-11) 전체 씬 정적 깊이 충돌 조사·시각 메시 보정·보존 검증. 송예찬.</p></main></html>'''
(O/'review.html').write_text(result,encoding='utf-8')
print(O/'review.html')
