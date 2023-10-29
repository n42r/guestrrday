import re
import os.path
import unidecode

class track:
	def __init__(self, title):
		self.filename_path = None
		if os.path.exists(title) and os.path.isfile(title) and has_music_ext(title):
			base = os.path.basename(title)
			self.filename_path = title
			title = base[ : base.rfind('.')]
		self.title = title
		self.track = None
		self.artist = None
		self.song_title = None
		self.extract_artist_title()
	
	def extract_artist_title(self):	
		self.title = cleanup_title(self.title)
		pat_str = '^\s*(\d*)\s*[\W_]?\s*(.+)(\s[\-\_~\：]|[\-\_~\：]\s|\s[\-\_~\：]\s)(.+)\[[0-9A-Za-z_-]{11}.*]'
		pat = re.compile(pat_str)
		match = re.findall(pat, self.title)
		if match == []:
			print("Couldn't match: " + self.title)
		else:
			match = match[0]
			self.track = int(match[0].strip())
			self.artist = match[1].strip()
			self.song_title = match[3].strip()
			self.title = self.artist + ' - ' + self.song_title
		self.title = self.title.replace('[','(')
		self.title = self.title.replace(']',')')

	
	# MyFolder\MyAlbum\02. Prince - Musicology.mp3
	def get_filename_path(self):
		return self.filename_path
		
	# Prince - Musicology
	def get_title(self):
		return self.title
	
	# Prince
	def get_artist(self):
		return self.artist
	
	# Musicology
	def get_song_title(self):
		return self.song_title

	# 2
	def get_track(self):
		return self.track
	
	def str(self):
		s = ''
		if self.filename_path != None:
			s += ' (' + self.filename_path + ')'
		s = self.title + s
		return s
		
	
	
def has_music_ext(fn):
	ext_idx = fn.rfind('.')
	if ext_idx > -1:
		ext = fn[ext_idx + 1:]
		#f_char = ext[0]
		audio_ext_list = ['mp3', 'flac', 'm4a', 'ogg', 'opus', 'wav', 'wma', 'aif', 'aiff']
		if ext in audio_ext_list:
			return True
	return False		

def cleanup_title(title):
	title = title.lower()
	title = title.replace(' and ', ' & ')
	title = title.replace(' feat.', ' & ')
	title = title.replace(' feat ', ' & ')
	title = title.replace(' ft. ', ' & ')		
	title = title.replace(' ft ', ' & ')
	title = title.replace(' featuring ', ' & ')
	title = title.replace("’","'")
	title = title.replace("´","'")
	title = title.replace('＂','"')
	title = title.replace('/',', ')
	title = title.replace('╱',', ')		
	title = title.replace(', ',' - ', 1)
	title = unidecode.unidecode(title)
	if title.rfind('"') > title.find('"') and title.find('"') > -1 and title.find(" - ") == -1:
		title = re.sub(' ?\" ?(.+) ?\"', ' - \\1', title)
	if title.find(' - ') == -1:
		if title.find('   ') > -1:
			title = title.replace('   ',' - ', 1)
		elif title.find('  ') > -1:
			title = title.replace('  ',' - ', 1)
	return title.strip()