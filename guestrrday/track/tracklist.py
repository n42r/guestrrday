"""Tracklist Module

This modules contains a simple class to represent a tracklist.

"""

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
	def __init__(self, trck_lst = [], location = '', eliminate_duplicates = False):
		self.__trck_lst = trck_lst
		self.location = location
		self.eliminate_duplicates = eliminate_duplicates
		self.__seen = set()
	
	def add(self, track):
		if self.eliminate_duplicates and track.get_title() in self.__seen:
			return
		self.__seen.add(track.get_title())
		self.__trck_lst.append(track)
		
	def get(self, index):
		if index < len(self.__trck_lst):
			return self.__trck_lst[index]
	
	def iter(self):
		return iter(self.__trck_lst)
		
	def len(self):
		return len(self.__trck_lst)
	
	def __str__(self):
		l = []
		for i in self.__trck_lst:
			l.append(i.str())
		return str(l)