import http from 'node:http';import {readFile} from 'node:fs/promises';import path from 'node:path';import assert from 'node:assert/strict';import puppeteer from 'puppeteer';
const root=path.resolve(import.meta.dirname,'..');const mime={'.css':'text/css','.html':'text/html','.js':'text/javascript','.json':'application/json','.glb':'model/gltf-binary','.png':'image/png'};
const server=http.createServer(async(req,res)=>{try{let p=decodeURIComponent(req.url.split('?')[0]);if(p.endsWith('/'))p+='index.html';const file=path.join(root,p);if(!file.startsWith(root+path.sep))throw Error();const data=await readFile(file);res.writeHead(200,{'content-type':mime[path.extname(file)]||'application/octet-stream'});res.end(data);}catch{res.writeHead(404);res.end();}});await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await puppeteer.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});let checks=0;
try{for(const [name,width,height]of[['desktop',1440,1000],['mobile',390,844]]){const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.setViewport({width,height});await page.goto(`http://127.0.0.1:${server.address().port}/web/`);await page.waitForFunction(()=>window.microRexLoaded===true,{timeout:30000});checks++;await page.addStyleTag({content:'html { scroll-behavior: auto !important; }'});
assert.equal(await page.$eval('#part-count',e=>e.textContent),'16개');checks++;
assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));checks++;
await page.screenshot({path:path.join(root,'artifacts',`viewer_${name}.png`)});
await page.click('#explode');assert.equal(await page.$eval('#explode',e=>e.textContent),'조립 상태로 보기');await page.click('#explode');checks++;
await page.click('#stock');assert.equal(await page.$eval('#stock',e=>e.textContent),'원본 부품 보이기');await page.click('#stock');checks++;
await page.click('#rotate');assert.equal(await page.$eval('#rotate',e=>e.textContent),'자동 회전 끄기');checks++;
assert.equal(await page.$$eval('#joints input',els=>els.length),14);checks++;
const moved=await page.evaluate(()=>{const j=window.microRex.jointControls.find(j=>j.joint.name==='head_yaw');const before=j.group.quaternion.toArray();j.input.value=.4;j.input.dispatchEvent(new Event('input'));return {before,after:j.group.quaternion.toArray(),label:j.output.textContent}});assert.notDeepEqual(moved.before,moved.after);assert.equal(moved.label,'23°');checks++;
await page.click('#part-list button');assert.ok(await page.$eval('#selection',e=>e.textContent.includes('CAD STEP')));checks++;
await page.click('#stock');assert.ok(await page.evaluate(()=>window.microRex.items.filter(m=>m.name.startsWith('stock_')).every(m=>!m.visible)));checks++;await page.click('#stock');
await page.click('#reset');assert.ok(await page.evaluate(()=>window.microRex.jointControls.every(j=>Number(j.input.value)===0)));checks++;
assert.deepEqual(errors,[]);checks++;await page.close();}
console.log(`${checks} browser checks passed`);}finally{await browser.close();server.close();}
