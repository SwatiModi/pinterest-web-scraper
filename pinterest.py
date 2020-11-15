import requests
from bs4 import *
from selenium import webdriver
import pandas as pd
import argparse
import re
import os
from selenium.webdriver.support import ui
import time

parser = argparse.ArgumentParser()
parser.add_argument(
    '--saveto', help='Target CSV to save the Image URLs', action='store', dest='CSVname')
parser.add_argument('--category', help='Product category to be searched ',
                    action='store', dest='category')
parser.add_argument('--username', help='username',
                    action='store', dest='login_name')
parser.add_argument('--password', help='password',
                    action='store', dest='login_pass')
args = parser.parse_args()

if(args.category):
    item_category = str(args.category)
else:
    item_category = str(
        input('Enter the search category (Ex : Nike Black shoes): '))

if(args.CSVname):
    csv_name = str(args.CSVname)
else:
    csv_name = item_category + '.csv'

if args.login_name:
	login_name = args.login_name
else:
	login_name = str(input('Enter your pinterest email id: '))

if args.CSVname:
	login_pass = args.login_pass
else:
	login_pass = str(input('Enter the pinterest password: '))

# Initialize and launch the chrome driver
driver = webdriver.Chrome()
driver.get("https://www.pinterest.com")

driver.implicitly_wait(20)


def page_is_loaded(driver):
    return driver.find_element_by_tag_name("body") != None


def login(driver, username, password):
    if driver.current_url != "https://www.pinterest.com/login/?referrer=home_page":
        driver.get("https://www.pinterest.com/login/?referrer=home_page")
    wait = ui.WebDriverWait(driver, 10)
    wait.until(page_is_loaded)
    email = driver.find_element_by_xpath("//input[@type='email']")
    password = driver.find_element_by_xpath("//input[@type='password']")
    email.send_keys(login_name)
    password.send_keys(login_pass)
    # driver.find_element_by_xpath("//div[@data-reactid='30']").click()
    password.submit()
    print("Teleport Successful!")


login(driver, login_name, login_pass)
driver.implicitly_wait(30)
time.sleep(3)

# prepare the URL for search
url = 'https://in.pinterest.com/search/pins/?q=' + \
    item_category.replace(" ", "%20")

# wait and get the query page
driver.implicitly_wait(30)
driver.get(url)
driver.implicitly_wait(30)

all_pin_data = []

while 1:
    # scroll
    driver.execute_script("window.scrollBy(0,10000)")
    time.sleep(3)
    driver.execute_script("window.scrollBy(0,10000)")
    time.sleep(3)

    # get the html now
    page_source = driver.page_source
    page = BeautifulSoup(page_source, 'html.parser')

    # 'GrowthUnauthPinImage' is the class of all the pins
    # Here we take divs which have a with href as pin number
    pin_data = page.find_all('div', "Yl- MIw Hb7")

    all_pin_data.extend(pin_data)
    all_pin_data = list(set(all_pin_data))

    print(len(pin_data))
    if len(all_pin_data) > 50:
        break


# get links for individual pages of all the Pins
hrefs = []
for i in range(len(all_pin_data)):
    hrefs.append('https://www.pinterest.com' +
                 all_pin_data[i].find('a')['href'] + 'visual-search/')

# save to CSV
df = pd.DataFrame({'PID_URLS': hrefs[:50]})
df.to_csv(csv_name, index=False)
