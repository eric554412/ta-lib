import requests
from loguru import logger
import json
import sys
import traceback
import socket
from datetime import datetime
from time import sleep
from threading import Lock, Thread
import websocket
import pandas as pd
import pandas as pd
import talib
import numpy as np
from tqdm import tqdm
import threading
import time
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from queue import Empty
from dc_key import DISCORD_BOT_TOKEN, DISCORD_DEVELOPER_CHANNEL_ID


class DCNotify:
    def __init__(self, token: str, client_channel_id: str = None, developer_channel_id: str = None):
        self.token = token
        self.client_channel_id = client_channel_id
        self.developer_channel_id = developer_channel_id
    
    def send_developer_message(self, msg: str, path: str = None):
        if path:
            self.semd_mes(path)
            
        if self.developer_channel_id :
            base_url = 'https://discord.com/api/v10'
            url = f'{base_url}/channels/{self.developer_channel_id}/messages'
            header = {
                "Authorization": f'Bot {self.token}'
                }
            
            data = {
                "content": msg
            }
            
            response = requests.post(url, headers=header, json=data)
            if response.status_code in (200, 204):
                logger.info(f'discord respone: {response.status_code}')
                logger.info('Message sent to developer')
            else:
                logger.error(f'Failed to send message to developer: {response.text}')
    
    def semd_mes(self, path: str):
        base_url = 'https://discord.com/api/v10'
        url = f'{base_url}/channels/{self.developer_channel_id}/messages'
        header = {
                "Authorization": f'Bot {self.token}'
                }
        
        with open(path, 'rb') as f:
            data = {
                "file": f
            }
            response = requests.post(url, headers=header, files=data)
            if response.status_code in (200, 204):
                logger.info(f'discord respone: {response.status_code}')
                logger.info('Message sent to developer')
            else:
                logger.error(f'Failed to send message to developer: {response.text}')


class Tick(object):
    def __init__(self):
        '''
        用來儲存每次抓取的資料
        '''
        self.df = pd.DataFrame(columns = ['symbol', 'timestamp', 'High', 'Low', 'Close', 'Volume', 'x'])
        self.max_len = 1000
    
    def add_data(self, data):
        '''
        實時更新資料並更新dataframe
        '''
        new_row = pd.DataFrame([data])
        self.df = pd.concat([self.df, new_row], ignore_index = True)
        
        if len(self.df) > self.max_len:
            self.df = self.df.iloc[-self.max_len:].reset_index(drop = True)
            
    def get_df(self):
        return self.df


