"""Digital eye/washer fit screen. Pull-out strength requires physical testing."""
from pathlib import Path
import hashlib,json,math
import cadquery as cq
R=Path(__file__).resolve().parents[1];checks=[];sources={}
for side,sgn in [('left',1),('right',-1)]:
    paths=[R/f'models/step/{name}_{side}.step' for name in ['skull_cheek','brow']]
    cheek,eye=[cq.importers.importStep(str(p)) for p in paths]
    # Candidate M2 fender washer: OD8, ID2.2, thickness0.5, behind cheek.
    washer=cq.Workplane('XZ',origin=(29,sgn*44,265)).circle(4).circle(1.1).extrude(sgn*.5)
    for label,a,b in [('eye_to_cheek',eye,cheek),('washer_to_eye',washer,eye),('washer_to_cheek',washer,cheek)]:
        volume=sum(s.Volume() for s in a.intersect(b).solids().vals())
        assert volume<.01,(side,label,volume)
        checks.append({'side':side,'pair':label,'overlap_mm3':round(volume,6)})
    sources.update({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
report={'revision':'C','scope':'Nominal static STEP intersections for eye and candidate washer only','checks':checks,'step_sha256':sources,'candidate_screw':'M2 x 6 plastic thread-forming, supplier not selected','pilot_diameter_mm':1.6,'pilot_depth_mm':6,'estimated_thread_engagement_mm':5.2,'estimated_tip_clearance_mm':.8,'stem_radial_clearance_mm':.2,'washer_bearing_area_mm2':round(math.pi*(4**2-2.7**2),2),'physical_pull_test_passed':False,'physical_torque_test_passed':False,'head_strap_routing_verified':False,'production_release':False}
(R/'artifacts/retention_check.json').write_text(json.dumps(report,indent=2)+'\n')
print('6 nominal eye/washer intersections clear; strength and physical fit unverified')
