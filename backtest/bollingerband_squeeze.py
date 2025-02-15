import pandas as pd
import talib
from back_test import BackTest
#python3 /Users/huyiming/Downloads/python練習/ta-lib/backtest/bollingerband.py

pd.set_option('display.max_rows',None)

data = pd.read_csv('/Users/huyiming/Downloads/python練習/binance/ETHUSDT_backtest.csv')

timeperiod = 40
BB_multiplier = 2
KC_multiplier = 1.5

data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = talib.BBANDS(
    data['Close'], timeperiod = timeperiod, nbdevup = BB_multiplier, nbdevdn = BB_multiplier, matype=1)

data['ATR'] = talib.ATR(data['High'], data['Low'], data['Close'], timeperiod = timeperiod)

data['KC_Middle'] = talib.EMA(data['Close'], timeperiod = timeperiod)
data['KC_Upper'] = data['KC_Middle'] + (KC_multiplier * data['ATR'])
data['KC_Lower'] = data['KC_Middle'] - (KC_multiplier * data['ATR'])

def bcwsma(series, l, m):
    result = pd.Series(index=series.index, dtype='float64')
    for i in range(len(series)):
        if i == 0:
            result.iloc[i] = series.iloc[i]  # 第一個值直接使用輸入值
        else:
            result.iloc[i] = (m * series.iloc[i] + (l - m) * result.iloc[i - 1]) / l
    return result

def calculate_kdj(data, period=23, signal=3):# 計算 RSV
    data['high_max'] = data['High'].rolling(window=period).max()
    data['low_min'] = data['Low'].rolling(window=period).min()
    data['RSV'] = 100 * (data['Close'] - data['low_min']) / (data['high_max'] - data['low_min'])

    # 平滑計算 K 和 D
    data['K'] = bcwsma(data['RSV'].fillna(0), signal, 1)
    data['D'] = bcwsma(data['K'], signal, 1)

    # 計算 J
    data['J'] = 3 * data['K'] - 2 * data['D']

    # 清理臨時列
    return data

kdj = calculate_kdj(data, period=23, signal=3)




squeeze_on_condition = (data['BB_Upper'] < data['KC_Upper']) & (data['BB_Lower'] > data['KC_Lower'])
data.loc[squeeze_on_condition, 'squeeze'] = 'squeeze_on'

squeeze_off_condition = (data['BB_Upper'] > data['KC_Upper']) | (data['BB_Lower'] < data['KC_Lower'])
data.loc[squeeze_off_condition, 'squeeze'] = 'squeeze_off'
'''
產生做多信號:1.處在擠壓 2.擠壓期間某一根k棒收盤後收在布林通道下線,並且kdj(j線)小於20 
           3.當kdj信號大於20以上,並且k棒要收漲,用此關鍵k棒close進場做多 4.停損在關鍵k棒近期最低點
           5.停利當kdj信號出現大於80以上做停利準備,從80下跌後馬上停利

產生做空信號:1.處在擠壓 2.擠壓期間某一根k棒收盤後收在布林通道上線,並且kdj(j線)大於80 
           3.當kdj信號小於80以下,並且k棒要收跌,用此k棒close進場做空 4.停損在關鍵k棒近期最高點
           5.停利當kdj信號出現小於20以下做停利準備,從20上漲後馬上停利
''' 
data['signal'] = 0

for i in range(1, len(data)):
    #做多信號,條件1:處於擠壓
    if data.loc[i, 'squeeze'] == 'squeeze_on'  :
        #條件二:收在布林通道下線以下,且j線小於20
        if data.loc[i , 'Close'] < data.loc[i, 'BB_Lower'] and data.loc[i, 'J'] < 20 :
            #從當前k棒往後檢查
            for j in range(i+1 , len(data)) :
                #條件三:j線大於20,且k棒收漲
                if data.loc[j, 'J'] > 20 and data.loc[j, 'Close'] > data.loc[j-1, 'Close'] :
                    data.loc[j, 'signal'] = 1
                    break
        #做空信號,條件2:收在布林上線以上,且j線大於80
        elif data.loc[i , 'Close'] > data.loc[i, 'BB_Upper'] and data.loc[i, 'J'] > 80 :
            #從當前k棒往後檢查
            for j in range(i+1, len(data)) :
                #條件三:j線小於80,且k棒收跌
                if data.loc[j, 'J'] < 80 and data.loc[j, 'Close'] < data.loc[j-1, 'Close'] :
                    data.loc[j, 'signal'] = -1
                    break

print(data)

if __name__ == '__main__' :
    bb_backtset = BackTest(data, equity = 10000)
    
    result = bb_backtset.run()
    
    trade = bb_backtset.trades()
    
    equity_curve = bb_backtset.get_equity_curve()
    
    print(result)
    
    print(trade)
    
        
