import pickle,base64
import io
import pickle
import smhasher
DEFAULT_PROTOCOL = 3

def _dumps(obj,):
	s = base64.b64encode(pickle.dumps(obj)).decode('ascii')
	return s

def _loads(obj):
	# return pickle.loads(obj.encode('ascii'))
	x = base64.b64decode(obj.encode('ascii'))
	return pickle.loads(x)

import pkg_resources

class MyPickleSession(object):
	load = pickle.load

	def get_version(self, distribution_name, strict):
	    try:
	        version = pkg_resources.get_distribution(distribution_name).version
	    except pkg_resources.DistributionNotFound:
	    	if strict:
	    		raise
	    	version = ''
	    return version

	def hash_bytes(self, s):
	    return smhasher.murmur3_x86_64(s)
	def __init__(self, modules = None):
		self._modules = modules or set()
		self._buffer = None

	@property
	def modules(self):
		return self._modules

	def pop_modules(self):
		modules = self._modules
		self._modules = set()
		return modules
	def pop_buffer(self,):
		if self._buffer is not None:
			v = self._buffer
			self._buffer = None
			return v
		else:
			return None
	def pop_modules_list(self, f=None):
		if f is not None:
			self._buffer = f()

		return list([(x,self.get_version(x,0)) for x in self.pop_modules()])

	def dump_sniff(self, obj,f,protocol=None):
		p = MyPickler(f, self.modules, protocol)
		p.dump(obj)

	def dump(self, obj,f,protocol=None):
		p = MyPickler(f, None, protocol)
		p.dump(obj)

	def dumps_sniff(self, obj, protocol=None):	
		f = io.BytesIO()
		p = MyPickler(f, self.modules, protocol)
		p.dump(obj)
		return f.getvalue()

	def bytes_to_ascii(self, s):
		return base64.b64encode(s).decode('ascii')

	def ascii_to_bytes(self,s):
		x = base64.b64decode(s.encode('ascii'))
		return x


	def dumps_sniff_b64(self, obj, protocol=None):
		s = self.dumps_sniff(obj,protocol)
		return self.bytes_to_ascii(s)
		# return base64.b64encode(s).decode('ascii')
		# f = io.BytesIO()
		# p = MyPickler(f, self.modules, protocol)
		# p.dump(obj)
		# return base64.b64encode(f.getvalue()).decode('ascii')

	def loads_b64(self, s):
		x = self.ascii_to_bytes(s)
		return pickle.loads(x)

	def dumps(self, obj, protocol=None):	
		f = io.BytesIO()
		p = MyPickler(f, None, protocol)
		p.dump(obj)
		return f.getvalue()
	def dumps_b64(self,obj,protocol=None):
		return self.bytes_to_ascii(self.dumps(obj,protocol))


class MyPickler(pickle._Pickler):
	def __init__(self, file, modules, protocol=None, fix_imports=True):
		if protocol is None:
			protocol = DEFAULT_PROTOCOL
		super().__init__(file, protocol,fix_imports=fix_imports)
		self.modules = modules
		self.sniff = modules is not None

	def save(self, obj, save_persistent_id=True):
		if self.sniff:
			if isinstance(obj, type):
				self.modules.add(obj.__module__.split('.',1)[0])
		super().save(obj,save_persistent_id)
