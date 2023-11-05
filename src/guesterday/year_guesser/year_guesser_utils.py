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

def replace_symbols_with_spaces(text):
	pat = re.compile('[^\w^\-]')
	text = re.sub('[^\w^\-]', ' ', text)
	text = re.sub('[\W\s][\d\-]+[\W\s]', ' ', text)
	dashed = re.findall('\w+\-\w+', text)	
	dashed = ' '.join(dashed)
	dashed = re.sub('\-', ' ', dashed)
	text = text + ' ' + dashed
	text = re.sub(' +', ' ', text)
	return text

# check that atleast two of the words in lst_pre occur in string st
def two_in(st1, st2, limit=2):
	st1 = replace_symbols_with_spaces(st1.lower().strip())
	st2 = replace_symbols_with_spaces(st2.lower().strip())
	return two_in_helper(st1, st2, limit=limit) #and two_in_helper(st2, st1)

# check that atleast two of the words in lst_pre occur in string st
def two_in_helper(st1, st2,limit=2):
	st1_words_init = st1.split(' ')
	st2_words_init = st2.split(' ')
	
	count = 0 
	#limit = 2
	
	st1_words = filter_out_stopwords_punc(st1_words_init)
	st2_words = filter_out_stopwords_punc(st2_words_init)
	
	if len(st1_words) == 0 or len(st2_words) == 0:
		st1_words = st1_words_init
		st2_words = st2_words_init
	
	st1_words = remove_accents(st1_words)
	st2_words = remove_accents(st2_words)

	limit_ = min(len(st1_words), len(st2_words))
	if limit_ < limit:
		limit = limit_
	
	for word in st1_words:
		if word in st2_words:
			count += 1
	
	if count >= limit:
		return True
	else:
		return False

def two_in_artist_title(str1, str2):
	print(str1, str2)
	if str1.find(' - ') > -1 and str2.find(' - ') > -1:
		art1 = str1[:str1.find(' - ')]
		tit1 = str1[str1.find(' - ') + 3:]
		art2 = str2[:str2.find(' - ')]
		tit2 = str2[str2.find(' - ') + 3:]
		return two_in(art1, art2) and two_in(tit1, tit2)
	else:
		return two_in(str1, str2, limit=3)

		
def process_results_discogs(page1, title, fn, google_res=False,single=True):
	top_hits = 10
	lowest_seen_yr = 3000
	lowest_seen_item = None
	yr = -1
	count = -1
	item = None
	art1 = title[:title.find(' - ')]
	tit1 = title[title.find(' - ') + 3:]
	for i in page1:
		count += 1
		if 'year' in i.data:
			yr = int(i.data['year'])
			if yr < lowest_seen_yr and i != None:
				art2 = i.title[:i.title.find(' - ')]
				tit2 = i.title[i.title.find(' - ') + 3:]
				if single:
					if two_in(art1, art2) and two_in(tit1, tit2):
						lowest_seen_item = i
						lowest_seen_yr = yr
				else:
					if two_in(art1, art2):
						lowest_seen_item = i
						lowest_seen_yr = yr
			if count >= top_hits:
				break
	
	item = lowest_seen_item
	yr = lowest_seen_yr
	if yr == 3000:
		yr = -1
	
	lbl = None
	
	if yr != -1:
		if 'label' in item.data.keys():
			lbl = item.data['label'][0]
			words = lbl.split()
			if len(words) > 3:
				words = words[0:3]
			lbl = ' '.join(words)
		fn = rename(fn, yr, lbl)
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
