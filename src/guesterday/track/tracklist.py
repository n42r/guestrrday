

class tracklist:

	def __init__(self, trck_lst = [], path = '', eliminate_duplicates = False):
		self.trck_lst = trck_lst
		self.path = path
		self.eliminate_duplicates = eliminate_duplicates
		self.seen = set()
		
	def add(self, track):
		if self.eliminate_duplicates:
			if track.str() not in self.seen:
				self.seen.add(track.str())
			else:
				return
		self.trck_lst.append(track)
	
	def get(self, index):
		if index < len(self.trck_lst):
			return self.trck_lst[index]
	
	def iter(self):
		return iter(self.trck_lst)
	
	def str(self):
		l = []
		for i in self.trck_lst:
			l.append(i.str())
		return str(l)