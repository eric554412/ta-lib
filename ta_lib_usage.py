import talib
import pandas as pd
import numpy as np


# python3 /Users/huyiming/Downloads/python練習/ta-lib/ta_lib_usage.py

pd.set_option('expand_frame_repr' , False)
pd.set_option('display.max_rows' , None)
df=pd.read_csv('/Users/huyiming/Downloads/python練習/binance/DOGEUSDT_vnpy.csv')
# print(df)

# df['Open_ma'] = talib.MA(df['Open'] , timeperiod=30)
# print(df)

# df['ADX'] = talib.ADX(df['High'] , df['Low'] , df['Close'] ,timeperiod=30)
# df['bop'] = talib.BOP(df['Open'] , df['High'] , df['Low'] , df['Close'])

# df['ATR'] = talib.ATR(df['High'] , df['Low'] ,df['Close'] ,timeperiod=30)


# df['CDL2CROWS'] =talib.CDL2CROWS(df['Open'] , df['High'] , df['Low'] , df['Close'])

#布林帶
# sma = talib.MA(df['Close'] , timeperiod = 30)
# std = talib.STDDEV(df['Close'] , timeperiod=30)

# df['up'] = sma + 2 * std
# df['down'] = sma - 2 * std

# df['donchian_up'] = talib.MAX(df['High'] , timeperiod = 30)
# df['donchian_down'] = talib.MIN(df['Low'] , timeperiod = 30)

#定義一個sma ,布林帶
def caculate_Bollinger_Bands(data , period = 30):
    data['close_sma'] = data['Close'].rolling(window = period).mean()
    std = data['Close'].rolling(window = period).std()
    data['up'] = data['close_sma'] + 2 * std
    data['down'] = data['close_sma'] - 2 * std 
# caculate_Bollinger_Bands(df)

#計算ATR
def caculate_ATR(data , period=30):
    data['prev_close'] = data['Close'].shift(1)
    data['TR'] = data.apply(lambda x : max((x['High'] - x['Low']) , 
                                    abs(x['High'] - x['prev_close']) ,
                                    abs(x['Low'] - x['prev_close']) ) ,axis=1)
    
    alpha = 2 / (period + 1)
    data['ATR'] = 0.0
    data['ATR'].iloc[period] = data['TR'][:(period+1)].mean()
    
    for i in range(period+1, len(data)):
        data['ATR'].iloc[i] = alpha * data['TR'].iloc[i] + (1-alpha) * data['ATR'].iloc[i-1]
    
    
    
    
    
    
    
caculate_ATR(df)



print(df.columns)