import pandas as pd
import talib
from tqdm import tqdm
import numpy as np
from back_test import BackTest



pd.set_option('display.max_rows', None)

df = pd.read_csv('/Users/huyiming/Downloads/python練習/ta-lib/backtest/ETHUSDT_backtest.csv')


'''
計算supertrend
'''
def atr(df, period, use_talib = True):
    if use_talib :
        df[f'atr_{period}'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod = period)
    else :
        df[f'atr{period}'] = df['High'].rolling(period).mean() - df['Low'].rolling(period).mean()
    return df

def supertrend(df, atr_period, multiplier):
    df1 = df.copy()
    df1 = atr(df, atr_period)
    
    df1[f'Up_{atr_period}'] = (df1['High'] + df1['Low']) / 2 - multiplier * df1[f'atr_{atr_period}']
    df1[f'Dn_{atr_period}'] = (df1['High'] + df1['Low']) / 2 + multiplier * df1[f'atr_{atr_period}']
    
    df1[f'trend_{atr_period}'] = 1
    df1['signal'] = 0
        
    for i in tqdm(range(1, len(df1))) :
        '''
        確保 Up(支撐位)和 Dn(阻力位)在趨勢延續時具有連續性：
        - 若價格突破 Dn,可能形成多頭趨勢；若價格跌破 Up,則可能形成空頭趨勢。
        - Up在多頭趨勢中只升不降:
            - 若前一根 K 線收盤價(Close)> 前一根 Up,則 Up = max(前一根 Up,本根 Up)。
            - 這表示 Up 只會上升,確保只有當價格真的跌破 Up 時,才確認進入空頭趨勢。
        - Dn在空頭趨勢中只降不升:
            - 若前一根 K 線收盤價(Close)< 前一根 Dn,則 Dn = min(前一根 Dn,本根 Dn)。
            - 這表示 Dn 只會下降,確保只有當價格真的突破 Dn 時,才確認進入多頭趨勢。
        '''
        if df1.loc[i-1, 'Close'] > df1.loc[i-1, f'Up_{atr_period}'] :
            df1.loc[i, f'Up_{atr_period}'] = max(df1.loc[i, f'Up_{atr_period}'], df1.loc[i-1, f'Up_{atr_period}'])
        else :
            df1.loc[i, f'Up_{atr_period}'] = df1.loc[i, f'Up_{atr_period}']
        
        if df1.loc[i-1, 'Close'] < df1.loc[i-1, f'Dn_{atr_period}'] :
            df1.loc[i, f'Dn_{atr_period}'] = min(df1.loc[i-1, f'Dn_{atr_period}'], df1.loc[i, f'Dn_{atr_period}'])
        else :
            df1.loc[i, f'Dn_{atr_period}'] = df1.loc[i, f'Dn_{atr_period}'] 
        
        #supertrend趨勢變化
        '''
        - 若當前趨勢為多頭(trend = 1),但價格跌破 Up,則轉為空頭(trend = -1).
        - 若當前趨勢為空頭(trend = -1),但價格突破 Dn,則轉為多頭(trend = 1).
        - 若未滿足上述條件，則維持前一根 K 線的趨勢狀態。
        '''
        if df1.loc[i-1, f'trend_{atr_period}'] == 1 and df1.loc[i, 'Close'] < df1.loc[i-1, f'Up_{atr_period}'] :
            df1.loc[i, f'trend_{atr_period}'] = -1
        elif df1.loc[i-1, f'trend_{atr_period}'] == -1 and df1.loc[i, 'Close'] > df1.loc[i-1, f'Dn_{atr_period}'] :
            df1.loc[i, f'trend_{atr_period}'] = 1
        else :
            df1.loc[i, f'trend_{atr_period}'] = df1.loc[i-1, f'trend_{atr_period}']
            
        if df1.loc[i-1, f'trend_{atr_period}'] == -1 and df1.loc[i, f'trend_{atr_period}'] == 1 :
            df1.loc[i, 'signal'] = 1
        elif  df1.loc[i-1, f'trend_{atr_period}'] == 1 and df1.loc[i, f'trend_{atr_period}'] == -1 :
            df1.loc[i, 'signal'] = -1
            
    
    
    return df1

