import pandas as pd
import pytest

from views.graphs import make_bar_chart, make_pie_chart


def test_make_bar_chart():
    assert make_bar_chart() is None
    with pytest.raises(ValueError, match="Data must be a pandas DataFrame or a dictionary that can be converted to one."):
        make_bar_chart(data=1)
    
    # Test with valid DataFrame
    df = pd.DataFrame({'category': ['A', 'B', 'A', 'C'], 'value': [1, 2, 3, 4]})
    fig = make_bar_chart(data=df, column='category')
    assert fig is not None

    # Test with valid dictionary
    data_dict = {'A': 3, 'B': 1, 'C': 1}
    fig = make_bar_chart(data=data_dict)
    assert fig is not None

def test_make_pie_chart():
    assert make_pie_chart() is None
    with pytest.raises(ValueError, match="Data must be a pandas DataFrame."):
        make_pie_chart(data=1, column='category')
    with pytest.raises(ValueError, match="Column must be a string."):
        make_pie_chart(data=pd.DataFrame(), column=1)
    
    # Test with valid DataFrame
    df = pd.DataFrame({'category': ['A', 'B', 'A', 'C']})
    fig = make_pie_chart(data=df, column='category')
    assert fig is not None
