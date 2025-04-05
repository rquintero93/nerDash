"""
Test the functions in utils.functions.py.

"""

import pandas as pd

from utils import clean_colors, clean_mana_cost, clean_timestamp


def test_clean_timestamp():
    row = 1638316800000
    result = clean_timestamp(row)
    assert result == pd.to_datetime(row, unit="ms")


def test_clean_colors():
    row = ["Red", "Blue"]
    result = clean_colors(row)
    assert result == ["R", "U"]

    row = ["Red", "Test"]
    result = clean_colors(row)
    assert result == ["Colorless", "R"]


def test_clean_mana_cost():
    row = ["{R}", "{G}", "{1}"]
    result = clean_mana_cost(row)
    assert result == {"R", "G", "1"}
