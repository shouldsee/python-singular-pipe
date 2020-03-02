# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from path import Path
import glob
from collections import namedtuple
import os
from attrdict import AttrDict

Code = type((lambda:None).__code__)


class TooManyArgumentsError(RuntimeError):
	pass
class TooFewArgumentsError(RuntimeError):
	pass
# class NotEnoughArgumentsError(RuntimeError):
# 	pass
class TooFewDefaultsError(RuntimeError):
	pass


# class Data(object):
# 	pass
class IdentAttrDict(AttrDict):
	pass
# 	def to_ident(self,f):
# 		return [f[]self.items()
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
		return AttrDict(v._asdict())
		# if len(v):
		# 	import pdb;pdb.set_trace()
		# 	# assert 0
		# return 


def Default(x):
	'''
	A dummy "class" mocked with a function
	'''
	return x

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


class File(Path):
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

class Prefix(Path):
	def __init__(self,*a,**kw):
		super(Prefix, self).__init__(*a,**kw)
	def fileglob(self, g, strict):
		res = [File(x) for x in glob.glob("%s%s"%(self,g))]
		if strict:
			assert len(res),'(%r,%r) expanded into nothing!'% (self,g)
		# return [File(str(x)) for x in glob.glob("%s%s"%(self,g))]
		return res
		pass
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
		input_ident_file  = '{pre_dir}/_singular_pipe/{pre_base}.{job_name}.{suffix}'.format(**locals())
	elif config == 'flat':
		input_ident_file = '{prefix}.{job_name}.{suffix}'.format(**locals())
		pass
	return File(input_ident_file)
	pass

class CacheFile(OutputFile):
	pass



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
		return json.dumps(self.__dict__,default=repr,indent=2)
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
