// Render the actual GLB and original joint rig for the README. No concept artwork.
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import puppeteer from 'puppeteer';
const root=path.resolve(import.meta.dirname,'..');
const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.glb':'model/gltf-binary'};
const server=http.createServer(async(req,res)=>{try{let p=decodeURIComponent(req.url.split('?')[0]);if(p.endsWith('/'))p+='index.html';const f=path.join(root,p);if(!f.startsWith(root+path.sep))throw Error();res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');res.end(await readFile(f));}catch{res.writeHead(404);res.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const browser=await puppeteer.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage();await page.setViewport({width:1200,height:800,deviceScaleFactor:1.5});
 await page.goto(`http://127.0.0.1:${server.address().port}/web/`);await page.waitForFunction(()=>window.microRexLoaded===true);
 const record=JSON.parse(await readFile(path.join(root,'artifacts/policy_replay_micro_rex.json'),'utf8'));
 await page.evaluate(async record=>{
  const THREE=await import('/web/vendor/three/build/three.module.js');
  const api=window.microRex,view=document.querySelector('#view');
  document.body.replaceChildren();document.body.style.cssText='margin:0;background:#f5f1e8;overflow:hidden;color:#163f32;font-family:Arial,sans-serif';
  const style=document.createElement('style');style.textContent='#view{position:absolute;left:350px;top:0;width:850px!important;height:800px!important;min-height:0!important;background:transparent;border:0} #view>*:not(canvas){display:none} canvas{outline:none}';document.head.append(style);
  document.body.append(view);
  const copy=document.createElement('div');copy.style.cssText='position:absolute;left:64px;top:82px;width:330px;z-index:2;pointer-events:none';
  copy.innerHTML='<p style="letter-spacing:4px;font-size:13px;color:#b66b29">MEET YOUR LITTLE DINOSAUR</p><h1 style="font-size:86px;line-height:.95;letter-spacing:-6px;margin:32px 0;color:#163f32">MICRO<br><span style="color:#e79a48">REX.</span></h1><p style="font-size:27px;line-height:1.6;margin:26px 0">같은 관절.<br>작은 공룡.</p><p style="font-size:13px;letter-spacing:1px;line-height:2.1">14 MICRODUCK JOINTS<br>UNCHANGED WALKING WEIGHTS</p>';
  document.body.append(copy);
  copy.querySelectorAll('p').forEach(p=>p.style.color='#527066');
  const footer=document.createElement('div');footer.style.cssText='position:absolute;left:64px;right:50px;bottom:33px;font-size:12px;letter-spacing:1px;display:flex;justify-content:space-between;color:#527066';footer.innerHTML='<span>ACTUAL CAD MODEL / REV C</span><span>SIMULATION TESTED · PHYSICAL BUILD PENDING</span>';document.body.append(footer);
  api.scene.background.set('#f5f1e8');
  api.renderer.toneMapping=THREE.ACESFilmicToneMapping;api.renderer.toneMappingExposure=1;
  const grid=api.scene.children.find(o=>o.type==='GridHelper');if(grid)grid.visible=false;
  const q=record.qpos[0];for(let j=0;j<record.joint_names.length;j++){const item=api.jointControls.find(c=>c.joint.name===record.joint_names[j]);item.input.value=q[7+j];item.input.dispatchEvent(new Event('input'));}
  const trunk=api.bodyGroups.get(api.rig.bodies.find(b=>b.parent===0).id);trunk.position.set(0,0,q[2]);trunk.quaternion.set(q[4],q[5],q[6],q[3]);
  api.controls.target.set(-.02,.143,0);api.camera.position.set(.35,.255,.49);api.controls.update();api.renderer.setSize(850,800);api.camera.aspect=850/800;api.camera.updateProjectionMatrix();api.renderer.render(api.scene,api.camera);
 },record);
 await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 await page.screenshot({path:path.join(root,'artifacts/readme_hero.png')});
 console.log('README portrait rendered from current GLB and recorded joint pose');
}finally{await browser.close();server.close();}
