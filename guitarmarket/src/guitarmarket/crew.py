from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
from crewai_tools import VisionTool
from pydantic import BaseModel, ValidationError
from typing import List
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
import os
import time
import base64
import requests
from bs4 import BeautifulSoup
from litellm import completion
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

class GuitarData(BaseModel):
    Model: str
    Price: float
    Condition: str

class ListingJson(BaseModel):
    marketGuitars: List[GuitarData]  
    listingGuitars: List[GuitarData]  

load_dotenv()
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

@CrewBase
class Guitarmarket():
	"""GuitarMarketplace crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# listing_read_tool = FileReadTool(file_path='src/crewaisimple/guitar_listings.csv')
	# market_read_tool = FileReadTool(file_path='src/crewaisimple/market_listings.csv')


	@tool("scraper tool")
	def scraper_tool() -> str:
		"""Does not take any input as it searches for guitars and then returns
			a listing of the guitars on the market place in the form of a json with \'Model\', \'Price\', and \'Condition\'"""
		os.makedirs("images", exist_ok=True)

		facebook_market_url = 'https://www.facebook.com/marketplace/spokane/search/?query=guitar&exact=false'
		login_url = "https://www.facebook.com/login/device-based/regular/login/"
		conditions = ['new','used_like_new', 'used_good']

		print("Scraper tool called")
		parsed = []

		with sync_playwright() as p:
			browser = p.chromium.launch(headless=False)
			page = browser.new_page()
			page.goto(login_url)
			time.sleep(2)
			try:
				# login(page)
				page.locator('input[name="email"]').type("j89666944@gmail.com",delay=150)
				time.sleep(2)
				page.wait_for_selector('input[name="pass"]').type("jamesjames4", delay=150)
				time.sleep(2)
				page.wait_for_selector('button[name="login"]').click()
				time.sleep(10)
				print("Login Completed")
			except:
				print("login failed")

			parsed = []
			i = 0
			for condition in conditions:
				facebook_market_condition_url = f'https://www.facebook.com/marketplace/spokane/search?itemCondition={condition}&query=guitar&exact=false'
				print(f"Going to page: {facebook_market_condition_url}")
				page.goto(facebook_market_condition_url, timeout=90000)
				time.sleep(2)

				divs = page.locator('div.x9f619.x78zum5.x1r8uery.xdt5ytf.x1iyjqo2.xs83m0k.x1e558r4.x150jy0e.x1iorvi4.xjkvuk6.xnpuxes.x291uyu.x1uepa24')
				count = divs.count()
				print(f"Found {count} divs")
				time.sleep(2)
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
					
					try:
						os.makedirs(f"images/guitar_{i}", exist_ok=True)
						print(f"Created image directory: \"images/guitar_{i}\"")
					except:
						print("Was not able to create directory \"images/guitar_{j}\"")
		   
					if len(images) == 0:
						img_url = listing.find('img').get('src')
						img_data = requests.get(img_url).content
						with open(f"images/guitar_{i}/image_{0}.jpg", "wb") as img_file:
							img_file.write(img_data)
						
					else:
						for k, image in enumerate(images):
							try:
								img_url = image.find('img').get('src')
								img_data = requests.get(img_url).content

								with open(f"images/guitar_{i}/image_{k}.jpg", "wb") as img_file:
									img_file.write(img_data)
							except:
								print("there was no image found")
								pass
						
					page.go_back()
					i += 1
					time.sleep(1)

			browser.close()
			print("Finished scraper tool")
			return parsed

	@tool("gc scraper tool")
	def gc_scraper_tool(listing_json: str) ->str:
		"""Takes in the ListingJson data object. 
		The guitars are all new and the return value is a list with \'Model\',\'Price\', and \'Condition\'"""
		try:
			print("Incoming listing_json (type):", type(listing_json))
			data = ListingJson.model_validate_json(listing_json)
		except ValidationError as e:
			return {"error": f"Invalid input format: {e}"}
		
		start_up_url = 'https://www.guitarcenter.com/'
		market_list = []
		for i, listing in enumerate(data.listingGuitars):
			_model = listing.Model
			print(f"Model passed into gs scraper: {_model}")

			with sync_playwright() as p:
					# Open a new browser page.
					browser = p.chromium.launch(headless=True)
					page = browser.new_page()
					# Navigate to the URL.
					page.goto(start_up_url)
					time.sleep(2)
					page.locator('input[id="header-search-input"]').type(_model)
					time.sleep(1)  
					page.wait_for_selector('button[class="absolute right-0 top-0 w-[56px] h-full flex items-center justify-center cursor-pointer"]').click()
					time.sleep(1)
					time.sleep(2)
					page.mouse.wheel(0,500)

					parsed = []
					html = page.content()

					soup = BeautifulSoup(html, 'html.parser')
					listings = soup.find_all('div', class_='jsx-f0e60c587809418b plp-product-details px-[10px]')
					print(f"Number of listings found: {len(listings)}")
					for list in listings:
							title = list.find('h2','jsx-f0e60c587809418b').text
							print("Title was found")
							price = list.find('span', 'jsx-f0e60c587809418b sale-price font-bold text-[#2d2d2d]').text
							print(f"Title found: {title}, Price found: {price}")
							market_list.append({
									'Model' : _model,
									'Price' : price,
									'Condition' : "new"
							})
							break
							
					time.sleep(3)
					browser.close
		return market_list

	@tool("img_get_tool")
	def img_get_tool(listing_json: str) -> dict:
		"""Takes in the ListingJson data structure containing all of the guitar data and 
		uses GPT-4o to identify the guitar model from an image"""

		try:
			print("Incoming listing_json (type):", type(listing_json))
			data = ListingJson.model_validate_json(listing_json)
		except ValidationError as e:
			return {"error": f"Invalid input format: {e}"}

		updated_listings = []

		for i, listing in enumerate(data.listingGuitars):
			image_messages = []

			for j in range(4):
				
				path = f"images/guitar_{i}/image_{j}.jpg"

				if not os.path.exists(path):
					print(f"Image not found at: {path}")
					updated_listings.append(listing.model_dump())
					continue

				with Image.open(path) as img:
					if img.mode in ("RGBA", "P"):
						img = img.convert("RGB")
					buffer = BytesIO()
					img.save(buffer, format="jpeg")
					buffer.seek(0)
					base64_image = base64.b64encode(buffer.read()).decode("utf-8")

				image_messages.append({
					"type": "image_url",
					"image_url": {
						"url": f"data:image/jpeg;base64,{base64_image}",
						"detail": "high"
					}
				})

			if not image_messages:
				print(f"No valid images found for listing {i}")
				updated_listings.append(listing.model_dump())
				continue
			
			print(f"Number of images given to gpt {len(image_messages)}")

			response = completion(
			model="gpt-4o",
			messages=[
				{
					"role": "user",
					"content": [
						{"type": "text", "text":( 
							f"The following guitar listing includes up to 4 images. "
    						f"The user-provided title for this guitar is: '{listing.Model}'. "
    						"Please analyze the images and provide the most accurate and specific make and model of the guitar. "
						)},
						*image_messages
					]
				}
			],
			max_tokens=300
			)

			updated_model = response["choices"][0]["message"]["content"]
			updated_listings.append({
                "Model": updated_model.strip(),
                "Price": listing.Price,
                "Condition": listing.Condition
            })
		
		return {
        "marketGuitars": [],  
        "listingGuitars": updated_listings
    	}
			
	@tool("comparison tool")
	def comparison_tool(listing_json: str) -> str:
		"""Takes a json including the all the data for the guitars. The tool then compares the prices
			and returns a string with the output of the comparisons"""
		
		try:
			# Convert the JSON string into a ListingJson object
			print("Incoming listing_json (type):", type(listing_json))
			listing_json = ListingJson.model_validate_json(listing_json)
		except ValidationError as e:
			return f"Error parsing input data: {e}"
		
		comparison = "Data post comparisons:\n"

		market_dict = {guitar.Model: guitar.Price for guitar in listing_json.marketGuitars}


		for listing in listing_json.listingGuitars:
			market_price = market_dict.get(listing.Model)

			if market_price:
				if listing.Price < market_price:
					comparison += (
						f"The listing price for {listing.Model} is better than the market value.\n"
						f"Listing value: {listing.Price}, Market value: {market_price}\n"
					)
				else:
					comparison += (
						f"The market price for {listing.Model} is better than the listing value.\n"
						f"Listing value: {listing.Price}, Market value: {market_price}\n"
					)
			else:
				comparison += f"No market data found for {listing.Model}.\n"
				
		return comparison

	@tool("email_sender_tool")
	def email_sender_tool(email_body: str) -> str:
		"""This tool takes in the body of an email and then composes and sends an email. 
			Returns a string saying it was successful or an error message"""
		msg = EmailMessage()
		msg.set_content(email_body)

		msg['Subject'] = "Guitar Comparisons"
		msg['From'] = email_address
		msg['To'] = email_address

		try:
			with smtplib.SMTP('smtp.gmail.com', 587) as server:
				server.ehlo()          # Identify with the server
				server.starttls()      # Secure the connection
				server.ehlo()          # Re-identify after starting TLS
				server.login(email_address, email_password)
				server.send_message(msg)
			return("Successfull")
		except Exception as e:
			return(f"An error occurred: {e}")
	
	@agent
	def facebook_listing_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['facebook_listing_agent'],
			# knowledge=[self.listing_source],
			tools=[self.scraper_tool],
			verbose=True,
			# llm=self.llm
		)
	
	@agent
	def img_comparison(self) -> Agent:
		return Agent(
			config=self.agents_config['img_comparison'],
			tools=[self.img_get_tool],
			verbose=True
		)
	
	@agent
	def market_value_finder(self) -> Agent:
		return Agent(
			config=self.agents_config['market_value_finder'],
			tools=[self.gc_scraper_tool],
			verbose=True,
		)
	
	@agent
	def comparison_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['comparison_agent'],
			tools=[self.comparison_tool, self.email_sender_tool],
			verbose=True,
			# llm=self.llm
		)

	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def listing_task(self) -> Task:
		return Task(
			config=self.tasks_config['listing_task'],
			output_model=ListingJson
		)
	

	@task
	def img_analyze_task(self) -> Task:
		return Task(
			config=self.tasks_config['img_analyze_task'],
			output_model=ListingJson
		)
	
	@task
	def market_task(self) -> Task:
		return Task(
			config=self.tasks_config['market_task'],
			output_model=ListingJson
		)
	
	@task
	def comparison_task(self) -> Task:
		return Task(
			config=self.tasks_config['comparison_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Crewaisimple crew"""

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			# process=Process.hierarchical,
			rules=["Agents may only use provided knowledge, tools, and memory"],
			verbose=True,
		)
