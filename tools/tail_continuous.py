"""One-piece hollow tail alternative avoids relying on untested segmented joints."""
from pathlib import Path
import cadquery as cq,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1]
a=[(-52,0,149,11),(-99,0,153,8),(-142,0,170,5),(-180,0,187,2)]
def loft(wall):
    path=cq.Workplane('YZ',origin=a[0][:3]).circle(a[0][3]-wall)
    for prev,current in zip(a,a[1:]):
        path=path.workplane(offset=current[0]-prev[0]).center(0,current[2]-prev[2]).circle(max(.4,current[3]-wall))
    return path.loft(combine=True).val()
shape=loft(0).cut(loft(1.6))
assert shape.isValid() and len(shape.Solids())==1
cq.exporters.export(shape,str(ROOT/'models/step/tail_continuous.step'))
cq.exporters.export(shape,str(ROOT/'models/parts/tail_continuous.stl'),tolerance=.15)
m=trimesh.load_mesh(ROOT/'models/parts/tail_continuous.stl');assert m.is_watertight
m.apply_transform(trimesh.geometry.align_vectors([-1,0,.25],[0,0,1]));lo,hi=m.bounds;m.apply_translation([-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]]);m.export(ROOT/'models/print/tail_continuous.stl')
print('Continuous tail alternative: one valid CAD solid and watertight STL')
