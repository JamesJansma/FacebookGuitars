from playwright.sync_api import sync_playwright
import os
import time
import pprint
from bs4 import BeautifulSoup


# Conditions: new, used_like_new, used_good, used_fair
conditions = ['new', 'used_like_new', 'used_good', 'used_fair']

facebook_market_url = 'https://www.facebook.com/marketplace/spokane/search/?query=guitar&exact=false'
login_url = "https://www.facebook.com/login/device-based/regular/login/"
# facebook_market_condition_url = f'https://www.facebook.com/marketplace/spokane/search?itemCondition={condition}&query=guitar&exact=false'


with sync_playwright() as p:
        # Open a new browser page.
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # Navigate to the URL.
        page.goto(login_url)
        time.sleep(2)
        try:
            # login(page)
            page.locator('input[name="email"]').type("j89666944@gmail.com",delay=150)
            time.sleep(2)
            page.wait_for_selector('input[name="pass"]').type("jamesjames4", delay=150)
            time.sleep(2)
            page.wait_for_selector('button[name="login"]').click()
            time.sleep(8)
        except:
            print('Login Unnsuccessful')

        for condition in conditions:
            facebook_market_condition_url = f'https://www.facebook.com/marketplace/spokane/search?itemCondition={condition}&query=guitar&exact=false'

            page.goto(facebook_market_condition_url)
            time.sleep(2)