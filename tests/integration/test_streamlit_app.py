import pytest

def test_streamlit_empty_state_smoke():
    pytest.importorskip('streamlit')
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file('app.py').run(timeout=20)
    assert not app.exception and app.markdown
