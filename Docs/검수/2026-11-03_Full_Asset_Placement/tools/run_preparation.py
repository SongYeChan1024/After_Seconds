# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
"""의사코드: 모델별 독립 프로세스로 내보내며 한 모델 실패가 나머지 준비를 중단하지 않게 한다."""
import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
names=sys.argv[1:] or ['Props_ReactorTank','Props_HVACUnit','Props_LaboratoryWorkbench','Props_PalletStorageRack','Props_ExhaustFan','Props_IndustrialCentrifuge','Props_MaintenanceToolCart','Props_GasCylinderRack','Env_SteelIBeam','Env_SteelGrating','Env_LoadingShutterWall']
status=[]
for name in names:
    start=time.time();log=R/'tools'/(name+'_prepare.log')
    with log.open('w',encoding='utf-8') as handle:
        p=subprocess.run([r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe','-b','--python',str(R/'tools'/'prepare_models.py'),'--',name],stdout=handle,stderr=subprocess.STDOUT)
    manifest=R/'prepared'/name/'manifest.json'
    good=manifest.exists() and (manifest.parent/'preview.png').exists() and all(not m['final']['strictCrossingPairs'] and not m['final']['boundaryEdges'] and not m['final']['overusedEdges'] for m in json.loads(manifest.read_text(encoding='utf-8'))['meshes'])
    item={'name':name,'success':good,'returnCode':p.returncode,'seconds':round(time.time()-start,1),'log':str(log)};status.append(item)
    (R/'tools'/'run_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(item,flush=True)
allrecords=[json.loads(p.read_text(encoding='utf-8')) for p in (R/'prepared').glob('*/manifest.json')]
for record in allrecords:
    for mat in record['materials']:mat['baseColorFactor']=[1,1,1,1]
    (Path(record['fbx']).parent/'manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
(R/'prepared'/'prepared_manifest.json').write_text(json.dumps(allrecords,indent=2),encoding='utf-8')
print('TOTAL',len(allrecords),'FAILED',[s['name'] for s in status if not s['success']],flush=True)

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
