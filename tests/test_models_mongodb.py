from unittest.mock import MagicMock

import pandas as pd

from models.mongo import get_mongo_cards, get_mongo_client


def test_get_mongo_client(mocker):
    mock_client = mocker.patch("models.mongo.MongoClient", autospec=True)
    client_instance = mock_client.return_value
    
    client = get_mongo_client()
    
    assert client == client_instance
    mock_client.assert_called_once()


def test_get_mongo_cards_kengrams(mocker):
    mock_client = mocker.patch("models.mongo.get_mongo_client")
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_client.return_value.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    mock_cursor = [
        {"anchorChange": [{"field1": "value1"}], "metadata": [{"field2": "value2"}]},
        {"anchorChange": [{"field1": "value3"}], "metadata": [{"field2": "value4"}]},
    ]
    mock_collection.aggregate.return_value = mock_cursor
    
    df = get_mongo_cards("test_db", "kengrams")
    
    assert isinstance(df, pd.DataFrame)
    assert "anchorChange" not in df.columns
    assert "metadata" not in df.columns
    assert len(df) == 2
    
    mock_client.return_value.close.assert_called_once()


def test_get_mongo_cards_non_kengrams(mocker):
    mock_client = mocker.patch("models.mongo.get_mongo_client")
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_client.return_value.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    mock_cursor = [
        {"field1": "value1", "field2": "value2"},
        {"field1": "value3", "field2": "value4"},
    ]
    mock_collection.aggregate.return_value = mock_cursor
    
    df = get_mongo_cards("test_db", "other_collection")
    
    assert isinstance(df, pd.DataFrame)
    assert "field1" in df.columns
    assert "field2" in df.columns
    assert len(df) == 2
    
    mock_client.return_value.close.assert_called_once()
