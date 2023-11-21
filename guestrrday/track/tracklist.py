"""Tracklist Module

This modules contains a simple class to represent a tracklist.

"""
from guestrrday.track import track
from guestrrday import utils

import os

class tracklist:
	"""A class to represent a tracklist, which is a list of track objects.

	Attributes:

	Example:
	tl = tracklist()
	tk = track('Method Man & Redman - Da Rockwilder')
	tk2 = track('Redman - Time 4 Sum Aksion (Explicit)')
	tl.add(tk)
	tl.add(tk2)
	t1.get(1).get_title() # => Redman - Time 4 Sum Aksion (Explicit)

	"""
	def __init__(self, trck_lst = None, location = None, eliminate_duplicates = False):
		if trck_lst is None:
			self.__trck_lst = []
		else:
			self.__trck_lst = trck_lst
		if location is None:
			location = ''
		self.location = location
		self.eliminate_duplicates = eliminate_duplicates
		self.type = None
		self.__seen = set()

	def add(self, trck):
		if self.eliminate_duplicates and trck.get_title() in self.__seen:
			return
		self.__seen.add(trck.get_title())
		self.__trck_lst.append(trck)

	def get(self, index):
		if index < len(self.__trck_lst):
			return self.__trck_lst[index]
		return None

	def len(self):
		return len(self.__trck_lst)

	def fill(self):
		if os.path.exists(self.location):
			if os.path.isfile(self.location):
				self.fill_from_file()
			else:
				self.fill_from_dir()
		else:
			self.fill_from_cli()

	def fill_from_dir(self):
		self.type = 'dir'
		files = os.listdir(self.location)
		for fn in files:
			tr = track( os.path.join(self.location, fn) )
			if utils.has_music_ext(fn):
				self.add(tr)

	def fill_from_file(self):
		self.type = 'file'
		with open(self.location, encoding='utf8') as f:
			for line in f:
				line = line.strip()
				if line == '' or line[0] == '#':
					continue
				tr = track(line)
				self.add(tr)

	def fill_from_cli(self):
		self.type = 'cli'
		lis = self.location.split(',')
		for i in lis:
			tr = track( i.strip() )
			self.add(tr)

	def __str__(self):
		l = []
		for i in self.__trck_lst:
			l.append(str(i))
		return str(l)

	def __iter__(self):
		return iter(self.__trck_lst)
