__doc__ = """
Interal exceptions, classes, functions to outline the 
identification system.

"""
# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from path import Path
import glob
from collections import namedtuple
import os
from orderedattrdict import AttrDict
import json
import re
from spiper._header import list_flatten,list_flatten_strict,rgetattr,rstrip



import spiper
import sys
spiper._types = sys.modules[__name__]


def DirtyKey(s):
	return re.sub('[^0-9a-zA-Z_]','_',s)	


Code = type((lambda:None).__code__)

class TooManyArgumentsError(RuntimeError):
	'''
	aaaa
	'''
	pass
class TooFewArgumentsError(RuntimeError):
	pass
# class NotEnoughArgumentsError(RuntimeError):
# 	pass
class TooFewDefaultsError(RuntimeError):
	pass


class CantGuessCaller(Exception):
	pass
class UndefinedTypeRoutine(Exception):
	pass

class OverwriteError(Exception):
	pass

class UndefinedRoutine(Exception):
	pass


class IdentAttrDict(AttrDict):
	pass



class cached_property(object):
	"""
	Descriptor (non-data) for building an attribute on-demand on first use.
	Source: https://stackoverflow.com/a/4037979
	"""
	def __init__(self, factory):
		"""
		<factory> is called such: factory(instance) to build the attribute.
		"""
		self._attr_name = factory.__name__
		self._factory = factory

	def __get__(self, instance, owner):
		# Build the attribute.
		attr = self._factory(instance)
		# Cache the value; hide ourselves.
		setattr(instance, self._attr_name, attr)
		return attr

class PicklableNamedTuple(object):
	__doc__ = """ 
	This class mimic `namedtuple`, except that an object of 
	this class is picklable whereas that of namedtuple is not.
	"""
	pass

# if 0:
	def __getstate__(self,):
		d = self.__dict__.copy()
		del d['cls']
		return d
	def __setstate__(self,d):
		self.__dict__ = d
		self.cls = namedtuple(d['name'], d['fields'])
	def __init__(self,name,fields):
		self.name = 'myData'
		self.cls = namedtuple(self.name,fields)
		self.fields = self.cls._fields
	def __call__(self,*a,**kw):
		v = self.cls(*a,**kw)
		# if len(v)>=3:
		# 	import pdb;pdb.set_trace()
		return AttrDict(v._asdict())

def Default(x):
	'''
	A dummy "class" mocked with a function
	'''
	return x

class _BaseFunction(object):
	pass



class NodeFunction(_BaseFunction):
	'''
	A :class:`NodeFunction` should not have any subnodes.
	`self.runner` is prohibited in a `NodeFunction`. 
	In other words, a :class:`NodeFunction` cannot have
	any children nodes.
	'''
	named = 1
	pass

# class SingleFileNodeFunction(NodeFunction):
# 	named = 0

# def SingleFileNode(func):
# 	func._type = SingleFileNodeFunction
# 	# UnnamedNodeFunction
# 	return func


def Node(func):
	"""
	Decorate that marks a function as :class:`NodeFunction`.

	Args:
		func: :obj:`function` the function to be decorated.

	"""
	func._type = NodeFunction
	return func

class FlowFunction(_BaseFunction):
	"""
	:class:`FlowFunction`
	will always be executed regardless of the :class:`_Runner`
	at runtime. Any time-consuming expression should
	not be put in a :class:`FlowFunction`.
	"""
	named = 1
	pass

def Flow(func):
	"""
	Mark a function as :class:`FlowFunction`.

	Args:
		func: :obj:`function`: the function to be decorated.
	"""
	func._type = FlowFunction
	return func





_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
	if os.path.isfile(fname):
		return os.stat(fname)
	else:
		return _os_stat_result_null

class Depend(Path):
	'''
	Abstract Dependency
	'''
	pass

