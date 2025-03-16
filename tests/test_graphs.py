'''
Tests for the views.graphs module.

'''

import pandas as pd
import pytest

from utils import constants
from views.graphs import make_bar_chart, make_pie_chart


def test_make_bar_chart():
    with pytest.raises(ValueError, match=constants.ERROR_MESSAGE_DATA_NONE):
        make_bar_chart()

    with pytest.raises(ValueError, match=constants.ERROR_MESSAGE_DATA_NOT_DF_OR_DICT):
        make_bar_chart(data=1)
    
    # Test with valid DataFrame and column
    df = pd.DataFrame({'category': ['A', 'B', 'A', 'C'], 'value': [1, 2, 3, 4]})
    fig = make_bar_chart(data=df, column='category')
    assert fig is not None

    # Test with valid dictionary
    data_dict = {'A': 3, 'B': 1, 'C': 1}
    fig = make_bar_chart(data=data_dict)
    assert fig is not None

    #Test wtih invalid DataFrame column argument
    df = pd.DataFrame({'invalid': ['A', 'B', 'A', 'C'], 'value': [1, 2, 3, 4]})

    with pytest.raises(ValueError, match=constants.ERROR_MESSAGE_COLUMN_NOT_IN_DF):
        make_bar_chart(data=df, column='category')

    assert fig is not None

def test_make_pie_chart():
    with pytest.raises(ValueError, match=constants.ERROR_MESSAGE_DATA_NONE):
        make_pie_chart()

    with pytest.raises(ValueError, match=constants.ERROR_MESSAGE_DATA_NOT_DF):
        make_pie_chart(data=1, column='category')

    with pytest.raises(ValueError, match=constants.ERROR_MESSAGE_COLUMN_NOT_IN_DF):
        make_pie_chart(data=pd.DataFrame(), column=1)
    
    # Test with valid DataFrame
    df = pd.DataFrame({'category': ['A', 'B', 'A', 'C']})
    fig = make_pie_chart(data=df, column='category')
    assert fig is not None