class BinanceWebsocket(object):
    '''
    BinanceWebsocket類
    '''

    def __init__(self, host, symbol, pinginterval=20):
        Thread.__init__(self)
        '''
        初始化
        '''
        self.host = host
        self.ping_interval = pinginterval

        self._ws = None
        self._ws_lock = Lock()

        self._worker_thread = None
        self._ping_thread = None

        self._last_sent_text = ""
        self._last_received_text = ""

        self.tick = Tick()
        self.symbol = symbol

    def start(self):
        '''
        啟動
        '''
        self.active = True
        self._worker_thread = Thread(target=self._run)
        self._worker_thread.start()

        self._ping_thread = Thread(target=self._run_ping)
        self._ping_thread.start()

    def stop(self):
        '''
        停止
        '''
        self.active = False
        self._disconnect()

    def join(self):
        '''
        等待
        '''
        self._ping_thread.join()
        self._worker_thread.join()

    def send_mes(self, msg: dict):
        '''
        發送訊息
        '''
        text = json.dumps(msg)
        self._record_last_sent_text(text)
        self._sent_text(text)

    def _sent_text(self, text: str):
        '''
        發送文字
        '''
        with self._ws_lock:
            ws = self._ws
            if ws:
                ws.send(text, opcode=websocket.ABNF.OPCODE_TEXT)

    def _ensure_connection(self):
        '''
        確保連接
        '''
        triggered = False
        with self._ws_lock:
            if self._ws is None:
                print(f'Connecting to {self.host}...')
                self._ws = websocket.create_connection(
                    self.host, sslopt={'cert_reqs': 0})
                triggered = True
                print('WebSocket connection established.')

        if triggered:
            self.on_open()

    def _disconnect(self):
        '''
        斷開
        '''
        triggered = False
        with self._ws_lock:
            if self._ws:
                ws = self._ws
                self._ws = None
                triggered = True
        if triggered:
            ws.close()
            self.on_close()

    def _run(self):
        '''
        接受訊息
        '''
        try:
            while self.active:
                try:
                    self._ensure_connection()
                    ws = self._ws
                    if ws:
                        text = ws.recv()  # 接收訊息
                        if not text:
                            self._disconnect()
                            continue
                        self.on_message(text)  # 處理訊息
                        self._record_last_received_text(text)
                except (websocket.WebSocketConnectionClosedException, socket.error):
                    self._disconnect()
                except Exception as e:
                    et, ev, tb = sys.exc_info()
                    self.on_error(et, ev, tb)
                    self._disconnect()
        except Exception as e:
            et, ev, tb = sys.exc_info()
            self.on_error()

    def _run_ping(self):
        '''
        運行ping
        '''
        while self.active:
            try:
                self._ping()
            except Exception as e:
                et, ev, tb = sys.exc_info()
                self.on_error(et, ev, tb)
            for i in range(self.ping_interval):
                if not self.active:
                    break
            sleep(1)

    def _ping(self):
        '''
        ping
        '''
        ws = self._ws
        if ws:
            ws.send('ping', websocket.ABNF.OPCODE_PING)

    def on_open(self):
        '''
        連接到send_mes方法
        '''
        print('WebSocket connection opened.')
        payload = {
            "method": "SUBSCRIBE",
            "params": [f"{self.symbol}@kline_1m"],
            "id": 1
        }
        self.send_mes(payload)

    def on_close(self):
        '''
        關閉
        '''
        print('WebSocket connection closed.')

    def on_message(self, data):
        '''
        接收訊息後處理
        '''
        data = json.loads(data)
        if 'k' in data:
            kline = data['k']
            if kline['x'] == True:
                new_data = {
                    'symbol': self.symbol,
                    'timestamp': kline['T'],
                    'High': float(kline['h']),
                    'Low': float(kline['l']),
                    'Close': float(kline['c']),
                    'Volume': kline['v'],
                    'x': kline['x']
                }
                self.tick.add_data(new_data)
        return self.tick.df


    def on_error(self, exception_type, exception_value, tb):
        error_details = self.exception_detail(
            exception_type, exception_value, tb)
        return sys.stderr.write(error_details)

    def exception_detail(self, exception_type: type, exception_value: Exception, tb):
        text = "[{}]: Unhandled WebSocket Error:{}\n".format(
            datetime.now().isoformat(), exception_type
        )
        text += "LastSentText:\n{}\n".format(self._last_sent_text)
        text += "LastReceivedText:\n{}\n".format(self._last_received_text)
        text += "Exception trace: \n"
        text += "".join(
            traceback.format_exception(exception_type, exception_value, tb)
        )
        return text

    def _record_last_sent_text(self, text: str):
        self._last_sent_text = text[:1000]

    def _record_last_received_text(self, text: str):
        self._last_received_text = text[0:1000]