class PrefixedNode(Depend):
	'''
	This class represents file(s) that 
	know(s) how to find its parent `Node`.
	'''
	def get_prefix_pointer(self, dir_layout):
		idFile = IdentFile( dir_layout, self, [] , '_prefix_pointer')		
		suc = 0
		res = None
		if idFile.exists():
			with open(idFile,'r') as f:
				s = json.load(f)[0]
				# s = f.read()
				suc = 1
				res = Prefix(idFile.dirname()/s).expand()

		return suc,res

	def callback_output(self, caller, name):
		# pass
		fn = self
		idFile = IdentFile( caller.dir_layout, fn, [] , '_prefix_pointer')
		with open(idFile,'w') as f:
			json.dump( [ caller.prefix_named.relpath(idFile.dirname())], f)

	def fileglob(self, g, strict,filter=1):
		res = [File(x) for x in glob.glob("%s%s"%(self,g))]
		if filter:
			res = [x  for x  in res
			if not x.endswith('.outward_edges') and not x.endswith('.outward_edges_old') and not x.endswith('._prefix_pointer')
			and not x.endswith('.mock')
			]
		if strict:
			assert len(res),'(%r,%r) expanded into nothing!'% (self,g)
		# return [File(str(x)) for x in glob.glob("%s%s"%(self,g))]
		return res



class File(PrefixedNode):
	'''
	As function inputs, :class:`File` will be 
	fingerprinted with its mtime and byte sizes.
	If this fingerprint changed, a downstream 
	recalculation will be triggered.
	'''
	def __init__(self,*a,**kw):
		super(File,self).__init__(*a,**kw)
	def to_ident(self,):
		stat = os_stat_safe(self)
		res = (self, stat.st_mtime, stat.st_size)
		return res
	def expanded(self):
		return [self]



class TempFile(File):
	def __init__(self,*a,**kw):
		super(TempFile,self).__init__(*a,**kw)
	pass

class InputFile(File):
	def __init__(self,*a,**kw):
		super(InputFile,self).__init__(*a,**kw)
	pass

class OutputFile(File):
	def __init__(self,*a,**kw):
		super(OutputFile,self).__init__(*a,**kw)
	pass

# import pickle
class Prefix(PrefixedNode):
	'''
	The definition of a Prefix is unclean.
	The expansion of :class:`Prefix` cannot
	takes place until the upstream job is done.
	
	For example, a tar archive job may wants to
	monitor all files under prefix :file:`./build`

	This node is useful when specifying a loosely
	defined fileset into :func:`LoggedSingularityCommand`
	'''
	def __init__(self,*a,**kw):
		super(Prefix, self).__init__(*a,**kw)
	def callback_output(self, caller, name):
		super().callback_output(caller, name)
		fs = self.fileglob('*',strict=1)
		for fn in fs:
			idFile = IdentFile( caller.dir_layout, fn, [] , '_prefix_pointer')
			with open(idFile,'w') as f:
				json.dump( [ self.relpath(idFile.dirname())], f)
				# f.write(self.relpath(idFile.dirname()))
		return 
	def expaneded(self):
		return self.fileglob('*',0)

class InputPrefix(Prefix):
	def __init__(self,*a,**kw):
		super( InputPrefix,self).__init__(*a,**kw)

class OutputPrefix(Prefix):
	def __init__(self,*a,**kw):
		super( OutputPrefix,self).__init__(*a,**kw)

job_result = namedtuple(
	'job_result',
	[
	'OUTDIR',
	'cmd_list',
	'output']
	)


def IdentFile(dir_layout, prefix, job_name, suffix):
	if isinstance(prefix, CacheFile):
		dir_layout = 'flat'
	prefix = Prefix(prefix)
	# if  callable(job_name):
	# 	import pdb;pdb.set_trace();
	if dir_layout == 'clean':
		pre_dir = prefix.dirname()
		pre_base = prefix.basename()
		lst = ['{pre_dir}/_spiper/{pre_base}'.format(**locals()),
				job_name,suffix]
		# input_ident_file = '{pre_dir}/_spiper/{pre_base}.{job_name}.{suffix}'.format(**locals())
	elif dir_layout == 'flat':
		lst = [prefix,job_name,suffix]
	else:
		assert 0,("dir_layout",dir_layout)
		# input_ident_file = '{prefix}.{job_name}.{suffix}'.format(**locals())
	input_ident_file = '.'.join(list_flatten_strict(lst))
	return File(input_ident_file)


class CacheFile(OutputFile):
	pass


