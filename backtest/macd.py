import pandas as pd
import talib
from tqdm import tqdm
from back_test import BackTest
#macd 策略
'''
做多:1.k棒收盤後高於ema200 2.macd線大於信號線形成金叉 3.SAR點在k棒下方 滿足前三點為關鍵k棒
     4.停損在關鍵k棒的SAR點上 5.停利目標按風險回報比1:1進行設置(假設進場價100止損90止盈110)
做空:1.k棒收盤後小於ema200 2.macd線小於信號線形成死叉 3.SAR點在k棒上方 滿足前三點為關鍵k棒
     4.停損在關鍵k棒的SAR點上 5.停利目標按風險回報比1:1進行設置(假設進場價100止損90止盈110)
'''
pd.set_option('display.max_rows', None)
data = pd.read_csv('/Users/huyiming/Downloads/python練習/binance/ETHUSDT_backtest.csv')
data['macd'], data['signal_line'], data['hist'] = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
data['sar'] = talib.SAR(data['High'], data['Low'], acceleration=0.02, maximum=0.2)
data['ema'] = talib.EMA(data['Close'], timeperiod = 200)
# print(data)

data['signal'] = 0

for i in tqdm(range(1, len(data))) :
    current_close = data.loc[i, 'Close']
    prev_macd = data.loc[i-1, 'macd']
    prev_signal_line = data.loc[i-1, 'signal_line']
    current_macd = data.loc[i, 'macd']
    current_signal_line = data.loc[i, 'signal_line']
    current_sar = data.loc[i, 'sar']
    ema = data.loc[i, 'ema']
    low = data.loc[i, 'Low']
    high = data.loc[i, 'High']
    if current_close > ema and prev_macd < prev_signal_line and current_macd > current_signal_line  and low < current_sar :
        data.loc[i, 'signal'] = 1
    elif current_close < ema and prev_macd > prev_signal_line and current_macd < current_signal_line and current_sar > high :
        data.loc[i, 'signal'] = -1

macd = BackTest(data = data, equity = 10000)
result = macd.run()
print(result)

macd.get_equity_curve()

print(macd.get_trades())
    
