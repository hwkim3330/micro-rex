"""Dimensioned projection drawings generated from the actual exported STL meshes."""
from pathlib import Path
import json,csv
import numpy as np,trimesh
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parents[1]
parts=json.loads((ROOT/'artifacts/parts.json').read_text());W,H=landscape(A3)
c=canvas.Canvas(str(ROOT/'drawings/Micro_Rex_Drawings.pdf'),pagesize=(W,H))
def header(title,subtitle):
    c.setFillColor(HexColor('#102a2a'));c.rect(0,H-90,W,90,fill=1,stroke=0)
    c.setFillColorRGB(1,1,1);c.setFont('Helvetica-Bold',25);c.drawString(35,H-42,title)
    c.setFont('Helvetica',11);c.drawString(35,H-66,subtitle)
    c.setFillColorRGB(.1,.15,.15)
def footer(page):
    c.setFont('Helvetica',9);c.drawString(35,28,'MICRO REX / Rev C / 2026-09-10 / mm / PROTOTYPE - verify fit before fabrication')
    c.drawRightString(W-35,28,f'{page} / {len(parts)+1}')
header('MICRO REX  /  ASSEMBLY REFERENCE','Microduck-compatible joint interface / independent T-rex retrofit / not factory manufacturing drawings')
c.drawImage(str(ROOT/'artifacts/micro_rex_side.png'),35,190,width=690,height=517,preserveAspectRatio=True,mask='auto')
c.setFont('Helvetica-Bold',15);c.drawString(760,680,'PRINTED RETROFIT BOM')
c.setFont('Helvetica',10)
for i,p in enumerate(parts):c.drawString(760,650-i*24,f'{i+1:02}  {p["name"]}  {p["mass_g"]:.1f} g')
c.setFont('Helvetica',11)
for i,line in enumerate(['Stock legs, motors, camera and head module are retained.', 'Cheek M2 bridge holes: diameter 2.4 mm; eye stem hole: diameter 5.4 mm.', 'Eye: M2 x 6 plastic screw + OD8 x 0.5 washer, pilot diameter 1.6 x 6 deep.', 'Head bridge strap slots: 4 x 2 mm; routing and retention need physical tests.', 'Cheek: 1.2 mm face with 3 mm perimeter rib and full-thickness screw lands.', 'Tail segment joints and decorative tooth retention remain unverified.', 'Arm brackets use M2 clearance and a 3 x 4 mm strap channel.', 'CAD coordinates use the source MJCF reference pose, not print-bed origin.']):c.drawString(45,160-i*16,line)
footer(1);c.showPage()
for index,p in enumerate(parts):
    mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
    header(p['name'].upper().replace('_',' '),f"Part {index+1:02} | parent: {p['parent']} | PLA solid-equivalent estimate {p['mass_g']:.2f} g")
    # Outline edges are drawn from actual mesh; dimension envelope is independent of orientation.
    for col,(axes,label) in enumerate([((0,2),'SIDE X/Z'),((0,1),'TOP X/Y'),((1,2),'FRONT Y/Z')]):
        a=mesh.vertices[:,axes];lo=a.min(axis=0);hi=a.max(axis=0);ext=hi-lo
        scale=min(295/max(ext[0],1),400/max(ext[1],1));origin=np.array([70+col*380,220])
        pts=(a-lo)*scale+origin
        c.setStrokeColor(HexColor('#2f675a'));c.setLineWidth(.25)
        # Unique silhouette/boundary and crease edges, avoiding triangulation clutter.
        edge_set=set()
        for face in mesh.faces:
            for u,v in zip(face,np.roll(face,-1)):
                key=tuple(sorted((int(u),int(v))));edge_set.add(key)
        # Project all edges lightly; exact source geometry remains available in STEP.
        for u,v in edge_set:
            if np.linalg.norm(pts[u]-pts[v])>.05:c.line(*pts[u],*pts[v])
        c.setFont('Helvetica-Bold',12);c.setFillColorRGB(.1,.2,.2);c.drawString(origin[0],675,label)
        c.setStrokeColorRGB(.2,.2,.2);c.setLineWidth(.8)
        x,y=origin;ww,hh=ext*scale
        c.line(x,y-25,x+ww,y-25);c.line(x,y-30,x,y-18);c.line(x+ww,y-30,x+ww,y-18)
        c.setFont('Helvetica',11);c.drawCentredString(x+ww/2,y-43,f'{ext[0]:.2f} mm')
        c.line(x-18,y,x-18,y+hh);c.drawString(x-25,y+hh+12,f'{ext[1]:.2f} mm')
    c.setFont('Helvetica',11)
    c.drawString(45,115,'Overall envelope: '+ ' x '.join(f'{x:.2f}' for x in p['dimensions_mm'])+' mm')
    c.drawString(45,95,'Reference projection only. Hole locations and solid geometry: matching editable STEP and cad/build.py.')
    c.drawString(45,75,'Stock mating fit, fastener engagement and printer tolerances are not physically verified.')
    footer(index+2);c.showPage()
c.save()
with open(ROOT/'drawings/retrofit_bom.csv','w') as f:
    writer=csv.writer(f,lineterminator='\n');writer.writerow(['part','qty','material_estimate','mass_g','STL','STEP'])
    for p in parts:writer.writerow([p['name'],1,p['material'],p['mass_g'],p['stl'],p['step']])
    writer.writerow(['eye_retention_screw',2,'Candidate M2 x 6 plastic thread-forming; supplier/torque pending','','',''])
    writer.writerow(['eye_retention_washer',2,'Candidate OD8 ID2.2 thickness0.5 mm; physical fit pending','','',''])
    writer.writerow(['head_retention_strap',2,'Candidate for 4 x 2 mm slots; routing/strength pending','','',''])
print(f'Wrote {len(parts)+1} drawing pages and BOM')
