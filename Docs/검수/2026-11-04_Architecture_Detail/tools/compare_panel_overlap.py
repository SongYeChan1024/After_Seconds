"""수정 전후의 패널 겹침을 같은 기준으로 비교한다."""
import json, subprocess, sys
from pathlib import Path
repo=Path(__file__).resolve().parents[4];tmp=repo/'tmp/ArchitectureDetail_20261104'
# 수정된 입력은 건드리지 않고 같은 진단 코드로 원래 모델을 다시 검사한다.
script=(Path(__file__).with_name('diagnose_panel_overlap.py')).read_text(encoding='utf-8-sig')
old=script.replace("tmp/'panel_template.json'","tmp/'panel_template.before_clearance.json'").replace("panel_internal_overlap.json","panel_internal_overlap_before.json")
old=old.split('instances={')[0]
exec(compile(old,str(Path(__file__).with_name('diagnose_panel_overlap.py')),'exec'))
print('BEFORE_REPORT_WRITTEN',flush=True)
