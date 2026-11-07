from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'verify_plan.py';s=p.read_text(encoding='utf-8')
old='labelchecks=[]'
new='''# Include the five additional as-built T01/T02 destination text footprints.
g=json.loads((H/'geometry.json').read_text(encoding='utf-8'))['corridor']
o=np.array([g['origin'][0],g['origin'][2]]);f=np.array([g['direction'][0],g['direction'][2]]);r=np.array([f[1],-f[0]])
for name,x,z in [('T02_VA_departure',1.15,2.5),('T02_VA_arrival',1.15,11.26),('T02_C02_departure',-1.15,11.26),('T02_C01_return',-1.15,3.8)]:
 c=o+r*x+f*z;poly=np.array([c+r*dx+f*dz for dx,dz in [(-.3,-.7),(.3,-.7),(.3,.7),(-.3,.7),(-.3,-.7)]]);labels.append((name,poly))
o=np.array([-17.23132775,-1.074689]);f=np.array([-.242535625,.9701425]);r=np.array([f[1],-f[0]]);c=o+r*1.15+f*6.73
labels.append(('T01_VA_through',np.array([c+r*dx+f*dz for dx,dz in [(-.3,-.7),(.3,-.7),(.3,.7),(-.3,.7),(-.3,-.7)]])))
labelchecks=[]'''
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
