from pathlib import Path
import json
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'models/print';out.mkdir(exist_ok=True)
parts=json.loads((ROOT/'artifacts/parts.json').read_text())
for p in parts:
    m=trimesh.load_mesh(ROOT/p['stl'])
    if p['name'].startswith('tail_segment'):
        axes=[[-47,0,4],[-43,0,17],[-38,0,17]];v=axes[int(p['name'][-1])-1]
    else:
        v=np.eye(3)[int(np.argmin(m.extents))]
    m.apply_transform(trimesh.geometry.align_vectors(v,[0,0,1]))
    lo,hi=m.bounds;m.apply_translation([-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]])
    m.export(out/(p['name']+'.stl'))
print(f'Created {len(parts)} centred, bed-oriented print STLs')
