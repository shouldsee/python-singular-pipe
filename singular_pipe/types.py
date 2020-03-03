# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from path import Path
import glob
from collections import namedtuple
import os
from orderedattrdict import AttrDict
import six


Code = type((lambda:None).__code__)

class TooManyArgumentsError(RuntimeError):
	pass
class TooFewArgumentsError(RuntimeError):
	pass
# class NotEnoughArgumentsError(RuntimeError):
# 	pass
class TooFewDefaultsError(RuntimeError):
	pass

class IdentAttrDict(AttrDict):
	pass
class CantGuessCaller(Exception):
	pass
class UndefinedTypeRoutine(Exception):
	pass



class PicklableNamedTuple(object):
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



def list_flatten(lst, strict=0, out=None, ):
	_this = list_flatten
	if out is None:
		out = []
	assert isinstance(lst, (tuple, list)),(type(lst), lst)
	for v in lst:
		if 0:
			pass
		elif isinstance(v,dict):
			v = v.items()
			_this(v, strict, out )
		elif isinstance(v,(list,tuple)):
			_this(v, strict, out)
		else:
			if strict:
				assert isinstance(v, six.string_types),(type(v),v)
			out.append(v)
	return out
def list_flatten_strict(lst):
	return list_flatten(lst,strict=1)

def rstrip(s,suffix):
	if s.endswith(suffix):
		s = s[:-len(suffix)]
	return s



# class cached_property(object):
#     """
#     Descriptor (non-data) for building an attribute on-demand on first use.
#     Source: https://stackoverflow.com/a/4037979
#     """
#     def __init__(self, factory):
#         """
#         <factory> is called such: factory(instance) to build the attribute.
#         """
#         self._attr_name = factory.__name__
#         self._factory = factory

#     def __get__(self, instance, owner):
#         # Build the attribute.
#         attr = self._factory(instance)
#         # Cache the value; hide ourselves.
#         setattr(instance, self._attr_name, attr)
#         return attr

# class Static(object):
# 	def __init__(self,a):
# 		pass
_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
	if os.path.isfile(fname):
		return os.stat(fname)
	else:
		return _os_stat_result_null

import json

class PrefixedNode(Path):
	def get_prefix_pointer(self, config):
		idFile = IdentFile( config, self, [] , '_prefix_pointer')		
		suc = 0
		res = None
		if idFile.exists():
			with open(idFile,'r') as f:
				s = json.load(f)[0]
				# s = f.read()
				suc = 1
				res = Prefix(idFile.dirname()/s)

		return suc,res

	def callback_output(self, caller, name):
		# pass
		fn = self
		idFile = IdentFile( caller.config, fn, [] , '_prefix_pointer')
		with open(idFile,'w') as f:
			json.dump( [ caller.prefix_named.relpath(idFile.dirname())], f)

			# f.write( self.relpath(idFile.dirname()) )
# tups =(prefix_job, self.DIR/'root','/tmp/pjob',)
# job = force_run(*tups)

class File(PrefixedNode):
	def __init__(self,*a,**kw):
		super(File,self).__init__(*a,**kw)
	def to_ident(self,):
		stat = os_stat_safe(self)
		res = (self, stat.st_mtime, stat.st_size)
		return res



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
	def __init__(self,*a,**kw):
		super(Prefix, self).__init__(*a,**kw)
	def callback_output(self, caller, name):
		super().callback_output(caller, name)
		fs = self.fileglob('*',strict=1)
		for fn in fs:
			idFile = IdentFile( caller.config, fn, [] , '_prefix_pointer')
			with open(idFile,'w') as f:
				json.dump( [ self.relpath(idFile.dirname())], f)
				# f.write(self.relpath(idFile.dirname()))
		return 
	def fileglob(self, g, strict):
		res = [File(x) for x in glob.glob("%s%s"%(self,g))
		if not x.endswith('.outward_edges') and not x.endswith('.outward_edges_old') and not x.endswith('._prefix_pointer')
		]
		if strict:
			assert len(res),'(%r,%r) expanded into nothing!'% (self,g)
		# return [File(str(x)) for x in glob.glob("%s%s"%(self,g))]
		return res

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


def IdentFile(config, prefix, job_name, suffix):
	prefix = Prefix(prefix)
	# if  callable(job_name):
	# 	import pdb;pdb.set_trace();
	if config == 'clean':
		pre_dir = prefix.dirname()
		pre_base = prefix.basename()
		lst = ['{pre_dir}/_singular_pipe/{pre_base}'.format(**locals()),
				job_name,suffix]
		# input_ident_file = '{pre_dir}/_singular_pipe/{pre_base}.{job_name}.{suffix}'.format(**locals())
	elif config == 'flat':
		lst = [prefix,job_name,suffix]
		# input_ident_file = '{prefix}.{job_name}.{suffix}'.format(**locals())
	input_ident_file = '.'.join(list_flatten_strict(lst))
	return File(input_ident_file)
	pass

class CacheFile(OutputFile):
	pass


from collections import OrderedDict as _dict
import requests
import json
# class HttpCheckLengthResult(object):
class HttpResponse(object):
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
	@property
	def response(self):
		x = requests.request( self.method, self.url, **self.kwargs)
		return x

	@property
	def text(self):
		return self.response.text

	def to_ident(self,):
		x = self.response
		d = x.headers
		return (self.__dict__, d['Content-Length'], d['Content-Type'], x.text)


class HttpResponseContentHeader(HttpResponse):
	def __init__(self,url,**kwargs):
		super().__init__('head', url,**kwargs)
