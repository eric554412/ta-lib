from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

'''
這是自動發送虛擬貨幣每四小時價格漲跌的line notification
'''

user_id = 'U569a3f2b4048bdfdaf8070bbe5f4ffa5'
token = 'lsQDjge0D07LCMBKJsDJxgOx+wZrAnp3D/OAjGqVnl/pZ5VRb735mMHVHZ+ygw+MxAlcAL5I8Un4RIGU22Myt5dkXtoX+UTxZlTx9S+0bYPoTlxqV0900JZLAxOY9i6FAWJybuzGE8LN4jC3q6GfhgdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(token)

url = 'https://notify-api.line.me/api/notify'
token = 'DYnvDmgyCoRPUH5YT1QUVL2LD0veoFPl75QKVCjE13F'
headers = {
    'Authorization': 'Bearer ' + token
}

def get_lastest_price() :
    binance_url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbols' : '["BTCUSDT","ETHUSDT","SOLUSDT","DOGEUSDT"]'}
    respone = requests.get(binance_url ,params = params)    
    if respone.status_code == 200 :
        data = respone.json()
        df = pd.DataFrame(data)
        df['timestamp'] = datetime.now()
        df['timestamp'] = df['timestamp'].apply(lambda x : str(x)[0:16])
        return df
    else : 
        print(f'fetching data error :{respone.status_code}')
        
def get_24hr_price_change() :
    binance_url = 'https://api.binance.com/api/v3/ticker/24hr'
    params = {'symbols' : '["BTCUSDT","ETHUSDT","SOLUSDT","DOGEUSDT"]'}
    respone = requests.get(binance_url, params = params)
    if respone.status_code == 200 :
        data = respone.json()
        df = pd.DataFrame(data)
        df['timestamp'] = datetime.now()
        df['timestamp'] = df['timestamp'].apply(lambda x : str(x)[0:16])
        df = df.rename(columns={'priceChangePercent':'24hr_priceChangePercent'})
        df = df[['symbol', "24hr_priceChangePercent"]]
        return df
    else : 
        print(f'fetching data error :{respone.status_code}')
    

def calculate_price_change(latest_df, historical_df) :
    merged_df = pd.merge(latest_df, historical_df, on = 'symbol', suffixes = ('_new', '_old'))
    merged_df['price_new'] = merged_df['price_new'].astype(float)
    merged_df['price_old'] = merged_df['price_old'].astype(float)
    merged_df['price_change'] = ((merged_df['price_new'] - merged_df['price_old']) / merged_df['price_old']) * 100
    return merged_df[['symbol', 'price_new', 'price_old', 'price_change', 'timestamp_new']]


def send_line_mess(result_df, daily_change_df = None) :
    messages = []
    for index, row in result_df.iterrows():
        message = f"""
幣種：{row['symbol']}
最新價格：{row['price_new'] }
四小時前價格：{row['price_old']}
漲跌幅：{row['price_change'] : .4f}%
時間：{row['timestamp_new']}
        """
        if daily_change_df is not None :
            daily_change = daily_change_df.loc[daily_change_df['symbol'] == row['symbol'], '24hr_priceChangePercent'].values[0]
            message += f"24小時漲幅{daily_change}%\n"
        
        messages.append(message)
    
    full_mess = '\n'.join(messages)
    data = {'message':full_mess}
    
    try:
        # line_bot_api.broadcast(TextSendMessage(full_mess))
        data = requests.post(url, headers = headers, data = data)
        print('推播成功')
    except Exception as e :
        print(f'推播失敗：{e}')
        
        
        
if __name__ == '__main__' :
    historical_data = None
    push_count = 0
    #初始化last_push_time為凌晨12.
    now = datetime.now()
    last_push_time = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    
    if now >= last_push_time :
        last_push_time += timedelta(days = 1)
    
    time.sleep((last_push_time - now).total_seconds())
    
    while True :
        current_time = datetime.now()
        
        if current_time > last_push_time :
            last_push_time += timedelta(hours = 4)
            print(f"[{current_time}] 開始執行一次邏輯...")
            
            lastest_data = get_lastest_price()
            
            if historical_data is None :
                historical_data = lastest_data
                print('初始化成功')
            
            else :
                try :
                    result = calculate_price_change(lastest_data, historical_data)
                    print('計算價格變動成功')
                    if push_count == 5 :
                        daily_price_change = get_24hr_price_change()
                        send_line_mess(result, daily_price_change)
                        # print(result)
                        # print(daily_price_change)
                        print("第六次推播，發送24小時漲跌幅。")
                        push_count = 0
                    else :
                        send_line_mess(result)
                        # print(result)
                        push_count += 1
                except Exception as e :
                    print(f"計算或推播失敗：{e}")
                
                historical_data = lastest_data
        time.sleep(1)
            
    
        
    




      




