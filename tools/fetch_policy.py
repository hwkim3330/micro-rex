"""Fetch an immutable official checkpoint; weights remain in an ignored cache."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[1]
REV='088524a64e2557dc453256b6071dbb9d23888802'
BASE=f'https://huggingface.co/pollen-robotics/microduck-policies/resolve/{REV}/'
out=ROOT/'.cache/policies';out.mkdir(parents=True,exist_ok=True)
files={}
for name in ['README.md','manifest.json','alpha_walking.onnx','alpha_stand.onnx']:
    data=urllib.request.urlopen(BASE+name,timeout=60).read()
    if name.endswith('.onnx') and len(data)<10000:raise ValueError('Missing weight payload')
    (out/name).write_bytes(data)
    files[name]={'url':BASE+name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
manifest=json.loads((out/'manifest.json').read_text())
assert manifest['obs_len']==61 and manifest['action_len']==14
record={'repository':'pollen-robotics/microduck-policies','revision':REV,'model_card_license':'apache-2.0','files':files,'manifest':manifest,'note':'Weights fetched from pinned source, not modified. Hardware license is separate.'}
(ROOT/'artifacts/policy_source.json').write_text(json.dumps(record,indent=2)+'\n')
print('Fetched official walking and standing checkpoints at',REV)
