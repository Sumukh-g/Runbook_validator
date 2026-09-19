import json
import pytest
from opsproof.core.exceptions import PolicyError
from opsproof.rules.loader import PolicyLoader

def pack(rule):return {"name":"test","version":"1","rules":[rule]}
def valid():return {"id":"T-001","name":"Test","category":"clarity","description":"Test.","rationale":"Test.","severity":"low","enabled":True,"evaluator":"vague_action","score_penalty":1,"remediation":"Clarify."}
def write(tmp_path,data,raw=False):
    path=tmp_path/'generic.yaml';path.write_text(data if raw else json.dumps(data));return PolicyLoader(tmp_path)
def test_valid_policy(tmp_path):assert write(tmp_path,pack(valid())).load()[0].id=='T-001'
@pytest.mark.parametrize('change',[{"severity":"extreme"},{"category":"magic"},{"score_penalty":101},{"evaluator":"__import__"}])
def test_invalid_typed_policy_rejected(tmp_path,change):
    rule=valid();rule.update(change)
    with pytest.raises(PolicyError):write(tmp_path,pack(rule)).load()
def test_duplicate_ids_rejected(tmp_path):
    rule=valid()
    with pytest.raises(PolicyError):write(tmp_path,{"name":"x","rules":[rule,rule]}).load()
def test_malformed_and_hostile_yaml_rejected(tmp_path):
    for raw in ('not: [closed','!!python/object/apply:os.system ["touch /tmp/pwned"]'):
        with pytest.raises(PolicyError):write(tmp_path,raw,True).load()
