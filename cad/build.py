"""Micro Rex parametric retrofit, millimetres. Prototype fit requires physical checking."""
from pathlib import Path
import json, math, hashlib
import cadquery as cq
import numpy as np
import trimesh
import mujoco
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
for name in ['models/parts','models/step','artifacts','drawings']: (ROOT/name).mkdir(parents=True,exist_ok=True)
parts=[]
def add(name,shape,body,color):
    if not shape.val().isValid(): raise ValueError(name+' invalid CAD')
    stl=ROOT/'models/parts'/f'{name}.stl';step=ROOT/'models/step'/f'{name}.step'
    cq.exporters.export(shape,str(stl),tolerance=0.04,angularTolerance=0.08)
    cq.exporters.export(shape,str(step))
    mesh=trimesh.load_mesh(stl,process=True)
    if not mesh.is_watertight: raise ValueError(name+' non-watertight')
    mass=shape.val().Volume()*1.24e-6
    parts.append({'name':name,'body':body,'color':color,'shape':shape,'mesh':mesh,'mass_kg':mass})
    return shape
jade=[0.16,0.48,0.37,1];gold=[1,0.51,0.12,1];ivory=[0.94,0.89,0.71,1];dark=[0.08,0.14,0.15,1]
# Rounded removable cheek covers follow the original head rather than extending its skeleton.
profile=[(-20,251),(-16,271),(0,282),(36,284),(65,279),(88,266),(98,251),(86,245),(64,247),(45,239),(13,233),(-11,236)]
for side,y in [('left',46),('right',-44)]:
    shape=cq.Workplane('XZ',origin=(0,y,0)).spline(profile,periodic=True).close().extrude(2)
    sign=1 if side=='left' else -1
    # Inside relief leaves a 1.2 mm face, 3 mm perimeter rib and full-thickness screw lands.
    pocket=cq.Workplane('XZ',origin=(0,sign*43.9,0)).spline(profile,periodic=True).close().offset2D(-3).extrude(-sign*.9)
    for x,z in [(29,265),(-6,278),(36,280)]:
        land=cq.Workplane('XZ',origin=(x,sign*47,z)).circle(5).extrude(sign*5)
        pocket=pocket.cut(land)
    shape=shape.cut(pocket)
    # Continuous cheek face; a clearance hole receives the eye's locating stem.
    shape=shape.cut(cq.Workplane('XZ',origin=(29,y+1,265)).circle(2.7).extrude(4))
    # M2 clearance; independent cross ties support the cheeks above the stock shell.
    for x,z in [(-6,278),(36,280)]:
        shape=shape.cut(cq.Workplane('XZ',origin=(x,y+1,z)).circle(1.2).extrude(4))
    add('skull_cheek_'+side,shape,'jaw_soft',jade)
    # Separate blunt teeth rail, safely rounded triangular design, not functional biting.
    points=[(61,249),(96,249),(90,241),(85,246),(78,240),(72,246),(65,242)]
    add('teeth_'+side,cq.Workplane('XZ',origin=(0,48 if side=='left' else -46,0)).polyline(points).close().extrude(2).edges('|Y').fillet(.7),'jaw_soft',ivory)
    sign=1 if side=='left' else -1
    eye=cq.Workplane('XY').sphere(13).translate((29,sign*40,265))
    eye=eye.intersect(cq.Workplane('XY').box(40,8,40).translate((29,sign*50.3,265)))
    stem=cq.Workplane('XZ',origin=(29,sign*46.3,265)).circle(2.5).extrude(sign*2)
    eye=eye.union(stem)
    pilot=cq.Workplane('XZ',origin=(29,sign*44.3,265)).circle(.8).extrude(-sign*6)
    eye=eye.cut(pilot)
    add('brow_'+side,eye,'jaw_soft',ivory) # retained part ID; now a convex eye finish carrier
# Roof bridges are open underneath; end bosses carry cheek screws.
for index,(x,z) in enumerate([(-6,278),(36,280)]):
    bridge=cq.Workplane('XY').box(7,92,4).edges('|Z').fillet(2).translate((x,0,z+4))
    for y in [-41,41]:
        boss=cq.Workplane('XY').box(7,6,8).translate((x,y,z+2))
        hole=cq.Workplane('XZ',origin=(x,y+5,z)).circle(1.2).extrude(10)
        bridge=bridge.union(boss).cut(hole)
    for y in [-18,18]:
        bridge=bridge.cut(cq.Workplane('XY').box(4,2,6).translate((x,y,z+4)))
    add('head_bridge_'+str(index+1),bridge,'jaw_soft',jade)
