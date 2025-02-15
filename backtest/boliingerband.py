'''
做多規則:1.k棒收盤後突破布林帶上軌且柱狀圖大於0.01 2.k棒下一根的open進場
        3.移動停利,當最新一根未收盤的k棒碰到上一根已收盤的k棒布林帶std:3.5上軌停利
        4.移動停損,當最新一根未收盤的k棒碰到上一根已收盤的k棒布林帶std:2.5中軌停利

做空規則:1.k棒收盤後突破布林帶下軌且柱狀圖大於0.01 2.k棒下一根的open進場
        3.移動停利,當最新一根未收盤的k棒碰到上一根已收盤的k棒布林帶std:3.5下軌停利
        4.採用移動停損,當最新一根未收盤的k棒碰到上一根已收盤的k棒布林帶std:2.5中軌停利
'''
import pandas as pd
import talib
from back_test import BackTest
from tqdm import tqdm

pd.set_option('display.max_rows', None)

time_period = 24

small_std = 2.5

big_std = 6.5

data = pd.read_csv('/Users/huyiming/Downloads/python練習/ta-lib/backtest/ETHUSDT_backtest.csv')

data['atr'] = talib.ATR(data['High'], data['Low'], data['Close'], timeperiod = 14)

data['S_BB_Upper'], data['S_BB_Middle'], data['S_BB_Lower'] = talib.BBANDS(
    data['Close'], timeperiod = time_period, nbdevup = small_std, nbdevdn = small_std, matype=0)

data['B_BB_Upper'], data['B_BB_Middle'], data['B_BB_Lower'] = talib.BBANDS(
    data['Close'], timeperiod = time_period, nbdevup = big_std, nbdevdn = big_std, matype=0)

data['BBW'] = (data['S_BB_Upper'] - data['S_BB_Lower']) / data['S_BB_Middle']

data['signal'] = 0
for i in tqdm(range(1, len(data))) :
    if data.loc[i, 'Close'] > data.loc[i, 'S_BB_Upper'] and data.loc[i, 'BBW'] > 0.04 :
        data.loc[i, 'signal'] = 1
    elif data.loc[i, 'Close'] < data.loc[i, 'S_BB_Lower'] and data.loc[i, 'BBW'] > 0.04 :
        data.loc[i, 'signal'] = -1


backtest = BackTest(data, equity = 10000)
result = backtest.run()

print(result)

backtest.get_equity_curve()

print(backtest.get_trades())


        
#2h: 30, 3, 7, 0.04
#1h: 24, 2.5, 6.5, 0.04, atr:10
#3h: 

