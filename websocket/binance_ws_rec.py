import json
import sys
import traceback
import socket
from datetime import datetime
from time import sleep
from threading import Lock,Thread
import websocket

#websocket api
#創建websocket client 對象後，需要使用start的方法去啟動worker和ping線程
# 1.worker線程會自動重連
# 2.使用stop方法去停止斷開或銷毀websocket client
# 3.四個回調方法（on_open,on_clsoe,on_message,on_error）
# start()方法方法調用後,ping線程每隔線程每隔60秒會自動調用一次

class Tick(object):
    def __init__(self) :
        self.bid_price1=0
        self.bid_price2=0
        self.bid_price3=0
        self.bid_price4=0
        self.bid_price5=0
        
        self.bid_volume1=0
        self.bid_volume2=0
        self.bid_volume3=0
        self.bid_volume4=0
        self.bid_volume5=0
        
        self.ask_price1=0
        self.ask_price2=0
        self.ask_price3=0
        self.ask_price4=0
        self.ask_price5=0
        
        self.ask_volume1=0
        self.ask_volume2=0
        self.ask_volume3=0
        self.ask_volume4=0
        self.ask_volume5=0


class BinanceWebsocket(object):
    def __init__(self,host=None,ping_interval=20):
        self.host=host
        self.ping_interval=ping_interval
        
        self._ws_lock=Lock()
        self._ws=None
        
        self._worker_thread=None
        self._ping_thread=None
        
        self._last_sent_text=None
        self._last_received_text=None
        
        self.tick=Tick()
    
    def start(self):
        self._active=True
        self._worker_thread=Thread(target=self._run)
        self._worker_thread.start()
        
        self._ping_thread = Thread(target=self._run_ping)
        self._ping_thread.start()
    
    def stop(self):
        self._active=False
        self._disconnect()
    
    def join(self):
        self._ping_thread.join()
        self._worker_thread.join()
    
    def  send_msg(self,msg:dict):
        text=json.dumps(msg)
        self._record_last_sent_text(text)
        self._sent_text(text)
    
    def _sent_text(self,text:str):
        ws=self._ws
        if ws:
            ws.send(text,opcode=websocket.ABNF.OPCODE_TEXT)
    
    def _ensure_connection(self):
        triggered=False
        with self._ws_lock:
            if self._ws is None:
                print(f"Connecting to {self.host}...")
                self._ws=websocket.create_connection(self.host, sslopt={"cert_reqs": 0})
                triggered=True
                print("WebSocket connection established.")
        
        if triggered:
            self.on_open()
    
    def _disconnect(self):
        triggered=False
        with self._ws_lock:
            if self._ws:
                ws:websocket.WebSocket=self._ws
                self._ws=None
                
                triggered=True
        if triggered:
            ws.close()
            self.on_close()
    
    def _run(self):
        try:
            while self._active:
                try:
                    self._ensure_connection()
                    ws=self._ws
                    if ws:
                        text=ws.recv()
                        if not text:
                            self._disconnect()
                            continue
                        
                        self._record_last_received_text(text)
                        self.on_message(text)
                except(websocket.WebSocketConnectionClosedException,socket.error):
                    
                    self._disconnect()
                except:
                    et,ev,tb=sys.exc_info()
                    self.on_error(et,ev,tb)
                    self._disconnect()
        except:
            et,ev,tb=sys.exc_info()
            self.on_error()
            
    def _run_ping(self):
        while self._active:
            try:
                self._ping()
            except:
                et,ev,tb=sys.exc_info()
                self.on_error(et,ev,tb)
                sleep(1)
            for i in range(self.ping_interval):
               if not self._active:
                break
            sleep(1)
    
    def _ping(self):
        ws=self._ws
        if ws:
            ws.send("ping",websocket.ABNF.OPCODE_PING)
    
    def on_open(self):
        print("on open")
        data={
"method": "SUBSCRIBE",
"params":
[
"dogeusdt@depth20"
],
"id": 1
}       
        self.send_msg(data)
    
    def on_close(self):
        """
        on close websocket
        """
    def on_message(self,data):
        data=json.loads(data)
        if 'e' in data and data['e']=='depthUpdate':
            bids=data['b']
            asks=data['a']
            for n in range(5):
                price,volume=bids[n]
                self.tick.__setattr__('bid_price%s'%(n+1),price)
                self.tick.__setattr__('bid_volume%s'%(n+1),volume)
            for n in range(5):
                price,volume=asks[n]
                self.tick.__setattr__('ask_price%s'%(n+1),price)
                self.tick.__setattr__('ask_volume%s'%(n+1),volume)
                print(f'bid_price5={self.tick.bid_price5}',f'bid_volume5={self.tick.bid_volume5}')
                print(f'bid_price4={self.tick.bid_price4}',f'bid_volume4={self.tick.bid_volume4}')     
                print(f'bid_price3={self.tick.bid_price3}',f'bid_volume3={self.tick.bid_volume3}')     
                print(f'bid_price2={self.tick.bid_price2}',f'bid_volume2={self.tick.bid_volume2}')     
                print(f'bid_price1={self.tick.bid_price1}',f'bid_volume1={self.tick.bid_volume1}')         
                print('*'*30)
                print(f'ask_price5={self.tick.ask_price5}',f'ask_volume5={self.tick.ask_volume5}')
                print(f'ask_price4={self.tick.ask_price4}',f'ask_volume4={self.tick.ask_volume5}')
                print(f'ask_price3={self.tick.ask_price3}',f'ask_volume3={self.tick.ask_volume5}')
                print(f'ask_price2={self.tick.ask_price2}',f'ask_volume2={self.tick.ask_volume5}')
                print(f'ask_price1={self.tick.ask_price1}',f'ask_volume1={self.tick.ask_volume5}')
                print('\n'*5)
    
    def on_error(self, exception_type, exception_value, tb):
        error_details = self.exception_detail(exception_type, exception_value, tb)
        return sys.stderr.write(error_details)
        
    
    def exception_detail(self,exception_type:type,exception_value:Exception,tb):
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
    
    def _record_last_sent_text(self,text:str):
        self._last_sent_text=text[:1000]
        
    def _record_last_received_text(self,text:str):
        self._last_received_text=text[0:1000]
        
if __name__=='__main__':
    bin=BinanceWebsocket(host="wss://fstream.binance.com/ws",ping_interval=20)
    bin.start()
            
    
                
        
        
        
            
                    
        
    
    
                    
                        
               
        
        
        
        
        
        
        
        
        
        
        
        
