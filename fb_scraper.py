from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup as bs
import os

# Function to archive the current webpage's content as an HTML file
def archive(driver, reviewList, index):
    driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
    time.sleep(10)
    
    # Scroll through the reviews and save the page source after a few scrolls
    for r in range(2):
        try:
            driver.execute_script("arguments[0].scrollIntoView();", reviewList[min(index + 15, len(reviewList)-1)])
        except:
            driver.execute_script("arguments[0].scrollIntoView();", reviewList[-1])
        time.sleep(3)
        
        with open(f'./model/{index}_{r}.html', "w", encoding="utf-8") as file:
            source_data = driver.page_source
            bs_data = bs(source_data, 'html.parser')
            file.write(str(bs_data.prettify()))
            print(f"Written: {index}, {r}")
            return index, r


# Main scraping function to access Facebook and collect reviews
def scrape(url, num_reviews_threshold):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Set path to chromedriver
    chromedriver_path = './chromedriver'
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

    # Login to Facebook
    with open('./model/fb_credentials.txt') as file:
        EMAIL, PASSWORD = file.readline().split()

    driver.get("http://facebook.com")
    wait = WebDriverWait(driver, 30)
    wait.until(EC.visibility_of_element_located((By.NAME, 'email'))).send_keys(EMAIL)
    password_element = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
    password_element.send_keys(PASSWORD + Keys.RETURN)
    
    # Wait for page to load after login
    time.sleep(5)
    driver.get(url)
    time.sleep(5)

    switch = True
    index, r = 0, 0

    while switch:
        # Unfold more reviews if possible
        openSeeMore(driver) 
        getBack(driver)
        
        # Scroll to the end of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(15)

        # Retrieve reviews on the current page
        reviewList = driver.find_elements(By.XPATH, '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]')
        numReviews = len(reviewList)
        print(f"Reviews: {numReviews}")

        # If threshold is met, stop scrolling and archive the page
        if numReviews >= num_reviews_threshold:
            index, r = archive(driver, reviewList, index)
            switch = False

    # Read the archived HTML file and parse the reviews
    with open(f'./model/{index}_{r}.html', "r", encoding="utf-8") as file:
        page = bs(file.read(), 'lxml')

    reviews = page.find_all('div', {'class': 'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z'})
    ratings, users, texts = [], [], []

    for review in reviews:
        # Extract rating
        rating = review.find('h2',{"class":"html-h2 xe8uvvx x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x1gslohp x1yc453h"})

        ratings.append("recommends" if rating and "recommends" in rating.get_text() else "does not recommend" if rating else "no rating")

        # Extract user name
        user = review.find('a',{'class':'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xzsf02u x1s688f'})

        users.append(user.get_text().strip().split()[0] if user else "No user")

        # Extract review text
        text = review.find('span',{'class':'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h'})

        if not text:
            text = review.find('div',{'class':'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a'})
        texts.append(' '.join([i.strip() for i in text.get_text().split()]) if text else "no text")

    # Store data in a DataFrame
    master = pd.DataFrame({
        'ratings': ratings,
        'users': users,
        'texts': texts
    })
    
    driver.quit()
    return master



