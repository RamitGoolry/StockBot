import pandas as pd
from binance.client import Client
import datetime
import json

with open('api.json') as api_file:
    api_dict = json.load(api_file)

bclient = Client(api_key=api_dict['binance-public'], api_secret=api_dict['binance-secret'])
del api_dict

start_date = datetime.datetime.strptime('1 Jan 2016', '%d %b %Y')
today = datetime.datetime.today()

def binanceBarExtractor(symbol):
    filename = f'data/{symbol}_MinuteBars.csv'

    klines = bclient.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, start_date.strftime("%d %b %Y %H:%M:%S"), today.strftime("%d %b %Y %H:%M:%S"), 1000)
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

    data.set_index('timestamp', inplace=True)
    data.to_csv(filename)
    print(f'Recieved {len(data)} datapoints.')


if __name__ == '__main__':
    # Obviously replace BTCUSDT with whichever symbol you want from binance
    # Wherever you've saved this code is the same directory you will find the resulting CSV file
    binanceBarExtractor('BTCUSDT')
