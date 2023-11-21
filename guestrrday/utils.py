import os
import re
from nltk.corpus import stopwords
import string
import unidecode

def has_music_ext(fn):
	"""Check if a filename has a music related extension.
	
	Args:
		fn (str): filename
		
	Returns:
		bool: True if has a music extension and False otherwise
	"""

	ext_idx = fn.rfind('.')
	if ext_idx > -1:
		ext = fn[ext_idx + 1:]
		#f_char = ext[0]
		audio_ext_list = ['mp3', 'flac', 'm4a', 'ogg', 'opus', 'wav', 'wma', 'aif', 'aiff']
		if ext in audio_ext_list:
			return True
	return False	
	
def get_base_title(title):
	"""Given an title of a song (Artist - song title) strip any strings between brackets (usually mix names)

	Example:
		Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'
	
	Args:
		title (str): The full song title
	
	Returns:
		str: The stripped song title
	"""

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
	"""Sanitise strings that will be used as filenames on the OS
	
	Args:
		fn (str): The unsanitised filename
	
	Returns:
		str: The sanitised filename
	"""
	os_blacklist = '\\/:*?"<>|'
	fn = fn.replace('"',"'")
	return ''.join([letter for letter in fn if not (letter in os_blacklist)])	

def filter_out_stopwords_punc(lst):
	"""Sanitize text for search be removing common english stopwords as well as punctuation
	
	Args:
		lst (list): A list of words, resulting fron a string split() by spaces
	
	Returns:
		list: A subset of the args with stopwords and punc elements removed
	"""
	return [word for word in lst if not (word in stopwords.words('english') or word in string.punctuation or len(word) < 2) ]

def remove_accents(lst):
	"""Simplify accented letters to the base letters used in english
	Args:
		lst (list): A list of words, resulting fron a string split() by spaces
	
	Returns:
		list: The list of words with all accents removes
	"""
	return [unidecode.unidecode(word) for word in lst]

def replace_symbols_with_spaces(text):
	"""Another search aid, remove symbols from search text
	Args:
		text (str): Pre-Search text
	
	Returns:
		str: Text with all symbols removed
	"""
	text = re.sub(r'[^\w^\-]', ' ', text)
	text = re.sub(r'[\W\s][\d\-]+[\W\s]', ' ', text)
	dashed = re.findall(r'\w+\-\w+', text)	
	dashed = ' '.join(dashed)
	dashed = re.sub(r'\-', ' ', dashed)
	text = text + ' ' + dashed
	text = re.sub(' +', ' ', text)
	return text


def two_in(st1, st2, limit=2):
	"""Check that atleast X of the words in the first param occur in the second param
	
	Args:
		st1 (str): The source string
		st2 (st2): The destination string
		limit (int): This is the X number of token in the first arg that must occur in the second one. Default is 2, hence the name of the func
	
	Returns:
		bool: True if condition of function is met, and False otherwise
	"""
	st1 = replace_symbols_with_spaces(st1.lower().strip())
	st2 = replace_symbols_with_spaces(st2.lower().strip())
	
	st1_words = filter_out_stopwords_punc(st1.split(' '))
	st2_words = filter_out_stopwords_punc(st2.split(' '))
	
	if len(st1_words) == 0 or len(st2_words) == 0:
		st1_words = st1
		st2_words = st2
	
	st1_words = remove_accents(st1_words)
	st2_words = remove_accents(st2_words)

	limit = min(len(st1_words), len(st2_words), limit)
	
	intersection = len(set(st1_words) & set(st2_words))

	return intersection >= limit
	
def get_earliest_matching_hit(hits, title, top_hits = 10, google_res=False,single=True):
	"""Given a result set, get the the hit that includes the search terms that has the earliest release date.
	
	The earliest because many music usually get reissued in a later date, and whenever possible we would like to avoid reissue dates because they are typically far from the originally release date.
	
	Args:
		hits (list): List of dicts including results
		title (str): The original search term
		top_hits (int): The number of hits to look into before returning a result (default 10)
		google_res (bool): Used in an earlier version of this tool, but that feature is currently frozen (planned for the future). So not used currently
		single (bool): Important flag because in case of a single we have to match the artist and title, but otherwise we try to do a simpler and less constraning match. See guestrrday.discogs_guess_track function for more info.
	
	Returns:
		tuple: First element is the year and the second is the label. If not found, it returns None
	"""
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

def format_output(title, yr=None, label=None, form='standard_plus_label'):
	"""Given the found year and label format the full song title adding to it the new info. There are three formats supported.
	
	Args:
		title (str): The original full song title.
		yr (int): The guessed year 
		lable (str): The guessed record label
		form (str): Enum of three different formats. "standard_plus_label" (default) appends (year, label) to the end of the song title, "standard" drops the label, and [anything else] it uses a format I personally used in the past: "YYYY -- FULL-SONG-TITLE {Label}"
	
	Returns:
		str: The formated name
	"""
	if yr == None or yr == -1:
		return title
	new_title = ''
	if form == 'standard_plus_label' and label == None:
		form = 'standard'
	if form == 'standard_plus_label':
		new_title = '{} ({}, {})'.format(title , label, yr)
	elif form == 'standard':
		new_title = '{} ({})'.format(title , yr)
	else:
		# the guesterday chronological format
		new_title = '{} -- {} {{{}}}'.format(yr, title , label)
	return new_title


def rename(tr):
	"""Rename a track from its original name to its new name which includes the guessed year and label
	
	Args:
		tr (guestrrday.track.track): And object encapsulating information about a track, which includes its original filename and its new filename already.
	
	Returns:
		str: The new name if year was found, else the old name unchanged.
	"""
	old_fn = tr.filename_path
	new_fn = tr.new_title
	path = '.'
	if new_fn is not None and old_fn is not None and old_fn != new_fn:
		try:
			os.rename( old_fn, new_fn )
		except OSError as e:
			path = os.path.dirname(new_fn)
			new_fn = remove_blacklist_chars(os.path.basename(new_fn))
			try:
				os.rename( old_fn, os.path.join(path, new_fn) )
			except OSError as e2:
				print(e2)
				return
		return os.path.join(path, new_fn)
	return old_fn