class ImpulseMACDStrategy:
    '''
    im_macd策略(impulse macd):
    1.先分別計算high,low的smma   
    2.計算hlc3_zlema:即先計算hlc3的ema在就此ema在平滑一次。
    3.計算md線為快線,如果hlc3_zlema大於high_smma則 md = hlc_zlema - high_smma,若hlc3_zlema小於low_smma則 md = hlc_zlema - high_smma
    若介於兩者間則等於0,如此可過濾橫盤信號。 
    4.sb線為慢線,為md線的sma

    做多規則：
    1.金叉時以收盤價做多 
    2.止損為移動止損 max(self.stop_loss, current_price - 1 * atr) 
    3.停利為固定買入價格的4倍atr

    做空規則：
    1.死叉時以收盤價做多 
    2.止損為移動止損 min(self.stop_loss, current_price + 1 * atr) 
    3.停利為固定買入價格的4倍atr
    '''
    def __init__(self, symbol, length_ma = 30, lenth_signal = 10):
        self.symbol = symbol
        self.length_ma = length_ma
        self.lenth_signal = lenth_signal

        # 初始化
        self.queue = Queue()
        self.stop_flag = False
        self.ws = BinanceWebsocket(
            'wss://stream.binance.com:9443/ws', self.symbol)
        self.dc_notify = DCNotify(
            token=DISCORD_BOT_TOKEN, developer_channel_id=DISCORD_DEVELOPER_CHANNEL_ID)

        # 三條執行緒
        self.thread_ws = threading.Thread(target=self.ws.start)
        self.thread_fetch = threading.Thread(target=self.fetch_data)
        self.thread_signal = threading.Thread(target=self.process_signal)
        self.lock = threading.Lock()

        # 追蹤持倉
        self.position = None  # 1為多單, -1為空單, none為沒有持倉
        self.atr_mulitplier = 1
        self.stop_loss = None

    def calc_smma(self, df, column, lenth):
        '''
        計算high,low的smma
        '''
        df[f'{column}_sma'] = talib.SMA(df[column], timeperiod=lenth)

        ssma = f'{column}_ssma'
        df[ssma] = np.nan

        df.loc[lenth-1, ssma] = df.loc[lenth-1, f'{column}_sma']

        for i in tqdm(range(lenth, len(df))):
            df.loc[i, ssma] = (df.loc[i-1, ssma] * (lenth - 1) +
                               df.loc[i, column]) / lenth

        return df

    def calc_zlema_df(self, df, column, lenth):
        '''
        計算hlc3_zlema:即先計算hlc3的ema在就此ema在平滑一次。
        '''

        df[f'{column}_ema'] = talib.EMA(df[column], timeperiod=lenth)
        df['sema'] = talib.EMA(df[f'{column}_ema'], timeperiod=lenth)
        zlema = f'{column}_zlema'
        df[zlema] = df[f'{column}_ema'] + (df[f'{column}_ema'] - df['sema'])
        return df

    def calc_impulse_macd(self, df, lenth):
        '''
        計算md線為快線,如果hlc3_zlema大於high_smma則 md = hlc_zlema - high_smma,若hlc3_zlema小於low_smma則 md = hlc_zlema - high_smma
        若介於兩者間則等於0,過濾橫盤信號,sb線為慢線,為md線的sma。 
        '''
        df['md'] = np.where(df['hlc3_zlema'] > df['High_ssma'], df['hlc3_zlema'] - df['High_ssma'],
                            np.where(df['hlc3_zlema'] < df['Low_ssma'], df['hlc3_zlema'] - df['Low_ssma'], 0))

        df['sb'] = talib.SMA(df['md'], timeperiod=lenth)

        df['sh'] = df['md'] - df['sb']
        return df

    def gen_signal(self, df):
        '''
        金叉時以收盤價做多,死叉時以收盤價做多    
        '''
        with self.lock:
            if 'stop_loss' not in df.columns:
                df['stop_loss'] = np.nan

            if 'signal' not in df.columns:
                df['signal'] = 0
            last_index = len(df) - 1

            if self.position is not None:  # 若有持倉則不發送信號
                return df

            atr = talib.ATR(df['High'], df['Low'], df['Close'],
                            timeperiod=14).iloc[-1]

            if df.loc[last_index-1, 'md'] > df.loc[last_index-1, 'sb'] and df.loc[last_index, 'md'] < df.loc[last_index, 'sb']:
                if df.loc[last_index, 'signal'] != -1:  # 避免重複發送
                    df.loc[last_index, 'signal'] = -1
                    self.position = -1
                    self.stop_loss = df.loc[last_index, 'Close'] + atr * self.atr_mulitplier
                    df.loc[last_index, 'stop_loss'] = self.stop_loss
                    self.notify_trade_signal(f'eth刺客🥷」 \n幣種 - {self.symbol}\n進場價格 - {df.loc[last_index, 'Close']}\n方向 - 空單📉\n策略為移動止盈，請隨時關注此策略📌\n僅供參考，不構成任何投資建議，請自行注意風險管理⚠️\n此訊息為機器人自動發出。\n')

            elif df.loc[last_index-1, 'md'] < df.loc[last_index-1, 'sb'] and df.loc[last_index, 'md'] > df.loc[last_index, 'sb']:
                if df.loc[last_index, 'signal'] != 1:  # 避免重複發送
                    df.loc[last_index, 'signal'] = 1
                    self.position = 1
                    self.stop_loss = df.loc[last_index, 'Close'] - atr * self.atr_mulitplier
                    df.loc[last_index, 'stop_loss'] = self.stop_loss
                    self.notify_trade_signal(f'eth刺客🥷」\n幣種 - {self.symbol}\n進場價格 - {df.loc[last_index, 'Close']}\n方向 - 多單📈\n 策略為移動止盈，請隨時關注此策略📌\n僅供參考，不構成任何投資建議，請自行注意風險管理⚠️\n此訊息為機器人自動發出。\n')
            return df

    def check_trailing_stop(self, df):
        '''
        移動止損邏輯
        '''
        with self.lock:
            last_index = len(df) - 1
            atr = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod = 14).iloc[-1]

            if self.position is not None :
                if np.isnan(df.loc[last_index, 'stop_loss']):
                    df.loc[last_index, 'stop_loss'] = self.stop_loss
        
                if self.position == 1:
                    new_stop_loss = df.loc[last_index,
                                           'Close'] - self.atr_mulitplier * atr
                    if new_stop_loss > self.stop_loss:
                        df.loc[last_index, 'stop_loss'] = new_stop_loss # 更新止損價
                        self.stop_loss = new_stop_loss
                elif self.position == -1:
                    new_stop_loss = df.loc[last_index,
                                           'Close'] + self.atr_mulitplier * atr
                    if new_stop_loss < self.stop_loss:
                        df.loc[last_index, 'stop_loss'] = new_stop_loss  # 更新止損價
                        self.stop_loss = new_stop_loss
        return df

    def check_exit(self, df):
        '''
        檢查是否出場
        '''
        with self.lock:
            last_index = len(df) - 1

            if self.position == 1 and df.loc[last_index, 'Close'] < df.loc[last_index, 'stop_loss']:
                self.notify_trade_signal(
                    f'「eth刺客🥷」 \n幣種 - {self.symbol}\n進場價格 - {df.loc[last_index, 'Close']}\n方向 - 平倉✅ \n策略為移動止盈，請隨時關注此策略📌\n僅供參考，不構成任何投資建議，請自行注意風險管理⚠️\n此訊息為機器人自動發出。\n' )
                self.position = None
                self.stop_loss = None

            elif self.position == -1 and df.loc[last_index, 'Close'] > df.loc[last_index, 'stop_loss']:
                self.notify_trade_signal(
                    f'「eth刺客🥷」\n 幣種 - {self.symbol}\n進場價格 - {df.loc[last_index, 'Close']}\n方向 - 平倉✅ \n策略為移動止盈，請隨時關注此策略📌\n僅供參考，不構成任何投資建議，請自行注意風險管理⚠️\n此訊息為機器人自動發出。\n')
                self.position = None
                self.stop_loss = None
            return df

    def fetch_data(self):
        '''
        將ws資料儲存在queue
        '''
        prev_df = None
        while not self.stop_flag:
            if len(self.ws.tick.df) > self.length_ma:
                current_df = self.ws.tick.df.copy()
                if prev_df is None or not current_df.equals(prev_df):
                    with self.lock:
                        self.queue.put(current_df)
                    prev_df = current_df
                time.sleep(1)

    def cal_hlc3(self, df):
        df['hlc3'] = (df['High'] + df['Low'] + df['Close']) / 3
        return df

    def process_signal(self):
        '''
        從 queue 拿出資料處理訊號
        '''
        with ThreadPoolExecutor(max_workers=6) as executor:
            while not self.stop_flag:
                try:
                    df = self.queue.get(timeout=1)

                    with self.lock:
                        df = df.copy()

                    # 第一階段：計算 smma 和 hlc3 (可並行)
                    future_smma_high = executor.submit(
                        self.calc_smma, df, 'High', self.length_ma)
                    future_smma_low = executor.submit(
                        self.calc_smma, df, 'Low', self.length_ma)
                    future_hlc3 = executor.submit(self.cal_hlc3, df)

                    # 等待這三個計算完成
                    df = future_smma_high.result()
                    df = future_smma_low.result()
                    df = future_hlc3.result()

                    # 第二階段：計算 hlc3_zlema (依賴 hlc3)
                    future_zlema = executor.submit(
                        self.calc_zlema_df, df, 'hlc3', self.length_ma)
                    df = future_zlema.result()

                    # 第三階段：計算 impulse macd (依賴 hlc3_zlema)
                    future_macd = executor.submit(
                        self.calc_impulse_macd, df, self.lenth_signal)
                    df = future_macd.result()

                    # 第四階段：產生交易訊號 (依賴 impulse macd)
                    future_signal = executor.submit(self.gen_signal, df)
                    df = future_signal.result()

                    # 若有持倉檢查stop_loss
                    df = self.check_trailing_stop(df)
                    df = self.check_exit(df)
                    print(df)

                except Empty:
                    pass
                except Exception as e:
                    print(f'error: {e}')

    def start(self):
        '''
        啟動策略
        '''
        self.thread_ws.start()
        self.thread_fetch.start()
        self.thread_signal.start()

    def stop(self):
        '''
        停止策略並關閉所以執行緒
        '''
        print('停止websocket與策略計算')
        self.stop_flag = True
        self.ws.stop()
        self.thread_ws.join()
        self.thread_fetch.join()
        self.thread_signal.join()
        print('策略停止')

    def notify_trade_signal(self, message):
        dc_notify = threading.Thread(
            target=self.dc_notify.send_developer_message, args=(message, ))
        dc_notify.start()


if __name__ == '__main__':
    try:
        strategy = ImpulseMACDStrategy(symbol='ethusdt')
        strategy.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        strategy.stop()