from startpage import StartPage
import pytube
import requests
import time
import yaml
import os.path
	
class search_engine:	
	
	def __init__(self, engine_name, sleeptime = 20):
		engine_name = engine_name.lower()
		if engine_name != 'google' and engine_name != 'startpage' and  engine_name != 'youtube':
			raise Exception("Illegal search_object type. Allowed: 'Google' or 'StartPage' or 'YouTube' (not case sensitive)")
		self.engine_name = engine_name
		self.sleeptime = sleeptime
		if engine_name == 'google':
			con = load_config()
			self.api_keys = con.get('api_keys')
			self.search_engine_ids = con.get('search_engine_ids')
			self.quota_user = con.get('quota_user')
			self.id_indx = 0
	
	def search_startpage(self, query):
		results = []
		task = StartPage()
		task.search(query,page=1)
		python_results = task.results['1']
		#python_results.extend(task.results['2'])
		for search_item in python_results:
			if search_item:
				title = search_item.get("title")
				link = search_item.get("link")
				snippet = ''
				item = {'title': title, 'link': link, 'snippet': snippet}
				results.append(item)
		time.sleep( self.sleeptime )
		return results
	
	
	def search_google(self, query):
		corrected = None
		results = []

		# using the first page
		page = 1
		# see https://developers.google.com/custom-search/v1/using_rest
		start = (page - 1) * 10 + 1
		url = f"https://www.googleapis.com/customsearch/v1?key={self.api_keys[self.id_indx]}&cx={self.search_engine_ids[self.id_indx]}&q={query}&start={start}&QuotaUser={self.quota_user}"
		data = requests.get(url).json()

		if 'error' in data and data['error']['code'] == 429:			
			if self.id_indx == min(len(self.search_engine_ids), len(self.api_keys)):
				raise Exception('I am getting error code 429 from google, limit exceeded, add more apis keys / search engine ids or get more quota.')
			else:
				self.id_indx += 1
				time.sleep( self.sleeptime )
				return self.search_google(query)				

		if 'spelling' in data and 'correctedQuery' in data['spelling']:
			corrected = data['spelling']['correctedQuery']

		search_items = data.get("items")
		if search_items == None and corrected != None:
			return search_google(corrected)
		
		for i, search_item in enumerate(search_items, start=1):
			title = search_item.get("title")
			snippet = search_item.get("snippet")
			link = search_item.get("link")
			item = {'title': title, 'link': link, 'snippet': snippet}
			results.append(item)
		time.sleep( self.sleeptime )
		return results
		

	def search_youtube(self, query):
		results = []
		s = pytube.Search(query)
		search_items = s.results
		for search_item in search_items:
			title = search_item.title
			snippet = search_item.description
			link = search_item.watch_url
			item = {'title': title, 'link': link, 'snippet': snippet}
			results.append(item)
		return results


	
	def search(self, query):
		if self.engine_name == 'google':
			return self.search_google(query)
		elif self.engine_name == 'startpage':
			return self.search_startpage(query)
		elif self.engine_name == 'youtube':
			return self.search_youtube(query)
			



def load_config():
	con = None
	if os.path.isfile('.\\src\\guesterday\\config.yaml'):
		with open('.\\src\\guesterday\\config.yaml', 'r') as stream:
			try:
				con = yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)
	if con == None:
		raise Exception("No 'config.yaml' found or is empty.")

	api_keys = con.get('api_keys')
	search_engine_ids = con.get('search_engine_ids')
	quota_user = con.get('quota_user')
	
	if api_keys == None or search_engine_ids == None or quota_user == None:
		raise Exception("You must provide one or more API keys and one or more Search Engine IDs and a quota user ID inside 'config.yaml' to initialize a google search_engine.")

	if type(api_keys) != list:
		con['api_keys'] = [api_keys]
	if type(search_engine_ids) != list:
		con['search_engine_ids'] = [search_engine_ids]
	return con
			