from collections import OrderedDict as _dict
import requests
import json
# class HttpCheckLengthResult(object):
class HttpResponse(object):
	'''
	Github tarball/master often take minutes to update itself
	'''
	headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
	}
	def __init__(self, method,url,**kwargs):
		self.method = method
		self.url = url
		kwargs.setdefault('headers', self.headers)
		self.kwargs =kwargs
	def __repr__(self):
		return "%s(%s)"%(
			self.__class__.__name__,
			json.dumps(
				_dict([(k,getattr(self,k)) for k in ['method','url']]),
				default=repr,separators=',=')
			)

	##### Evaluate this response only once during the lifespan of this object
	@cached_property
	# @property
	def response(self):
		x = requests.request( self.method, self.url, **self.kwargs)
		return x

	@property
	def text(self):
		return self.response.text

	def to_ident(self,):
		x = self.response
		d0=  self.__dict__.copy()
		d0.pop('response', None)

		# d = dict(x.headers.copy())
		_d = {}
		d = x.headers
		via =  d.get('via','')
		_d['header_ident'] = None
		if 'varnish' in via:
			_d['header_ident'] = d.get('etag', None)
		if _d['header_ident'] is None:
			_d['header_ident'] = d.get('content-length', None)
		if _d['header_ident'] is None:
			_d['header_ident'] = d.get('content-disposition', None)
		if _d['header_ident'] is None:
			if not x.text:
				raise Exception('HTTP header is not informative!%s'%json.dumps(_dict(x.headers),indent=2))
		# hd = _dict()
		# hd['clen'] =  d.get('Content-Length', None)
		# hd['cdisp'] = d.get('Content-Disposition',None)
		# hd['ctype'] = d.get('Content-Type', None)
		# assert hd['clen'] or hd['cdisp'], hd

		# return [ sorted(d0.items()), ('_header_ident',list(hd.values())), ('_text',x.text)]
		return [ sorted(d0.items()), ('_header_ident',_d['header_ident']), ('_text',x.text)]



class HttpResponseContentHeader(HttpResponse):
	def __init__(self,url,**kwargs):
		super().__init__('head', url,**kwargs)


def lstrip(x,s):
	if x.startswith(s):
		x = x[len(s):]
	return x
def PythonPackage(package_path, imported_name=None):
	'''
	Tries to parse package_path according to pkg_resources.Requirement.parse()

	Args:
	------------------------

	package_path: (str)
		A :pep:`508`-compatible string without version specification
	
	Note:
	----------------------
	pip uses PackageFinder to mimic easy_install
	see https://github.com/pypa/pip/blob/e5375afffded829dc6a8373e0d07149ab3c74bed/src/pip/_internal/index/package_finder.py#L597
	'''

	# assert version is None
	err = UndefinedRoutine('PythonPackage(%r)'%((package_path)))
	# print(package_path)
	# package_path = str(package_path)
	# x = pkg_resources.Requirement.parse(package_path)
	if '@' in package_path:
		_name, _url = package_path.split('@',1)
	else:
		_name = None
		_url  = package_path

	extras = ()
	if _url is not None:
		# url = _url
		# package_name, url = package_path.split('@',1)
		if _url.startswith('http'):
			extras = HttpResponseContentHeader(_url)
		elif _url.startswith('file://'):
			extras = Prefix(lstrip( _url, 'file://'))
		elif _url.startswith('/'):
			raise Exception('Use file://<path> to specify a local package')
		else:
			raise err
	mod = _PythonPackage( package_path, _name, imported_name, extras)

	# mod = _PythonPackage( x.name, imported_name, x.url, x.specs, extras)
	# else:
		# x = pkg_resources.Requirement.parse(package_path)
		# package_name = x.key
		# url = 
		# raise err
	return mod


from spiper._pickler import get_version as get_package_version
from spiper._shell import _shellcmd
import sys,importlib
import pkg_resources
import json
# from pip._internal.utils.virtualenv import virtualenv_no_global

