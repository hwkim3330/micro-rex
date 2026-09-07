import os
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import xml.etree.ElementTree as ET
import mujoco,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def render(source,prefix):
    tree=ET.parse(source);r=tree.getroot();r.find('compiler').set('meshdir',str(ROOT/'vendor/microduck/assets'))
    visual=r.find('visual')
    if visual is None:visual=ET.SubElement(r,'visual')
    ET.SubElement(visual,'global',offwidth='1600',offheight='1200')
    ET.SubElement(visual,'quality',shadowsize='4096',offsamples='4')
    ET.SubElement(visual,'headlight',ambient='0.35 0.35 0.35',diffuse='0.6 0.6 0.6')
    w=r.find('worldbody');ET.SubElement(w,'geom',name='stage',type='plane',size='2 2 .01',rgba='.10 .14 .16 1',pos='0 0 0')
    ET.SubElement(w,'light',pos='0.5 -0.6 1',dir='-.3 .3 -1',diffuse='.9 .85 .74',castshadow='true')
    model=mujoco.MjModel.from_xml_string(ET.tostring(r,encoding='unicode'));d=mujoco.MjData(model);mujoco.mj_forward(model,d)
    # Raised reference pose, not a walking performance claim.
    opt=mujoco.MjvOption();opt.geomgroup[3]=0
    renderer=mujoco.Renderer(model,height=900,width=1200)
    for label,az,el in [('hero',135,-14),('side',90,-5),('front',180,-8),('rear',35,-15)]:
        cam=mujoco.MjvCamera();cam.lookat[:]=[-.018,0,.15];cam.distance=.57;cam.azimuth=az;cam.elevation=el
        renderer.update_scene(d,camera=cam,scene_option=opt)
        Image.fromarray(renderer.render()).save(ROOT/'artifacts'/f'{prefix}_{label}.png')
    renderer.close()
render(ROOT/'models/micro_rex.xml','micro_rex')
render(ROOT/'vendor/microduck/robot_walk.xml','microduck_reference')
