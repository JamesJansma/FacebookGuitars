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
import litellm
from litellm import completion


class GuitarData(BaseModel):
    Model: str
    Price: float
    Condition: str

class ListingJson(BaseModel):
    marketGuitars: List[GuitarData]  
    listingGuitars: List[GuitarData]  

@CrewBase
class Guitarmarket():
	"""GuitarMarketplace crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	vision_tool = VisionTool()

	# listing_read_tool = FileReadTool(file_path='src/crewaisimple/guitar_listings.csv')
	# market_read_tool = FileReadTool(file_path='src/crewaisimple/market_listings.csv')

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

	@tool("scraper tool")
	def scraper_tool() -> str:
		"""Does not take any input as it searches for guitars and then returns
			a listing of the guitars on the market place in the form of a json with \'Model\', \'Price\', and \'Condition\'"""
		os.makedirs("images", exist_ok=True)

		facebook_market_url = 'https://www.facebook.com/marketplace/spokane/search/?query=guitar&exact=false'
		login_url = "https://www.facebook.com/login/device-based/regular/login/"
		conditions = ['new']
		print("Scraper tool called")
		parsed = []
		with sync_playwright() as p:
			browser = p.chromium.launch(headless=True)
			page = browser.new_page()
			page.goto(login_url)
			time.sleep(2)
			try:
				# login(page)
				page.locator('input[name="email"]').type("",delay=150)
				time.sleep(2)
				page.wait_for_selector('input[name="pass"]').type("", delay=150)
				time.sleep(2)
				page.wait_for_selector('button[name="login"]').click()
				time.sleep(10)
				print("Login Completed")
			except:
				print("login failed")


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
					for i, listing in enumerate(listings):
						if i >= 2: continue
						try:
							title = listing.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6').text
							price = listing.find('span', 'x4zkp8e').text
							parsed.append({
									'Model': title,
									'Price': price.replace('$',''),
									'Condition' : condition
								})
							img_url = listing.find('img').get('src')
							
							img_data = requests.get(img_url).content
							
							with open(f"images/image_{i}.jpg", "wb") as img_file:
								img_file.write(img_data)
						except:
							pass
			browser.close()
			print("Finished scraper tool")
			return parsed

	@tool("gc scraper tool")
	def gc_scraper_tool(model: str) ->str:
		"""Takes in the name of the model of a guitar and then finds the first few results of that model from a 
			guitar store. The guitars are all new and the return value is a json with \'Model\',\'Price\', and \'Condition\'"""
		
		start_up_url = 'https://www.guitarcenter.com/'
		_model = model
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
				current_url = page.url
				current_url += '&filters=condition:New'
				page.goto(current_url)
				time.sleep(2)
				page.mouse.wheel(0,1500)

				parsed = []
				html = page.content()

				soup = BeautifulSoup(html, 'html.parser')
				listings = soup.find_all('div', class_='jsx-f0e60c587809418b plp-product-details px-[10px]')

				for listing in listings:
						title = listing.find('h2','jsx-f0e60c587809418b').text
						price = listing.find('span', 'jsx-f0e60c587809418b sale-price font-bold text-[#2d2d2d]').text
						parsed.append({
								'Model' : _model,
								'Price' : price,
								'Condition' : "new"
						})
						break
						
				time.sleep(3)
				browser.close
				return parsed

	@tool("image get tool")
	def img_get_tool(listing_json: str) -> dict:
		"""Takes in a json containing all of the guitar data and 
		uses GPT-4o to identify the guitar model from an image"""

		try:
			print("Incoming listing_json (type):", type(listing_json))
			data = ListingJson.model_validate_json(listing_json)
		except ValidationError as e:
			return {"error": f"Invalid input format: {e}"}

		updated_listings = []

		for i, listing in enumerate(data.listingGuitars):
			path = f"images/image_{i}.jpg"

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

			response = completion(
			model="gpt-4o",
			messages=[
				{
					"role": "user",
					"content": [
						{"type": "text", "text": f"What make and model is this guitar? Be specific. The name given with the guitar is '{listing.Model}' however it may be vague."},
						{
							"type": "image_url",
							"image_url": {
								"url": f"data:image/jpeg;base64,{base64_image}",
								"detail": "high"
							}
						}
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
			
	
	
	@agent
	def listing_finder(self) -> Agent:
		return Agent(
			config=self.agents_config['listing_finder'],
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
			tools=[self.comparison_tool],
			verbose=True,
			# llm=self.llm
		)

	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def listing_task(self) -> Task:
		return Task(
			config=self.tasks_config['listing_task'],
		)
	

	@task
	def img_analyze_task(self) -> Task:
		return Task(
			config=self.tasks_config['img_analyze_task'],
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
