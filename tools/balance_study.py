"""Static projected CoM versus nominal two-foot sole hull, not dynamic balance proof."""
from pathlib import Path
import ast,hashlib,json,math
import mujoco,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
source=R/'upstream/microduck_rl/scripts/infer_policy.py'
home=next(np.array(ast.literal_eval(n.value.args[0])) for n in ast.parse(source.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFAULT_POSE' for t in n.targets))
def hull(points):
    points=sorted(set(map(tuple,points)))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    def half(seq):
        result=[]
        for p in seq:
            while len(result)>1 and cross(result[-2],result[-1],p)<=0:result.pop()
            result.append(p)
        return result
    return np.array(half(points)[:-1]+half(points[::-1])[:-1])
def margin(polygon,point):
    return min(((b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0]))/np.linalg.norm(b-a) for a,b in zip(polygon,np.roll(polygon,-1,axis=0)))
models={'microduck':R/'vendor/microduck/robot_walk.xml','micro_rex':R/'models/micro_rex.xml'}
results={};draw={}
cases=[('HOME',None,0)]+[(joint+suffix,joint,sign*math.radians(15)) for joint in ['neck_pitch','head_pitch','head_roll'] for suffix,sign in [('_minus15',-1),('_plus15',1)]]
for name,path in models.items():
    m=mujoco.MjModel.from_xml_path(str(path));results[name]=[]
    for label,joint,offset in cases:
        d=mujoco.MjData(m);d.qpos[:7]=[0,0,.125,1,0,0,0]
        d.qpos[m.jnt_qposadr[m.actuator_trnid[:,0]]]=home
        if joint:
            j=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,joint);a=m.jnt_qposadr[j];d.qpos[a]=np.clip(d.qpos[a]+offset,*m.jnt_range[j])
        mujoco.mj_forward(m,d)
        feet=[]
        for body in ['ankle_left','ankle_right']:
            b=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,body);points=[]
            for g in range(m.body_geomadr[b],m.body_geomadr[b]+m.body_geomnum[b]):
                if m.geom_contype[g]==0 or m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_MESH:continue
                mid=m.geom_dataid[g];a=m.mesh_vertadr[mid];n=m.mesh_vertnum[mid]
                v=m.mesh_vert[a:a+n]@d.geom_xmat[g].reshape(3,3).T+d.geom_xpos[g]
                points.extend(v[v[:,2]<=v[:,2].min()+.001,:2])
            feet.append(hull(points))
        polygon=hull(np.concatenate(feet));com=d.subtree_com[1].copy()
        entry={'pose':label,'com_mm':np.round(com*1000,3).tolist(),'nominal_two_foot_margin_mm':round(float(margin(polygon,com[:2]))*1000,3)}
        if name=='micro_rex':
            head=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'jaw_soft');trunk=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'trunk_base')
            mass=float(m.body_mass.sum());loaded=(mass*com+.005*d.xpos[head]+.005*d.xpos[trunk])/(mass+.010)
            entry['assumed_10g_hardware_budget_com_mm']=np.round(loaded*1000,3).tolist()
            entry['assumed_10g_hardware_budget_margin_mm']=round(float(margin(polygon,loaded[:2]))*1000,3)
        results[name].append(entry)
        if label=='HOME':draw[name]=(feet,polygon,com)
shift=(draw['micro_rex'][2]-draw['microduck'][2])*1000
report={'scope':'Static common HOME and +/-15 degree head/neck poses. Nominal sole vertices within 1 mm of lowest mesh vertex; both feet assumed supported. No measured contact, ZMP, force, terrain or walking stability proof.','source_pose_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in models.values()},'home_com_shift_mm':np.round(shift,3).tolist(),'results':results,'physical_validation':False,'dynamic_stability_verified':False}
report['hardware_budget_assumption']='Additional unmeasured hardware: 5 g at jaw_soft origin plus 5 g at trunk_base origin, static sensitivity only. Not included in the standard ONNX rollout or a weighed BOM.'
(R/'artifacts/balance_study.json').write_text(json.dumps(report,indent=2)+'\n')
fig,ax=plt.subplots(figsize=(8,6),layout='constrained');fig.patch.set_facecolor('#f5f1e8');ax.set_facecolor('#f5f1e8')
for i,foot in enumerate(draw['microduck'][0]):ax.fill(foot[:,0]*1000,foot[:,1]*1000,color='#c5d8cc',label='Original sole projection' if i==0 else None)
poly=draw['microduck'][1]*1000;poly=np.vstack([poly,poly[0]]);ax.plot(poly[:,0],poly[:,1],'--',color='#668375',label='Nominal two-foot hull')
for name,color in [('microduck','#174d40'),('micro_rex','#db8b33')]:
    com=draw[name][2]*1000;ax.scatter(com[0],com[1],s=90,c=color,label=name,zorder=4)
ax.set(aspect='equal',xlabel='Forward X (mm)',ylabel='Left Y (mm)',title='Same-joint HOME: projected centre of mass')
ax.legend(loc='upper left',fontsize=8);ax.grid(alpha=.15);fig.text(.5,.005,'Nominal static geometry only — physical support and dynamic balance unverified',ha='center',fontsize=8)
fig.savefig(R/'artifacts/balance_study.png',dpi=170);plt.close(fig)
print('HOME CoM shift XYZ mm:',np.round(shift,3).tolist())
print('Rex nominal margins mm:',[x['nominal_two_foot_margin_mm'] for x in results['micro_rex']])
