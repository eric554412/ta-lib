import pandas as pd
import numpy as np
import talib
from back_test import BackTest

pd.set_option('display.max_rows' , None)

data = pd.read_csv('/Users/huyiming/Downloads/python練習/binance/BTCUSDT_backtest.csv')

long_period = 40
short_period = 13

data['long_sma'] = talib.SMA(data['Close'], timeperiod = long_period)
data['short_sma'] = talib.SMA(data['Close'], timeperiod = short_period)

'''
做多規則:1.short_sma > long_sma 多頭趨勢 2.k棒收盤後小於短均線 3.收盤價的值-長均線的值 > 收盤價的值 * 3.5% 此為關鍵K棒
4.停損在關鍵k棒的長均線 5.停利:(關鍵k棒收盤價-長均線的值)*0.3 + 收盤價

做空規則:1.short_sma < long_sma 空頭趨勢 2.k棒收盤後大於短均線 3.長均線的值-收盤價的值 > 收盤價的值 * 3.5% 此為關鍵k棒
4.停損在關鍵k棒的長均線 5.停利:收盤價-(長均線的值-關鍵k棒收盤價)*0.3
'''

long_condition = data['short_sma'] > data['long_sma']
data.loc[long_condition, 'trend'] = 'long'
short_condition = data['short_sma'] < data['long_sma']
data.loc[short_condition, 'trend'] = 'short'

data['signal'] = 0

for i in range(1, len(data)):
    if data.loc[i, 'signal'] == 0 and data.loc[i, 'trend'] == 'long' :
        if data.loc[i, 'Close'] < data.loc[i, 'short_sma'] and (data.loc[i, 'Close'] - data.loc[i, 'long_sma']) > data.loc[i, 'Close'] * 0.035 :
                data.loc[i, 'signal'] = 1
    
    elif data.loc[i, 'signal'] == 0 and data.loc[i, 'trend'] == 'short' :
        if data.loc[i, 'Close'] > data.loc[i, 'short_sma'] and (data.loc[i, 'long_sma'] - data.loc[i, 'Close']) > data.loc[i, 'Close'] * 0.035 :
                data.loc[i, 'signal'] = -1

print(data)

if __name__ == '__main__' :
    sma_backtest = BackTest(data, equity = 10000)
    result = sma_backtest.run()
    print(result)
    sma_backtest.get_equity_curve()
    trade = sma_backtest.trades()
    print(trade)

 
         
                     
                            
                
        
            
        
