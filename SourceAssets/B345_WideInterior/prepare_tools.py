from pathlib import Path
S=Path(__file__).resolve().parent;R=S.parents[1]
p=(R/'SourceAssets/B345_ArchedInterior/build_arches.py').read_text(encoding='utf-8')
a=p.index('def arch_profile(');b=p.index('def cove(',a)
p=p[:a]+'''def arch_profile(w,h):
 left=-w/2+.32;rx=-left;ry=rx;top=h-.18;cy=top-ry
 path=[(left+.14,.06),(left+.14,.25),(left+.09,.48),(left+.025,.80),(left,1.1),(left,cy)]
 for i in range(1,33):
  angle=math.pi-i*math.pi/32;path.append((rx*math.cos(angle),cy+ry*math.sin(angle)))
 path.extend([(-x,y) for x,y in reversed(path[:6][:-1])])
 return path
''' +p[b:]
p=p.replace(".012 if mat=='Shell' else .004",".022 if mat=='Shell' else .005")
p=p.replace("rad=.62 if min(cw,cd)<4 else .80","rad=1.02 if room['kind']=='corridor' else .80")
p=p.replace("band(name,arch_profile(width,h),mapper,.28,.16)","band(name,arch_profile(width,h),mapper,.44,.24)")
p=p.replace("band(name+'_InnerSeal',arch_profile(width-.13,h-.055),mapper,.10,.022,'Inset')","band(name+'_InnerSeal',arch_profile(width-.22,h-.095),mapper,.12,.025,'Inset')")
p=p.replace('width/2-.215','width/2-.46').replace('width/2-.19','width/2-.32')
p=p.replace("[.28 if horizontal else .16,.90,.16 if horizontal else .28]","[.44 if horizontal else .24,.90,.24 if horizontal else .44]")
p=p.replace("[.28 if horizontal else .16,1.98,.16 if horizontal else .28]","[.44 if horizontal else .24,1.50,.24 if horizontal else .44]")
p=p.replace("[uu-24,1.89,vv-16]","[uu-24,1.65,vv-16]")
p=p.replace("bx=side*(width/2-.26)","bx=side*(width/2-.43)").replace('2.55','1.95').replace('.29 if horizontal else .035','.45 if horizontal else .035').replace('.035 if horizontal else .29','.035 if horizontal else .45')
p=p.replace('int(length/6)','int(length/8)')
p=p.replace("h-.055,pv,1.65 if horizontal else width-1.05,.045,width-1.05 if horizontal else 1.65,'Inset',.009","h-.004,pv,1.70 if horizontal else 1.02,.038,1.02 if horizontal else 1.70,'Shell',.008")
p=p.replace("h-.083,pv,1.48 if horizontal else width-1.22,.020,width-1.22 if horizontal else 1.48,'Diffuser',.006","h-.025,pv,1.55 if horizontal else .87,.014,.87 if horizontal else 1.55,'Diffuser',.003")
p=p.replace("'intensity':13.0","'intensity':14.0")
p=p.replace("palette={'Shell'","palette={'Floor':(.49,.51,.52,1),'Ceiling':(.77,.79,.79,1),'Shell'")
p=p.replace("  horizontal=w>d;", "  box(rid+'_Floor_SeamBacking',u+w/2,-.18,v+d/2,w,.08,d,'Floor',.003)\n  box(rid+'_Ceiling_SeamBacking',u+w/2,h+.12,v+d/2,w,.10,d,'Ceiling',.003)\n  horizontal=w>d;")
# Continuous half-cylinder, with side-door lunettes; no flat ceiling visible inside the corridors.
a=p.index('  inset=.16;');b=p.index("  if room['kind']!='corridor':continue",a)
old=p[a:b];p=p[:a]+"  if room['kind']=='corridor':\n   tunnel(room,h,plan);rows['roomsWithCoves'].append(rid)\n  elif room.get('roof',{}).get('kind')=='dome':\n   dome(room,rows);rows['roomsWithCoves'].append(rid)\n  else:\n"+''.join(' '+line+'\n' for line in old.splitlines())+p[b:]
p=p.replace('def export(floor,rows):',(S/'tunnel_geometry.txt').read_text(encoding='utf-8')+'\n'+(S/'dome_geometry.txt').read_text(encoding='utf-8')+'\ndef export(floor,rows):')
p=p.replace("<1.6 for door in relevant","<2.65 for door in relevant")
p=p.replace("    chosen=a;break","    if any(abs(a-bay['x'])<1.25 for bay in plan.get('serviceBays',[]) if horizontal and v-.01<bay['y']<v+d+.01):continue\n    chosen=a;break")
p=p.replace("(0,.65,-.65,1.1,-1.1)","(0,.65,-.65,1.1,-1.1,1.6,-1.6)")
p=p.replace("[uu-24,1.65,vv-16]","[uu-24,1.45,vv-16]").replace(".24,1.50,.24", ".24,1.10,.24")
p='\n'.join(line for line in p.splitlines() if "box(rid+'_Recess_'" not in line and "box(rid+'_Diffuser_'" not in line)+'\n'
p=p.replace("f'AR_{floor}_Interior.blend'","f'WA_{floor}_Interior.blend'").replace("f'AR_{floor}_Interior.fbx'","f'WA_{floor}_Interior.fbx'")
# Close two short perimeter gaps where rigid stair/core projection meets enlarged corridors.
p=p.replace('\n export(floor,rows)', '''
 for v,d in ((.4,.8),(33.4,1.2)):
  box('Core_Junction_Closure',42.6,2,v,.24,4,d,'Shell',.01)
  rows['colliders'].append({'name':'Core_Junction_'+str(v),'center':[18.6,2,v-16],'size':[.24,4,d]})
 export(floor,rows)''')
