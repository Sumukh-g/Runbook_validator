from evaluation.calibration import run

def test_calibration_disabled_without_legitimate_minimum(tmp_path):
    path=tmp_path/'scores.csv';path.write_text('document_id,critical_count,high_count,medium_count,graph_defects,failure_coverage,risk_index,command_risk_count,human_quality_score\n')
    result=run(path)
    assert result['enabled'] is False and result['authoritative'] is False and '30' in result['reason']
