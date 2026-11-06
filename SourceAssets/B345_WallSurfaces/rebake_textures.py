from pathlib import Path
p=Path(__file__).resolve().parent/'build_walls.py'
exec(compile(p.read_text(encoding='utf-8-sig').split("if __name__=='__main__':")[0],str(p),'exec'))
textures()
