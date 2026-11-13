"""Build the local review from captured evidence; does not edit Unity assets."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Docs/Review/2026-11-13_1F_SurfaceDetail'


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8-sig'))


final = read('final_check.json')
shader = read('shader_validation.json')
play = read('play.json')
refs = read('cross_references.json')
applied = read('apply.json')
preservation = json.loads((OUT.parent / '2026-11-13_1F_RoofLiftWilderness/preservation.json').read_text(encoding='utf-8'))
preservation['surfaceTransformChanges'] = final['transformChanges']
(OUT / 'preservation.json').write_text(json.dumps(preservation, ensure_ascii=False, indent=2), encoding='utf-8')

md = f'''# 1F 표면 디테일 검수 V0.01

작성자: 송예찬 · 2026-11-13

외벽의 벽돌 무늬와 지나치게 넓은 녹 얼룩을 보수했다. 낡은 폐공장 분위기를 유지하며 외장판·금속·콘크리트·목재·고무·직물의 가까운 표면을 구별했다. [전후 화면](review.html)과 [수정값 안내](../../../SourceAssets/F1_SurfaceDetail/README.md)를 함께 볼 수 있다.

## 반영한 표현

- 외벽: 벽돌 알베도·노멀 연결을 제거했다. 도장한 금속 외장판의 긴 이음새, 작은 체결점, 가는 빗물 자국과 국소 녹으로 바꿨다. 기존 `AE_M_Plaster` 이름과 GUID는 참조 보존을 위해 유지한다.
- 철골·설비·난간·승강칸·도르래: 큰 갈색 번짐을 작은 도장 벗겨짐과 부식점으로 바꿨다. 벗겨진 가장자리와 표면 긁힘에 법선·거칠기 차이를 넣었다.
- 콘크리트: 굵은 균열과 흐릿한 얼룩을 줄이고 가는 균열과 입자를 넣었다. 목재는 방향 있는 결, 고무와 직물은 낮은 금속성과 서로 다른 미세 표면을 사용한다.
- 기존 파손 형상, 색 계열, 조명, 식생과 황야 배치는 유지했다. 표면 무늬는 오브젝트의 실제 크기를 기준으로 하므로 이후 승강칸과 문을 움직일 때 함께 움직인다.

재질 {len(applied['materials'])}개를 수정했다. 그중 13개가 수정된 전용 셰이더를 사용하며 관련 Renderer는 {shader['affectedRenderers']}개다. 나머지 `AE_M_Brick`은 잔해의 기본색만 회색 계열로 조정했다. 반사 텍스처 8개를 새 표면으로 갱신했다.

## 검증 결과

| 항목 | 결과 | 근거 |
|---|---|---|
| 외벽/전용 표면의 벽돌 텍스처 연결 | {len(shader['brickTextureBindings'])}개 | [셰이더 검사](shader_validation.json) |
| 셰이더 컴파일 오류 | {shader['errors']}개, 현재 플랫폼 지원 | [셰이더 검사](shader_validation.json) |
| 표면 수정 전후 배치 | {final['transforms']:,} Transform, 변경 {len(final['transformChanges'])}개 | [최종 검사](final_check.json) |
| 충돌체 | {final['colliders']}개 유지 | [수정 전](before_audit.json) · [수정 후](final_check.json) |
| 누락 스크립트·메시·재질 | 모두 0개 | [최종 검사](final_check.json) |
| 실제 Play | 임시 카메라 {play['views']}시점, {play['framesAdvanced']}프레임 진행, 오류 {len(play['errors'])}개 | [Play 기록](play.json) |
| 플레이어·입력 수정 | {play['changesToPlayerOrInput']}개 | [Play 기록](play.json) |
| 현재 콘솔 | 오류 0·경고 0, 컴파일 완료 | [콘솔](console.json) |
| 1F 밖의 해당 재질/셰이더 참조 | {len(refs['outside1F'])}개 | [참조 검사](cross_references.json) |
| 보호 범위 | 추적 중인 Unity 파일 {preservation['protectedTrackedFiles']:,}개에 범위 밖 변경 없음 | [보존 검사](preservation.json) |

Play의 프레임 시간은 이 PC의 Editor에서 측정한 중앙값 {play['medianMs']:.2f}ms, 95백분위 {play['p95Ms']:.2f}ms다. 빌드 성능을 보장하는 측정은 아니다. 이번 Play 검수는 표면 렌더링을 확인했으며, 통행 검수는 아래 구조 단계 기록에 있다.

## 이전 요청과 연결

[천장·승강기·VB 계단·황야 검수](../2026-11-13_1F_RoofLiftWilderness/Review.md)에서 완료한 구조를 그대로 유지했다. 그 단계의 전후 화면은 표면 보수 전 기록이다. 현재 외형은 이 문서의 화면을 우선한다.

승강기에는 고정 승강로와 분리된 승강칸·균형추·도르래·로프·문이 있다. **상하 이동과 문 제어, 엔딩 스크립트는 사용자가 후속 구현한다.** [부품 이름·축·이동 범위 안내](../../../SourceAssets/F1_RoofLiftWilderness/README.md)를 참고한다.

저장된 `Level_1F_Factory`가 최신이다. Unity는 편집 모드이며 `AE_C01_Walls` 외벽 근접 시야를 선택했다. 이번 변경은 로컬 저장 상태이고 커밋/push는 하지 않았다. 이전 전체 제작기와 단계별 Apply를 현재 씬에 일괄 재실행하지 않는다.

변경 이력: V0.01 (2026-11-13) 표면 보수와 전후/Play/보존 검수 기록. 송예찬.
'''
(OUT / 'Review.md').write_text(md, encoding='utf-8')

pairs = [
    ('Exterior', '공장 전경', '외벽의 벽돌 노출과 넓은 녹이 작은 마모로 바뀐 모습'),
    ('C01_roof', '철골과 파손 지붕', '기존 파손 구조를 유지하고 금속 표면의 녹 크기를 축소'),
    ('C03', '사무 구역', '외장판과 콘크리트의 구분'),
    ('Car_Close', '승강칸 근접', '넓은 갈색 번짐을 작은 도장 박리와 부식점으로 변경'),
    ('Hoist_Close', '도르래와 권상 장치', '금속 반사와 국소 마모'),
    ('Floor_Close', '바닥 근접', '굵은 균열을 줄이고 미세한 콘크리트 표면으로 조정'),
    ('Stair_Close', '계단 근접', '난간과 계단의 재질별 디테일'),
]


def figure(path, caption):
    assert (OUT / path).is_file(), path
    return f'<figure><a href="{path}"><img src="{path}" loading="lazy" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'


parts = []
for key, title, note in pairs:
    parts.append(f'<section><h2>{title}</h2><p>{note}</p><div class="pair">' + figure(f'before/{key}.jpg', '수정 전') + figure(f'after/{key}.jpg', '수정 후') + '</div></section>')
parts.append('<section><h2>수정 후 외벽 근접</h2><p>금속판 이음새·체결점·박리 가장자리를 별도 근접 시야에서 확인했습니다.</p><div class="pair">' + figure('after/Facade_Close.jpg', '외벽 근접') + figure('after/Facade_Oblique.jpg', '외벽 사선 시야') + '</div></section>')
parts.append('<section><h2>실제 Play 화면</h2><p>플레이어와 입력을 변경하지 않고, 실제 프레임이 진행되는 동안 임시 카메라로 확인했습니다.</p><div class="triple">' + ''.join(figure(f'play_{key}.jpg', caption) for key, caption in [('Facade','외벽'),('Car','승강칸'),('Factory','공장 내부')]) + '</div></section>')
page = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1F 표면 디테일 — 전후 비교</title>
<style>body{margin:0;background:#171b1b;color:#e4e4dc;font:16px/1.7 system-ui,sans-serif}main{max-width:1560px;margin:auto;padding:32px}h1{font-size:32px;margin-bottom:12px}h2{font-size:23px;margin-bottom:6px}p{color:#bfc5bd}a{color:#cfb57f}section{margin:36px 0;border-top:1px solid #424a42;padding-top:18px}.pair,.triple{display:grid;gap:16px;grid-template-columns:repeat(2,minmax(0,1fr))}.triple{grid-template-columns:repeat(3,minmax(0,1fr))}figure{margin:0;background:#242b28;border:1px solid #414b43;border-radius:6px;overflow:hidden}img{display:block;width:100%;height:auto}figcaption{padding:8px 12px}.facts{background:#29322c;padding:16px;border-left:4px solid #9d9f6c}@media(max-width:850px){main{padding:18px}.pair,.triple{grid-template-columns:1fr}}</style>
<main><h1>1F 표면 디테일 — 전후 비교</h1><p>송예찬 · 2026-11-13 · V0.01</p>
<p>낡은 폐공장 분위기를 유지하며 벽돌 무늬와 과도한 녹 면적을 수정했습니다. 이미지를 누르면 원본 크기로 볼 수 있습니다. 각 전후 쌍은 동일한 카메라 시야입니다.</p>
<p class="facts">14개 재질 수정 · 관련 Renderer 444개 · 기존 배치 1,778개와 Collider 165개 유지 · 셰이더 오류 0 · 실제 Play 3시점 확인</p>
<p><a href="Review.md">검수 기록</a> · <a href="../../../SourceAssets/F1_SurfaceDetail/README.md">표면 수정값</a> · <a href="../2026-11-13_1F_RoofLiftWilderness/review.html">앞선 구조 작업 화면</a> · <a href="../../../SourceAssets/F1_RoofLiftWilderness/README.md">승강기 가동 부품 안내</a></p>
''' + ''.join(parts) + '<p>로컬 저장 상태입니다. 승강기 운행·문 제어·엔딩 스크립트는 사용자 후속 구현 범위입니다.</p></main></html>'
(OUT / 'review.html').write_text(page, encoding='utf-8')
print(json.dumps({'report': str(OUT), 'comparisonPairs': len(pairs), 'closeViews': 2, 'playViews': 3}, ensure_ascii=False))
