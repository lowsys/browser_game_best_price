# This is a sample Python script.
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tabulate import tabulate

fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True

#here you have to modify lines according to your paths and credentials
binary = FirefoxBinary("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
geckodriver = "C:\\python\\Python37\\geckodriver.exe"
user_name = "login"
password = "password"
#end of your modifications
delay = 5
heat_icon_CSS = """#root > div > div > div.game-content > div.combine-main-area > div.game-right-panel > 
div.right-panel-currency > div:nth-child(2) > img"""
gold_icon_CSS = """#root > div > div > div.game-content > div.combine-main-area > div.game-right-panel > 
div.right-panel-currency > div:nth-child(1) > img"""
prices_table_CSS = """#root > div > div > div.game-content > div.combine-main-area > div.play-area-chat > 
div.play-area-container > div.play-area.theme-default > div > table"""
market_table_CSS = """#root > div > div > div.game-content > div.combine-main-area > div.play-area-chat > 
div.play-area-container > div.play-area.theme-default > div > div.marketplace-content > div"""
back_button_CSS = """#root > div > div > div.game-content > div.combine-main-area > div.play-area-chat > 
div.play-area-container > div.play-area.theme-default > div > div > div > button.marketplace-back-button"""
offers_quantity_xpath = "/html/body/div[1]/div/div/div[4]/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr"
#open Firfox in headless mode
browser = webdriver.Firefox(options=fireFoxOptions, firefox_binary=binary, executable_path="geckodriver")
heat_market_list = []
burnable_items = ["Book", "Coal", "Branch", "Log", "Oak Log", "Willow Log", "Maple Log", "Yew Log", "Pyre Log"
                    , "Pyre Oak Log", "Pyre Willow Log", "Pyre Maple Log", "Pyre Yew Log"]
heat_values = {"Book": 50, "Coal": 10, "Branch": 1, "Log": 5, "Oak Log": 10, "Willow Log": 20, "Maple Log": 70,
               "Yew Log": 200, "Pyre Log": 100, "Pyre Oak Log": 200, "Pyre Willow Log": 400, "Pyre Maple Log": 800,
               "Pyre Yew Log": 3000}

def user_login():
    browser.find_element_by_css_selector(".btn-round").click()
    browser.find_element_by_css_selector("#username").send_keys(user_name)
    browser.find_element_by_css_selector("#password").send_keys(password)
    browser.find_element_by_css_selector("button.mt-5:nth-child(3)").click()

def access_market():
    try:
        #Wait for loaded site by checking gold icon
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gold")))
        #print("market available!")
        browser.find_element_by_css_selector("#gold").click()
        #print("i'm on the market!")
    except TimeoutException:
        print("cannot find gold icon")
    #I didn't find nice way to wait until market loads

def get_heat_amount():
    global heat_amount
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, heat_icon_CSS)))
        print("heat rough value present!")
        browser.find_element_by_css_selector(heat_icon_CSS).click()
        #space in a heat value is \xa0. heat value converted into integer
        heat_amount = int(browser.find_element_by_css_selector("#heat-tooltip > span").get_attribute("innerText").\
            replace("\xa0", ""))
    except TimeoutException:
        print("cannot find heat")
def get_gold_amount():
    global gold_amount
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, gold_icon_CSS)))
        print("gold rough value present!")
        browser.find_element_by_css_selector(gold_icon_CSS).click()
        # space in a heat value is \xa0. heat value converted into integer
        gold_amount = int(browser.find_element_by_css_selector("#gold-tooltip > span").get_attribute("innerText"). \
                          replace("\xa0", ""))
        print(gold_amount)
    except TimeoutException:
        print("cannot find gold")

def get_heat_prices(item_name):
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, market_table_CSS)))
        #print("market fully loaded!")
        item_prices_list=[]
        #testing on books
        market_icon = browser.find_element_by_css_selector(f'[alt="{item_name}"]')
        #element with alt name is not clickable, take next one (which is <span>
        market_icon.find_element_by_xpath("./following-sibling::span").click()
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, prices_table_CSS)))
        print(f"Getting prices for {item_name}")
        #check number of item offers
        offers_number = browser.find_elements_by_xpath(offers_quantity_xpath)
        #cut to get only first 3
        if len(offers_number) > 3:
            offers_number = 3
        #or less than 3
        else:
            offers_number = len(offers_number)
        #get values from offers
        for i in range(1,offers_number + 1):
            item_prices_list.append(item_name)
            item_prices_list.append(i)
            #get amount and prices without spaces
            for j in range(3,5):
                try:
                    item_amount_price = browser.find_element_by_xpath\
                        (f'//*[@id="root"]/div/div/div[4]/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[{i}]/td[{j}]').\
                        text.replace(" ", "")
                    item_prices_list.append(item_amount_price)
                except:
                    pass
        heat_market_list.append(item_prices_list)
        #print(item_prices_list)
        print(heat_market_list)
        #go back to markets item list
        browser.find_element_by_css_selector(back_button_CSS).click()

    except TimeoutException:
        print("market list unavailable")
    except InvalidSelectorException:
        print(f"{item_name} is not available in the market")
    except NoSuchElementException:
        print(f"{item_name} is not available in the market")
def top_best_offers():
    global three_best_offers
    three_best_offers = []
    # preparation of proper list with item name, offer row, amount available, price per unit
    k = 0

    for i in range(len(heat_market_list)):
        for j in range(0, len(heat_market_list[i]), 4):
            print(heat_market_list[i][j:j + 4])
            price = heat_market_list[i][j + 3]
            heat_value = heat_values.get(heat_market_list[i][j])
            three_best_offers.append(heat_market_list[i][j:j + 4])
            three_best_offers[k].append(round((int(price) / int(heat_value)),2))
            k += 1

    # sort list by gold per heat
    three_best_offers.sort(key=lambda x: x[4])
    # get only 5 cheapest offers
    three_best_offers = three_best_offers[0:3]
    print(three_best_offers)
def show_best_offers():
    headers = ["Item", "Offer No", "Amount", "Price per piece", "Gold per one heat"]
    print(f"Three best heat offers at the market are:\n")
    print(tabulate(three_best_offers, headers=headers))



#open game site
try:
    browser.get("URL")
except TimeoutException:
    print("Site is not responding, check your connetion")

user_login()
get_gold_amount()

access_market()
for item in burnable_items:
     get_heat_prices(item)
top_best_offers()
show_best_offers()
