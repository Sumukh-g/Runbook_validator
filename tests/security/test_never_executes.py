from unittest.mock import patch
import pytest
from opsproof.services.analysis_service import AnalysisService

PAYLOADS=[
 b"# Hostile\n## Procedure\n1. `sudo rm -rf /`\n2. `DELETE FROM users;`\n",
 b"# Substitution\n## Procedure\n1. `echo $(touch /tmp/pwned)`\n2. `echo `touch /tmp/pwned``\n",
 b"# Chaining\n## Procedure\n1. `echo ok; shutdown -h now`\n2. `true && rm -rf /tmp/*`\n",
 b"# Languages\n## Procedure\n1. `exec('bad')`\n2. `Remove-Item -Recurse C:\\`\n3. `cat x > /etc/config`\n",
]
@pytest.mark.parametrize("payload",PAYLOADS)
def test_hostile_commands_are_never_executed(payload):
    names=['os.system','subprocess.run','subprocess.Popen','subprocess.call','subprocess.check_call','subprocess.check_output']
    with patch(names[0]) as a,patch(names[1]) as b,patch(names[2]) as c,patch(names[3]) as d,patch(names[4]) as e,patch(names[5]) as f:result=AnalysisService().analyse('hostile.md',payload)
    for mock in (a,b,c,d,e,f):mock.assert_not_called()
    assert result.non_execution_statement

def test_script_like_evidence_is_preserved_as_text():
    result=AnalysisService().analyse('../../evil.md',b'# Safe\n## Procedure\n1. Check <script>alert(1)</script> works.\n')
    assert result.document.file_name=='evil.md' and '<script>' in result.document.steps[0].text
