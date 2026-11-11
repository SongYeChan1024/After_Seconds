from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1]
layout=json.loads((H/'layout.json').read_text(encoding='utf8'));models={}
for p in H.glob('models_*.json'):models.update(json.loads(p.read_text()))
data=dict(title='B1 전체 정적 외형 제작 출처 V0.01',author='송예찬',date='2026-11-11',scene='Assets/Afrer_Seconds/01.Scenes/Stage/Level_B1_Circular.unity',source='SourceAssets/B1_FullFloor',design='Docs/도면/Decision/원형공동/B1_제작현황/as_built_layout.json',models=list(models.values()),cleanedMeshes=json.loads((H/'clean_models.json').read_text()),reusedAssets=sorted({p['asset'] for p in layout['placements'] if '/B1/BL_' not in p['asset']}),runtimeImplementation=False,notes='공용 원본과 GUID를 보존한 신규 B1 정적 레벨. Blender 제작 코드와 기존 프로젝트 자산 재사용. 새 VARCO 생성/외부 서비스 사용 없음. 최종 상태에서 전체 제작기 재실행 금지.')
out=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B1_FullFloor.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
p=H/'CleanApply.cs';s=p.read_text(encoding='utf8').replace('new[]{-.76f,.76f}','new[]{-.81f,.81f}').replace('new[]{-.27f,.27f}','new[]{-.285f,.285f}').replace('new Vector3(x,.58f,z)','new Vector3(x,.51f,z)').replace('new Vector3(.038f,.37f,.038f)','new Vector3(.038f,.35f,.038f)');p.write_text(s,encoding='utf8')
print('Provenance written; final sink join dimensions recorded')
