"""병/인쇄물/기구 간섭 공통 보수. 작성자: 송예찬."""
from pathlib import Path
import bpy,math,json,runpy
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent

def apply(e,name):
    box,cyl,mesh=e['box'],e['cyl'],e['mesh'];display=runpy.run_path(str(H.parent/'C01_InstrumentDetail/display_geometry.py'))
    for key,col in [('PR_VialGlass',(.7,.83,.84,.20)),('PR_Polymer',(.78,.84,.84,1)),('PR_SampleFluid',(.32,.54,.49,1))]:display['mat'](e,key,col)
    for k in ['SpecimenA','SpecimenB','Reagent','Pouch']:display['mat'](e,'PR_Label_'+k)
    def remove(prefix):
        for ob in list(bpy.context.scene.objects):
            if ob.name.startswith(prefix):bpy.data.objects.remove(ob,do_unlink=True)
    def objects(prefix):return [o for o in bpy.context.scene.objects if o.name.startswith(prefix)]
    def bounds(o):
        vs=[o.matrix_world@v.co for v in o.data.vertices];return [min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]
    def lathe(n,x,y,z,profile,mat,segments=32,knurl=False):
        vs=[]
        for j,(dy,r) in enumerate(profile):
            for i in range(segments):
                a=i*math.tau/segments;rr=r*(1+(.038 if i%2==0 else -.018)) if knurl and j in [2,3] else r;vs.append((x+rr*math.cos(a),y+dy,z+rr*math.sin(a)))
        fs=[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(profile)-1) for i in range(segments)]
        fs.extend([tuple(range(segments-1,-1,-1)),tuple((len(profile)-1)*segments+i for i in range(segments))]);ob=mesh(n,vs,fs,mat,0,True);ob['rounded_surface']=True;ob['knurl_surface']=knurl;return ob
    def wrap(n,x,y,z,r,h,mat,half=math.pi/2,segments=16):
        # Same angular samples as the 32-sided bottle: constant 0.18 mm surface offset.
        angles=[-half+2*half*i/segments for i in range(segments+1)];vs=[(x+r*math.sin(a),y+dy*h/2,z+r*math.cos(a)) for dy in [-1,1] for a in angles];k=segments+1
        ob=mesh(n,vs,[(i,i+1,k+i+1,k+i) for i in range(segments)],mat,0,True);uv=ob.data.uv_layers.new(name='UVMap')
        for p in ob.data.polygons:
            for li in p.loop_indices:
                vi=ob.data.loops[li].vertex_index;uv.data[li].uv=(1-(vi%k)/segments,vi//k)
        ob['display_uv']=True;ob['label_standoff_m']=.00018;return ob
    def horizontal(n,x,y,z,w,d,mat):
        ob=display['make_quad'](e,n,x,y,z,w,d,mat);pivot=Vector(e['xyz'](x,y,z));ob.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-pivot)@ob.matrix_world
        # Printed text is upright from the working side (+Z).
        for uv in ob.data.uv_layers.active.data:uv.uv=(uv.uv.x,1-uv.uv.y)
        return ob
    bottles=objects('Specimen_Vial');remove('Vial_Cap');remove('Vial_Label');records=[]
    for index,o in enumerate(bottles):
        lo,hi=bounds(o);x,z=-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2;y=lo[2];h=hi[2]-lo[2];r=(hi[0]-lo[0])/2;bpy.data.objects.remove(o,do_unlink=True)
        small=r<.038;profile=[(0,r*.82),(.018*h,r*.94),(.045*h,r),(.69*h,r),(.77*h,r*.96),(.86*h,r*.78),(.91*h,r*.64),(h,r*.64)]
        lathe('PR_Bottle_Body',x,y,z,profile,'PR_VialGlass' if small else 'PR_Polymer')
        if small:
            lathe('PR_Visible_Sample',x,y+h*.05,z,[(0,r*.75),(.02*h,r*.86),(.49*h,r*.86),(.50*h,r*.84)],'PR_SampleFluid')
        # Proportional threaded closure: neck collar, tamper ring and fine grip flutes.
        lathe('PR_Neck_Collar',x,y+h*.93,z,[(0,r*.64),(.008,r*.66)],'PR_Polymer')
        ch=min(.018,max(.010,h*.10));cr=r*.79
        lathe('PR_Tamper_Ring',x,y+h-.004,z,[(0,cr*.88),(.001,cr*.94),(.003,cr*.94),(.004,cr*.88)],'Blue')
        lathe('PR_Knurled_Cap',x,y+h,z,[(0,cr*.93),(.0015,cr),(.003,cr),(ch-.003,cr),(ch-.001,cr),(ch,cr*.92)],'Blue',48,True)
        key='Reagent' if not small else ('SpecimenA' if index%2==0 else 'SpecimenB')
        label=wrap('PR_Conformal_Bottle_Label',x,y+h*.44,z,r+.00018,h*.38,'PR_Label_'+key)
        records.append({'center':[x,y,z],'radius':r,'height':h,'material':key,'labelOffset':.00018,'labelFaces':len(label.data.polygons)})
    # Print on cartons rather than attaching a thick colored cuboid.
    remove('Pack_Band')
    for o in objects('Sealed_ReagentPack'):
        lo,hi=bounds(o);x,y,z=-(lo[0]+hi[0])/2,(lo[2]+hi[2])/2,-lo[1]+.00018
        display['make_quad'](e,'PR_Carton_Print',x,y,z,(hi[0]-lo[0])*.87,(hi[2]-lo[2])*.68,'PR_Label_Reagent')
    if name=='CP_OpticalAnalyzer':
        box('PR_Cartridge_Dock',.27,.313,.17,.292,.026,.205,'Blue',.006)
        # Cartridge/monitor gap is measured from evaluated geometry below.
    elif name=='CP_PreparationKit':
        for prefix in ['Specimen_Tray','Tray_Rim','Sealed_Specimen_Pouch','PF_Decal_Sealer','Sample_Record_Display']:remove(prefix)
        box('PR_Tray_Base',-.10,.031,.17,.46,.016,.16,'Steel',.004)
        for x in [-.327,.127]:box('PR_Tray_Rim',x,.052,.17,.006,.027,.16,'Steel',.002)
        for z in [.093,.247]:box('PR_Tray_Rim',-.10,.052,z,.448,.027,.006,'Steel',.002)
        for x in [-.25,-.105,.04]:
            box('PR_Sealed_Pouch',x,.0402,.17,.095,.0018,.115,'Paper',.0004)
            horizontal('PR_Pouch_Print',x,.0413,.17,.087,.105,'PR_Label_Pouch')
        horizontal('PR_Tablet_Pixels',.31,.0828,.15,.235,.15,'ID_LCD_Printer')
    elif name=='ID_PipetteWorkstation':
        remove('PF_Decal_Pipette')
        for x in [.17,.27,.37]:wrap('PR_Pipette_Calibration',x,.33,-.06,.01818,.075,'PF_Decal_Pipette',math.pi/4,8)
    elif name in ['ID_SterileSealer','ID_LabelPrinter']:
        if name=='ID_SterileSealer':
            for p in ['Sterile_Pouch','Pouch_Seal','Pouch_Weld_Seam','PF_Decal_Sealer']:remove(p)
            for x in [-.20,0,.20]:
                box('PR_Sterile_Pouch',x,.161,.10,.16,.0018,.24,'Paper',.0003)
                horizontal('PR_Sealed_Print',x,.1621,.10,.148,.226,'PR_Label_Pouch')
                for dx in [-.074,.074]:box('PR_Fused_Edge',x+dx,.1622,.10,.002,.0003,.22,'Blue',0)
        else:
            remove('Printed_Label_Strip');remove('PF_Decal_Barcode')
            rows=[(.226,.222),(.217,.240),(.194,.270),(.181,.300),(.178,.320)]
            paper=mesh('PR_Fed_Output_Paper',[(x,y,z) for y,z in rows for x in [-.09,.09]],[(j*2,j*2+1,j*2+3,j*2+2) for j in range(len(rows)-1)],'PF_Decal_Barcode',0,True)
            uv=paper.data.uv_layers.new(name='UVMap')
            for poly in paper.data.polygons:
                for li in poly.loop_indices:
                    vi=paper.data.loops[li].vertex_index;uv.data[li].uv=(1-vi%2,1-(vi//2)/(len(rows)-1))
            paper['display_uv']=True;solid=paper.modifiers.new('Paper_Thickness','SOLIDIFY');solid.thickness=.00045
    # Evidence is measured in source coordinates, before merging parts in FBX.
    evidence={'asset':name,'bottles':records,'oldCubeBottleLabels':len(objects('Vial_Label'))}
    if name=='CP_OpticalAnalyzer':
        monitor=[o for o in bpy.context.scene.objects if any(o.name.startswith(p) for p in ['Display_Recess','Bezel_','LCD_','Optical_CoverGlass'])]
        bottom=min(bounds(o)[0][2] for o in monitor);top=max(bounds(o)[1][2] for o in objects('Inserted_Cartridge'));evidence['monitorCartridgeClearanceM']=bottom-top;assert bottom-top>.02
    if name=='CP_PreparationKit':
        evidence['pouchesInsideTray']=all(-.324<-bounds(o)[1][0] and -bounds(o)[0][0]<.124 and .096<-bounds(o)[1][1] and -bounds(o)[0][1]<.244 for o in objects('PR_Sealed_Pouch'));assert evidence['pouchesInsideTray']
    if name=='ID_DualVortexMixer':evidence['vialBaseAboveCupFloorM']=min(b['center'][1] for b in records)-.224
    (H/(name+'.json')).write_text(json.dumps(evidence,indent=2),encoding='utf-8')
