#這是幣安永續合約的websocket
import websocket
import json
import zlib

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

tick=Tick()
        
    
def on_open(ws):
    data={
"method": "SUBSCRIBE",
"params":
[
"dogeusdt@depth20"
],
"id": 1
}
    ws.send(json.dumps(data))


def on_error(ws,error):
    print(f'error={error}')

def on_close(ws,close_status_code,close_msg):
    print(f'on close,close_status_code={close_status_code},close_msg={close_msg}')


def on_message(ws,msg):
    print('on message')
    if 'ping' in msg:
        ws.send(json.dumps({"pong":msg['ping']}))
    msg=json.loads(msg)
    bids=msg['b']
    asks=msg['a']
    if 'e' in msg and msg['e']=='depthUpdate':
        for n in range(5):  #迴圈執行五次
            price,volume = bids[n] #從bids陣列中提取price和volume
            tick.__setattr__("bid_price%s"%(n+1),price)
            tick.__setattr__("bid_volume%s"%(n+1),volume)
        for n in range(5):
            price,volume=asks[n]
            tick.__setattr__("ask_price%s"%(n+1),price)
            tick.__setattr__("ask_volume%s"%(n+1),volume)
            print(f'bid_price5={tick.bid_price5}',f'bid_volume5={tick.bid_volume5}')
            print(f'bid_price4={tick.bid_price4}',f'bid_volume4={tick.bid_volume4}')     
            print(f'bid_price3={tick.bid_price3}',f'bid_volume3={tick.bid_volume3}')     
            print(f'bid_price2={tick.bid_price2}',f'bid_volume2={tick.bid_volume2}')     
            print(f'bid_price1={tick.bid_price1}',f'bid_volume1={tick.bid_volume1}')         
            print('*'*30)
            print(f'ask_price5={tick.ask_price5}',f'ask_volume5={tick.ask_volume5}')
            print(f'ask_price4={tick.ask_price4}',f'ask_volume4={tick.ask_volume5}')
            print(f'ask_price3={tick.ask_price3}',f'ask_volume3={tick.ask_volume5}')
            print(f'ask_price2={tick.ask_price2}',f'ask_volume2={tick.ask_volume5}')
            print(f'ask_price1={tick.ask_price1}',f'ask_volume1={tick.ask_volume5}')
            print('\n'*5)
            
            #買進越來越低，賣出越來越高
            
            
        
        
        
 

if __name__ == '__main__':
    wss_url='wss://fstream.binance.com/ws'
    ws=websocket.WebSocketApp(wss_url,
                           on_open=on_open,
                           on_close=on_close,
                           on_message=on_message,
                           on_error=on_error)
    ws.run_forever(ping_interval=15,sslopt={"cert_reqs": 0})
    








 