"""Inset physical LCD modules, with texture UVs and a separate optical cover."""
import bpy
def make_quad(e,name,x,y,z,w,h,mat):
 ob=e['mesh'](name,[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)],[(0,3,2,1)],mat,0)
 # Recalculate-face-normals is ambiguous on isolated open planes; explicitly face the bezel front.
 if ob.data.polygons[0].normal.y>0:ob.data.flip_normals()
 uv=ob.data.uv_layers.new(name='UVMap');coords=[(1,0),(0,0),(0,1),(1,1)]
 for poly in ob.data.polygons:
  for li in poly.loop_indices:uv.data[li].uv=coords[ob.data.loops[li].vertex_index]
 ob['display_uv']=True;return ob
def mat(e,name,color=(1,1,1,1)):
 if name not in e['mats']:
  m=bpy.data.materials.new(name);m.diffuse_color=color;e['mats'][name]=m
 return name
def screen(e,x,y,z,w=.47,h=.28,kind='Assay'):
 b=e['box'];m=mat(e,'ID_LCD_'+kind);glass=mat(e,'ID_DisplayGlass',(.4,.6,.65,.045))
 rim=min(.017,w*.055)
 b('Display_Recess',x,y,z,w+rim*2.7,h+rim*2.7,.052,'Dark',.008)
 for xx in [x-w/2-rim/2,x+w/2+rim/2]:b('Bezel_Side',xx,y,z+.036,rim,h+rim*2,.026,'Dark',.005)
 for yy in [y-h/2-rim/2,y+h/2+rim/2]:b('Bezel_Rail',x,yy,z+.036,w,rim,.026,'Dark',.004)
 make_quad(e,'LCD_ActivePixels',x,y,z+.0268,w,h,m)
 make_quad(e,'Optical_CoverGlass',x,y,z+.035,w,h,glass)
 b('Standby_Indicator',x+w*.43,y-h/2-rim*.53,z+.050,.006,.002,.002,'Trace',0)
def nameplate(e,x,y,z,w=.18,kind='Optics'):
 m=mat(e,'ID_Label_'+kind);e['box']('Recessed_Nameplate',x,y,z,w+.008,w*.25+.008,.006,'Dark',.002)
 make_quad(e,'Manufactured_Label',x,y,z+.0031,w,w*.25,m)
