import * as THREE from 'three';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
const rig=JSON.parse(readFileSync(new URL('../models/rig.json',import.meta.url)));
const expected=JSON.parse(execFileSync('python3',['-c',`import os,json,mujoco
os.environ['MUJOCO_GL']='disable'
m=mujoco.MjModel.from_xml_path('vendor/microduck/robot_walk.xml'); d=mujoco.MjData(m)
for j in range(m.njnt):
 if m.jnt_type[j]==mujoco.mjtJoint.mjJNT_HINGE:d.qpos[m.jnt_qposadr[j]]=.15
mujoco.mj_forward(m,d)
print(json.dumps({str(i):dict(pos=d.xpos[i].tolist(),mat=d.xmat[i].reshape(3,3).tolist()) for i in range(1,m.nbody)}))`],{cwd:new URL('../',import.meta.url)}).toString());
const groups=new Map([[0,new THREE.Group()]]);
for(const b of rig.bodies){const g=new THREE.Group();g.position.fromArray(b.position);const [w,x,y,z]=b.quaternion;const base=new THREE.Quaternion(x,y,z,w);g.quaternion.copy(base);for(const j of b.joints){const q=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(...j.axis),.15);const p=new THREE.Vector3(...j.pivot);g.position.add(p.clone().sub(p.clone().applyQuaternion(q)).applyQuaternion(base));g.quaternion.multiply(q)}groups.get(b.parent).add(g);groups.set(b.id,g)}
groups.get(0).updateMatrixWorld(true);
for(const b of rig.bodies){const matrix=groups.get(b.id).matrixWorld.elements,e=expected[b.id];for(let i=0;i<3;i++){assert.ok(Math.abs(matrix[12+i]-e.pos[i])<1e-8,`${b.name} position`);for(let j=0;j<3;j++)assert.ok(Math.abs(matrix[j*4+i]-e.mat[i][j])<1e-8,`${b.name} rotation`)}}
console.log(`Browser rig transforms match MuJoCo for ${rig.bodies.length} bodies with all 14 hinges at 0.15 rad.`);
