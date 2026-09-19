from opsproof.core.enums import Category,Severity
from opsproof.core.models import Finding,SourceRef
from opsproof.scoring.baseline import calculate_score

def finding(rule='T-1',category=Category.CLARITY,severity=Severity.LOW,impact=-2,step=1):
    return Finding(id=f'{rule}-{step}',rule_id=rule,category=category,severity=severity,title='Clear title',explanation='Specific explanation.',evidence=['evidence'],source_refs=[SourceRef(file_name='x.md',step_number=step,evidence_text='evidence')],remediation='Fix it precisely.',score_impact=impact,detector='test')
def test_no_findings_is_100():assert calculate_score([]).overall==100
def test_duplicate_location_is_not_penalized_twice():assert calculate_score([finding(),finding()]).categories['clarity']==98
def test_many_low_findings_respect_category_cap():assert calculate_score([finding(f'T-{x}',impact=-3,step=x) for x in range(30)]).categories['clarity']==40
def test_scoring_is_order_independent():
    findings=[finding('A',Category.SAFETY,Severity.CRITICAL,-20),finding('B',Category.OWNERSHIP,Severity.MEDIUM,-5,2)]
    assert calculate_score(findings)==calculate_score(list(reversed(findings)))
def test_multiple_categories_expose_contributions():
    score=calculate_score([finding('A',Category.SAFETY,Severity.CRITICAL,-20),finding('B',Category.VERIFICATION,Severity.HIGH,-10,2)])
    assert score.categories['safety']==80 and score.categories['verification']==90 and len(score.contributions)==2
