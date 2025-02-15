import pandas as pd

#假設資料為每一小時

class backtest(object):
    def __init__(self , data , equity , commission = 0.0001):
        self.data = data.copy()
        self.equity = equity
        self.commission = commission
        self.position = 0
        self.data['equity'] = self.equity
        self.data['position'] = self.position
        self.data['Datetime'] = pd.to_datetime(self.data['Datetime'])
        self.transaction = None
        self.trade = []
        
    def long(self , row_index , amount):
        price = self.data.loc[row_index , 'Close']
        #平空倉
        if self.position < 0 :
            self.equity += price * amount * (1 - self.commission)
            self.position = 0
            self.trade.append({'time' : self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours=1), 'action' : 'close_short' , 
                           'amount' : self.position , 'price' : price , 'equity' : self.equity})
        
        #開多倉
        self.position += amount
        self.equity -= price * amount * (1 + self.commission)
        self.data.loc[row_index , 'equity'] = self.equity
        self.data.loc[row_index , 'position'] = self.position
        self.data.loc[row_index , 'transaction'] = f'long_{amount}_at_{price}'
        self.trade.append( {'time' : self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours=1) , 'action' : 'long' , 
                           'amount' : amount , 'price' : price , 'equity' : self.equity} )
    
    def short(self, row_index , amount):
        price = self.data.loc[row_index , 'Close']
        #平多倉
        if self.position > 0 :
            self.equity -= price * amount * (1 + self.commission)
            self.position = 0
            self.trade.append( {'time' : self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours=1) , 'action' : 'close_long' , 
                           'amount' : amount , 'price' : price , 'equity' : self.equity} )
        
        #開空倉
        self.position -= amount
        self.equity += price * amount * (1 + self.commission)
        self.data.loc[row_index , 'equity'] = self.equity
        self.data.loc[row_index , 'position'] = self.position
        self.data.loc[row_index , 'transaction'] = f'short_{amount}_at_{price}'
        self.trade.append( {'time' : self.data.loc[row_index , 'Datetime'] + pd.Timedelta(hours=1) , 'action' : 'short' , 
                           'amount' : amount , 'price' : price , 'equity' : self.equity} )
    
    def close_position(self):
        price = self.data.loc[self.data.index[-1] , 'Close']
        
        if self.position > 0 :
            self.equity -= self.position * price * (1 + self.commission)
        elif self.position < 0 :
            self.equity += abs(self.position) * price * (1 - self.commission)
        
        self.position = 0
        self.data.loc[self.data.index[-1] , 'position'] = self.position
        self.data.loc[self.data.index[-1] , 'equity'] = self.equity
        self.data.loc[self.data.index[-1] , 'transaction'] = f'close_position_at_{price}'
        self.trade.append( {'time' : self.data.loc[self.data.index[-1] , 'Datetime'] , 'action' : 'close_position' , 
                           'amount' : self.position , 'price' : price , 'equity' : self.equity} )
    
    def run(self):
        for i in range(1 , len(self.data)):
            if self.data.loc[i , 'signal'] == 1:
                self.long(row_index = i , amount=1)
            elif self.data.loc[i , 'signal'] == -1:
                self.short(row_index = i , amount=1)
            else:
                self.data.loc[i , 'equity'] = self.equity
                self.data.loc[i , 'position'] = self.position
        
        self.close_position()
        
        return self.data
    
    def trades(self):
        return pd.DataFrame(self.trade)
        
        
        
    
    
        