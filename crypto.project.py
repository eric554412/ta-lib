import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CryptoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cryto_label = QLabel("Enter crypto name: ", self)
        self.crpto_input = QLineEdit(self)
        self.get_price_botton = QPushButton('Get price', self)
        self.cryto_price_label = QLabel(self)
        self.daily_price_change = QLabel(self)
        self.emoji_label = QLabel(self)
        self.initUI()
        
    
    def initUI(self):
        self.setWindowTitle('Crypto_App')
        
        vbox = QVBoxLayout()
        
        vbox.addWidget(self.cryto_label)
        vbox.addWidget(self.crpto_input)
        vbox.addWidget(self.get_price_botton)
        vbox.addWidget(self.cryto_price_label)
        vbox.addWidget(self.daily_price_change)
        vbox.addWidget(self.emoji_label)
        
        self.setLayout(vbox)
        
        self.cryto_label.setAlignment(Qt.AlignCenter)
        self.crpto_input.setAlignment(Qt.AlignCenter)
        self.cryto_price_label.setAlignment(Qt.AlignCenter)
        self.daily_price_change.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        
        self.cryto_label.setObjectName("cryto_label")
        self.crpto_input.setObjectName("crpto_input")
        self.get_price_botton.setObjectName("current_price_botton")
        self.cryto_price_label.setObjectName("cryto_price_label")
        self.daily_price_change.setObjectName("daily_price_change")
        self.emoji_label.setObjectName("emoji_label")
        
        self.crpto_input.setFixedHeight(20)
        self.emoji_label.setFont(QFont('Apple Color Emoji', 50))
        
        self.setStyleSheet("""
            QLabe, QpushButton{
                font-family: calibri;
            }
            QLabelc#cryto_label{
                font-size: 20px;
                font-style: italic;
            }
            QLineEdit#crpto_input{
                font-size: 20px
                height: 20px
            }
            QPushButton#get_price_botton{
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#cryto_price_label{
                font-size: 75px;
            }
            QLabel#daily_price_change{
                font-size: 50px;
            }
            QLabel#emoji_label{
                font-size: 100px;
            }
            """)
        
        self.get_price_botton.clicked.connect(self.get_price)
        
    
    def get_price(self):
        crypto_name = self.crpto_input.text()
        price_url = f'https://api.binance.com/api/v3/ticker/price'
        params = {'symbol': crypto_name.upper()}
        price_change_url = f'https://api.binance.com/api/v3/ticker/24hr'
        
        try :
            price_data, price_status = self.get_data(price_url, params)
            price_change_data, price_change_status = self.get_data(price_change_url, params)
            
            if price_status == 200 and price_change_status == 200 :
                self.display_price(price_data, price_change_data)
                # print(price_data)
                # print(price_change_data)
            else :
                self.handle_http_error(price_status or price_change_status)
        
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Erroe:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Time out error:\nThe request time out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the url")
        except requests.exceptions.RequestException as req_error :
            self.display_error(f"Request Error:\n{req_error}") 
    
    
    
    def handle_http_error(self, status_code):
        match status_code :
            case 400:
                self.display_error("Bad Request:\nCheck your parameters.")
            case 401:
                self.display_error("Unauthorized:\nInvalid API key or signature.")
            case 403:
                self.display_error("Forbidden:\nAccess denied (WAF Restriction).")
            case 404:
                self.display_error("Not Found:\nInvalid crypto symbol or resource.")
            case 429:
                self.display_error("Too Many Requests:\nRate limit exceeded.")
            case 418:
                self.display_error("IP Banned:\nYou have been rate-limited.")
            case 500:
                self.display_error("Internal Server Error:\nBinance servers are down.")
            case 502:
                self.display_error("Bad Gateway:\nInvalid response from server.")
            case 503:
                self.display_error("Service Unavailable:\nServer is overloaded or down.")
            case 504:
                self.display_error("Gateway Timeout:\nNo response from Binance.")
            case _:
                self.display_error(f"HTTP Error occured:\n{status_code}")
                  
        
    def get_data(self, url, params):
        respone = requests.get(url ,params = params)
        data = respone.json()
        status_code = respone.status_code
        return data, status_code
    

        
    def display_error(self, message):
        self.cryto_price_label.setText(message)
        self.daily_price_change.clear()
        self.emoji_label.clear()
    
    
    def display_price(self,price_data, price_change_data):
        current_price_matrix = price_data['price']
        daily_price_change_matrix = price_change_data['priceChangePercent']
        
        self.cryto_price_label.setText(f'current price: {current_price_matrix}')
        self.daily_price_change.setText(f'daily pct change: {daily_price_change_matrix}%')
        self.emoji_label.setText(self.get_price_emoji(price_change_data))
    
    
    @staticmethod
    def get_price_emoji(price_change_data):
        daily_price_change_matrix = float(price_change_data['priceChangePercent'])
        if daily_price_change_matrix > 0 :
            return '🚀'
        else :
            return '📉'
        
        
        
if __name__ == '__main__' :
    app = QApplication(sys.argv)
    crypto_app = CryptoApp()
    crypto_app.show()
    sys.exit(app.exec_())