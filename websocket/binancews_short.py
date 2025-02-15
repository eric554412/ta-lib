import json
from ws_inherbited import Tick,BinanceWebsocket
#websocket api
#創建websocket client 對象後，需要使用start的方法去啟動worker和ping線程
# 1.worker線程會自動重連
# 2.使用stop方法去停止斷開或銷毀websocket client
# 3.四個回調方法（on_open,on_clsoe,on_message,on_error）
# start()方法方法調用後,ping線程每隔線程每隔60秒會自動調用一次



class BinanceWebsocket(BinanceWebsocket,Tick):
    def __init__(self):
        super(BinanceWebsocket,self).__init__(host="wss://fstream.binance.com/ws",ping_interval=20)
        
    def on_open(self):
        print("on open")
        data={
"method": "SUBSCRIBE",
"params":
[
"dogeusdt@depth20",
],
"id": 1
}       
        self.send_mes(data)
    
    def on_message(self,data):
        data=json.loads(data)
        print(data)
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
        
if __name__=='__main__':
    bin=BinanceWebsocket()
    bin.start()