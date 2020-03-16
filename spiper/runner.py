import spiper
from spiper import rcParams
from spiper import VERSION,jinja2_format

import spiper._types
from spiper._types import File,InputFile,OutputFile
from spiper._types import IdentFile,CacheFile, AttrDict
# from spiper._types import InputFile,OutputFile,File,TempFile,? ,Path,
from spiper._types import Prefix,InputPrefix,OutputPrefix
from spiper._types import HttpResponse
from spiper._types import IdentAttrDict

from spiper._types import CantGuessCaller, UndefinedTypeRoutine
from spiper._types import TooManyArgumentsError
from spiper._types import NodeFunction,FlowFunction
from spiper._types import DirtyKey

# from spiper._types import FakeCode,FakeJob

from spiper.base import get_func_name, list_flatten,list_flatten_strict
from spiper.base import job_from_func

from  spiper._pickler import MyPickleSession


import os,sys,shutil
import io
import inspect
import json

from itertools import zip_longest
from collections import namedtuple
import collections
from functools import partial
from orderedattrdict import AttrDict as _dict
# _dict = collections.OrderedDict

def _dumps(obj):
	return MyPickleSession().dumps_b64(obj)

def _loads(obj):
	return MyPickleSession().loads_b64(obj)

def ident_load(ident_file,key):	
	ident_dump_old = ''
	try:
		if file_not_empty(ident_file):
			ident_dump_old = json.loads(open(ident_file,'r').read())[key]
			# ident_dump_old = str(json.loads(open(ident_file,'r').read())[key])
	except Exception as e:
		raise e
		print(e)
	return ident_dump_old

def ident_changed(ident, ident_file, key):
	ident_dump = MyPickleSession().dumps_b64(ident)
	ident_dump_old = ident_load( ident_file, key )
	return ident_dump != ident_dump_old


def ident_dump(d, ident_file, comment=[],version=VERSION):	
	if isinstance(ident_file, io.IOBase):
		f = ident_file
	else:
		f = open(ident_file,'w')
	with f:
	# with open(ident_file,'w') as f:
		# assert 0
		_d = _dict([
			('version',version),
			# ('comment',comment),
			# ('ident', _dumps(ident) ),
			] + list(_dict(d).items()))

		json.dump(_d,
			f,
			indent=2,
		)
		# collections.OrderedDict
		# pickle.dump( ident,  f )

def _raise(e):
	raise e


def func_orig(func):
	while True:
		if hasattr(func,'__wrapped__'):
			func = func.__wrapped__
		elif hasattr(func,'__func__'):
			func = func.__func__
		else:
			break
	return func


def FakeCode(code):
	# out = (code.co_code, [])
	consts = []
	for const in code.co_consts:
		if isinstance(const, spiper._types.Code):
			consts.append( FakeCode(const) )
		else:
			consts.append( const )
	return FakeCode._codecls( code.co_code, consts)
FakeCode._codecls = _cls= namedtuple('_codecls','co_code co_consts')
_cls.__qualname__ = 'FakeCode._codecls'

class FakeJob(object):
	# code_tree = code_tree
	_codecls = FakeCode._codecls
	def __init__(self,job):
		self.__name__     = job.__name__
		self.__code__     = FakeCode( job.__code__) 
		# self.__code__     = self._codecls( job.__code__.co_code, job.__code__.co_consts)
		self.__qualname__ = job.__qualname__
		self.__module__   = str(job.__module__)
		self._output_type = job._output_type
	# def code_tree(self):
		# self.__code__  = 
		return 

class SubflowOutput(object):
	def __str__(self):
		return self.key

	def __init__(self, key, name=None):
		raise NotImplementedError
		# assert 'SubflowOutput' i
		if name is None:
			name = key
		self.name = name
		self.key  = key

	pass

def is_mock_file(v, call=None,):
	if (v+'.old.mock').isfile():
		call(v,v+'.old.mock') if call is not None else None
		return 1
	if (v+'.empty.mock').isfile():
		call(v,v+'.empty.mock') if call is not None else None
		return 1
	return 0


			

def _get_changed_files(caller):
	return _get_all_files(caller, 1)
def _get_all_files(caller, changed):
	lst = []
	for f in caller.output.values():
		if not changed or is_mock_file(f):
			lst.append(f)
	for flow in caller.subflow.values():
		res = _get_all_files(flow, changed)
		lst.append( res)
	return lst				

		