(S/'build_arches.py').write_text(p,encoding='utf-8')
# External-only checkers use updated routes and map fixed old-section sample points.
for old,new in [('ValidateArches','WideValidate'),('ArchWalk','WideWalk'),('ArchReview','WideReview')]:
 p=(R/f'SourceAssets/B345_ArchedInterior/{old}.cs').read_text(encoding='utf-8').replace(old,new).replace('2026-11-06_B345_ArchedInterior','2026-11-06_B345_WideInterior')
 if old=='ArchWalk':
  p=p.replace('new Vector3(u-24,h,v-16)','new Vector3(WideX(u)-24,h,WideY(v,u>=38.99f)-16)')
  p=p.replace('p=>P((float)p[0],0,(float)p[1])','p=>new Vector3((float)p[0]-24,0,(float)p[1]-16)')
 if old=='ArchReview':p=p.replace('new Vector3(a[0],a[1],a[2]),new Vector3(a[3],a[4],a[5])','Map(new Vector3(a[0],a[1],a[2])),Map(new Vector3(a[3],a[4],a[5]))')
 if old=='ArchReview':p=p.replace('new[]{-20f,1.65f,9.5f','new[]{-18f,1.65f,9.5f')
 if old=='ValidateArches':p=p.replace('foreach(Transform prop in root.transform.Find("Dressing_Props"))','foreach(Transform prop in root.transform.Find("Dressing_Props").Cast<Transform>().Concat(root.transform.Find("Corridor_WallEquipment").Cast<Transform>()))')
 if old=='ValidateArches':p=p.replace('public static object ReflectionsB5()', 'public static object ReflectionsB4()=>ReflectFloors(new[]{"B4"});\n public static object ReflectionsB5()')
 if old=='ValidateArches':
  p=p.replace('p.resolution=128;bool ok=Lightmapping.BakeReflectionProbe', 'p.resolution=128;p.renderDynamicObjects=true;bool ok=Lightmapping.BakeReflectionProbe')
  p=p.replace('floors.Length==1?"reflections_B5_final":"reflections"', 'floors.Length==1?"reflections_"+floors[0]+"_final":"reflections"')
 if old=='ArchReview':p=p.replace('public static object Inspect(string stage){','public static object AfterB4()=>Inspect("After",new[]{"B4"});\n public static object Inspect(string stage,string[] only=null){').replace('foreach(string f in new[]{"B5","B4","B3"}){\n   var s=', 'foreach(string f in only??new[]{"B5","B4","B3"}){\n   var s=')
 if old in ('ArchWalk','ArchReview'):
  methods=(S/'WarpMethods.txt').read_text(encoding='utf-8')
  p=p.replace('public static class '+new+' {','public static class '+new+' {\n'+methods)
 (S/f'{new}.cs').write_text(p,encoding='utf-8')
