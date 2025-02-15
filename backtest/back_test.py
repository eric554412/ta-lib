import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.ticker as mticker



class BackTest(object):
        def __init__(self , data , equity , commission = 0.00075):
            
            self.data = data.copy()
            self.equity = equity
            self.commission = commission
            self.position = 0
            self.entry_price = None
            self.data['equity'] = equity
            self.data['position'] = 0
            self.data['transaction'] = None
            self.data['Datetime'] = pd.to_datetime(self.data['Datetime'])
            self.trade = []
            self.highest_price = 0
            self.lowest_price = 0
                     
        def long(self , row_index, price):
            '''
            做多時有空頭倉位先平倉,並動態紀錄equity,並記錄進場的high和low
            '''
            
            #開多倉
            amount = (self.equity)  / price
            self.position += amount
            self.equity -= amount * price * (1 + self.commission)
            #紀錄進場的high和low
            self.highest_price = self.data.loc[row_index , 'High']
            self.lowest_price = self.data.loc[row_index , 'Low']
            
            self.data.loc[row_index , 'equity'] = self.get_total_equity(price = price)
            self.data.loc[row_index , 'position'] = self.position
            self.data.loc[row_index , 'transaction'] = f'buy_{amount}_at_{price}'
            self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours = 1) , 
                            'action':'long' , 'amount':amount , 'price' : price , 
                            'equity' : self.get_total_equity(price = price)})
        
        def short(self , row_index, price):
            '''
            做空時有多頭倉位先平倉,記錄進場的high和low
            '''
            
            #開空倉
            amount = (self.equity) / price
            self.position -= amount
            self.equity += amount * price * (1 - self.commission)
            #紀錄進場時的high和low
            self.highest_price = self.data.loc[row_index , 'High']
            self.lowest_price = self.data.loc[row_index , 'Low']
                    
            self.data.loc[row_index , 'equity'] = self.get_total_equity(price = price)
            self.data.loc[row_index , 'position'] = self.position
            self.data.loc[row_index , 'transaction'] = f'short_{amount}_at_{price}'
            self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours = 1) , 
                            'action':'short' , 'amount':amount , 'price' : price , 
                            'equity' : self.get_total_equity(price = price)})
            
        def sell(self, row_index, price):
            '''
            平多倉的函數
            '''
            
            if self.position > 0 :
                self.equity += self.position * price * (1 - self.commission)
                self.data.loc[row_index , 'transaction'] = f'close_long _{self.position}_at_{price}'
                self.position = 0
                self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours = 1) , 
                                'action':'close_long' , 'amount':self.position , 'price' : price , 
                                'equity' : self.equity})
            
            return self.equity , self.position
        
        
        def cover(self, row_index, price):
            '''
            平空倉的函數
            '''
            
            if self.position < 0 :
                self.equity -= abs(self.position) * price * (1 + self.commission)
                self.data.loc[row_index , 'transaction'] = f'close_short _{self.position}_at_{price}'
                self.position = 0 
                self.trade.append({'time': self.data.loc[row_index , 'Datetime'] +pd.Timedelta(hours = 1) ,
                                'action':'close_short' , 'amount':self.position , 'price' : price , 
                                'equity' : self.equity})
            
            return self.equity , self.position
                
        
        
        def get_total_equity(self , price):
            '''
            紀錄equity的函數,包含未實現損益
            '''
            
            unrealized_profit = self.position * price
            total_equity = self.equity + unrealized_profit
            return total_equity
        
        
        def close_position(self):
            '''
            基於最後一根k線的close,平倉,結束回測
            '''
            
            final_price = self.data.loc[self.data.index[-1] , 'Open']

            if self.position > 0 :
                self.equity += self.position * final_price * (1 - self.commission)
            elif self.position < 0 :
                self.equity -= abs(self.position) * final_price * (1 + self.commission)
            self.position = 0
            self.data.loc[self.data.index[-1], 'position'] = self.position
            self.data.loc[self.data.index[-1], 'equity'] = self.equity
            self.data.loc[self.data.index[-1], 'transaction'] = f'close_position_at_{final_price}'
            self.trade.append({'time': self.data.loc[self.data.index[-1] , 'Datetime'] , 
                            'action':'close_position' , 'amount':self.position , 'price' : final_price , 
                            'equity' : self.equity})
            
        def calculate_max_drawdown(self):
                equity = self.data['equity']
                peak = equity.expanding().max()
                drawdown = (equity - peak) / peak
                max_drawdown = drawdown.min()
                #找出最大回撤時間點
                max_drawdown_end = drawdown.idxmin()
                max_drawdown_start = (equity[:max_drawdown_end]).idxmax()
                
                return max_drawdown , max_drawdown_start , max_drawdown_end
        
        def run(self):
                '''
                超級趨勢
                '''
               
                for i in tqdm(range(1, len(self.data))) :
                    current_price = self.data.loc[i, 'Close']
                    atr = self.data.loc[i, 'atr_9']
                    if self.position == 0 :
                        if self.data.loc[i, 'signal'] == 1 :
                            self.long(row_index = i, price = current_price)
                            self.stop_loss = self.data.loc[i, 'stop_loss']
                        
                        
                        elif self.data.loc[i, 'signal'] == -1 :
                            self.short(row_index = i, price = current_price)
                            self.stop_loss = self.data.loc[i, 'stop_loss']
                         
                            
                    
                    elif self.position > 0 :
                        if self.data.loc[i, 'signal'] == -1 :
                            self.sell(row_index = i,price = current_price)
                            self.stop_loss = None
                        elif current_price < self.stop_loss :
                            self.sell(row_index = i,price = current_price)
                            self.stop_loss = None
                    
                    elif self.position < 0 :
                        if self.data.loc[i, 'signal'] == 1 :
                            self.cover(row_index = i, price = current_price)
                            self.stop_loss = None
                        elif current_price > self.stop_loss :
                            self.cover(row_index = i, price = current_price)
                            self.stop_loss = None
                    
                    self.data.loc[i, 'position'] = self.position
                    self.data.loc[i, 'equity'] = self.get_total_equity(price = current_price)
                
                self.close_position()
                self.max_drawdown = self.calculate_max_drawdown() 
                
                return self.data[['Datetime','Close' , 'signal' , 'equity' , 'position' , 'transaction']]
                            
        def get_trades(self):
            '''
            打印交易日誌
            '''
            return pd.DataFrame(self.trade)
             
        
        def get_equity_curve(self):
            '''
            繪製equity_curve,並標記最大回撤範圍
            '''
            max_drawdown, max_drawdown_start, max_drawdown_end = self.calculate_max_drawdown()
            
            # 繪製 Equity Curve
            plt.figure(figsize=(16, 8))  # 增加圖表尺寸
            plt.plot(self.data['Datetime'], self.data['equity'], 
                    label='Equity Curve', color='blue', linewidth=2)

            # 繪製最大回撤區間
            start_date = self.data.loc[max_drawdown_start, 'Datetime']
            end_date = self.data.loc[max_drawdown_end, 'Datetime']
            start_equity = self.data.loc[max_drawdown_start, 'equity']
            end_equity = self.data.loc[max_drawdown_end, 'equity']

            # 最大回撤虛線
            plt.plot([start_date, end_date], [start_equity, end_equity], 
                    color='red', linestyle='--', label='Max Drawdown')
            plt.scatter(start_date, start_equity, color='green', label='Peak', zorder=5)
            plt.scatter(end_date, end_equity, color='red', label='Trough', zorder=5)

            # 添加圖表標題與標籤
            plt.title(f'Equity Curve (Max Drawdown: {max_drawdown:.2%})', fontsize=20)
            plt.xlabel('Time', fontsize=14)
            plt.ylabel('Equity', fontsize=14)

         
            ax = plt.gca()
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))  # 顯示完整數字

            plt.legend(fontsize=12)
            plt.grid(alpha=0.5)
            plt.tight_layout()
            plt.show()


    