class Caller(object):
	def get_changed_files(self,flat=1):
		res = _get_changed_files(self)
		if flat:
			res = list_flatten(res)
		return res

	def get_all_files(self,allow=[File],flat=1,):
		res = _get_all_files(self, 0)
		if flat:
			res = list_flatten(res)
			if allow:
				#### [FRAGILE]
				res = [x for x in res if type(x) in allow]
		return res

	def is_mock_file(self,v,call):
		return is_mock_file(v,call)

	@property
	def job_type(self):
		return self._job_type
	
	@property
	def output_cache_file(self):
		# return self._foo
		return IdentFile( self.dir_layout, self.prefix_named, [], 'cache_pk')

	@property
	def output(self):
		return self._output_dict
		# _caller  = self
		# if issubclass(_caller.job_type,(spiper._types.FlowFunction)):
		_ = '''
		output can be derived before evaluation
		'''
		pass

		#### calculate output files
		### cast all files all as prefix
		### here we add cache_file as a constitutive output.		
		return self._output_dict

		# return get_output_files( self.job, self.prefix, self._output_type._typed_fields)

	@property
	def f(self):
		return func_orig(self.job)
	@property
	def prefix(self):
		return (self.arg_tuples[0][1])
	@property	
	def prefix_named(self):
		if self.named:
			return self.prefix+'.%s'%self.__name__
		else:
			return self.prefix
		# '.'.join([self.prefix+]

	@property
	def arg_values(self):
		self._arg_values = [v for k,v in self.arg_tuples[:] if not k.endswith('_')]
		return self._arg_values
	@property
	def dotname(self):
		return "%s.%s"%( (inspect.getmodule(self.f) or object()).__name__, self.f.__qualname__)
	@property
	def subflow(self):
		return self._subflow
	
	def get_subflow(self,k):
		return self.subflow[k]
	def get_output(self,k):
		return self.output[k]

	def get_output_files( self ):
		return list(self.output.values())
		# res = self.output
		# # res += (CacheFile(self.output_cache_file),)
		# return list(res.values())
	# @staticmethod
	def is_mock(self,call=lambda *x:None,fast=1):
		mock = 0
		for k,v in self.output.items():
			mock = self.is_mock_file(v,call)
			if mock: 
				break
		return mock

	@classmethod
	def from_input(Caller, job, _input, dir_layout, tag):
		if not getattr(job,'_spiper',False):
			job = job_from_func(job)
		# _tmp  = []
		_tmp  = AttrDict()
		_null = namedtuple('_null',[])()
		_zip = lambda: zip_longest(job._input_names, job._input_types, _input,fillvalue=_null)
		_dump = lambda: json.dumps([repr(namedtuple('tuple','argname type input_value')(*x)) for x in _zip()],indent=0,default=repr)
		for n,t,v in _zip():
			if n[0]=='_':
				if v is not _null:
					raise TooManyArgumentsError('{dump}\nToo many arguments specified for {job._origin_code}\n argname started with _ should not have input_value \n'.format(
						dump=_dump(),**locals()))
				else:
					## v is _null, t is default value
					# _tmp.append((n,t))
					if callable(t):
						t = t(args = _tmp)
					_tmp[n] = t
			elif v is _null:
				raise spiper._types.TooFewArgumentsError(
					'{dump}\nToo few arguments specified for {job._origin_code}\n normal argname are without "_" are necessary for evaluation \n'.format(
				dump=_dump(),**locals()))
			else:
				if not isinstance(v,t):
					v = t(v)
				_tmp[n] = v
		# _tmp.setdefault('_single_file',0)
		# for k,v in _tmp.items():
		# 	if isinstance(v,Caller):
		# 		self.upstream
				# _tmp.append( (n, t(v)) )
		# assert isinstance(_tmp[0]
		_caller = Caller( job, _tmp, dir_layout, tag)
		# _caller = Caller( job, list(_tmp.items()), dir_layout, tag)
		return _caller
	def __getitem__(self,k):
		return getattr(self,k)
	def __getstate__(self):
		d = self.__dict__.copy()
		job = self.job
		d['job'] = FakeJob(job)
		d['runner'] = None
		d['config_runner'] = None
		# d['returned'] = ('LoadFrom',self.output_cache_file)
		return d

	def __setstate__(self,d):
		self.__dict__ = d

	def __init__(self, job, arg_dict, dir_layout, tag):
		# if not getattr(job,'_spiper',False):
		# 	job = job_from_func(job)		
		arg_tuples = list(arg_dict.items())
		arg_dict.setdefault('_single_file', 0)
		self.named = arg_dict._single_file == 0
		assert isinstance(arg_tuples[0][1], File),(arg_tuples[0])
		# arg_tuples[0] = ('prefix', (arg_tuples[0][1]).expand().realpath())
		for i,(k,v) in enumerate(arg_tuples):
			if isinstance(v,(Prefix, File)):				
				arg_tuples[i] = (k,v.expand().realpath())
		if not hasattr(job,'_type',):
			job = spiper._types.Node(job)
		# self.named = named = job._type.named
		# named = True
		if self.named:
			if tag: assert DirtyKey(tag) == tag,(tag,DirtyKey(tag))
			assert isinstance(tag,(type(None),str)),(type(tag),tag)
			tag  = tag or []
			_tag = '_'.join(list_flatten([ job.__name__, tag]))
		else:
			# _tag = self.prefix
			_tag = arg_tuples[0][1]
			# _tag = job.__name__
		self.__name__     = _tag
		self.job          = job
		self._output_type = job._output_type
		self._job_type    = self.job._type
		assert self._job_type is not None
		self.arg_tuples   = arg_tuples
		self.dir_layout   = dir_layout
		self._subflow     = _dict()


		### create output directory
		self.prefix_named.dirname().makedirs() if not self.prefix_named.dirname().isdir() else None

		### initialise FlowFunciton._output_dict differently by mock_do and mock_undo
		self._output_dict = self._get_output_files( self.prefix, self._output_type._typed_fields)
		self._output_dict['_cache_file'] = CacheFile(self.output_cache_file)
		if not self.named:
			self._output_dict['prefix_file'] = File(self.prefix_named)
		for k in self._output_dict:
			self._output_dict[k] = self._output_dict[k].expand().realpath() 
		self.runner = None


	def _get_output_files( self, prefix, _output_typed_fields):
		'''
		Assuming all output_files are Prefix because types arent checked
		'''
		tups = []
		for s in _output_typed_fields:
			# print('[get-output]',s,type(s))
			if not isinstance(s,(Prefix,File,)):
				### Assuming type is File  if unspecified
				assert isinstance(s,str),(type(s),s)
				typ = File
			else:
				typ = type(s)

			s = "{self.prefix_named}.{suffix}".format(suffix = s, **locals())
			s = typ(str(s))
			assert not isinstance(s, (InputFile,InputPrefix)),('Must be Ouputxxx not Input...,%r'%s)
			tups.append(s)

		tups = self._output_type(*tups)
		return tups		
		# if self.subflow:
		# 	self._subflow.clear()
		# 	self( partial(mock_run,last_caller=self,mock=-1) )
			# self(mock_undo)	
		return tups		
	def to_ident(self):
		'''
		
		'''
		### argument to jobs without prefix
		### argument with name ending with '_' will be discarded in idenitty
		# _job_args = [v for k,v in self.arg_tuples[1:] if not k.endswith('_')]
		# _job_args = [v for k,v in self.arg_tuples[:] if not k.endswith('_')]
		# _job_args = list(zip(*self.arg_tuples[1:])) 
		_input = [
			FakeCode( self.f.__code__),
			self.arg_values,
		]		
		return _input
	def to_dict(self):
		'''
		For visualisation / json.dumps
		'''
		f = self.f
		res = collections.OrderedDict([
				('job', repr(f.__code__)),
				('dotname',self.dotname),
				# ('dotname',"%s.%s"%(inspect.getmodule(f).__name__, f.__qualname__)),
				('arg_tuples', collections.OrderedDict([
					(
						k,
						"%s.%s::%s"%(type(v).__module__,type(v).__qualname__, repr(v).strip('"'"'") ),
						# str(type(v))+':'+repr(v).strip('"'"'") ,
						# _raise(Exception())
					) for k,v in self.arg_tuples
					if not k.endswith('_')
					]) ),
				# ('co_code',f.__code__.co_code),
				# ('co_consts',f.__code__.co_consts),
				])
		return res		

	def __repr__(self):
		f = self.f
		return '%s.%s(%s)'%(
			self.__class__.__module__,
			self.__class__.__name__,
			','.join(['%s=%r'%(k,getattr(self,k)) for k in ['dotname','prefix_named']]),
			# self.dotname, self.prefix_named,
			# json.dumps( self.to_dict(),
			# indent=2,default=repr)
			)

	def cache(self, obj, check=1):
		assert not self._cached,"Cannot cache twice in a function"
		assert self._allow_cache, "self.cache is not available for %r"%(self.job_type,)
		with open( self.output_cache_file,'wb') as f: 
			p = MyPickleSession()
			p.dump_sniff( obj, f)
		with open( self.output_cache_file+'.json','w') as  f:
			json.dump( dict(modules=p.pop_modules_list()), f, indent=2)
		self._cached = True

	def load_cache(self, ):
		if self.is_mock():
			output_cache_file = self.output_cache_file + '.old.mock'
		else:
			output_cache_file = self.output_cache_file
		with open(self.output_cache_file+'.json','r') as f:
			modules = json.load(f)['modules']
		## inplement modules check
		with open(output_cache_file,'rb') as f: 
			result = MyPickleSession().load(f)
		return result 

	def __call__(self, runner, config_runner=None):
		if not isinstance(runner,partial):
			runner = partial(runner)
		self.runner = runner
		self.config_runner = config_runner
		# self.runner = partial( runner, last_caller=last_caller)
		if issubclass(self.job_type, NodeFunction):
			self._cached = False
			self._allow_cache = 1
			returned = self.job(self, *[x[1] for x in self.arg_tuples])
			assert returned in [self,None],"Return statement is disallowed in NodeFunction. Use self.cache(obj) instead or decorate as @Flow"			
			returned = self
			if not self._cached:
				self.cache(returned,)
			# return self
		else:
			self._cached = False
			self._allow_cache = 0
			returned = self.job(self, *[x[1] for x in self.arg_tuples])
			self._allow_cache = 1
			self.cache(returned)

		self.config_runner = None
		self.runner = None
		return returned


	def mock_undo(self,strict,verbose):
		_caller = self
		# print(self)
		# verbose = 4
		for k,v in _caller.output.items():
			if (v+'.old.mock').isfile():
				(v+'.old.mock').move(v.unlink())
				print('[REMOVING.mock]%s.old.mock'%v) if verbose >=4 else None

			if (v+'.empty.mock').isfile():
				(v+'.empty.mock').unlink()
				v.unlink()
				print('[REMOVING.mock]%s.empty.mock'%v) if verbose >= 4 else None
			else:
				print('[SPARING.mock]%s'%v) if verbose >= 4 else None
		(_caller.output_cache_file+'.output_changed.mock').unlink_p()
		if strict:
			assert not _caller.is_mock(lambda *x:print(x) if verbose >=5 else None)		
	def mock_do(self, output_ident_changed, strict,verbose):
		_caller = self
		# print(self)
		# verbose = 4
		for k,v in _caller.output.items():
			f = v
		# for f in v.expanded():
			if f.isfile():
				if not (f+'.old.mock').isfile():
					f.move(f+'.old.mock')
					f.touch()
			else:
				(f+'.empty.mock').touch()
				f.touch()
			print('[CREATING.mock]%s'%f) if verbose >=4 else None
		if output_ident_changed:
			(_caller.output_cache_file+'.output_changed.mock').touch()	

		### [need:test] test permission for writing
		outward_dir_list = get_outward_json_list( self.arg_tuples, self.dir_layout)
		[ outward_dir.makedirs_p().access(os.W_OK) for outward_dir in outward_dir_list]

		if strict:
			assert _caller.is_mock(lambda *x:print(x) if verbose >=5  else None)		
				
	def to_table_node_label(self):
		# node = self
		s = '''
	<		
	<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
	  <TR>
	    <TD ALIGN="LEFT" BGCOLOR="lightblue">attr</TD>
	    <TD ALIGN="LEFT" BGCOLOR="lightblue">type</TD>
	    <TD ALIGN="LEFT" BGCOLOR="lightblue">value</TD>
	  </TR>

	  {# <TR>
	  	<TD ALIGN="LEFT">Prefix</TD>
	    <TD ALIGN="LEFT">{{node.prefix}}</TD>
	  </TR>
	  #}
	  	{% for k,v in [('dotname',node.dotname),('prefix_named', node.prefix_named)] +node.arg_tuples[:] %}
		  <TR>
		  	<TD ALIGN="LEFT">{{k}}</TD>
		  	<TD ALIGN="LEFT">{{v.__class__.__name__}}</TD>
		    <TD ALIGN="LEFT">{{v}}</TD>
		  </TR>
	    {% endfor %}
	</TABLE>
	>
	'''.strip()
		return jinja2_format(s, node=self)
		# return s.format(self=self)
