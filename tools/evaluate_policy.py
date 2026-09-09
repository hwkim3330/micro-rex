"""Paired CPU MuJoCo rehearsal with unchanged official ONNX and upstream BAM.

No motor hardware access. Results describe the configured simulation only.
"""
from pathlib import Path
import argparse,contextlib,hashlib,importlib.util,io,json,os,tempfile
import xml.etree.ElementTree as ET
os.environ.setdefault('MUJOCO_GL','egl')
import mujoco,numpy as np
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'upstream/microduck_rl/scripts/infer_policy.py'
spec=importlib.util.spec_from_file_location('upstream_inference',source)
up=importlib.util.module_from_spec(spec);spec.loader.exec_module(up)

def scene(path):
    tree=ET.parse(path);r=tree.getroot()
    r.find('compiler').set('meshdir',str(ROOT/'vendor/microduck/assets'))
    ET.SubElement(r.find('worldbody'),'geom',name='evaluation_floor',type='plane',size='3 3 .01',friction='1 .005 .0001')
    return ET.tostring(r,encoding='unicode')

def run(path,velocity,seconds,seed,standing=False,head_pitch=0):
    with tempfile.NamedTemporaryFile(suffix='.xml',mode='w') as f,contextlib.redirect_stdout(io.StringIO()):
        f.write(scene(path));f.flush()
        motor=up.load_bam_model(200.,7.4,None)
        m,d,controller,_=up.load_mujoco_with_bam(f.name,motor,.005,.1,6.)
        policy=up.PolicyInference(m,d,walking_onnx_path=None if standing else str(ROOT/'.cache/policies/alpha_walking.onnx'),standing_onnx_path=str(ROOT/'.cache/policies/alpha_stand.onnx') if standing else None,bam_ctrl=controller,new_cmd_obs=True,use_projected_gravity=True)
        policy.set_vel_cmd(*velocity)
        policy.head_offset[1]=head_pitch;policy._update_command()
        jid=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,'trunk_base_freejoint');adr=m.jnt_qposadr[jid]
        d.qpos[adr:adr+7]=[0,0,.125,1,0,0,0]
        rng=np.random.default_rng(seed)
        d.qpos[policy.joint_qpos_indices]=policy.default_pose+rng.normal(0,.003,14)
        controller.reset(d.qpos);policy.set_position_targets(policy.default_pose);mujoco.mj_forward(m,d)
        assert policy.get_observations().shape==(61,)
        frames=[];tilts=[];heights=[];failed_at=None
        for step in range(round(seconds*50)):
            action=policy.infer()
            assert action.shape==(14,) and np.isfinite(action).all()
            policy.apply_action(action)
            for _ in range(4):controller.update();mujoco.mj_step(m,d)
            mujoco.mj_forward(m,d)
            if not np.isfinite(d.qpos).all():raise ValueError('nonfinite dynamics')
            tilt=float(np.degrees(np.arccos(np.clip(d.xmat[policy.trunk_base_id].reshape(3,3)[2,2],-1,1))))
            height=float(d.xpos[policy.trunk_base_id,2]);tilts.append(tilt);heights.append(height)
            frames.append(np.round(d.qpos,7).tolist())
            if failed_at is None and (tilt>45 or height<.065):failed_at=round(d.time,3)
        result={'seed':seed,'velocity_command':velocity,'duration_s':seconds,'mass_kg':float(m.body_mass.sum()),'max_tilt_deg':round(max(tilts),2),'min_trunk_height_m':round(min(heights),4),'final_xy_m':np.round(d.qpos[adr:adr+2],4).tolist(),'mean_world_vx_m_s':round(float(d.qpos[adr])/seconds,4),'final_yaw_deg':round(float(np.degrees(np.arctan2(d.xmat[policy.trunk_base_id].reshape(3,3)[1,0],d.xmat[policy.trunk_base_id].reshape(3,3)[0,0]))),2),'first_fall_s':failed_at,'upright_entire_trial':failed_at is None,'finite':True}
        trajectory={'model':path.name,'dt':.02,'qpos':frames,'joint_names':[mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,int(j)) for j in m.actuator_trnid[:,0]],'result':result}
        result['policy']='alpha_stand' if standing else 'alpha_walking';result['head_pitch_command_rad']=head_pitch
        return result,trajectory

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=float,default=10);parser.add_argument('--seeds',type=int,default=3);args=parser.parse_args()
    provenance=json.loads((ROOT/'artifacts/policy_source.json').read_text())
    for name in ['alpha_walking.onnx','alpha_stand.onnx']:
        assert hashlib.sha256((ROOT/'.cache/policies'/name).read_bytes()).hexdigest()==provenance['files'][name]['sha256']
    results={}
    for name,path in [('microduck',ROOT/'vendor/microduck/robot_walk.xml'),('micro_rex',ROOT/'models/micro_rex.xml')]:
        results[name]=[]
        for command in [[0.,0.,0.],[.1,0.,0.],[.3,0.,0.],[0.,0.,.3]]:
            for seed in range(args.seeds):
                result,trajectory=run(path,command,args.seconds,seed);results[name].append(result);print(name,result,flush=True)
                if command[0]==.3 and seed==0:(ROOT/f'artifacts/policy_replay_{name}.json').write_text(json.dumps(trajectory,separators=(',',':'))+'\n')
    report={'source_revision':provenance['revision'],'weight_sha256':provenance['files']['alpha_walking.onnx']['sha256'],'inference_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actuator_model':'upstream BAM M6 XL330, kp_fw=200, vin=7.4, sag_gain=0.1, no firmware current limiter','observation':'61D; upstream projected gravity, joint-relative HOME and command layout','control_hz':50,'physics_hz':200,'protocol':'Same seeds and 0/0.1 m/s/0.3 rad/s commands; fall = trunk tilt >45 degrees or height <65 mm; fixed flat floor; no hardware','results':results,'hardware_compatibility_verified':False,'limitations':['No sim-to-real validation','No varied terrain or sensor noise','Approximate retrofit collision envelopes','Finite trial duration does not establish reliable walking']}
    report['model_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['vendor/microduck/robot_walk.xml','models/micro_rex.xml']}
    report['protocol']='Same seeds; zero, 0.1 and 0.3 m/s forward, 0.3 rad/s turn commands. Fall = tilt >45 degrees or height <65 mm; fixed flat floor, no hardware. Command tracking reported separately from upright status.'
    report['standing_weight_sha256']=provenance['files']['alpha_stand.onnx']['sha256']
    report['standing_head_command_trials']={}
    for name,path in [('microduck',ROOT/'vendor/microduck/robot_walk.xml'),('micro_rex',ROOT/'models/micro_rex.xml')]:
        report['standing_head_command_trials'][name]=[]
        for pitch in [-.25,0.,.25]:
            result,_=run(path,[0.,0.,0.],args.seconds,0,standing=True,head_pitch=pitch)
            report['standing_head_command_trials'][name].append(result);print(name,'stand/head',result,flush=True)
    (ROOT/'artifacts/policy_evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
