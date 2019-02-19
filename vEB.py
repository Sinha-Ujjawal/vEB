from math import sqrt as _sqrt, ceil as _ceil

class Set:
	class _Node:
		def __init__(self, x, u):
			self.min = self.max = x
			self.cluster = {} if u > 2 else None
			self.summary = None
	
	def __init__(self, lb=0, ub=1023):
		assert isinstance(lb, int) and isinstance(ub, int) and lb <= ub
		self._lb = lb
		self._ub = ub
		self._u = ub - lb + 1
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
	def __add(V, x, u):
		if V == None:
			return Set._Node(x, u)
		if x == V.min or x == V.max:
			pass
		else:
			if x < V.min:
				x, V.min = V.min, x
			elif x > V.max:
				V.max = x
			if u > 2:
				new_u = _ceil(_sqrt(u))
				c, i = Set.__hierarchicalCoords(x, new_u)
				if c not in V.cluster:
					V.summary = Set.__add(V.summary, c, new_u)
					V.cluster[c] = Set.__add(None, i, new_u)
				else:
					V.cluster[c] = Set.__add(V.cluster[c], i, new_u)
		return V
		
	@staticmethod
	def __remove(V, x, u):
		if V == None:
			return None
		new_u = _ceil(_sqrt(u))
		if x == V.min:
			if V.summary != None:
				c = V.summary.min
				x = V.min = Set.__indexOf(c, V.cluster[c].min, new_u)
			else:
				return None
		if u > 2:
			c, i = Set.__hierarchicalCoords(x, new_u)
			t = Set.__remove(V.cluster[c], i, new_u)
			if t == None:
				del V.cluster[c]
				V.summary = Set.__remove(V.summary, c, new_u)
				
		if V.summary == None:
			V.max = V.min
		else:
			c = V.summary.max
			V.max = Set.__indexOf(c, V.cluster[c].max, new_u)
			
		return V
		
	@staticmethod
	def __contains(V, x, u):
		if V == None:
			return False
		elif x == V.min or x == V.max:
			return True
		if u > 2:
			new_u = _ceil(_sqrt(u))
			c, i = Set.__hierarchicalCoords(x, new_u)
			return Set.__contains(V.cluster.get(c, None), i, new_u)
		return False
		
	@staticmethod
	def __successor(V, x, u):
		if V == None:
			return None
		if x < V.min:
			return V.min
		if u > 2:
			new_u = _ceil(_sqrt(u))
			c, i = Set.__hierarchicalCoords(x, new_u)
			if c in V.cluster and i < V.cluster[c].max:
				i = Set.__successor(V.cluster[c], i, new_u)
				return Set.__indexOf(c, i, new_u)
			else:
				c = Set.__successor(V.summary, c, new_u)
				if c != None:
					return Set.__indexOf(c, V.cluster[c].min, new_u)
		if x < V.max:
			return V.max
				
	@staticmethod
	def __predecessor(V, x, u):
		if V == None:
			return None
		if x > V.max:
			return V.max
		if u > 2:
			new_u = _ceil(_sqrt(u))
			c, i = Set.__hierarchicalCoords(x, new_u)
			if c in V.cluster and i > V.cluster[c].min:
				i = Set.__predecessor(V.cluster[c], i, new_u)
				return Set.__indexOf(c, i, new_u)
			else:
				c = Set.__predecessor(V.summary, c, new_u)
				if c != None:
					return Set.__indexOf(c, V.cluster[c].max, new_u)
		if x > V.min:
			return V.min
		
	def add(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		if x not in self:
			self._root = Set.__add(self._root, x - self._lb, self._u)
			self._len += 1
		
	def remove(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		if x in self:
			self._root = Set.__remove(self._root, x - self._lb, self._u)
			self._len -= 1
		else:
			raise KeyError('key {} not found!'.format(x))
			
	def contains(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		return Set.__contains(self._root, x - self._lb, self._u)
			
	def successor(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		ret = Set.__successor(self._root, x - self._lb, self._u)
		if ret != None: return ret + self._lb
		
	def predecessor(self, x):
		assert isinstance(x, int) and self._lb <= x <= self._ub
		ret = Set.__predecessor(self._root, x - self._lb, self._u)
		if ret != None: return ret + self._lb
		
	def min(self):
		return (self._lb + self._root.min) if not self.isEmpty() else None
		
	def extractMin(self):
		if not self.isEmpty():
			x = self._lb + self._root.min
			self._root = Set.__remove(self._root, self._root.min, self._u)
			self._set.remove(x)
			return x
		
	def max(self):
		return (self._lb + self._root.max) if not self.isEmpty() else None
		
	def extractMax(self):
		if not self.isEmpty():
			x = self._lb + self._root.max
			self._root = Set.__remove(self._root, self._root.max, self._u)
			self._set.remove(x)
			return x
		
	def keys_generator(self, reverse=False):
		f = self.predecessor if reverse else self.successor
		value = self.max() if reverse else self.min()
		while value != None:
			yield value
			value = f(value)
			
	def keys(self, reverse=False):
		return list(self.keys_generator(reverse=reverse))
