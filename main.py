import json
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.style.use('ggplot')

def main():

    with open('api.json') as api_file:
        api = json.load(api_file)
        api_key = api['api_key']
        del api

    ts = TimeSeries(key = api_key, output_format='pandas')
    data, metadata = ts.get_intraday('GOOGL', interval = '1min', outputsize = 'full')

    print(data.head())

if __name__ == '__main__':
    main()