# PIP_BIN = 'pip3'
class _PythonPackage(object):
	'''
	Object to manage local module installation status.
	``_PythonModule(*args).loaded()`` returns the imported module.
	Currently, local modules must be unique with regards to :obj:`package_name`,
	Upon name conflict, that is if package `foo` is already installed 
	through ``PythonModule("foo",url1)`` and ``PythonModule("foo",url2)`` is called,
	then original installation will be cleared and `url2` would be used for a second install.
	This solution is *sub-optimal* because back-and-force installations is possible.
	Changing this would require a complete re-setup of `pip`-style package management.

	pip.main()? https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program

	Attributes:
		package_name (str): name of this package
		url (str): a PEP-508-compatible string without version spec.
		extras (dynamic): Any object with a ``to_ident`` method to serve as package fingerprint. 
	'''
	def __init__(self, package_path, package_name, imported_name,  extras):
		self.package_path = package_path
		self.package_name = package_name
		self.imported_name = imported_name
		 # or package_name
		# self.specs = specs
		# self.url = url
		self.extras = extras
		# self._resp = HttpResponseContentHeader(url)
		# self.version = version


	def __repr__(self):
		return ("{self.__class__.__name__}"
		"(imported_name={self.imported_name!r},"
		"extras={self.extras!r}"
		# "version={self.version!r}"
		")").format(**locals())


	def to_ident(self):
		res = sorted(self.__dict__.items())
		# res = _dict(self.__dict__)
		# res = list_flatten(res)
		return res

	@property
	def egg_info(self):
		verbose=0
		fn = ''
		try:
			dist = pkg_resources.get_distribution(self.package_name)
			fn = Path( dist.egg_info )
			# if fn.endswith('.dist-info'):
			# 	fn = rstrip(fn,'.dist-info')+'.egg-info'
		except pkg_resources.DistributionNotFound as e:
			if verbose:
				print(e)
		return Path(fn)

	@property
	def ident_file(self):
		if self.egg_info: 
			return self.egg_info / 'URL_RESPONSE_HEADER'
		else:
			return ''


	def get_installed_ident(self, ):
		# ident = ''
		fn = self.ident_file
		# ident = []
		ident = ''
		if fn and fn.isfile(): 
			with open( fn,'r') as f:
				ident = f.read()
				# try:
				# 	ident = json.loads(f)
				# except:
				# 	pass
		return ident
	def dumps(self, x):
		x = get_identity( x,strict=1)
		return json.dumps( x,indent=2)

	def is_compatible(self):
		# return 0 

		#### Use content header to check whether is compatible
		installed_ident   =  self.get_installed_ident()
		self_ident		=  self.dumps([self])
		return self_ident == installed_ident


	def is_installed(self):
		'''
		If get_package_version did not return
		'''
		version = get_package_version(self.package_name, 0)
		return 0

	def is_loaded(self):
		if self.imported_name is None:
			return 0
		else:
			return self.imported_name in sys.modules

	# def __getattr__(self, key):
	# 	'''
	# 	Get module attribute if not 
	# 	'''


	def loaded(self):
		verbose = 0
		PIP_BIN = [sys.executable,'-m','pip',]
		mod = None
		if not self.is_loaded():
			# print(self.ident_file)
			if not self.is_compatible():
				'''
				Overwrite the local installation by default
				'''
				print('[installing]',self.package_path,'\n',self.egg_info)
				if self.egg_info:
					# print('')
					for x in self.egg_info.dirname().glob(self.egg_info.basename().split('-',1)[0]+'*'):
						if x.isfile(): x.unlink_p()
						if x.isdir(): x.rmtree_p()
				# [x.rmtree_p() for x in self.egg_info.dirname().glob(self.egg_info.basename().split('-',1)[0]+'*')]
				# self.egg_info.rmtree_p()
				
				######## Monkey Patchhhhhhhhhhhhhhhhhh #####
				from spiper._pip_patch import virtualenv_no_global
				##### see https://github.com/pypa/pip/blob/520e76ddb950e05c1b6e50b1108196c79c5e856f/src/pip/_internal/commands/install.py#L576
				CMD = [
					[PIP_BIN,'uninstall','-y',self.package_name,';'],
					PIP_BIN,'install','-vvv', 
					[[] if virtualenv_no_global() else '--user'],
					self.package_path,
					# self.package_name+'@'+self.url,
				]
				suc, stdout, stderr = _shellcmd(CMD, 1, 0, 'utf8', None, None, None, 1)
				assert self.egg_info.isdir(),'Installation of given url did not create a valid egg_info directory:\negg_info={self.egg_info}'.format(**locals())

				print(stdout) if verbose>=2 else None
				with open(self.ident_file,'w') as f:
					f.write(self.dumps([self]))
			if self.imported_name:
				mod = importlib.import_module(self.imported_name)
		else:
			if self.imported_name:
				mod = sys.modules[self.imported_name]
		return mod

