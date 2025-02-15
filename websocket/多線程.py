#多線程，同時發送多個多個請求，獲取多個交易所得的ticker數據

from  threading import Thread,Lock

# def print_hello(a):
#     print(a)

# t1=Thread(target=print_hello,args=("hello world",))
# t1.start()

# def print_hello2(a,b,c):
#     print(a)
#     print(b)
#     print(c)

# t2=Thread(target=print_hello2,args=(1,2,3))  #kwargs={'a':1,'c':3,'b':2}
# t2.start()

# import threading
# import time
# def run(num):
#     print('子線程%s開始...'%(threading.current_thread().name))
#     time.sleep(2)
#     print(num)
#     time.sleep(2)
#     print('子線程%s結束...'%(threading.current_thread().name))
    
# if __name__=='__main__':
#     print('主線程%s啟動...'%(threading.current_thread().name))
#     t=Thread(target=run,args=(1,))
#     t.start()
#     t.join() #代表等待子線程結束才執行下面程式碼 
#     print('主線程%s結束'%(threading.current_thread().name))

#多線程共享資源,lock(鎖)的運用避免多線程結果不一致
# from threading import Lock 
# lock=Lock() 
# num=0
# def run(n):
#     global num
#     for i in range(10000):
    #   num =num- n
    #   num =num+ n  
        
#method1  lock.acquire()  
        # num = num+n
        # num = num-n
        # lock.release()

#method2  with lock:
        # num +=n
        # num -=n
        
        
# if __name__=='__main__':
#     t1=Thread(target=run,args=(6,))
#     t2=Thread(target=run,args=(9,))
#     t3=Thread(target=run,args=(5,))
#     t1.start()
#     t2.start()
#     t3.start()
#     t1.join()
#     t2.join()
#     t3.join()
#     print("num=%s"%num)
    

  
from threading import Thread
import time

class MyThread(Thread):
    def __init__(self,exchange):
        super(MyThread,self).__init__()
        self.name="hello world"
        self.exchange=exchange
    def run(self):
        while True:
           print(f"request {self.exchange} btcusdt....")
           time.sleep(2)
           

if __name__=='__main__':
    thread1=MyThread('huobi')
    thread1.start()
    
    thread2=MyThread('binance')
    thread2.start()
    

    