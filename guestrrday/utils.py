import os
import time
import re
from nltk.corpus import stopwords
import string
import unidecode

def has_music_ext(fn):
	ext_idx = fn.rfind('.')
	if ext_idx > -1:
		ext = fn[ext_idx + 1:]
		#f_char = ext[0]
		audio_ext_list = ['mp3', 'flac', 'm4a', 'ogg', 'opus', 'wav', 'wma', 'aif', 'aiff']
		if ext in audio_ext_list:
			return True
	return False	
	
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
	pat = re.compile(r'[^\w^\-]')
	text = re.sub(r'[^\w^\-]', ' ', text)
	text = re.sub(r'[\W\s][\d\-]+[\W\s]', ' ', text)
	dashed = re.findall(r'\w+\-\w+', text)	
	dashed = ' '.join(dashed)
	dashed = re.sub(r'\-', ' ', dashed)
	text = text + ' ' + dashed
	text = re.sub(' +', ' ', text)
	return text

# check that atleast two of the words in lst_pre occur in string st
def two_in(st1, st2, limit=2):
	st1 = replace_symbols_with_spaces(st1.lower().strip())
	st2 = replace_symbols_with_spaces(st2.lower().strip())
	
	st1_words = filter_out_stopwords_punc(st1.split(' '))
	st2_words = filter_out_stopwords_punc(st2.split(' '))
	
	if len(st1_words) == 0 or len(st2_words) == 0:
		st1_words = st1_words_init
		st2_words = st2_words_init
	
	st1_words = remove_accents(st1_words)
	st2_words = remove_accents(st2_words)

	limit = min(len(st1_words), len(st2_words), limit)
	
	intersection = len(set(st1_words) & set(st2_words))

	return intersection >= limit
	
def get_earliest_matching_hit(hits, title, fn, top_hits = 10, google_res=False,single=True):
	num_of_words_to_accept = 1
	if single:
		num_of_words_to_accept = 4

	hits = [h for h in hits if h is not None and h.get('year') is not None]
	hits = hits[0 : top_hits - 1]
	hits.sort(key=lambda i: int(i.get('year')))
	 
	for h in hits:
		if two_in(title, h.get('title'), num_of_words_to_accept):
			lbl = h.get('label')
			if lbl != None:
				words = lbl.split()[:3]
				lbl = ' '.join(words)
			yr = int(h.get('year'))
			return (yr, lbl)

def format_output(title, yr=None, label=None, format='standard_plus_label'):
	if yr == None or yr == -1:
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
			
	return os.path.join(path, new_fn)
