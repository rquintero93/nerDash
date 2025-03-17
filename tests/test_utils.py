'''
Test the functions in controllers.utils.py.

'''

import pandas as pd

from utils.functions import clean_colors, clean_mana_cost, clean_timestamp


def test_clean_timestamp():
    row = 1638316800000
    result = clean_timestamp(row)
    assert result == pd.to_datetime(row, unit='ms')

def test_clean_colors():
    row = ['Red', 'Blue']
    result = clean_colors(row)
    assert result == ['R', 'U']

def test_clean_mana_cost():
    row = ['{R}', '{G}', '{1}']
    result = clean_mana_cost(row)
    assert result == {'R', 'G', '1'}