# Three hollow tail segments: shallow sockets can be tuned in a CAD editor.
anchors=[(-52,0,149,11),(-99,0,153,8),(-142,0,170,5),(-180,0,187,2)]
for i in range(3):
    a=np.array(anchors[i][:3],float);b=np.array(anchors[i+1][:3],float);v=b-a;length=np.linalg.norm(v)
    r0=anchors[i][3];r1=anchors[i+1][3]
    outer=cq.Solid.makeCone(r0,r1,length,cq.Vector(*a),cq.Vector(*v))
    inner=cq.Solid.makeCone(max(0.6,r0-1.6),max(0.5,r1-1.6),length+0.1,cq.Vector(*a),cq.Vector(*v))
    add('tail_segment_'+str(i+1),cq.Workplane(obj=outer.cut(inner)),'trunk_base',jade)
# Strap-mounted tail saddle: slotted, no unverified stock screw pattern assumed.
saddle=cq.Workplane('YZ',origin=(-51,0,144)).rect(34,30).extrude(3)
for y in [-12,12]:
    saddle=saddle.cut(cq.Workplane('YZ',origin=(-52,y,141)).rect(3,17).extrude(6))
add('tail_saddle',saddle,'trunk_base',gold)
# Little forelimbs are removable static styling; no extra policy outputs.
for side,sign in [('left',1),('right',-1)]:
    poly=[(4,174),(17,177),(32,163),(40,166),(46,161),(38,154),(29,155),(14,166),(4,165)]
    arm=cq.Workplane('XZ',origin=(0,39 if sign==1 else -36,0)).polyline(poly).close().extrude(3).edges('|Y').fillet(.7)
    arm=arm.cut(cq.Workplane('XZ',origin=(10,40 if sign==1 else -35,170)).circle(1.2).extrude(5))
    add('forearm_'+side,arm,'trunk_base',jade)
    bracket=cq.Workplane('XY').box(10,10,15).translate((10,sign*31,168))
    bracket=bracket.cut(cq.Workplane('XZ',origin=(10,sign*31+8,170)).circle(1.2).extrude(16))
    bracket=bracket.cut(cq.Workplane('YZ',origin=(3,sign*31,163)).rect(3,4).extrude(14))
    add('arm_standoff_'+side,bracket,'trunk_base',gold)

# Save added-parts assembly as exact CAD. Positions are reference zero-pose coordinates.
assembly=cq.Assembly(name='Micro_Rex_Retrofit')
for p in parts: assembly.add(p['shape'],name=p['name'],color=cq.Color(*p['color']))
assembly.export(str(ROOT/'models/micro_rex_retrofit.step'))
# Compose original robot and additions into a portable MJCF. Preserve joint/sensor ABI.
upstream=ROOT/'vendor/microduck/robot_walk.xml'
m=mujoco.MjModel.from_xml_path(str(upstream));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
tree=ET.parse(upstream);xml=tree.getroot();xml.set('model','micro_rex')
xml.find('compiler').set('meshdir','../vendor/microduck/assets')
asset=xml.find('asset'); scene=trimesh.Scene(); bm={}
for p in parts:
    bid=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,p['body'])
    R=d.xmat[bid].reshape(3,3);t=d.xpos[bid]
    local=p['mesh'].copy();local.vertices=(local.vertices*0.001-t)@R
    local.export(ROOT/'models/parts'/f"{p['name']}_local.stl")
    ET.SubElement(asset,'mesh',name=p['name'],file=f"../../../models/parts/{p['name']}_local.stl")
    body=xml.find(f".//body[@name='{p['body']}']")
    ET.SubElement(body,'geom',name='rex_'+p['name'],type='mesh',mesh=p['name'],**{'class':'visual','rgba':' '.join(map(str,p['color'])),'mass':'0'})
    # Account for additive mass and inertia; stock inertial values remain in aggregate.
    bm.setdefault(p['body'],[]).append((p['mass_kg'],local))
    world=p['mesh'].copy()
    colors=np.tile((np.array(p['color'])*255).astype(np.uint8),(len(world.vertices),1))
    if p['name'].startswith('brow_'):
        x,y,z=world.vertices.T;sgn=1 if p['name'].endswith('left') else -1
        pupil=(sgn*y>46.3)&(((x-31)/6.4)**2+((z-265)/7.8)**2<1)
        colors[pupil]=[15,32,29,255]
        glint=pupil&(((x-29)/2.0)**2+((z-268)/2.3)**2<1)
        colors[glint]=[255,253,239,255]
        # A painted black pupil approximation for the MuJoCo visual renderer.
        # Zero mass/collision; finish does not add a mechanical component.
        point=(np.array([31,sgn*51.9,265])*.001-t)@R
        ET.SubElement(body,'geom',name='finish_'+p['name'],type='sphere',pos=' '.join(map(str,point)),size='.006',rgba='.04 .08 .07 1',mass='0',contype='0',conaffinity='0',group='2')
    world.vertices*=0.001;world.visual.vertex_colors=colors
    scene.add_geometry(world,node_name=p['name'])
