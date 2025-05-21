import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as selenium_exc

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    )
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_reviews_container(wait, retries=3, delay=2):
    for i in range(retries):
        try:
            container = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//div[contains(@class,"m6QErb") and contains(@class,"DxyBCb")]')
            ))
            return container
        except selenium_exc.TimeoutException:
            print(f"Attempt {i+1} to find review container failed, retrying after {delay}s...")
            time.sleep(delay)
    raise RuntimeError("Couldn't find the review scroll container after retries.")

def scrape(url, num_reviews_threshold=20):
    driver = init_driver()
    wait = WebDriverWait(driver, 30)

    print(f"Loading URL: {url}")
    driver.get(url)
    time.sleep(3)

    try:
        print("Looking for the 'Reviews' tab...")
        reviews_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[.//div[text()="Reviews"]]')
        ))
        print("Clicking the 'Reviews' tab...")
        reviews_tab.click()
        time.sleep(2)
    except Exception as e:
        driver.quit()
        raise RuntimeError("Couldn't find or click the 'Reviews' tab. Check URL.") from e

    try:
        print("Waiting for the review scroll container to be visible...")
        scroll_div = wait_for_reviews_container(wait)
    except Exception:
        driver.quit()
        raise

    reviews = []
    seen_reviews = set()
    scroll_attempts = 0
    max_scroll_attempts = 30

    while len(reviews) < num_reviews_threshold and scroll_attempts < max_scroll_attempts:
        review_elems = driver.find_elements(By.XPATH, '//div[@data-review-id]')
        print(f"Found {len(review_elems)} review elements")

        for btn in driver.find_elements(By.XPATH, '//button[contains(text(), "More")]'):
            try:
                driver.execute_script("arguments[0].click();", btn)
            except:
                pass

        new_count = 0
        for elem in review_elems:
            try:
                user = elem.find_element(By.CLASS_NAME, "d4r55").text
                rating = elem.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
                text = elem.find_element(By.CLASS_NAME, "wiI7pd").text
                identifier = (user, text)

                if identifier in seen_reviews:
                    continue

                reviews.append({"user": user, "rating": rating, "text": text})
                seen_reviews.add(identifier)
                new_count += 1

                if len(reviews) >= num_reviews_threshold:
                    break
            except:
                continue

        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_div
            )
            time.sleep(2)
        except Exception as e:
            print("Could not scroll the reviews container:", e)

        if new_count == 0:
            scroll_attempts += 1
            print(f"No new reviews added. Attempt {scroll_attempts}/{max_scroll_attempts}")
        else:
            scroll_attempts = 0

    print(f"Finished. Collected {len(reviews)} reviews.")
    driver.quit()

    return pd.DataFrame(reviews[:num_reviews_threshold])
