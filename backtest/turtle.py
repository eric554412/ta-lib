import pandas as pd
import talib
from back_test import BackTest
#python3 /Users/huyiming/Downloads/python練習/ta-lib/backtest/turtle.py

pd.set_option('display.max_rows', None)

data = pd.read_csv('/Users/huyiming/Downloads/python練習/binance/DOGEUSDT_backtest.csv')

# print(data)

data['entry_up'] = talib.MAX(data['High'].shift(1) , 50)
data['entry_dn'] = talib.MIN(data['Low'].shift(1) , 50)

data['exit_up'] = talib.MAX(data['High'].shift(1) , 13)
data['exit_dn'] = talib.MIN(data['Low'].shift(1) , 13)

data['atr'] = talib.ATR(data['High'] , data['Low'] , data['Close'] , timeperiod = 14)


'''
當close突破長週期信號則做多或做空
'''

class Turtle_Strategy(object):
    def __init__(self, data):
        self.data = data.copy()
        self.position = 0
        self.data['symbol'] = 0
    
    def gernerate_signal(self):
        for row_index in range(1, len(self.data)) :
            entry_up = self.data.loc[row_index , 'entry_up']
            entry_dn = self.data.loc[row_index , 'entry_dn']
            current_price = self.data.loc[row_index , 'Close']
            if current_price > entry_up :
                self.data.loc[row_index, 'signal'] = 1
            elif current_price < entry_dn :
                self.data.loc[row_index, 'signal'] = -1
            else:
                self.data.loc[row_index, 'signal'] = 0
                
        return self.data

data1=Turtle_Strategy(data)

data2 = data1.gernerate_signal()
# data2['signal'] = data2['signal'].mask(data2['signal'].cumsum() == 1, 0)
data2 = data2[['Datetime', 'Open', 'High', 'Low' , 'Close' , 'entry_up' , 'entry_dn', 'exit_up', 'exit_dn', 'atr', 'signal']]
                
print(data2)                

turtle_backtest = BackTest(data2 , equity=10000)

result = turtle_backtest.run()

trade = turtle_backtest.trades()

equity_curve = turtle_backtest.get_equity_curve()
print(result)

print(trade)