# DEFAULT_DIR_LAYOUT = 'clean'
def force_run(job, *args,**kw):
	'''
	Run a jobs regardless of whether it has a valid cache
	'''
	return cache_run(job,*args,force=True,**kw)
	_input = args
	res = job(*_input)
	return res
def cache_check(job, *args,**kw):
	'''
	Check whether there is a valid cache for this job
	'''
	return cache_run(job,*args, check_only=True,**kw)
def cache_check_changed(job, *args,  check_changed=1,**kw):
	return cache_run(   job,  *args, check_changed=check_changed,**kw)

def cache_run_verbose(job,*args, verbose=1, **kw):
	return cache_run(job,*args,verbose=verbose,**kw)

def mock_run(job, *args, mock = 1, **kw):
	return cache_run(job,*args, mock=mock,**kw)

def mock_undo(job, *args, mock = -1, **kw):
	return cache_run(job,*args, mock=mock,**kw)

def get_changed_files(job, *args, allow=[File],flat=1, **kw):
	res = mock_run(job,*args,**kw).get_changed_files(flat)
	mock_undo(job,*args,**kw)
	if allow:
		#### [FRAGILE]
		res = [x for x in res if type(x) in allow]
	return res

def get_all_files(job, *args, allow=[File],flat=1, **kw):
	res = mock_run(job,*args,**kw).get_all_files(allow=allow,flat=flat)
	mock_undo(job,*args,**kw)
	return res
	# if allow:
	# 	#### [FRAGILE]
	# 	res = [x for x in res if type(x) in allow]
	# return res	

