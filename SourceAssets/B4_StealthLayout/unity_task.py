from pathlib import Path
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REPOSITORY = Path(__file__).resolve().parents[2]
PROJECT = REPOSITORY / 'Unity/After_Seconds_Build_V0.01'
CLI = Path('C:/Users/Administrator/AppData/Local/Unity/bin/unity.exe')
command = [str(CLI), 'command', *sys.argv[1:], '--caller', 'plugin', '--skill', 'unity-cli', '--project-path', str(PROJECT), '--format', 'json']
result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=240)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
if result.returncode:
    raise SystemExit(result.returncode)
response = json.loads(result.stdout)
payload = response.get('data', {}).get('result', {}) if isinstance(response.get('data'), dict) else {}
if not response.get('success') or (isinstance(payload, dict) and payload.get('success') is False):
    raise SystemExit(1)