class BackTestLimit(object):
    def __init__(self, data, equity, commission = 0.001):
        '''
        為限價單的回測
        '''
        self.data = data.copy()
        self.equity = equity
        self.commission = commission
        self.position = 0
        self.entry_price = None
        self.data['equity'] = equity
        self.data['position'] = 0
        self.data['transaction'] = None
        self.data['Datetime'] = pd.to_datetime(self.data['Datetime'])
        self.data['limit_price'] = 0
        self.data['order'] = None
        self.trade = []
    
    def get_total_equity(self, price):
        
        unrealized_profit = price * self.position
        
        total_equity = self.equity + unrealized_profit
        
        return total_equity

    def long(self, row_index):
        '''
        做多以限價單做多
        '''
        price = self.data.loc[row_index, 'limit_price']
        #開多倉
        amount = self.equity / price
        self.position += amount
        self.equity -= amount * price * (1 + self.commission)
         
        self.data.loc[row_index, 'equity'] = self.get_total_equity(price = price)
        self.data.loc[row_index, 'position'] = self.position
        self.data.loc[row_index, 'transaction'] = f'buy_{amount}_at{price}'
        self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours = 1) , 
                            'action':'long' , 'amount':amount , 'price' : price , 
                            'equity' : self.get_total_equity(price = price)})
        
    def short(self, row_index):
        '''
        做空以限價單做空
        '''
        price = self.data.loc[row_index, 'limit_price']
        #開空倉
        amount = self.equity / price
        self.position += amount
        self.equity += amount * price * (1 - self.commission)
        
        self.data.loc[row_index, 'equity'] = self.get_total_equity(price = price)
        self.data.loc[row_index, 'position'] = self.position
        self.data.loc[row_index, 'transaction'] = f'short_{amount}_at{price}'
        self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours = 1) , 
                            'action':'short' , 'amount':amount , 'price' : price , 
                            'equity' : self.get_total_equity(price = price)})
    
    def sell(self, row_index, price):
        '''
        平多倉的函數
        '''
        if self.position > 0 :
            amount_closed = self.position
            self.equity = self.position * price * (1 - self.commission)
            self.data.loc[row_index, 'transaction'] = f'close_long _{self.position}_at_{price}'
            self.position = 0 
            self.trade.append({'time': self.data.loc[row_index , 'Datetime'] +pd.Timedelta(hours = 1) ,
                                'action':'close_long' , 'amount':amount_closed , 'price' : price , 
                                'equity' : self.equity})
            return self.equity, self.position
        
    def cover(self, row_index, price):
        '''
        平空倉的函數
        '''
        
        if self.position < 0 :
            amount_closed = abs(self.position)
            self.equity -= abs(self.position) * price * (1 + self.commission)
            self.data.loc[row_index, 'transaction'] = f'close_short _{self.position}_at_{price}'
            self.position = 0
            self.trade.append({'time': self.data.loc[row_index , 'Datetime'] +pd.Timedelta(hours = 1) ,
                                'action':'close_short' , 'amount':amount_closed , 'price' : price , 
                                'equity' : self.equity})
            return self.position, self.equity   
    
    def calculate_max_drawdown(self) :
        equity = self.data['equity']
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min()
        #最大回撤期間
        max_drawdown_end = drawdown.idxmin()
        max_drawdown_start = (equity[:max_drawdown_end]).idxmax()
        return max_drawdown , max_drawdown_start , max_drawdown_end
    
    def run(self) :
        '''
        尋找交易訊號
        '''
       
                
            
        
        
        
        
                
        
        
            
  
        
        