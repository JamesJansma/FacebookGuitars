from playwright.sync_api import sync_playwright
import os
import time
import pprint
from bs4 import BeautifulSoup


start_up_url = 'https://www.guitarcenter.com/'
model = 'stratocaster'

with sync_playwright() as p:
        # Open a new browser page.
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # Navigate to the URL.
        page.goto(start_up_url)
        time.sleep(2)
        page.locator('input[id="header-search-input"]').type(model)
        time.sleep(1)  
        page.wait_for_selector('button[class="absolute right-0 top-0 w-[56px] h-full flex items-center justify-center cursor-pointer"]').click()
        time.sleep(1)
        current_url = page.url
        current_url += '&filters=condition:New'
        page.goto(current_url)
        time.sleep(2)
        page.mouse.wheel(0,500)

        parsed = []
        html = page.content()

        soup = BeautifulSoup(html, 'html.parser')
        listings = soup.find_all('div', class_='jsx-f0e60c587809418b plp-product-details px-[10px]')

        for listing in listings:
                title = listing.find('h2','jsx-f0e60c587809418b').text
                price = listing.find('span', 'jsx-f0e60c587809418b sale-price font-bold text-[#2d2d2d]').text
                parsed.append({
                        'title' : title,
                        'price' : price
                })
                
        time.sleep(3)
        browser.close
        pprint.pprint(parsed, sort_dicts=False, width=150)


