from pathlib import Path
H=Path(__file__).resolve().parent
s=(H/'prepare.py').read_text(encoding='utf8')
exec(s[s.index('for old,new in'):])
