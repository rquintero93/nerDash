
import pandas as pd

from utils.utils import (clean_colors, clean_mana_cost, clean_timestamp,
                         count_colors, count_concept)


def test_count_colors():
    data = pd.DataFrame({'colors': [['Red', 'Green'], ['Blue'], ['Red', 'Blue']]})
    result = count_colors(data, 'colors')
    assert result == {'Red': 2, 'Green': 1, 'Blue': 2}

def test_count_concept():
    data = pd.DataFrame({'concept': [['A', 'B'], ['A'], ['B', 'C']]})
    result = count_concept(data, 'concept')
    assert result == {('A', 'B'): 1, ('A',): 1, ('B', 'C'): 1}

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

