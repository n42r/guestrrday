from datetime import datetime
import discogs_client
import yaml
import time
import os

from roeld import track, discogs_guesser_utils

class discogs_guesser:
	def __init__(self, year_mn=1910, year_mx=datetime.now().year, inc_compilations=False):
		self.year_mn = year_mn
		self.year_mx = year_mx
		self.inc_compilations = inc_compilations
		self.decade = ''
		if year_mx - year_mn == 9 and year_mn % 10 == 0:
			self.self.decade = year_mn
		con = load_config()
		self.discogs_user_token = con.get('discogs_user_token')
		self.d_client = discogs_client.Client('ExampleApplication/0.1', user_token=self.discogs_user_token)

	def get_by_release_id(self, id):
		pass
		
	def get_page_one(self, results):
		time.sleep( 2 )
		page1 = None
		try:
			page1 = results.page(1)
		except Exception as e:
			print(e)
			time.sleep( 60 )
		return page1
	
	def print_and_return(self, fn, yr):
		if yr > -1:
			print('Year => {}: {}'.format(yr, os.path.basename(fn)))
		else:
			print('Year => ????: {}'.format(os.path.basename(fn)))
		return yr
		

	def guess(self, track):
		
		#####
		# first attempt: search for track as a single
		#####
		
		title = track.get_title()
		fn = track.get_filename_path()
		
		for i in [1,2]:
			results = self.d_client.search(title, type='release', format="Single|12''|10''|7''", sort='year,asc', decade=self.decade)
			page1 = self.get_page_one(results)
			if page1 != None:
				break
		
		yr_res = discogs_guesser_utils.process_results_discogs(page1, title, fn, self.year_mn, self.year_mx, inc_compilations=self.inc_compilations)
		if yr_res != -1:
			return self.print_and_return(fn, yr_res)
			


		####################
		# second attempt: any 'kind' of release (albums, compilations) + remove all text after brackets (usually mix name)
		####################
				
		# from 'Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
		base_title = discogs_guesser_utils.get_base_title(title)
		
		for i in [1,2]:
			results = self.d_client.search(base_title, type='release', sort='year,asc', decade=self.decade)
			page1 = self.get_page_one(results)
			if page1 != None:
				break
				
		yr_res = discogs_guesser_utils.process_results_discogs(page1, base_title, fn, self.year_mn, self.year_mx, inc_compilations=self.inc_compilations)
		if yr_res != -1:
			return self.print_and_return(fn, yr_res)

			
		####################
		# third attempt: Try to add a 'The' before artists (hack for discogs search engine) or remove it if it exists
		####################
		
		base_title = base_title.lower()
		if base_title.find('the') == -1:
			base_title = 'the ' + base_title
		else:
			base_title = base_title.replace('the', '')

		for i in [1,2]:
			results = self.d_client.search(base_title, type='release', sort='year,asc', decade=self.decade)
			page1 = self.get_page_one(results)
			if page1 != None:
				break

		yr_res = discogs_guesser_utils.process_results_discogs(page1, base_title, fn, self.year_mn, self.year_mx, inc_compilations=self.inc_compilations)
		if yr_res != -1:
			return self.print_and_return(fn, yr_res)
		
		return self.print_and_return(fn, -1)
		
	def guess_by_dir(self, dirpath):
		files = os.listdir(dirpath)
		for fn in files:
			tr = track.track( os.path.join(dirpath, fn) )
			#print(tr.title)
			self.guess(tr)

	
def load_config():
	con = None
	if os.path.isfile('.\\roeld\\config.yaml'):
		with open('.\\roeld\\config.yaml', 'r') as stream:
			try:
				con = yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)
	if con == None:
		raise Exception("No 'config.yaml' found or is empty.")
	
	if con.get('discogs_user_token') == None:
		raise Exception("You must provide a discogs_user_token inside 'config.yaml' to use discogs functions.")
	return con
			