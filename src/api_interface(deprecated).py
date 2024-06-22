#!/Users/user/Documents/TradeSentinel/venv/bin/python

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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

class SchwabAPI:
    ###INIT##
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
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

        try:
            # Set up Chrome options
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

            # Adding argument to disable the AutomationControlled flag 
            chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
 
            # Exclude the collection of enable-automation switches 
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
 
            # Turn-off userAutomationExtension 
            chrome_options.add_experimental_option("useAutomationExtension", False) 

            #Set up the WebDriver (using Chrome in this example)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


            
            #open url
            driver.get(auth_url)

            print(driver.page_source)
            
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.ID, 'loginIdInput')))
            print("id located")
            password_field = wait.until(EC.presence_of_element_located((By.ID, 'passwordInput')))
            print("password located")

            # Input the username and password
            time.sleep(2)
            username_field.send_keys(self.username)
            time.sleep(2)
            password_field.send_keys(self.password)
            print("login and pw typed in")

            # Submit the form
            password_field.send_keys(Keys.RETURN)  # This will press the Enter key
            print("login entered")


            # Wait for the next page to load and the checkbox to be present
            checkbox = wait.until(EC.presence_of_element_located((By.ID, 'acceptTerms')))
            if not checkbox.is_selected():
                time.sleep(1)
                checkbox.click()

            # Wait for the continue button to be clickable and check its visibility
            continue_button = wait.until(EC.element_to_be_clickable((By.ID, 'submit-btn')))
            driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
    
            # Check if the button is visible
            if continue_button.is_displayed():
                continue_button.click()
            else:
                print("Continue button is not visible or clickable.")

        except Exception as e:
            print(f"Exception occurred: {e}")
            
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
