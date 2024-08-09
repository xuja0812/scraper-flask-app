from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import urllib.request
import json
import time
import re
import datetime

def openSeeMore(driver):
    seeMores = driver.find_elements(By.XPATH, '//div[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux61 x1qhh985 xm0m39n x9f619 x1y0dohk xt0psk2 xe8uvvx xdj226r x11i5rm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg x1h12dhg xggy1nq x1a2a7pz x1sur9pj xkrqix2 xzsf02u x1s688f"]')
    if(len(seeMores) > 0):
        count = 0
        for i in seeMores:
            actions = ActionChains(driver)
            try:
                actions.move_to_element(i).click().perform()
                count+=1
            except:
                try:
                    driver.execute_script("arguments[0].click();", i) # MANIPULATES DOM IN JS INSTEAD OF ACTIONS
                    count+=1
                except:
                    continue
        time.sleep(1)
    else:
        pass

def getBack(driver):
    if not driver.current_url.endswith('reviews'):
        driver.back()

def archive(driver, reviewList):
    driver.execute_script("window.scrollTo(0, -document.body.scrollheight);")
    time.sleep(10)

    for index, l in enumerate(reviewList):
        print("hello there")
        if(index % 10 == 0):
            driver.execute_script("arguments[0].scrollIntoView();", reviewList[0]) if index < 15 else driver.execute_script("arguments[0].scrollIntoView();", reviewList[index-15])
        time.sleep(1)
        try:
            driver.execute_script("arguments[0].scrollIntoView();", reviewList[index+15])
        except:
            driver.execute_script("arguments[0].scrollIntoView();", reviewList[-1])

        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();", reviewList[index])
            
        for r in range(2):
            time.sleep(3)
            try:
                driver.execute_script("arguments[0].scrollIntoView();", reviewList[index+5])
                time.sleep(3)
            except:
                driver.execute_script("arguments[0].scrollIntoView();", reviewList[-1])
                driver.execute_script("arguments[0].scrollIntoView();", reviewList[index+r*3])
                time.sleep(3)
                with open(f'/Users/jasmi/Downloads/personal-project-xuja0812-3/model/{str(index)}_{r}.html',"w", encoding="utf-8") as file:
                    source_data = driver.page_source
                    bs_data = bs(source_data, 'html.parser')
                    file.write(str(bs_data.prettify()))
                    print("written:",index)
                    return index, r

def scrape(url, n):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    cService = webdriver.ChromeService(executable_path=('/Users/jasmi/Downloads/chromedriver-win32/chromedriver-win32/chromedriver.exe'))
    driver = webdriver.Chrome(service = cService, options = chrome_options)

    with open('/Users/jasmi/Downloads/personal-project-xuja0812-3/model/fb_credentials.txt') as file:
        line = file.readline()
        EMAIL = line.split()[0]
        PASSWORD = line.split()[1]

    # LOGS INTO FACEBOOK USING INFORMATION FROM THE TEXT FILE
    driver.get("http://facebook.com")
    wait = WebDriverWait(driver, 30)
    email_element = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
    email_element.send_keys(EMAIL)
    password_element = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
    password_element.send_keys(PASSWORD)
    password_element.send_keys(Keys.RETURN)

    # RETRIEVES ANY PAGE ONCE THE USER IS LOGGED IN
    time.sleep(5)
    driver.get("https://www.facebook.com/McDonalds/reviews")
    print("url:",url)
    # driver.get(url)
    time.sleep(5)

    # UNFOLDS ALL THE ELEMNENTS ON THE PAGE BY OPENING REPLIES AND COMMENTS AND SCROLLING TO THE END OF THE PAGE
    count = 0
    switch = True
    old_numReviews = 0
    numberReviews = 0

    index = 0
    r = 0

    while(switch):

        print("hello")
        
        openSeeMore(driver) 
        getBack(driver)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(15)

        reviewList = driver.find_elements(By.XPATH, '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]')
        numReviews = len(reviewList)
        print("reviews:",numReviews)
        old_numReviews = numReviews

        # TERMINATE
        if numReviews >= numberReviews:
            index, r = archive(driver, reviewList)
            switch = False

    with open(f'/Users/jasmi/Downloads/personal-project-xuja0812-3/model/{str(index)}_{r}.html',"r", encoding="utf-8") as file:
        f = file.read()

    page = bs(f, 'lxml')
    reviews = page.find_all('div', {
        'class':'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z'
                                })

    ratings = []
    users = []
    texts = []
    print("\n\n\n\nTHE LENGTH OF THE REVIEWS IS:",len(reviews),"\n\n\n\n")
    for idx, r in enumerate(reviews):
        rating = r.find('h2',{"class":"html-h2 xe8uvvx x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x1gslohp x1yc453h"})
        if rating is not None:
            rating = rating.get_text()
            if("recommends" in rating):
                ratings.append("recommends")
            else:
                ratings.append("does not recommend")
        else:
            ratings.append("no rating")

        user = r.find('a',{'class':'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xzsf02u x1s688f'})
        if user is not None:
            users.append(user.get_text().strip().split(" ")[0])
        else:
            users.append("No user")
        
        text = r.find('span',{'class':'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h'})
        if text is not None:
            texts.append(' '.join([i.strip() for i in text.get_text().split()]))
        else:
            text = r.find('div',{'class':'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a'})
            if text is not None:
                texts.append(text.get_text().strip())
            else:
                texts.append('no text')

    master = pd.DataFrame({
        'ratings':ratings, 
        'users':users,
        'texts':texts
                    })
    
    return master