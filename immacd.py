import pandas as pd
import talib
import numpy as np
from back_test import BackTest
from tqdm import tqdm

'''
改良過後的macd策略(impulse macd):
1.先分別計算high,low的smma   
2.計算hlc3_zlema:即先計算hlc3的ema在就此ema在平滑一次。
3.計算md線為快線,如果hlc3_zlema大於high_smma則 md = hlc_zlema - high_smma,若hlc3_zlema小於low_smma則 md = hlc_zlema - high_smma
  若介於兩者間則等於0,如此可過濾橫盤信號。 
4.sb線為慢線為md線的sma

做多規則：
1.金叉時以收盤價做多 
2.止損為移動止損 max(self.stop_loss, current_price - 1 * atr) 
3.停利為固定買入價格的4倍atr

做空規則：
1.死叉時以收盤價做多 
2.止損為移動止損 min(self.stop_loss, current_price + 1 * atr) 
3.停利為固定買入價格的4倍atr
'''


pd.set_option('display.max_rows', None)

df = pd.read_csv('/Users/huyiming/Downloads/python練習/binance/ETHUSDT_backtest.csv')

length_ma = 30
lenth_signal = 10
lenth_atr = 12


df['atr'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod = lenth_atr)
df['hlc3'] = (df['High'] + df['Low'] + df['Close']) / 3

def calc_smma(df, column, lenth):
    df[f'{column}_sma'] = talib.SMA(df[column], timeperiod = lenth)
    
    ssma = f'{column}_ssma'
    df[ssma] = np.nan
    
    df.loc[lenth-1, ssma] = df.loc[lenth-1, f'{column}_sma']
    
    for i in tqdm(range(lenth, len(df))):
        df.loc[i, ssma] = (df.loc[i-1, ssma] * (lenth - 1) + df.loc[i, column]) / lenth
    
    return df

low_df = calc_smma(df, 'Low', length_ma)
both_df = calc_smma(low_df, 'High', length_ma)

def calc_zlema_df(df, column, lenth):
    df[f'{column}_ema'] = talib.EMA(df[column], timeperiod = lenth)
    df['sema'] = talib.EMA(df[f'{column}_ema'], timeperiod = lenth)
    zlema = f'{column}_zlema'
    df[zlema] = df[f'{column}_ema'] + (df[f'{column}_ema'] - df['sema'])
    return df

third_df = calc_zlema_df(both_df, 'hlc3', length_ma)

def calc_impulse_macd(df, lenth):
    df['md'] = np.where(df['hlc3_zlema'] > df['High_ssma'], df['hlc3_zlema'] - df['High_ssma'], 
                        np.where(df['hlc3_zlema'] < df['Low_ssma'], df['hlc3_zlema'] - df['Low_ssma'], 0))
    
    df['sb'] = talib.SMA(df['md'], timeperiod = lenth)
    
    df['sh'] = df['md'] - df['sb']
    return df



forth_df = calc_impulse_macd(third_df, lenth_signal)

def ger_signal(df):
    for i in tqdm(range(1, len(df))):
        if df.loc[i-1, 'md'] > df.loc[i-1, 'sb'] and df.loc[i, 'md'] < df.loc[i, 'sb']:
            df.loc[i, 'signal'] = -1
        elif df.loc[i-1, 'md'] < df.loc[i-1, 'sb'] and df.loc[i, 'md'] > df.loc[i, 'sb']:
            df.loc[i, 'signal'] = 1
        
    return df



fifth_df =ger_signal(forth_df)

if __name__ == '__main__' :
    backtest = BackTest(data = fifth_df, equity = 10000)
    result = backtest.run()
    print(result)
    trade = backtest.get_trades()
    print(trade)
    backtest.get_equity_curve()
    
    sharpe_ratio = backtest.calculate_annual_sharpe_ratio()
    print(f"年化夏普比率: {sharpe_ratio:.2f}")
    cr = backtest.calculate_cumulative_return()
    print(f'累積報酬率: {cr:.2%}')   
    ar = backtest.calculate_annual_return()
    print(f'年化報酬率:{ar :.2%}')
    av = backtest.calculate_annualized_volatility()
    print(f'年化波動度: {av:.2f}')
    rr = backtest.calculate_profit_factor()
    print(f'風險回報比: {rr:.2f}')
    hb = backtest.calculate_avg_hold_bars()
    print(f'平均持有K棒數: {hb:.2f}')
    bh = backtest.calculate_buy_and_hold_return()
    print(f'Buy and hold return:{bh:.2%}') 
    trade_metrics = backtest.calculate_trade_stats()
    print(trade_metrics)
    long_avg_profit, long_avg_loss = backtest.calculate_long_trade_performance()
    print(f'多單平均獲利:{long_avg_profit:.2%}, 多單平均虧損:{long_avg_loss:.2%}')
    short_avg_profit, short_avg_loss = backtest.calculate_short_trade_performance()
    print(f'空單平均獲利:{short_avg_profit:.2%}, 空單平均虧損:{short_avg_loss:.2%}')
    all_trade_pro, all_trade_loss = backtest.calculate_all_trade_performance()
    print(f'平均獲利:{all_trade_pro:.2%}, 平均虧損:{all_trade_loss:.2%}')
    backtest.plot_pnl_distribution()
    
    
    
 
