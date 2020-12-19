import os, sys

from numpy.lib.stride_tricks import as_strided
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports modules form parent directory

from data_factory import DataFactory
import json
import pandas as pd

with open('api.json') as api_file: # Getting API Key
    api = json.load(api_file)
    api_key = api['api_key']
    del api

def test_load_data():
    factory = DataFactory(api_key)
    factory.load_data_intraday('GOOGL')

    assert isinstance(factory.data, pd.DataFrame)
    assert len(factory.data) > 0

def test_save_data_normal():
    factory = DataFactory(api_key)
    factory.load_data_intraday('GOOGL')

    filename = factory.save_data()
    assert os.path.exists(filename)

    os.remove(filename) # Cleanup

def test_save_data_unloaded():
    factory = DataFactory(api_key)

    try:
        filename = factory.save_data()
        assert False, "ValueError not thrown"
    except:
        assert True
