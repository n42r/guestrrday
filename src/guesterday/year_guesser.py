from datetime import datetime
import discogs_client
import yaml
import time
import os

from guesterday.track import track
from guesterday import year_guesser_utils

class year_guesser:
	def __init__(self):
		con = load_config()		
		self.discogs_user_token = con.get('discogs_user_token')
		self.d_client = discogs_client.Client('ExampleApplication/0.1', user_token=self.discogs_user_token)

	def get_by_release_id(self, id):
		pass

	def search_and_get_results(self, title, format, type, sort, first=True):
		time.sleep( 1 )
		page1 = None
		results = self.d_client.search(title, type=type, format=format, sort=sort)
		try:
			page1 = results.page(1)
		except discogs_client.exceptions.HTTPError as e:
			print(e)
			time.sleep( 60 )
			return self.search_and_get_results(title, format, type, sort, first=False)
		return page1
	
	def guess(self, track):
		res = self.guess_(track)
		fn = track.get_filename_path()
		tit = track.get_title()
		if res == None or res[0] == -1:
			print('Year => ????: {}'.format(fn))
			return None
		
		yr = res[0]
		lbl= res[1]		
		
		print('Year => {}: {}'.format(yr, fn))
		if fn != None:
			year_guesser_utils.rename(fn, yr, lbl)
		return res
		
		
	def guess_(self, track):
		title = track.get_title()
		fn = track.get_filename_path()
		
		#####
		# first attempt: search for track as a single
		#####
		
		page1 = self.search_and_get_results(title, type='release', format="Single|12''|10''|7''", sort='year,asc')
		results = convert_discogs_results(page1)
		yr_res = year_guesser_utils.get_earliest_matching_hit(results, title, fn)
		if yr_res != None:
			return yr_res
			

		####################
		# second attempt: singles but drop anything between brackets (mix name typically)
		####################
				
		# from 'Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
		title = year_guesser_utils.get_base_title(title)
		
		page1 = self.search_and_get_results(title, type='release', format="Single|12''|10''|7''", sort='year,asc')
		results = convert_discogs_results(page1)
		yr_res = year_guesser_utils.get_earliest_matching_hit(results, title, fn)
		if yr_res != None:
			return yr_res


		####################
		# third attempt: any 'kind' of release (albums, compilations by the artist, note that 'various artist' compilations are not considered). Plus no mix name
		####################
				
		# from 'Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
		title = year_guesser_utils.get_base_title(title)
				
		page1 = self.search_and_get_results(title, type='release', format='', sort='year,asc')
		results = convert_discogs_results(page1)
		yr_res = year_guesser_utils.get_earliest_matching_hit(results, title, fn, single=False)
		if yr_res != None:
			return yr_res

			
		####################
		# Fourth attempt: Try to add a 'The' before artists (hack for discogs search engine) or remove it if it exists
		####################
		
		# title = title.lower()
		# if title.find('the') == -1:
			# title = 'the ' + title
		# else:
			# title = title.replace('the', '')
		
		#page1 = self.search_and_get_results(title, type='release', format='', sort='year,asc')
		#results = convert_discogs_results(page1)
		#yr_res = year_guesser_utils.get_earliest_matching_hit(results, title, fn, single=False)
		# if yr_res != None:
			# return yr_res
		
		return None
		
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

def convert_discogs_results(page):
	res = []
	for i in page:
		item = {}
		if i == None:
			continue
		item['year']  = i.data.get('year')
		item['title'] = i.title
		item['label'] = i.data.get('label')[0]
		res.append(item)
	return res
			