# symbolicResult =  object()
# def cache_run(job, *args, dir):

def cache_run(job, *args,
	dir_layout = None,
	mock = False,
	check_only=False, check_changed=False, force=False,verbose=0,
	last_caller = None):
	dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
	# print('[dir_layout]',dir_layout)
	# print('[id2]',id(rcParams),rcParams)
	return _cache_run(job,args,dir_layout,mock,check_only,check_changed,force,verbose,last_caller)

def _cache_run(job, args, dir_layout,mock,check_only,check_changed,force,verbose, last_caller):
	return _Runner(dir_layout,mock,check_only,check_changed,force,verbose).run(job, *args,last_caller=last_caller)

class _Runner(object):
	def __init__(self, dir_layout,  mock, check_only,check_changed,force,verbose ):
		self.dir_layout = dir_layout
		self.mock = mock
		self.check_only = check_only
		self.check_changed = check_changed
		self.force = force
		self.verbose = verbose
	def before_run(self, job, args):
		pass
	def after_run(self, job, args):
		pass

	def run(self, job, *args, last_caller = None, tag = None):
		result = self._run(job, args, last_caller, tag)
		return result
	__call__ = run

	def _run(self, job, args, last_caller, tag):
		'''
		return: job_result
			Check whether a valid cache exists for a job receipe.
			Load cache as result if so, otherwise recalculate the job.

		##### we want to avoid re-calculating the output if they already exist and is intact
		##### this is done by storing an identity information on disk 
		##### this identity information is calculated from the outputted files
		##### which could be md5sum or timestamp		
		'''
		dir_layout      = self.dir_layout
		mock            = self.mock
		check_only      = self.check_only
		check_changed   = self.check_changed
		force           = self.force
		verbose         = self.verbose


		_caller         = Caller.from_input(job, args, dir_layout, tag)
		###### the _input is changed if one of the func.co_code/func.co_consts/input_args changed
		###### the prefix is ignored in to_ident() because it would point to a different ident_file
		#####  Caller.from_input() would also cast types for inputs
		_input          = args		
		# runner          = partial(self.run, last_caller=_caller)
		runner          = partial(self, last_caller=_caller)
		config_runner   = lambda _caller=_caller,**kw:partial(self, last_caller=_caller, **kw)
		if last_caller is not None:
			assert _caller.__name__ not in last_caller._subflow,'Duplicated subflows %s in %r '%( _caller.__name__, last_caller)
			last_caller._subflow[ _caller.__name__ ] = _caller

		print("%r\n  %r"%(last_caller,_caller)) if verbose >=2 else None
		func_name       = get_func_name()
		prefix          = args[0]
		_ = '''self.subflow needs to be appended using the runner by supplyig calling frame 
		as argument to self.run
		'''
		# def runner(job,*args,last_caller=_caller):
		# 	print("%r\n%r"%(job,last_caller))
		# 	return self.run(job,*args, last_caller=last_caller)

		_input  = [_caller.to_ident()]	
		print(repr(_caller)) if verbose >= 3 else None


		input_ident_file =  IdentFile( dir_layout, _caller.prefix_named, [] , 'input_json' )
		output_ident_file=  IdentFile( dir_layout, _caller.prefix_named, [] , 'output_json' )
		output_cache_file=  _caller.output_cache_file
		File(input_ident_file).dirname().makedirs_p().access(os.W_OK)
		_caller.output_cache_file.dirname().makedirs_p().access(os.W_OK)




		_output = _caller.get_output_files()

		# _output = get_output_files( job, prefix, job._output_type._typed_fields) + (CacheFile(output_cache_file),)
		# print('[out1]',_output)

		input_ident_changed  = ident_changed( get_identity( _input, ), input_ident_file, 'ident')
		if _caller.is_mock():
			output_ident_changed = (_caller.output_cache_file+'.output_changed.mock').isfile()
		else:
			output_ident_changed = ident_changed( get_identity( _output, ), output_ident_file,'ident')
		use_cache = not input_ident_changed and not output_ident_changed
		if check_only:
			return use_cache
		if check_changed:
			if check_changed >=2:
				input_ident = get_identity(_input)
				# input_ident_old = _loads(json.load(open(input_ident_file,'r'))['ident'])
				output_ident = get_identity(_output)
				# output_ident_old = _loads(json.load(open(output_ident_file,'r'))['ident'])
				import pdb; pdb.set_trace();
			return (input_ident_changed, output_ident_changed)

		if verbose:
			print('[{func_name}]'.format(**locals()),
				json.dumps(_dict([
				('job_name',_caller.__name__),
				('use_cache',use_cache),
				('input_ident_changed', int(input_ident_changed)),
				('output_ident_chanegd',int(output_ident_changed))])
					,separators='_=')
				# .replace('"','')
				)
			if verbose >= 2:
				import pdb; pdb.set_trace()

		if check_only:
			return bool(use_cache)		

		if force:
			use_cache = False
		# if mock:
		# 	use_cache = False

		#### if any of the output file is mock, then do not use cache
		#### if input and output are not changed, then mocking is skipped.
		# if (_caller.output_cache_file+'.mock').isfile():
		# 	use_cache = False
		# print((job.__name__,use_cache))
		if use_cache:
			result = _caller.load_cache()

		else:
			# if not issubclass(_caller.job_type, spiper._types.NodeFunc):
			# 	mock = 0
			if mock == 1:
				_ = '''
				The current file will be replaced with a mock file to propagate the signal downwards

				'''

				_caller.mock_do(output_ident_changed, 1, verbose)
				if issubclass(_caller.job_type, spiper._types.NodeFunction):
					result = _caller
				else:
					### recurse if not a Terminal Node
					result = _caller(runner, config_runner)
			elif mock == -1:
				#### unmock
				#### restore mocked file if available
				_caller.mock_undo(1, verbose)
				result = _caller

			elif mock == 0:
				_caller.mock_undo(1, verbose)
				result = _caller(runner, config_runner )

				for k,v in _caller.output.items():
					func = getattr( v,'callback_output',lambda *x:None)
					func(_caller,k)
					# method(_caller)
					# if hasattr(x,'callback_output'):
					# 	x.output_callback(_caller)				
				# ident_dump( result, output_cache_file, )
				_input_ident  = get_identity( _input)
				_output_ident = get_identity(_output)

				p = MyPickleSession()
				ident_dump( [
					('comment',[[repr(x) for x in _output],_output_ident]),
					('modules',     p.pop_modules_list(   lambda:  p.dumps_sniff_b64(_output))),
					('output_dump', p.pop_buffer()),
					('ident',       p.dumps_b64(_output_ident)),
					], 
					output_ident_file,
					)
					 # comment = [[repr(x) for x in _output],get_identity(_output)] ) ### outputs are all
				input_image = [
						('comment',      _caller.to_dict()),
						('modules',      p.pop_modules_list(  lambda: p.dumps_sniff_b64( _caller))),
						('caller_dump',  p.pop_buffer()),
						('ident',        p.dumps_b64(_input_ident)),

					]
				ident_dump( input_image, input_ident_file)
				# ident_dump( _input_ident  , input_ident_file,  comment = (_caller.to_dict(),  _dumps( _caller)))

				#### add edge_file to inputs 
				### add input and output ident to outward_pk
				# outward_dir_list = get_outward_json_list( _input, config)
				
				_input_ident_hash = p.hash_bytes( p.dumps(_input_ident) )

				outward_dir_list = get_outward_json_list( _caller.arg_tuples, dir_layout)
				for outward_dir in outward_dir_list:
					outward_dir.makedirs_p().access(os.W_OK)

				for outward_dir in outward_dir_list:
					outward_edge_file = outward_dir /  '%s.%s.json'%( DirtyKey(_caller.__name__), _input_ident_hash)
					ident_dump( input_image, outward_edge_file)			

				#### remove edge_file of outputs
				outward_dir_list = get_outward_json_list( _caller._output_dict.items(), dir_layout)
				for outward_dir in outward_dir_list:
					shutil.move(outward_dir.makedirs_p().access(os.W_OK) , (outward_dir+'_old').rmtree_p())
					outward_dir = outward_dir.makedirs_p().access(os.W_OK)
			else:
				assert 0, 'Mock value not understood mock=%r'%mock
		return result
		# return _caller, result