# Combine inertias in body coordinates using parallel axis theorem.
for body_name,added in bm.items():
    body=xml.find(f".//body[@name='{body_name}']");e=body.find('inertial')
    mass=float(e.get('mass'));c=np.fromstring(e.get('pos'),sep=' ');v=np.fromstring(e.get('fullinertia'),sep=' ')
    I=np.array([[v[0],v[3],v[4]],[v[3],v[1],v[5]],[v[4],v[5],v[2]]])
    all_items=[(mass,c,I)]
    for am,mesh in added:
        props=mesh.mass_properties;ratio=am/props['mass']
        all_items.append((am,props['center_mass'],props['inertia']*ratio))
    total=sum(x[0] for x in all_items);center=sum(mm*cc for mm,cc,_ in all_items)/total
    tensor=sum(ii+mm*(np.eye(3)*np.dot(cc-center,cc-center)-np.outer(cc-center,cc-center)) for mm,cc,ii in all_items)
    e.set('mass',str(total));e.set('pos',' '.join(map(str,center)));e.set('fullinertia',' '.join(map(str,[tensor[0,0],tensor[1,1],tensor[2,2],tensor[0,1],tensor[0,2],tensor[1,2]])))
# Visual geometry remains exact surface meshes; conservative separate collision envelopes.
for body_name,added in bm.items():
    body=xml.find(f".//body[@name='{body_name}']")
    for i,(mass,mesh) in enumerate(added):
        lo,hi=mesh.bounds
        ET.SubElement(body,'geom',name=f'rex_collision_{body_name}_{i}',type='box',pos=' '.join(map(str,(lo+hi)/2)),size=' '.join(map(str,np.maximum((hi-lo)/2,0.0005))),group='3',contype='1',conaffinity='1',mass='0',rgba='0.8 0.2 0.1 0.2')
ET.indent(tree);tree.write(ROOT/'models/micro_rex.xml',encoding='unicode')
for i in range(m.ngeom):
    if m.geom_type[i]!=mujoco.mjtGeom.mjGEOM_MESH or m.geom_group[i]!=2:continue
    mid=m.geom_dataid[i];va=m.mesh_vertadr[mid];vn=m.mesh_vertnum[mid];fa=m.mesh_faceadr[mid];fn=m.mesh_facenum[mid]
    vertices=m.mesh_vert[va:va+vn]@d.geom_xmat[i].reshape(3,3).T+d.geom_xpos[i]
    mesh=trimesh.Trimesh(vertices=vertices,faces=m.mesh_face[fa:fa+fn],process=False)
    color=m.mat_rgba[m.geom_matid[i]] if m.geom_matid[i]>=0 else m.geom_rgba[i]
    mesh.visual.vertex_colors=(np.array(color)*255).astype(np.uint8)
    scene.add_geometry(mesh,node_name=f'stock_{i}')
scene.export(ROOT/'models/micro_rex.glb')
report=[]
for p in parts:
    mesh=p['mesh'];bounds=mesh.bounds
    report.append({'name':p['name'],'parent':p['body'],'material':'PLA estimate, density 1.24 g/cm3','mass_g':round(p['mass_kg']*1000,3),'dimensions_mm':np.round(mesh.extents,3).tolist(),'bounds_mm':bounds.tolist(),'watertight':bool(mesh.is_watertight),'solids':len(p['shape'].solids().vals()),'stl':f"models/parts/{p['name']}.stl",'step':f"models/step/{p['name']}.step"})
(ROOT/'artifacts/parts.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Built {len(parts)} CAD parts; additive mass {sum(p["mass_kg"] for p in parts)*1000:.1f} g')
