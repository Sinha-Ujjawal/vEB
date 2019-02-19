from sortedcollections import SortedSet as _SortedSet
from math import sqrt as _sqrt, ceil as _ceil, log2 as _log2

class Set:
	class _Node:
		def __init__(self, x, u, threshold):
			self.min = self.max = x
			if u > threshold:
				self.cluster = {}
				self.summary = None
			else:
				self.list = _SortedSet()
				self.list.add(x)
	
	def __init__(self, lb=0, ub=1023, c=100):
		assert isinstance(lb, int) and isinstance(ub, int) and lb <= ub and isinstance(c, int) and c > 0
		self._lb = lb
		self._ub = ub
		self._u = ub - lb + 1
		self._threshold = max(2, _ceil(c * _log2(_log2(self._u))))
		self._root = None
		self._len = 0
		
	def __len__(self):
		return self._len
		
	def __iter__(self):
		return self.keys_generator()
		
	def __repr__(self):
		return 'Set({})'.format(list(self))
		
	def __contains__(self, x):
		return self.contains(x)
		
	def isEmpty(self):
		return self._root == None
		
	@staticmethod
	def __hierarchicalCoords(x, u):
		return x // u, x % u
		
	@staticmethod
	def __indexOf(i, j, u):
		return i * u + j
		
	@staticmethod
	def __add(V, x, u, threshold):
		if V == None:
			return Set._Node(x, u, threshold)
		if u > threshold:
			if x == V.min or x == V.max:
				pass
			else:
				if x < V.min:
					x, V.min = V.min, x
				elif x > V.max:
					V.max = x
				new_u = _ceil(_sqrt(u))
				c, i = Set.__hierarchicalCoords(x, new_u)
				if c not in V.cluster:
					V.summary = Set.__add(V.summary, c, new_u, threshold)
					V.cluster[c] = Set.__add(None, i, new_u, threshold)
				else:
					V.cluster[c] = Set.__add(V.cluster[c], i, new_u, threshold)
		else:
			if x < V.min: V.min = x
			elif x > V.max: V.max = x
			V.list.add(x)
		return V
		
	@staticmethod
	def __remove(V, x, u, threshold):
		if V == None:
			return None
		if u > threshold:
			new_u = _ceil(_sqrt(u))
			if x == V.min:
				if V.summary != None:
					c = V.summary.min
					x = V.min = Set.__indexOf(c, V.cluster[c].min, new_u)
				else:
					return None
			c, i = Set.__hierarchicalCoords(x, new_u)
			t = Set.__remove(V.cluster[c], i, new_u, threshold)
			if t == None:
				del V.cluster[c]
				V.summary = Set.__remove(V.summary, c, new_u, threshold)
			if V.summary == None:
				V.max = V.min
			else:
				c = V.summary.max
				V.max = Set.__indexOf(c, V.cluster[c].max, new_u)
		else:
			try:
				V.list.remove(x)
			except:
				pass
			
		return V
		
	@staticmethod
	def __contains(V, x, u, threshold):
		if V == None:
			return False
		if u > threshold:
			if x == V.min or x == V.max: return True
			new_u = _ceil(_sqrt(u))
			c, i = Set.__hierarchicalCoords(x, new_u)
			return Set.__contains(V.cluster.get(c, None), i, new_u, threshold)
		else:
			return x in V.list
		
	@staticmethod
	def __successor(V, x, u, threshold):
		if V == None:
			return None
		if u > threshold:
			if x < V.min: return V.min
			new_u = _ceil(_sqrt(u))
			c, i = Set.__hierarchicalCoords(x, new_u)
			if c in V.cluster and i < V.cluster[c].max:
				i = Set.__successor(V.cluster[c], i, new_u, threshold)
				return Set.__indexOf(c, i, new_u)
			else:
				c = Set.__successor(V.summary, c, new_u, threshold)
				if c != None:
					return Set.__indexOf(c, V.cluster[c].min, new_u)
		else:
			index = V.list.bisect_right(x)
			return V.list[index] if index < len(V.list) else None
				
	@staticmethod
	def __predecessor(V, x, u, threshold):
		if V == None:
			return None
		if u > threshold:
			if x > V.max: return V.max
			new_u = _ceil(_sqrt(u))
			c, i = Set.__hierarchicalCoords(x, new_u)
			if c in V.cluster and i > V.cluster[c].min:
				i = Set.__predecessor(V.cluster[c], i, new_u, threshold)
				return Set.__indexOf(c, i, new_u)
			else:
				c = Set.__predecessor(V.summary, c, new_u, threshold)
				if c != None:
					return Set.__indexOf(c, V.cluster[c].max, new_u)
		else:
			index = V.list.bisect_left(x)
			return V.list[index - 1] if index else None
		
	def add(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		if x not in self:
			self._root = Set.__add(self._root, x - self._lb, self._u, self._threshold)
			self._len += 1
		
	def remove(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		if x in self:
			self._root = Set.__remove(self._root, x - self._lb, self._u, self._threshold)
			self._len -= 1
		else:
			raise KeyError('key {} not found!'.format(x))
			
	def contains(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		return Set.__contains(self._root, x - self._lb, self._u, self._threshold)
			
	def successor(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		ret = Set.__successor(self._root, x - self._lb, self._u, self._threshold)
		if ret != None: return ret + self._lb
		
	def predecessor(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		ret = Set.__predecessor(self._root, x - self._lb, self._u, self._threshold)
		if ret != None: return ret + self._lb
		
	def min(self):
		return (self._lb + self._root.min) if not self.isEmpty() else None
		
	def extractMin(self):
		if not self.isEmpty():
			x = self._lb + self._root.min
			self._root = Set.__remove(self._root, self._root.min, self._u, self._threshold)
			self._len -= 1
			return x
		
	def max(self):
		return (self._lb + self._root.max) if not self.isEmpty() else None
		
	def extractMax(self):
		if not self.isEmpty():
			x = self._lb + self._root.max
			self._root = Set.__remove(self._root, self._root.max, self._u, self._threshold)
			self._len -= 1
			return x
		
	def keys_generator(self, reverse=False):
		f = self.predecessor if reverse else self.successor
		value = self.max() if reverse else self.min()
		while value != None:
			yield value
			value = f(value)
			
	def keys(self, reverse=False):
		return list(self.keys_generator(reverse=reverse))