class RemotePythonObject(object):

# class RemotePythonObject(object):
	def __init__(self, package_path, module_name=None, attribute_name=None):
		'''
		Args:
			pacakge_path: str
				PEP-508 styled package requirement string
			module_name: str or None
				the imported module_name. default to package_name extracted from package_path
			attribute_name:
				the name to be imported from the given module

		'''

		# if len(args)==3:
		# 	package_path, module_name, attribute_name = args
		# if len(args)==2:
		# 	package_path, attribute_name = args
		# 	module_name = None
		self.package = PythonPackage(package_path, None)
		module_name = module_name or ''
		if ':' in module_name:
			assert attribute_name is None
			module_name,attribute_name = module_name.split(':',1)
		if module_name.startswith('TOPLEVEL'):
			module_name = module_name.replace('TOPLEVEL',self.package.package_name)
		self.module_name = module_name or self.package.package_name
		self.attribute_name = attribute_name
	def __repr__(self):
		return ("{self.__class__.__name__}"
		"("
			"attribute_name={self.attribute_name!r},"
			"module_name={self.module_name!r}"
		")").format(**locals())
	def loaded(self):
		self.package.loaded()
		mod = importlib.import_module(self.module_name)
		if self.attribute_name is not None:
			mod =  getattr(mod, self.attribute_name)
		return mod

	def to_ident(self):
		return sorted(self.__dict__.items())

ModuleAttr = RemotePythonObject
PythonModuleAttr = RemotePythonObject
PythonFunction = RemotePythonObject
PythonClass = RemotePythonObject
RPO = RemotePythonObject
import json
def get_identity(lst, out = None, verbose=0, strict=0):
	'''
	Append to file names with their mtime and st_size
	'''
	this = get_identity
	assert out is None
	out = []
	debug = 0
	verbose = 0
	# assert isinstance(lst, (tuple, list)),(type(lst), lst)
	flist = list_flatten(lst)
	# print('[lst]',lst,'\n[flist]',flist)
	for ele in flist:
		if  isinstance(ele, Prefix):
			res = ele.fileglob("*", ele is InputPrefix)
			###### exclude outward_edges for DIR_LAYOUT=flat
			res = [x for x in res if x not in [ ele+'.outward_edges', ele+'.outward_edges_old']]
			print('[expanding]\n  %r\n  %r'%(ele,res)) if verbose else None
			res = get_identity( res, None, verbose, strict)
			out.append( res)

		elif isinstance(ele, (File, HttpResponse, )):
			print('[identing]%r'%ele) if verbose else None
			res = ele.to_ident() #### see types.File, use (mtime and st_size) to identify
			# stat = os_stat_safe(ele)
			# res = (ele, stat.st_mtime, stat.st_size)
			out.append(res)	

		elif hasattr(ele, 'to_ident'):
			# assert 0,'call to_ident() yourself before passing into get_files()'
			#### Caller.to_ident()
			res = ele.to_ident()
			res = get_identity( res, None, verbose, strict)
			out.append( res)

		elif isinstance(ele,spiper._types.Code):
			res = (ele.co_code, get_identity(ele.co_consts, None, verbose, strict))
			out.append(res)
			print('[identing]%s,%s'%(ele.co_code,ele.co_consts)) if verbose else None

			if debug:
				# res = (ele.co_code, [get_identity([x], [], verbose, strict) for x in ele.co_consts])
				# print([ele.co_consts)
				print(json.dumps([(type(x),x) for x in ele.co_consts],default=repr,indent=2))
				# for x in ele.co_consts
				# print(res[1])
				print(len(res[1]),list(zip(ele.co_consts,res[1:])))
				if any([isinstance(x,spiper._types.Code) for x in ele.co_consts]):
					assert 0
		elif isinstance(ele, (str,type(None),int,)):
			out.append(ele)
		else:
			if strict:
				raise UndefinedTypeRoutine("get_identity(%s) undefined for %r"%(type(ele),ele))
			out.append(ele)
	return out


# class Static(object):
# 	def __init__(self,a):
# 		pass