def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0



def _get_outward_json_file(ele, strict, dir_layout=None):
	if dir_layout is None:
		dir_layout = rcParams['dir_layout']
	if isinstance(ele, (File,Prefix)):
		fn = IdentFile(dir_layout, ele,[],'outward_edges')
		res = [fn]
	else:
		if strict:
			raise UndefinedTypeRoutine("get_identity(%s) undefined for %r"%(type(ele),ele))
		res = []
	return res	
	# return f


def get_outward_json_list( arg_tuples, dir_layout, strict=0, out = None, verbose=0,):
	if out is None:
		out = []
	for k, v in arg_tuples:
		if k =='_output':
			continue
		v = list_flatten([v])
		for ele in v:
			res = _get_outward_json_file(ele, strict,dir_layout)
			out += res
	print('[OUT]',arg_tuples, out) if verbose else None
	return out 


from spiper._types import get_identity

##################################################
##################################################
##################################################
#### the following computes closures on the DAG ##
#### aka upstream/downstream


# from spiper.graph import file_to_node
def file_to_node(obj, strict, dir_layout,):
	'''
	One can only guess the prefix by removing the suffix
	'''
	err = CantGuessCaller("Cannot guess the Caller() for %r"%obj) 

	# res = obj.rsplit('.',2)
	# if len(res)!=3:
	# 	return (_raise(err) if strict else None)
	# prefix, job_name, suffix = res 

	suc, prefix_named = obj.get_prefix_pointer(dir_layout)
	if suc:
		prefix, caller_name = prefix_named.rsplit('.',1)
		succ = 1
	else:
		return (_raise(err) if strict else None)

	input_ident_file =  IdentFile(dir_layout, prefix_named, [] , 'input_json' )
	output_ident_file = IdentFile(dir_layout, prefix_named, [] , 'output_json' )
	lst = _loads(json.load(open(output_ident_file,'r'))['ident'])  ##[FRAGILE]
	obj_ident = get_identity([obj])[0]
	'''
	[IMPLEMENT]
	strict=1 should detect a identity change
	contained in output_ident_file() -> Tracked
	not contained in output_ident_file() -> Dangling/Untracked
	'''
	if obj_ident in lst:
		x = _loads(json.load(open(input_ident_file,'r'))['caller_dump'])
	else:
		return (_raise(err) if strict else None)
	return x
