import os
import time
#import mutagen
#import nltk
import re
#import google 
from nltk.corpus import stopwords
import string
import unidecode
#from PIL import Image
#import shutil
#import urllib

debug = False

def get_base_title(title):
	dash_idx = title.find(' - ')
	idx = title.find('[', dash_idx)
	if idx > -1:
		title = title[0:idx]

	idx = title.find('(', dash_idx)
	if idx > -1:
		title = title[0:idx]
	
	tsplit = title.split(' - ')
	if len(tsplit) == 2:
		[artist, tit] = tsplit
		artist = artist.replace(',', ' & ')
		artist = artist.replace(';', ' & ')
		artist = artist.replace(' with ', ' & ')
		temp_artist = artist.split('&')[0].strip()		
		if len(temp_artist.split(' ')) > 1:
			artist = temp_artist
		title = artist + ' - ' + tit
	
	return title

def remove_blacklist_chars(fn):
	os_blacklist = '\\/:*?"<>|'
	fn = fn.replace('"',"'")
	return ''.join([letter for letter in fn if not (letter in os_blacklist)])	

def filter_out_stopwords_punc(lst):
	return [word for word in lst if not (word in stopwords.words('english') or word in string.punctuation or len(word) < 2) ]

def remove_accents(lst):
	return [unidecode.unidecode(word) for word in lst]

# check that atleast two of the words in lst_pre occur in string st
def two_in(lst_pre, st):
	return two_in_helper(lst_pre, st) or two_in_helper(st.split(' '), ' '.join(lst_pre))

# check that atleast two of the words in lst_pre occur in string st
def two_in_helper(lst_pre, st, first=True):
	count = 0 
	limit = 2
	lst = filter_out_stopwords_punc(lst_pre)
	st_temp = filter_out_stopwords_punc(st.split(' '))
	if len(st_temp) > 0:
		st = ' '.join(st_temp)
	
	lst2 = []
	for w in lst:
		unaccented_string = unidecode.unidecode(w)
		lst2.append(unaccented_string)
	lst=lst2
	st = unidecode.unidecode(st)

	len_lst = len(lst)

	if len_lst == 0:
		lst = lst_pre
	if len_lst <= limit:
		if len_lst == 2:
			limit = 2
		else:
			limit = len_lst - 1
		if limit == 0:
			limit = 1
						
	num_of_words_in_result = len(st.split(' '))
	if limit > num_of_words_in_result:
		limit = num_of_words_in_result
	
	for word in lst:
		word = word.lower()
		stl = st.lower() + ' '
		if len(word) < 3:
			word = word + ' '
		if stl.find(word) > -1:
			count = count + 1
		if count >= limit:
			return True
			
	if first == True and len(lst) < 3:
		new_lst = []
		for poss_acronym in lst:
			if poss_acronym.find('.') > -1 and len(poss_acronym) < 9:
				poss_acronym = poss_acronym.replace('.','')
				new_lst.append(poss_acronym)
			elif poss_acronym.find('.') == -1 and len(poss_acronym) < 5:
				ls = list(poss_acronym)
				ac = '.'.join(ls) + '.'
				new_lst.append(ac) 
		return two_in_helper(new_lst, st, False)
	return False

def process_results_discogs(page1, base_title, fn, year_mn, year_mx, google_res=False, inc_compilations=False):
	global debug
	if len(page1) == 0:
		if debug:
			print('no search results')
		return -1
	
	yr = -1
	item = None
	for i in page1:
#		print(i.images)
		if 'year' in i.data:
			yr = int(i.data['year'])
			item = i
			if yr >= year_mn and yr <= year_mx:
				break
	
#	yr = int(item.data['year'])

	if yr < year_mn or yr > year_mx:
		if debug:	 
			print('Year out of range: ', yr)
		return -1
	
	# from 'Puff Daddy - I will always love you (Abas remix)' => ['puff', 'daddy', '']
	artist_keywords = base_title.split(' - ')[0]
	artist_keywords= re.split("\. |,|-|'|&\*", artist_keywords)

	tit = item.title
	tit = tit.replace('*', '')
	
	if tit.find(' - ') > -1:
		tit = tit.split(' - ')[0]
		tit = ' '.join(re.split("\. |,|-|'|&\*", tit))
		
	if google_res == False and inc_compilations == False:
		if not(two_in(artist_keywords, tit)):
			if debug:
				print('artist keywords not in result')
				print('({}=>{})'.format(' '.join(artist_keywords), tit))
			return -1
	
	lbl = None

	if 'label' in item.data.keys():
		lbl = item.data['label'][0]
		words = lbl.split()
		if len(words) > 3:
			words = words[0:3]
		lbl = ' '.join(words)
	
	if yr != -1:
		fn = rename(fn, yr, lbl)
	else:
		if debug:
			print('No Year')
	return yr

def rename(fn, yr=0, label=None, format='standard_plus_label'):
	if yr == 0 and label == None:
		return fn
	path = '.'
	if os.path.basename(fn) != fn:
		path = os.path.dirname(fn)
		fn = os.path.basename(fn)
		
	ext_idx = fn.rfind('.')
	base_fn = fn[ 0 : ext_idx ]
	ext = fn[ ext_idx + 1 : ]
	
	if format == 'standard_plus_label':
		if label == None:
			base_fn = '{} ({})'.format(base_fn , yr)
		elif yr == 0:
			base_fn = '{} ({})'.format(base_fn , label)		
		else:
			base_fn = '{} ({}, {})'.format(base_fn , label, yr)
	elif format == 'standard':
		if yr == 0:
			return fn
		else:
			base_fn = '{} ({})'.format(base_fn , yr)
	else:
		# the guesterday chronological format
		base_fn = '{} -- {} {{{}}}'.format(yr, base_fn , label)		
		
	new_fn = "{}.{}".format(base_fn, ext)
		
	try:
		os.rename( os.path.join(path, fn), os.path.join(path, new_fn) )
	except Exception as e:
		print(e)
		try:
			new_fn = remove_blacklist_chars(new_fn)
			os.rename( os.path.join(path, fn), os.path.join(path, new_fn) )
		except Exception as e:
			print(e)
			return
			
	return new_fn