'''
計算Heikin Ashi K 線,並使用ema平滑兩次
'''
df['HA_close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
df['HA_open'] = 0

for i in tqdm(range(1, len(df))) :
    if i == 0:
        df.loc[i, 'HA_open'] = df.loc[i, 'Open']
    else :
        df.loc[i, 'HA_open'] = (df.loc[i - 1, 'HA_open'] + df.loc[i - 1, 'HA_close']) / 2

ema_1 = 52
ema_2 = 10

df['EMA1'] = talib.EMA(df['HA_close'], timeperiod = ema_1)
df['EMA2'] = talib.EMA(df['EMA1'], timeperiod = ema_2)

df['HA_trend'] = np.where(df['EMA2'].diff() > 0, 'Green', 'Red')

df['stop_loss'] = np.where(df['HA_trend'] == 'Green', df['EMA1'], df['EMA2'])

'''
計算QQE mod
'''
rsi_lenth_period = 6
rsi_smoothing_period = 5
qqe_factor_primary = 3
df['rsi'] = talib.RSI(df['Close'], timeperiod = rsi_lenth_period)
df['rsi_smooth'] = talib.EMA(df['rsi'], timeperiod = rsi_smoothing_period)

atr_rsi = abs(df['rsi_smooth'].diff())
df['atr_rsi_smooth'] = talib.EMA(atr_rsi, timeperiod = rsi_lenth_period * 2 - 1)
df['dynamic_atr'] = df['atr_rsi_smooth'] * qqe_factor_primary

df['long_band'] = np.nan
df['short_band'] = np.nan
df['trend_direction'] = 0  # Pine Script 預設為 0
df['QQE_trend_line'] = np.nan

for i in tqdm(range(1, len(df))) :
    new_long_band = df.loc[i, 'rsi_smooth'] - df.loc[i, 'dynamic_atr']
    new_short_band = df.loc[i, 'rsi_smooth'] + df.loc[i, 'dynamic_atr'] 
    if df.loc[i - 1, 'rsi_smooth'] > df.loc[i - 1, 'long_band'] and df.loc[i, 'rsi_smooth'] > df.loc[i - 1, 'long_band'] :
        df.loc[i, 'long_band'] = max(df.loc[i - 1, 'long_band'], new_long_band)
    else :
        df.loc[i, 'long_band'] = new_long_band
    
    if df.loc[i - 1, 'rsi_smooth'] < df.loc[i - 1, 'short_band'] and df.loc[i, 'rsi_smooth'] < df.loc[i - 1, 'short_band'] :
        df.loc[i, 'short_band'] = min(df.loc[i - 1, 'short_band'], new_short_band)
    else :
        df.loc[i, 'short_band'] = new_short_band
    
    if df.loc[i, 'rsi_smooth'] > df.loc[i - 1, 'short_band'] :
        df.loc[i, 'trend_direction'] = 1
    elif df.loc[i, 'rsi_smooth'] < df.loc[i - 1, 'long_band'] :
        df.loc[i, 'trend_direction'] = -1
    else :
        df.loc[i, 'trend_direction'] = df.loc[i-1, 'trend_direction']
    
    if df.loc[i, 'trend_direction'] == 1:
        df.loc[i, 'QQE_trend_line'] = df.loc[i, 'long_band']
    elif df.loc[i, 'trend_direction'] == -1 :
        df.loc[i, 'QQE_trend_line'] = df.loc[i, 'short_band']

'''
計算布林通道
'''
bollinger_length = 50
bollinger_multiplier = 0.35

bollinger_basis = talib.SMA(df['QQE_trend_line'] - 50, timeperiod=bollinger_length)
bollinger_deviation = bollinger_multiplier * talib.STDDEV(df['QQE_trend_line'] - 50, timeperiod=bollinger_length, nbdev=1)

df['bollinger_upper'] = bollinger_basis + bollinger_deviation
df['bollinger_lower'] = bollinger_basis - bollinger_deviation

df['Color'] = np.where(df['rsi_smooth'] - 50 > df['bollinger_upper'], 'Blue',
                       np.where(df['rsi_smooth'] - 50 < df['bollinger_lower'], 'Red', 'Gray'))


df['trade_signal'] = 0
        
if __name__ == '__main__' :
    df1 = supertrend(df, atr_period = 9, multiplier = 3.9)
    
    for i in tqdm(range(1, len(df1))) :
        if df1.loc[i, 'signal'] == 1 and df1.loc[i, 'Color'] == 'Blue' and df1.loc[i, 'HA_trend'] == 'Green' :
            df1.loc[i, 'trade_signal'] = 1
        elif df1.loc[i, 'signal'] == -1 and df1.loc[i, 'Color'] == 'Red' and df1.loc[i, 'HA_trend'] == 'Red' :
            df1.loc[i, 'trade_signal'] = -1
    
    
    backtest = BackTest(data = df1, equity = 10000)
    result = backtest.run()
    print(result)
    trade = backtest.get_trades()
    print(trade)
    backtest.get_equity_curve()

        