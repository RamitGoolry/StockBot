from alpha_vantage.timeseries import TimeSeries

class DataFactory(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.data = None
        self._symbol = None

    def load_data_intraday(self, symbol, interval='1min', outputsize='full'):
        ts = TimeSeries(key = self.api_key, output_format='pandas')
        self.data, _ = ts.get_intraday(symbol, interval=interval, outputsize=outputsize)

        self._symbol = symbol

    def save_data(self):
        if self.data is None:
            raise ValueError("DataFactory: No Data Loaded")
        
        self.data.to_csv(f'data/{self._symbol}-{self.data.index.max()}-{self.data.index.min()}')
        return f'data/{self._symbol}-{self.data.index.max()}-{self.data.index.min()}'