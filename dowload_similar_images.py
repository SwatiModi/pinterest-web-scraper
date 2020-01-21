import pandas as pd
import urllib.request
import argparse
from bs4 import *
from selenium import webdriver
import re
import os
from selenium.webdriver.support import ui
import time
import os

# add argument parser for passing the target CSV for saving the image URLs and no. of pages to be scraped
parser = argparse.ArgumentParser()
parser.add_argument('--csv', help='CSV with PID URLs', action='store', dest='CSVname')
parser.add_argument('--username', help='username', action='store', dest='login_name')
parser.add_argument('--password', help='', action='store', dest='login_pass')
args = parser.parse_args()

if args.CSVname :
	csvname = args.CSVname
else:
	csvname = str(input('Enter the "input CSV" name: '))

if args.login_name :
	login_name = args.login_name
else:
	login_name = str(input('Enter your pinterest username/email id: '))

if args.CSVname :
	login_pass = args.login_pass
else:
	login_pass = str(input('Enter the pinterest password: '))

dest_dir = csvname.split('.csv')[0]
dest_dir = dest_dir + '/'

try:
	os.mkdir(dest_dir)
except:
	pass

df = pd.read_csv(csvname)   # CSV with PINS' visual search URLs
urls = df['PID_URLS']

# create directories to save the images
for i in range(len(df)):
	pin_number = urls[i].split('/')[-3]
	try:
		os.mkdir(dest_dir + pin_number + '/')
	except:
		pass

error_url = []

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
    time.sleep(3)
    print("Teleport Successful!")

def get_images_and_tags(url):
    url_set = set() 				# using set instead of list to avoid duplicate urls
    tag_set = []

    try:
    	driver.get(url)
    except:
    	print('ERRORRRRR')

    SCROLL_PAUSE_TIME = 0.5

    while True:
		# Scroll down to bottom
    	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	    # Wait to load page
    	time.sleep(SCROLL_PAUSE_TIME)

	    # Calculate new scroll height and compare with last scroll height
    	new_height = driver.execute_script("return document.body.scrollHeight")
    	# print(new_height)

    	if new_height >= 15000:								# increase this scroll height threshould to get more no. of images
    		break

    page = driver.page_source
    bs = BeautifulSoup(page,'html.parser')
    # images = bs.find_all('img', {'src':re.compile('.jpg')})
    images = bs.find_all('img','hCL kVc L4E MIw')
    for image in images: 			
        url_set.add(image['src'])

    # tags = bs.find_all('div','flashlightAnnotationListItem')     
    # for tag in tags: 			
    #     tag_set.append(tag.text)
    # # driver.quit()
    return list(url_set), tag_set   

def download_items(url_set,dest_dir, image_num):
    
    """
    This function download the items referred by URL in given set of url.

    Parameters :
    url_set (Set): A set containing URL to items
    dest_dir (string): Path to Destination Directory where items are to be downloaded
    item_category (string ) : A string specifying the category to which the item belongs

    Returns:
        NONE
    """

    
    for index,url in enumerate(url_set):
        path = dest_dir + image_num + "/"+ str(index) + ".jpg"
        # print(path)
        try:
        	urllib.request.urlretrieve(url, path)
        except :
            print("An excpetion occured during downloading data \n")
            continue
        # time.sleep(3)
    return

driver =   webdriver.Chrome()
login(driver, login_name, login_pass)

for i in range(len(urls)):
	image_urlset, tag_set = get_images_and_tags(urls[i])

	pin_number = urls[i].split('/')[-3]

	image_urlCSV = pd.DataFrame({'URLs':image_urlset})
	image_urlCSV.to_csv(str(dest_dir) + str(pin_number) + '/' + str(pin_number) + '_URLs' + '.csv',index = False)

	# tagsCSV = pd.DataFrame({'Tags':tag_set})
	# tagsCSV.to_csv(str(dest_dir) + str(pin_number) + '/' + str(pin_number) + '_tags' + '.csv',index = False)

	download_items(image_urlset[:50],str(dest_dir), str(pin_number))   
	time.sleep(6)