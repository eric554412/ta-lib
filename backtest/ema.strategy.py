import pandas as pd
import numpy as np
from back_test import BackTest
import talib
'''
當金叉時做多,死叉時做空
'''
data = pd.read_csv('/Users/huyiming/Downloads/python練習/ta-lib/backtest/ETHUSDT_backtest.csv')
#python3 /Users/huyiming/Downloads/python練習/ta-lib/backtest/ema.strategy.py
pd.set_option('display.max_rows', None)
pd.set_option('expand_frame_repr' , False)

data['long_ema'] = talib.EMA(data['Close'] , timeperiod = 40)
data['short_ema'] = talib.EMA(data['Close'] , timeperiod = 20)
data['atr'] = talib.ATR(data['High'] , data['Low'] , data['Close'] , timeperiod = 10 )


def signal(data):
    data['signal'] = 0
    for i in range(1 , len(data)):
        short_ema = data.loc[i, 'short_ema']
        long_ema = data.loc[i, 'long_ema']
        prev_short_ema = data.loc[i-1, 'short_ema']
        prev_long_ema = data.loc[i-1, 'long_ema']
        
        if pd.isna(short_ema) or pd.isna(long_ema):
            continue
        
        if prev_long_ema >= prev_short_ema  and short_ema > long_ema :
            data.loc[i , 'signal'] = 1
        elif prev_long_ema <= prev_short_ema and short_ema < long_ema :
            data.loc[i ,'signal'] = -1
        else :
            data.loc[i , 'signal'] = 0
    return data

signal_data = signal(data)



# print(data)
ema_backtest = BackTest(signal_data , equity= 10000)
result = ema_backtest.run()

trade = ema_backtest.get_trades()

ema_backtest.get_equity_curve()

print(result)

print(trade) 


    





            
    