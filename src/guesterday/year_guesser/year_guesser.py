from datetime import datetime
import discogs_client
import yaml
import time
import os

from guesterday.track import track
from guesterday.year_guesser import year_guesser_utils

class year_guesser:
	def __init__(self, year_mn=1910, year_mx=datetime.now().year):
		self.year_mn = year_mn
		self.year_mx = year_mx
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
	
	def search_and_get_results(self, title, format, type, sort):
		for i in [1,2]:
			results = self.d_client.search(title, type=type, format=format, sort=sort, decade=self.decade)
			page1 = self.get_page_one(results)
			if page1 != None:
				break
		return page1
	
	def print_and_return(self, fn, title, yr):
		if fn == None:
			fn = title
		if yr > -1:
			print('Year => {}: {}'.format(yr, fn))
		else:
			print('Year => ????: {}'.format(fn))
		return yr
	
	def guess(self, track):
		title = track.get_title()
		fn = track.get_filename_path()
		
		#####
		# first attempt: search for track as a single
		#####
		
		page1 = self.search_and_get_results(title, type='release', format="Single|12''|10''|7''", sort='year,asc')
		
		yr_res = year_guesser_utils.process_results_discogs(page1, title, fn, self.year_mn, self.year_mx)
		if yr_res != -1:
			return self.print_and_return(fn, title, yr_res)
			

		####################
		# second attempt: singles but drop anything between brackets (mix name typically)
		####################
				
		# from 'Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
		title = year_guesser_utils.get_base_title(title)
		
		page1 = self.search_and_get_results(title, type='release', format="Single|12''|10''|7''", sort='year,asc')
		
		yr_res = year_guesser_utils.process_results_discogs(page1, title, fn, self.year_mn, self.year_mx)
		if yr_res != -1:
			return self.print_and_return(fn, title, yr_res)


		####################
		# third attempt: any 'kind' of release (albums, compilations by the artist, note that 'various artist' compilations are not considered). Plus no mix name
		####################
				
		# from 'Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
		title = year_guesser_utils.get_base_title(title)
				
		page1 = self.search_and_get_results(title, type='release', format='', sort='year,asc')
				
		yr_res = year_guesser_utils.process_results_discogs(page1, title, fn, self.year_mn, self.year_mx, single=False)
		if yr_res != -1:
			return self.print_and_return(fn, title, yr_res)

			
		####################
		# Fourth attempt: Try to add a 'The' before artists (hack for discogs search engine) or remove it if it exists
		####################
		
		# title = title.lower()
		# if title.find('the') == -1:
			# title = 'the ' + title
		# else:
			# title = title.replace('the', '')
		
		#page1 = self.search_and_get_results(title, type='release', format='', sort='year,asc')

		# yr_res = year_guesser_utils.process_results_discogs(page1, title, fn, self.year_mn, self.year_mx, inc_compilations=self.inc_compilations)
		# if yr_res != -1:
			# return self.print_and_return(fn, title, yr_res)
		
		return self.print_and_return(fn, title, -1)
		
	def guess_by_dir(self, dirpath):
		files = os.listdir(dirpath)
		for fn in files:
			tr = track.track( os.path.join(dirpath, fn) )
			#print(tr.title)
			self.guess(tr)
		
def load_config():
	con = None
	if os.path.isfile('.\\guesterday\\config.yaml'):
		with open('.\\guesterday\\config.yaml', 'r') as stream:
			try:
				con = yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)
	if con == None:
		raise Exception("No 'config.yaml' found or is empty.")
	
	if con.get('discogs_user_token') == None:
		raise Exception("You must provide a discogs_user_token inside 'config.yaml' to use discogs functions.")
	return con
			