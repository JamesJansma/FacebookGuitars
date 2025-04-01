# Listings: x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24
# now in a particular listing
# name/title: x1lliihq x6ikm8r x10wlt62 x1n2onr6
# pricing: x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u


from playwright.sync_api import sync_playwright
import os
import requests
import time
import pprint
from bs4 import BeautifulSoup


# Conditions: new, used_like_new, used_good, used_fair
conditions = ['new']

facebook_market_url = 'https://www.facebook.com/marketplace/spokane/search/?query=guitar&exact=false'
login_url = "https://www.facebook.com/login/device-based/regular/login/"
# facebook_market_condition_url = f'https://www.facebook.com/marketplace/spokane/search?itemCondition={condition}&query=guitar&exact=false'

async def scroll(page):
    page.wheel(0,1000)
    time.sleep(5)


async def login(page):
    page.locator('input[name="email"]').type("j89666944@gmail.com",delay=100)
    page.wait_for_selector('input[name="pass"]').type("jamesjames4", delay=100)
    page.wait_for_selector('button[name="login"]').click()
    


with sync_playwright() as p:
        os.makedirs("images", exist_ok=True)

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
        
        parsed = []

        for condition in conditions:
            facebook_market_condition_url = f'https://www.facebook.com/marketplace/spokane/search?itemCondition={condition}&query=guitar&exact=false'

            page.goto(facebook_market_condition_url)
            time.sleep(2)
            for i in range(1):
                # page.mouse.wheel(0,15000)
                # time.sleep(2)
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                listings = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')
                elements = page.locator("span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.xlh3980").all()
                for i, listing in enumerate(listings):
                    try:
                        title = listing.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6').text
                        price = listing.find('span', 'x4zkp8e').text
                        parsed.append({
                                'title': title,
                                'price': price.replace('$',''),
                                'condition' : condition
                            })
                        
                        img_url = listing.find('img').get('src')

                        img_data = requests.get(img_url).content

                        with open(f"images/image_{i}.jpg", "wb") as img_file:
                            img_file.write(img_data)
                        
                    except:
                        pass
            
            
        browser.close()
        result = []
        pprint.pprint(parsed, sort_dicts=False, width=150)




                  


        