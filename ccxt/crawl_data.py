'''
爬取各交易所的數據(主要為幣安)
'''
import os
import datetime
import time
import pandas as pd
import ccxt

pd.set_option('expand_frame_repr' , False)
pd.set_option('display.max_rows' , None)

binance = ccxt.binance()
binance.load_markets()
# print(binance.symbols)
Binance_Limit = 1000
Huobi_Limit = 2000
OKX_Limit = 100

def crawl_exchange_data(exchange_name , symbol , start_time , end_time ):
    '''
    爬取交易所數據的方法
    :param exchange_name:交易所名稱
    :param symbol: 請求的symbol:like dogeusdt , btcusdt
    :param start_time: like 2024-1-1
    :param end_time: like 2024-12-31
    :return:
    '''
    exchange_class = getattr(ccxt , exchange_name)  #獲取交易所的名稱如：ccxt.binance
    exchange = exchange_class()  #初始化如: ccxt.binance()
    print(exchange)
    
    current_path = os.getcwd()
    
    file_dir = os.path.join(current_path , exchange_name , symbol.replace('/' , ''))
    
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    
    start_time = datetime.datetime.strptime(start_time , '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time , '%Y-%m-%d')
    
    start_time_stamp = int(time.mktime(start_time.timetuple())) * 1000
    end_time_stamp = int(time.mktime(end_time.timetuple())) * 1000
     
    limit_count = 1000
    if exchange == 'binance' :
        limit_count = Binance_Limit
    elif exchange == 'Huobi' :
        limit_count = Huobi_Limit
    elif exchange == 'OKX' :
        limit_count = OKX_Limit
        
    while True :
        try:
            if start_time_stamp > end_time_stamp :
                print('數據抓取完成')
                break
            
            print(start_time_stamp)
            data = exchange.fetch_ohlcv(symbol , timeframe = '1h' , since = start_time_stamp , limit = limit_count) 
            df = pd.DataFrame(data)
            
            df.rename(columns={0:'open_time' , 1:'open' , 2:'high' , 3:'low' , 4:'close' , 5:'volume'} , inplace=True)
            
            print(df)
            
            start_time_stamp = int(df.iloc[-1]['open_time']) #獲取下一次的請求時間
            
            file_name = str(start_time_stamp) + '.csv'
            save_file_path = os.path.join(file_dir , file_name)
            
            print(f'文件保存路徑為：{save_file_path}')
            
            df.set_index('open_time' , inplace=True , drop=True)
            df.to_csv(save_file_path)
            
            if start_time_stamp > end_time_stamp :
                print('完成數據的請求')
                break
            
            if len(df) < limit_count :
                print('數據不夠了')
                break
            
            time.sleep(3)
        except Exception as error:
            print(error)
            time.sleep(10)
            
def sample_data(exchange_name , symbol):
    path = os.path.join(os.getcwd() , exchange_name , symbol.replace('/' , ''))
    
    file_paths = []
    for root , dirs , files in os.walk(path):
        if files :
            for file in files :
                if file.endswith('.csv'):
                   file_paths.append(os.path.join(path , file))
    
    file_paths = sorted(file_paths)
    all_df = pd.DataFrame()
    for file in file_paths:
        df = pd.read_csv(file)
        all_df = pd.concat([all_df , df] , ignore_index = True)
    
    all_df = all_df.sort_values(by = 'open_time' , ascending = 1)
    
    df = all_df
    
    df['open_time'] = df['open_time'].apply(lambda x : (x // 60) *60 )
    df['Datetime'] = pd.to_datetime(df['open_time'] , unit= 'ms') + pd.Timedelta(hours = 8)
    df.drop_duplicates(subset=['open_time'] , inplace = True)
    # 2024-12-31 12:00:00
    df['Datetime'] = df['Datetime'].apply(lambda x : str(x)[0:19])
    df['high'] = df.apply(lambda x : max(x['open'] , x['high'] , x['low'] , x['close']) , axis = 1)
    df['low'] = df.apply(lambda x : min(x['open'] , x['high'] , x['low'] , x['close']) , axis = 1)
    df.set_index('Datetime' , inplace = True)
    
    df.rename(columns={'open' : 'Open' , 'high' : 'High' ,'low' : 'Low' , 
                       'close' : 'Close' ,'volume':'Volume'} , inplace = True)
    
    df.to_csv(path + '_backtest.csv')

if __name__=='__main__':
    crawl_exchange_data('binance', 'SOL/USDT' , '2018-1-1' , '2025-2-9')
    sample_data('binance' , 'SOL/USDT')
    
        
        
        


