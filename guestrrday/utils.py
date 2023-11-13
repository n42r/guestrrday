import os
import time
import re
from nltk.corpus import stopwords
import string
import unidecode


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
def two_in_helper(st1, st2, limit=2):
	st1_words_init = st1.split(' ')
	st2_words_init = st2.split(' ')
	
	count = 0 
	
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
	
def get_earliest_matching_hit(hits, title, fn, google_res=False,single=True):
	top_hits = 10
	lowest_seen_yr = 3000
	lowest_seen_item = None
	yr = -1
	count = -1
	item = None
	for i in hits:
		count += 1
		if yr == None or i.get('year') == None:
			continue
		yr = int(i.get('year'))
		if yr < lowest_seen_yr:
			if single:
				if two_in(i.get('title'), title, 4):
					lowest_seen_item = i
					lowest_seen_yr = yr	
			else:
				lowest_seen_item = i
				lowest_seen_yr = yr	
		if count >= top_hits:
			break
			
	
	item = lowest_seen_item
	yr = lowest_seen_yr
	
	if yr == -1 or yr == 3000 or item == None:
		return None
	
	lbl = item.get('label')
	if lbl != None:
		words = lbl.split()
		if len(words) > 3:
			words = words[0:3]
		lbl = ' '.join(words)
	return (yr, lbl)

def format_output(title, yr=-1, label=None, format='standard_plus_label'):
	if yr == -1 and label == None:
		return title
	new_title = ''
	if format == 'standard_plus_label' and label == None:
		format = 'standard'
	if format == 'standard_plus_label':
		new_title = '{} ({}, {})'.format(title , label, yr)
	elif format == 'standard':
		new_title = '{} ({})'.format(title , yr)
	else:
		# the guesterday chronological format
		new_title = '{} -- {} {{{}}}'.format(yr, title , label)
	return new_title


def rename(fn, yr=-1, label=None, format='standard_plus_label'):
	path = '.'
	if os.path.basename(fn) != fn:
		path = os.path.dirname(fn)
		fn = os.path.basename(fn)
		
	ext_idx = fn.rfind('.')
	base_fn = fn[ 0 : ext_idx ]
	ext = fn[ ext_idx + 1 : ]
	
	base_fn = format_output(base_fn, yr, label, format)
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
