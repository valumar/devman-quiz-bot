def test_match_data():

    from load_data import match_data
    from .data import CONTENT, RESULTS

    assert match_data(CONTENT) == RESULTS
