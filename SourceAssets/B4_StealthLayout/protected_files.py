from pathlib import Path
import hashlib
import json
import subprocess
import sys

repository = Path(__file__).resolve().parents[2]
report_file = repository / 'Docs/검수/2026-11-06_B5_B4/protected_before.json'
tracked = subprocess.check_output(['git','ls-files','-z'],cwd=repository).decode('utf-8').split('\0')
paths = [path for path in tracked if path.startswith('Unity/') and (path.endswith(('.cs','.asmdef','.controller','.unity')) or '/Packages/' in path or '/ProjectSettings/' in path or '/07.Animator/' in path)]
gateway = 'Unity/After_Seconds_Build_V0.01/ProjectSettings/AI.Assistant/GatewaySettings.asset'
if (repository/gateway).exists() and gateway not in paths:
    paths.append(gateway)
if '--verify' in sys.argv:
    before = json.loads(report_file.read_text(encoding='utf-8'))
    relocated = {}
    hashes = {}
    for path in before:
        actual = repository/path
        if not actual.exists() and actual.name in ('Level_B4_Observation.unity','Level_B5_Isolation.unity'):
            archived = actual.parent/'Old'/actual.name
            if archived.exists():
                actual = archived
                relocated[path] = actual.relative_to(repository).as_posix()
        hashes[path] = hashlib.sha256(actual.read_bytes()).hexdigest() if actual.exists() else None
    changes = [path for path,digest in before.items() if hashes.get(path)!=digest]
    result = {'protected':len(before),'changed':changes,'relocated':relocated}
    print(json.dumps(result,ensure_ascii=False))
    (report_file.parent/'protected_after.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    raise SystemExit(bool(changes))
if '--restore-line-endings' in sys.argv:
    before = json.loads(report_file.read_text(encoding='utf-8'))
    restored = []
    for path,digest in before.items():
        content=(repository/path).read_bytes()
        if hashlib.sha256(content).hexdigest()==digest:
            continue
        candidate=content.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
        if hashlib.sha256(candidate).hexdigest()==digest:
            (repository/path).write_bytes(candidate)
            restored.append(path)
    print(json.dumps({'lineEndingsRestored':restored}))
    raise SystemExit(0)
if report_file.exists():
    raise SystemExit('Baseline exists; use --verify')
hashes = {path:hashlib.sha256((repository/path).read_bytes()).hexdigest() for path in paths}
report_file.parent.mkdir(parents=True,exist_ok=True)
report_file.write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(json.dumps({'protected':len(hashes)}))
