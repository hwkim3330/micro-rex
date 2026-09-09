"""Compare the actual compiled robot interfaces and mesh outputs; no hardware claims."""
from pathlib import Path
import json,os,hashlib
os.environ.setdefault('MUJOCO_GL','disable')
import mujoco,numpy as np,trimesh
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def grounded(path):
    tree=ET.parse(path);r=tree.getroot();r.find('compiler').set('meshdir',str(ROOT/'vendor/microduck/assets'))
    ET.SubElement(r.find('worldbody'),'geom',name='test_ground',type='plane',size='2 2 .01')
    return mujoco.MjModel.from_xml_string(ET.tostring(r,encoding='unicode'))
base=grounded(ROOT/'vendor/microduck/robot_walk.xml')
rex=grounded(ROOT/'models/micro_rex.xml')
checks=[]
def check(condition,label):
    if not condition:raise AssertionError(label)
    checks.append(label)
check(base.nq==rex.nq and base.nv==rex.nv and base.nu==rex.nu,'Same configuration, velocity and control dimensions')
for obj,n in [(mujoco.mjtObj.mjOBJ_JOINT,base.njnt),(mujoco.mjtObj.mjOBJ_ACTUATOR,base.nu),(mujoco.mjtObj.mjOBJ_SENSOR,base.nsensor)]:
    check([mujoco.mj_id2name(base,obj,i) for i in range(n)]==[mujoco.mj_id2name(rex,obj,i) for i in range(n)],f'Preserved names and order: {obj.name}')
for key in ['body_parentid','body_pos','body_quat','jnt_range','jnt_axis','jnt_pos','jnt_qposadr','jnt_dofadr','actuator_trnid','actuator_ctrlrange','actuator_forcerange','sensor_type','sensor_dim','sensor_objid']:
    check(np.array_equal(getattr(base,key),getattr(rex,key)),f'Preserved {key}')
glb=trimesh.load(ROOT/'models/micro_rex.glb',force='scene')
colors=set()
for geometry in glb.geometry.values():
    colors.update(map(tuple,geometry.visual.to_color().vertex_colors.tolist() if hasattr(geometry.visual,'to_color') else geometry.visual.vertex_colors.tolist()))
check(len(colors)>=4,'GLB retains distinct material colors')
parts=json.loads((ROOT/'artifacts/parts.json').read_text())
for p in parts:
    mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
    check(mesh.is_watertight and mesh.volume>0,f'Closed positive-volume STL: {p["name"]}')
    check((ROOT/p['step']).is_file(),f'Editable STEP exists: {p["name"]}')
check(float(rex.body_mass.sum())>float(base.body_mass.sum()),'Added mass is included in dynamics')
# Compare dynamics without claiming a pretrained policy still balances the changed body.
states={}
for name,m in [('microduck',base),('micro_rex',rex)]:
    d=mujoco.MjData(m);mujoco.mj_forward(m,d);com=d.subtree_com[1].copy()
    # Holding upstream HOME pose, default native PD, 3 s. Report tilt and height, even on failure.
    home=np.array([0,-.0873,-.4579,-.0049,.4530,.3491,.3491,0,0,0,.0873,.4579,.0049,-.4530])
    d.qpos[7:]=home;d.ctrl[:]=home
    mujoco.mj_forward(m,d)
    for _ in range(round(3/m.opt.timestep)):mujoco.mj_step(m,d)
    check(np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all(),f'{name}: 3 s finite CPU dynamics')
    tilt=float(np.degrees(np.arccos(np.clip(d.xmat[1].reshape(3,3)[2,2],-1,1))))
    states[name]={'mass_kg':float(m.body_mass.sum()),'reference_com_m':com.tolist(),'hold_3s_trunk_z_m':float(d.xpos[1,2]),'hold_3s_tilt_deg':tilt,'upright_3s':tilt<15 and float(d.xpos[1,2])>.08}
report={'checks_passed':len(checks),'checks':checks,'nq':rex.nq,'nv':rex.nv,'nu':rex.nu,'states':states,'added_mass_g':(states['micro_rex']['mass_kg']-states['microduck']['mass_kg'])*1000,'hardware_fit':'UNVERIFIED','policy_performance':'NOT VALIDATED; 14-action ABI preservation does not prove policy or sim-to-real compatibility','manufacturing':'Prototype CAD; physical fit, tolerances and fasteners require validation'}
policy_path=ROOT/'artifacts/policy_evaluation.json'
if policy_path.exists():
    policy=json.loads(policy_path.read_text())
    report['policy_performance']='Scoped ONNX/BAM simulation results in policy_evaluation.json; command tracking and hardware compatibility are not established'
    report['policy_simulation_report']='artifacts/policy_evaluation.json'
    for path,sha in policy['model_sha256'].items():check(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,'Current policy test model '+path)
    for name in ['microduck','micro_rex']:
        replay=json.loads((ROOT/f'artifacts/policy_replay_{name}.json').read_text())
        check(len(replay['joint_names'])==14 and len(replay['qpos'])==round(replay['result']['duration_s']/replay['dt']),'Policy replay dimensions '+name)
        check(np.isfinite(replay['qpos']).all() and np.array(replay['qpos']).shape[1]==21,'Policy replay finite '+name)
files=[p for folder in ['models','cad','drawings'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p)]
(ROOT/'artifacts/SHA256SUMS.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n')
report['checks_passed']=len(checks)
(ROOT/'artifacts/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
