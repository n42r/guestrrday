import re
import os.path
import unidecode
from guestrrday import utils

class track:

	def __init__(self, title):
		"""Init for the class track

		Note: This is not only simple setter init, it includes on its last line a call

		to a function (extract_artist_title) that tries to sanitize messy track names and

		extract the artist and title and mix name separately. This updates some of the

		attributes such as artist and title

		Args:
			title (str): A valid filename on the system or a string song title.
				The code will guess which based on the input, you don't have to worry about that.

		Returns:
			list: list of objects that containt attributes as well as a dict called data

				which includes most of the info (see convert_discogs_results below)
		"""

		self.filename_path = None
		if os.path.exists(title) and os.path.isfile(title) and utils.has_music_ext(title):
			base = os.path.basename(title)
			self.filename_path = title
			title = base[ : base.rfind('.')]
		self.title = title
		self.track = None
		self.artist = None
		self.year = None
		self.label = None
		self.qualifier = None
		self.song_title = None
		self.id = id
		self.new_title = None
		self.extract_artist_title()

	def get_filename_path(self):
		"""Get filename path

		Example:
			MyFolder/MyAlbum/02. Prince - Musicology (Timelife Mix).mp3

		"""

		return self.filename_path

	def get_full_title(self):
		"""Get full title (including track num, if any)

		Example:
			002. Prince - Musicology (Timelife Mix)

		"""

		tit = self.title
		if self.track is not None:
			tr = str(self.track).zfill(3)
			tit = f'{tr}. {tit}'
		return tit

	def get_title(self):
		"""Get title (without track num)

		Example:
			Prince - Musicology (Timelife Mix)

		"""

		return self.title

	def get_artist(self):
		"""Get artist

		Example:
			Prince

		"""

		return self.artist

	def get_song_title(self):
		"""Get song title

		Example:
			Musicology

		"""

		return self.song_title

	def get_track(self):
		"""Get track num

		Example:
			2

		"""

		return self.track

	def get_qualifier(self):
		"""Get track qualifier or mix name, or whatever is in brackets at the end of the file (.)

		Example:
			Timelife Mix

		"""

		return self.qualifier

	def get_year(self):
		return self.year

	def get_label(self):
		return self.label

	def get_id(self):
		return self.id

	# def is_track(self):
		# return self.artist != None and self.song_title != None

	def get_new_name(self):
		return self.new_title

	def set_new_name(self, new):
		"""Set the new filename (or string title) of the song with the year/label

		Args:
			new (str): new base file name (does not include path).

				The path is assumed the same as original, i.e., files are renamed

		"""

		self.new_title = new
		if self.filename_path is not None:
			path = os.path.dirname(self.filename_path)
			base = os.path.basename(self.filename_path)
			ext = base[ base.rfind('.') + 1 : ]
			self.new_title = os.path.join(path, f'{self.new_title}.{ext}')

	def __str__(self):
		if self.filename_path is not None:
			return self.filename_path
		return self.get_full_title()

	def extract_artist_title(self):

		"""The function is there to try as best as possible to sanitize the input
			and detect the artist name and song title, etc.

		Args:
			None: It operates on the existing attributes in self

		Returns:
			None: It updates and reflects on the state of the current object

		"""

		self.title = cleanup_title(self.title)
		pat_str = r'^\s*(\d*)\s*[\W_]?\s*(.+)(?:(\s[\-\_~\：]|[\-\_~\：]\s|\s[\-\_~\：]\s))(.*)$'
		pat = re.compile(pat_str)
		match = re.findall(pat, self.title)
		if match != []:
			match = match[0]
			if match[0] != '':
				self.track = int(match[0].strip())
			self.artist = match[1].strip()
			if len(match) == 5 and match[4] != '':
				self.year = match[4]
			sng_tit = match[3].strip()
			pat_2 = re.compile(r'^\s*(.+)\s*(?:\((.[\w\s\W]+)\))\s*$')
			match_2 = re.findall(pat_2, sng_tit)
			if match_2 != []:
				match_2 = match_2[0]
				sng_tit = match_2[0].strip()
				self.qualifier = match_2[1].strip()
			self.song_title = sng_tit
			self.title = self.artist + ' - ' + self.song_title
			if self.qualifier is not None:
				self.title += ' (' + self.qualifier + ')'
			#if self.year != None:
			#	self.title += ' (' + self.year + ')'
		else:
			pat2= r'^\s*(\d*)\s*[\W_]?\s*(.+)$'
			pat2 = re.compile(pat2)
			match2 = re.findall(pat2, self.title)
			if match2 != [] and match2[0][0].strip() != '':
				self.track = int(match2[0][0].strip())
				self.title = match2[0][1].strip()
				#print("Couldn't match: " + self.title)
			self.artist = self.title
			self.song_title = self.title

def cleanup_title(title):
	"""Part of extract_artist_title, also to sanitize dirty title, music filenames, etc.

	Args:
		title (str): full song title

	Returns:
		str: sanitized full song title

	"""

	#title = title.lower()
	title = title.replace('[','(')
	title = title.replace(']',')')
	title = title.replace('{','(')
	title = title.replace('}',')')
	title = title.replace('–','-')
	title = title.replace("’","'")
	title = title.replace("´","'")
	title = title.replace('＂','"')
	title = title.replace(' and ', ' & ')
	title = title.replace(' feat.', ' & ')
	title = title.replace(' feat ', ' & ')
	title = title.replace(' ft. ', ' & ')

	title = title.replace(' ft ', ' & ')
	title = title.replace(' featuring ', ' & ')
	title = unidecode.unidecode(title)
	title = title.replace('*', '')
	title = title.replace("''", '"')
	if title.rfind('"') > title.find('"') and title.find('"') > -1 and title.find(" - ") == -1:
		title = re.sub(' ?\" ?(.+) ?\"', ' - \\1', title)
	if title.find(' - ') == -1:
		if title.find('   ') > -1:
			title = title.replace('   ',' - ', 1)
		elif title.find('  ') > -1:
			title = title.replace('  ',' - ', 1)
		elif title.find('-') > -1:
			title = title.replace('-',' - ', 1)
	title = title.replace('"', '')
	return title.strip()
