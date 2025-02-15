from ws_inherbited import BinanceWebsocket,Tick
import json
import zlib   

class HuobiWebsocket(BinanceWebsocket):
    def __init__(self):
        super(HuobiWebsocket,self).__init__(host=wss_url, ping_interval=20)

    def on_open(self):
        print('open')
        data={
"sub":"market.DOGE-USDT.depth.step20",
"id":"id5"
}  
        self.send_mes(data)
    

    def on_message(self,msg):
        msg=json.loads(zlib.decompress(msg,31))
        if 'ch' in msg and msg['ch']=='market.DOGE-USDT.depth.step20':
            bids=msg['tick']['bids']
            asks=msg['tick']['asks']
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
    wss_url='wss://api.hbdm.com/linear-swap-ws'
    huobiws=HuobiWebsocket()
    huobiws.start()
    
    
    