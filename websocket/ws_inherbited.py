import json
import sys
import traceback
import socket
from datetime import datetime
from time import sleep
from threading import Thread,Lock
import websocket

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
        
        

class BaseWebsocket(object):
    def __init__(self,host,ping_interval):
        self.host=host
        self.ping_interval=ping_interval
        
        self._ws=None
        self._ws_lock=Lock()
        
        self._worker_thread=None
        self._ping_thread=None
        
        self._last_sent_text=None
        self._last_recv_text=None
        
        self.tick=Tick()
        
    def start(self):
        self.active=True
        self._worker_thread=Thread(target=self._run)
        self._worker_thread.start()
        
        self._ping_thread=Thread(target=self._run_ping)
        self._ping_thread.start()
    
    def stop(self):
        self.active=False
        self.on_close()
    
    def join(self):
        self._worker_thread.join()
        self._ping_thread.join()
    
    def send_mes(self,mes:dict):
        text=json.dumps(mes)
        self._record_last_sent_text(text)
        self.sent_text(text)
    
    def sent_text(self,text:str):
        ws=self._ws
        if ws:
            ws.send(text,opcode=websocket.ABNF.OPCODE_TEXT)
    
    def ensure_connection(self):
        triggered=False
        with self._ws_lock:
            if self._ws is None:
                print("Create Connection....")
                self._ws=websocket.create_connection(self.host, sslopt={"cert_reqs": 0})
                triggered=True
                print("Websocket connection established")
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
            while self.active:
                try:
                    self.ensure_connection()
                    ws=self._ws
                    if ws:
                        text=ws.recv()
                        if not ws:
                            self._disconnect()
                            continue
                    
                    self._record_last_sent_text(text)
                    self.on_message(text)
                except(websocket.WebSocketAddressException,socket.error):
                    self._disconnect()
                except:
                    et,ev,tb=sys.exc_info()
                    self.on_error(et,ev,tb)
                    self._disconnect()
        except:
            et,ev,tb=sys.exc_info()
            self.on_error(et,ev,tb)
    
    def _run_ping(self):
        while self.active:
            try:
                self._ping()
            except:
                et,ev,tb=sys.exc_info()
                self.on_error(et,ev,tb)
            for i in range(self.ping_interval):
                if not self.active:
                    break
            sleep(1)
    
    def _ping(self):
        ws=self._ws
        if ws:
            ws.send("ping",websocket.ABNF.OPCODE_PING)
    
    
    def on_close(self):
        """
        沒有用的函數
        """
    
    def on_error(self,exception_type,exception_value,tb):
        error_details=self.exception_details(exception_type,exception_value,tb)
        return sys.stderr.write(error_details)
    
    def exception_details(self,exception_type:type,exception_value:Exception,tb):
        text  = "[{}]:Unhandled WebSocket Error:{}\n".format(datetime.now().isoformat(),exception_type)
        text += "LastSentText:\n{}\n".format(self._last_sent_text)
        text += "LastReceivedText:\n{}\n".format(self._last_recv_text)
        text += "".join(traceback.format_exception(exception_type,exception_value,tb))
        return text
    
    def _record_last_sent_text(self,text:str):
        self._last_sent_text=text[:1000]
    
    def _record_last_recv_text(self,text:str):
        self._last_recv_text=text[:1000]


        
            
        


                
            
            
                                
        
        
        
                    
    
    
              
        