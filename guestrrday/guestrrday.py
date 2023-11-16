from datetime import datetime
import discogs_client
import yaml
import time
import os

from guestrrday.track import track
from guestrrday import utils

D_CLIENT = None

def guess(input):
	if os.path.exists(input):
		if os.path.isfile(input):
			guess_by_tracklist(input)
		else:
			guess_by_dir(input)
			
			
def guess_track(track):
	title = track.get_title()
	fn = track.get_filename_path()

	#####
	# first attempt: search for track as a single
	#####
	
	page1 = search_and_get_results(title, type='release', format="Single|12''|10''|7''", sort='year,asc')
	results = convert_discogs_results(page1)
	res1 = utils.get_earliest_matching_hit(results, title, fn)


	####################
	# second attempt: singles but drop anything between brackets (mix name typically)
	####################
			
	# from 'Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
	title = utils.get_base_title(title)
	
	page1 = search_and_get_results(title, type='release', format="Single|12''|10''|7''", sort='year,asc')
	results = convert_discogs_results(page1)
	res2 = utils.get_earliest_matching_hit(results, title, fn)


	####################
	# third attempt: any 'kind' of release (albums, compilations by the artist, note that 'various artist' compilations are not considered). Plus no mix name
	####################
			
	# from 'Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
	title = utils.get_base_title(title)
			
	page1 = search_and_get_results(title, type='release', format='', sort='year,asc')
	results = convert_discogs_results(page1)
	res3 = utils.get_earliest_matching_hit(results, title, fn, single=False)


	####################
	# Fourth attempt: Try to add a 'The' before artists (hack for discogs search engine) or remove it if it exists
	####################
	
	# title = title.lower()
	# if title.find('the') == -1:
		# title = 'the ' + title
	# else:
		# title = title.replace('the', '')
	
	#page1 = search_and_get_results(title, type='release', format='', sort='year,asc')
	#results = convert_discogs_results(page1)
	#yr_res = utils.get_earliest_matching_hit(results, title, fn, single=False)
	
	return get_min_index(res1, res2, res3)
		
		
def guess_by_dir(dirpath, format='standard_plus_label'):
	files = os.listdir(dirpath)
	for fn in files:
		tr = track( os.path.join(dirpath, fn) )
		res = guess_track(tr)
		if res is not None:
			yr = res[0]
			lbl = res[1]
			new_name = utils.rename(os.path.join(dirpath, fn), yr, lbl, format='standard_plus_label')
			print(new_name)
		else:
			print(os.path.join(dirpath, fn))
			
def guess_by_tracklist(trklst, format='standard_plus_label'):		
	out  = ''
	with open(trklst, encoding='utf8') as f:
		for line in f:
			line = line.strip()
			if line == '' or line[0] == '#':
				out += f'{line}\n' 
				continue
			tr = track(line)
			res = guess_track(tr)
			if res is not None:
				yr = res[0]
				lbl = res[1]
				new_title = utils.format_output(tr.get_full_title(), yr, lbl, format='standard_plus_label')
				out += f'{new_title}\n'
				print(new_title)
			else:
				print(tr.get_full_title())
	
	outfile = trklst + '-guessed'
	if trklst.find('.') > -1:
		outfile = trklst[:trklst.rfind('.')] + '-guessed' + trklst[trklst.rfind('.'):]
	with open(outfile, 'w', encoding='utf8') as f:
		f.write(out)
	f.close()
	

def search_and_get_results(title, format, type, sort, first=True):
	time.sleep( 1 )
	global D_CLIENT 
	if D_CLIENT is None:
		D_CLIENT = discogs_client.Client('ExampleApplication/0.1', user_token=load_config().get('discogs_user_token'))
	page1 = None
	results = D_CLIENT.search(title, type=type, format=format, sort=sort)
	try:
		page1 = results.page(1)
	except discogs_client.exceptions.HTTPError as e:
		print(e)
		time.sleep( 60 )
		return search_and_get_results(title, format, type, sort, first=False)
	return page1


def get_min_index(*args):
	idx_mn = -1
	mn = 9999
	idx = 0
	for i in args:
		if i != None and i[0] < mn:
			idx_mn = idx
			mn = i[0]
		idx += 1
	if idx_mn != -1:
		return args[idx_mn]
		
		
def load_config():
	con = None
	if os.path.isfile('.\\guestrrday\\config.yaml'):
		with open('.\\guestrrday\\config.yaml', 'r') as stream:
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
			