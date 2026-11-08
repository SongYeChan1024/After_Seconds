from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_Observation'
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8');title,body=s.split('\n',1);assert 'V0.49' in title
note='2026-11-08 B4 대표 구역 반영: C01 중앙 관찰동과 T02 접근 복도를 새 Level_B4_Circular 씬에 저장했다. C01 반지름12m/바닥-66m, 북측2.5m 관찰 데크와 양쪽15단 계단, 광학 측정/준비/제어/기록 설비를 구현했다. 관측석은 시험 바닥 방향으로 배치하고 뒤쪽 통행을 확보했다. 중성 작업광18개, 이동7/7와 실제 키보드 Play3구역 새 경고/오류0. 기존5,788파일/B5/게임 코드/Animator 보존. 아직 C01 대표 구역 사용자 확인 단계이며 남은12돔·3코어·21복도와 층간 연결은 후속이다. 다음 C02 진단동→T01/VA 순으로 확장한다. B5 1차 수용을 전체 최종 아트 확정으로 간주하지 않는다. 작성자 송예찬. [검수 화면](검수/2026-11-08_B4_Observation/review.html).'
p.write_text(title.replace('V0.49','V0.50')+'\n\n'+note+'\n\n이전 단계 기록:\n'+body.lstrip()+'\n- V0.50 (2026-11-08): B4 C01/T02 대표 구역 구현과 검수 결과·후속 확장 순서. 송예찬.\n',encoding='utf-8')
p=O/'검수결과.md';s=p.read_text(encoding='utf-8');needle='파일 YAML 직접 수정은 없다.';s=s.replace(needle,needle+' 복사 과정에서 상속된 B5 가림 데이터는 새 B4 씬의 참조만 Unity SerializedObject로 해제했다. 기존 B5 가림 데이터 원본은 보존했으며 B4 카메라의 가림 기능은 전체 층 베이크 전까지 비활성이다.');p.write_text(s,encoding='utf-8')
p=P/'Assets/Afrer_Seconds/06.Data/AssetSources/B4_Observation_20261108.json';d=json.loads(p.read_text(encoding='utf-8'));d['sceneAssembly'].append('SourceAssets/B4_Observation/OcclusionSettings.cs:Detach');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# All report links are local and all gallery images must exist.
missing=[n for n in ['02_deck','04_console','03_from_deck','05_preparation','07_stairs','06_corridor','01_arrival','play_corridor','play_stairs','play_deck'] if not (O/(n+'.png')).exists()]
assert not missing,missing
print('Main plan V0.50; gallery images 10/10; source record updated.')
