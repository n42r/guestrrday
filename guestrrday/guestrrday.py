from datetime import datetime
import discogs_client
import yaml
import time
import os

from guestrrday.track import track, tracklist
from guestrrday import utils

D_CLIENT = None

			
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
	
	ls = [i for i in [res1,res2,res3] if i is not None]
	if len(ls) > 0:
		mn = min(ls, key=lambda t: t[0])
		track.year = mn[0]
		track.label = mn[1]
	return track


def guess(input, format='standard_plus_label'):
	tl = tracklist(location=input)
	tl.fill()
	for tr in tl:
		guess_track(tr)
		print(tr.year)
		print(tr.label)
		new_name = utils.format_output(tr.get_full_title(), tr.year, tr.label, format='standard_plus_label')
		tr.set_new_name(new_name)
		print(tr.get_new_name())
	return flush_results(tl)
	
def flush_results(tl):
	if tl.type == 'dir':
		rename_tracks(tl)
	elif tl.type == 'file':
		writeout_tracklist(tl)
	else:
		return [tr.get_new_name() for tr in tl]
	
def rename_tracks(tl):
	for tr in tl:
		if tr.year != None:
			utils.rename(tr.get_filename_path(), tr.year, tr.label)

def writeout_tracklist(tl):
	ext = tl.location[tl.location.rfind('.'):]
	base_name = tl.location[:tl.location.rfind('.')]
	if '.' not in tl.location:
		ext = ''
		base_name = tl.location
	outfile = f'{base_name}-guessed.{ext}'
	out = [tr.get_new_name() for tr in tl ]
	with open(outfile, 'w', encoding='utf8') as f:
		f.write('\n'.join(out))
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
			