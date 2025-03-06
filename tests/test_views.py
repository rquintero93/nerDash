import pandas as pd
import pytest

from views.graphs import make_bar_chart, make_pie_chart


def test_make_bar_chart():
    assert make_bar_chart() is None
    with pytest.raises(ValueError, match="Data must be a pandas DataFrame or a dictionary that can be converted to one."):
        make_bar_chart(data=1)

def test_make_pie_chart():
    assert make_pie_chart() is None
    with pytest.raises(ValueError, match="Data must be a pandas DataFrame."):
        make_pie_chart(data=1,column=str)
    with pytest.raises(ValueError, match="Column must be a string."):
        make_pie_chart(data=pd.DataFrame(),column=1)

