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

            divs = page.locator('div.x9f619.x78zum5.x1r8uery.xdt5ytf.x1iyjqo2.xs83m0k.x1e558r4.x150jy0e.x1iorvi4.xjkvuk6.xnpuxes.x291uyu.x1uepa24')
            count = divs.count()
            print(f"Found {count} divs")
            # page.mouse.wheel(0,15000)
            # time.sleep(2)
            for j in range(3): #this now deals with amount of guitars.
                divs.nth(j).click()
                time.sleep(1)
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                listing = soup.find('div', class_='x1bwycvy x16xn7b0 x1bifzbx x6ikm8r x10wlt62 xh8yej3 x7pk29f x1dr59a3 xiylbte')
                images = soup.find_all('div',class_='x1rg5ohu x2lah0s xc9qbxq x14qfxbe x1mnrxsn x1w0mnb')
                print(f"Images count: {len(images)}")
                title = listing.find('span', 'x1xlr1w8').text
                print(f"Title: {title}")
                pre_price = listing.find('span', 'xk50ysn').text

                pre_price = pre_price.split('$')
                price = pre_price[1]
                print(f"Price: {price}")

                parsed.append({
                        'title': title,
                        'price': price,
                        'condition' : condition
                    })

                os.makedirs(f"images/guitar_{j}", exist_ok=True)

                if len(images) == 0:
                    img_url = listing.find('img').get('src')
                    img_data = requests.get(img_url).content
                    with open(f"images/guitar_{j}/image_{0}.jpg", "wb") as img_file:
                        img_file.write(img_data)
                else:
                    for i, image in enumerate(images):
                        try:
                            img_url = image.find('img').get('src')
                            print(f"Img url: {img_url}")
                            img_data = requests.get(img_url).content

                            with open(f"images/guitar_{j}/image_{i}.jpg", "wb") as img_file:
                                img_file.write(img_data)
                        except:
                            print("there was no image found")
                            pass
                    
                page.go_back()
                time.sleep(1)
            
            
        browser.close()
        pprint.pprint(parsed, sort_dicts=False, width=150)




                  


        