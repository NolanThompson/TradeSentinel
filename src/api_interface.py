#standard
import os
import requests
import time

#third party
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

class SchwabAPI:
    ###INIT###
    def __init__(self):
        self.client_id = os.getenv("API_KEY")
        self.client_secret = os.getenv("API_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.account_id = os.getenv("ACCOUNT_ID")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.base_url = "https://api.schwabapi.com"
        self.token = self.get_access_token()

    ###AUTH###
    #authorize and grab access token
    def get_access_token(self):
        #get authorization code
        auth_code = self.get_authorization_code()

        #exchange authorization code for access token
        url = f"{self.base_url}/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    #automated oauth authorization and auth code fetch
    def get_authorization_code(self):
        auth_url = f"{self.base_url}/v1/oauth/authorize?&client_id={self.client_id}&redirect_uri={self.redirect_uri}"

        #selenium webdriver automation
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        try:
            #open url
            driver.get(auth_url)
            
            #automate oauth login
            time.sleep(3)   #let page load
            driver.find_element(By.NAME, "username").send_keys(self.username)   #verify parameter
            driver.find_element(By.NAME, "password").send_keys(self.password)   #verify parameter
            driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
            
            #wait for authorization and redirection 
            time.sleep(5)
            
            #extract authorization code
            current_url = driver.current_url
            auth_code = current_url.split("code=")[1]
            return auth_code
        finally:
            driver.quit()

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    ###FUNCTIONS###
    #grab ticker data
    def get_ticker(self, symbol):
        url = f"{self.base_url}/v1/marketdata/{symbol}/quotes"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    #order method
    def place_order(self, symbol, quantity, instruction, order_type, price=None, stop_price=None, trail_amount=None):
        #payload structure
        order_data = {
            "orderType": order_type,
            "session": "NORMAL",
            "duration": "GOOD_TILL_CANCEL",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [{
                "instruction": instruction,
                "quantity": quantity,
                "instrument": {
                    "symbol": symbol,
                    "assetType": "EQUITY"
                }
            }]
        }

        #conditional payload adaptation
        if price:
            order_data["price"] = price
        if stop_price:
            order_data["stopPrice"] = stop_price
        if trail_amount:
            order_data["trailAmount"] = trail_amount

        #api call
        url = f"{self.base_url}/v1/accounts/{self.account_id}/orders"
        headers = self.get_headers()
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        return response.json()

    #buy at current market value
    def buy_stock(self, symbol, quantity, price):
        return self.place_order(symbol, quantity, "BUY", "MARKET", price=price)

    #place stop loss
    def place_stop_loss(self, symbol, quantity, stop_price):
        return self.place_order(symbol, quantity, "SELL", "STOP", stop_price=stop_price)

    #place target sell price
    def place_target_sell(self, symbol, quantity, target_price):
        return self.place_order(symbol, quantity, "SELL", "LIMIT", price=target_price)

    #place trailing stop loss
    def place_trailing_stop(self, symbol, quantity, trail_amount):
        return self.place_order(symbol, quantity, "SELL", "TRAILING_STOP", trail_amount=trail_amount)


#example usage
if __name__ == "__main__":
    schwab_api = SchwabAPI()
    ticker = "AAPL"
    ticker_data = schwab_api.get_ticker(ticker)
    print(json.dumps(ticker_data, indent=4))
