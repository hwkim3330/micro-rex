"""Export existing original visual meshes, excluding all retrofit geometry.
Upstream hardware terms remain applicable; this is not a commercial relicensing.
"""
from pathlib import Path
import trimesh
R=Path(__file__).resolve().parents[1]
scene=trimesh.load(R/'models/micro_rex.glb',force='scene')
keep={scene.graph[node][1] for node in scene.graph.nodes_geometry if node.startswith('stock_')}
scene.delete_geometry([key for key in scene.geometry if key not in keep])
assert len(scene.geometry)==70
scene.export(R/'models/microduck_original.glb')
print('Exported 70 original visual meshes, no retrofit parts')
