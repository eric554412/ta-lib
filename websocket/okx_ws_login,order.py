from ws_inherbited import BaseWebsocket,Tick
import json
import time
import hashlib
import hmac
import base64

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


class OKXWebsocket(BaseWebsocket):
    def __init__(self):
        super(OKXWebsocket,self).__init__(host='wss://wsaws.okx.com:8443/ws/v5/public',ping_interval=20)
        
    
    
    def subscribe_topic(self):
        self.send_mes({
    "op": "subscribe",
    "args": [{
        "channel": "positions",
        "instType": "FUTURES",
        "instFamily": "BTC-USD"
    }]
})      
      
        
    
    def on_open(self):
        print("on open")
        data={
    "op": "subscribe",
    "args": [{
        "channel": "books5",
        "instId": "DOGE-USDT"
    }]
}
        self.send_mes(data)
#         api_key='e6a04eb7-cfe5-4f05-bf23-ca3dbb98eb99'
#         api_secret='B9F6C0806BF455D0A4837517A6A547BA'
#         passphrase='Eric20020601@'
#         timestamp=str(time.time())
#         msg=timestamp+'GET'+ '/users/self/verify'
#         sign=hmac.new(api_secret.encode('utf-8'),msg.encode('utf-8'),digestmod=hashlib.sha256).digest()
#         sign=base64.b64encode(sign).decode('utf-8')
#         data={
#  "op": "login",
#  "args":
#   [
#      {
#        "apiKey": api_key,
#        "passphrase": passphrase,
#        "timestamp": timestamp,
#        "sign":sign
#       }
#    ]
# }
#         self.send_mes(data)
        
    def on_close(self):
        """
        on close websocket
        """
    def on_message(self,msg):
        msg=json.loads(msg)
        # print(msg)
        # if "event" in msg:
        #     if msg['event']=='login':
        #         print('登錄成功')
        #     self.subscribe_topic()
                
        if 'arg' in msg and msg['arg']['channel'] == 'books5' and 'data' in msg:
            data=msg['data'][0]
            asks = data['asks']
            bids = data['bids']
            for n,buf in enumerate(bids[0:5]):
                price,volume=buf[0],buf[1]
                self.tick.__setattr__("bid_price%s"%(n+1),price)
                self.tick.__setattr__("bid_volume%s"%(n+1),volume)
            for n,buf in enumerate(asks[0:5]):
                price,volume=buf[0],buf[1]
                self.tick.__setattr__("ask_price%s"%(n+1),price)
                self.tick.__setattr__("ask_volume%s"%(n+1),volume)
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
                
        
        
if __name__=='__main__':
    OKX=OKXWebsocket()
    OKX.start()
   
    