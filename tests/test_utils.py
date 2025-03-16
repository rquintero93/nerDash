'''
Test the functions in controllers.utils.py.

'''

import pandas as pd

from controllers.utils import (clean_colors, clean_mana_cost, clean_timestamp,
                               count_concept, count_primary_colors,
                               get_cards_df)


def test_count_primary_colors():
    data = pd.DataFrame({'colors': [['Red', 'Green'], ['Blue'], ['Red', 'Blue']]})
    result = count_primary_colors(data, 'colors')
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

def test_get_cards_df(mocker):
    mock_get_mongo_cards = mocker.patch('controllers.utils.get_mongo_cards')
    mock_get_mongo_cards.side_effect = [
        pd.DataFrame({'colors': [['Red'], ['Green']], 'retrievalCount': [1, 2], '_id': [1, 2], 'from': ['user1', 'user2'], 'chatId': ['chat1', 'chat2']}),
        pd.DataFrame({'colors': [['Blue'], ['Red']], 'retrievalCount': [3, 4], '_id': [3, 4], 'from': ['user3', 'user4'], 'chatId': ['chat3', 'chat4']})
    ]
    df_cards = get_cards_df()
    assert not df_cards.empty
    assert 'colors' in df_cards.columns
    assert 'retrievalCount' in df_cards.columns
    assert df_cards['colors'].iloc[0] == ['R']
    assert df_cards['colors'].iloc[1] == ['G']
    assert df_cards['colors'].iloc[2] == ['U']
    assert df_cards['colors'].iloc[3] == ['R']
