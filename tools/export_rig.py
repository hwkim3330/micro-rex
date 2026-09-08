"""Export upstream body transforms and joint axes for a kinematic browser rig."""
import os
os.environ.setdefault('MUJOCO_GL','disable')
from pathlib import Path
import json
import mujoco
ROOT=Path(__file__).resolve().parents[1]
m=mujoco.MjModel.from_xml_path(str(ROOT/'vendor/microduck/robot_walk.xml'))
d=mujoco.MjData(m);mujoco.mj_forward(m,d)
bodies=[]
for i in range(1,m.nbody):
    joints=[]
    for j in range(m.body_jntadr[i],m.body_jntadr[i]+m.body_jntnum[i]):
        if m.jnt_type[j]!=mujoco.mjtJoint.mjJNT_HINGE:continue
        joints.append(dict(name=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,j),axis=m.jnt_axis[j].tolist(),pivot=m.jnt_pos[j].tolist(),range=m.jnt_range[j].tolist()))
    bodies.append(dict(id=i,parent=int(m.body_parentid[i]),name=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,i),position=m.body_pos[i].tolist(),quaternion=m.body_quat[i].tolist(),joints=joints))
meshes={}
for i in range(m.ngeom):
    if m.geom_type[i]==mujoco.mjtGeom.mjGEOM_MESH and m.geom_group[i]==2:
        meshes[f'stock_{i}']=dict(body=int(m.geom_bodyid[i]),label=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_MESH,int(m.geom_dataid[i])))
for p in json.loads((ROOT/'artifacts/parts.json').read_text()):
    meshes[p['name']]=dict(body=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,p['parent']),label=p['name'])
(ROOT/'models/rig.json').write_text(json.dumps(dict(bodies=bodies,meshes=meshes,mode='kinematic; no physics or collision enforcement'),indent=2)+'\n')
print('Exported',sum(len(b['joints']) for b in bodies),'hinge joints')
