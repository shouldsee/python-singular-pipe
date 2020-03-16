import six


class StringUtil(object):
	pass
class Concat(StringUtil):
	def __init__(self,*args):
		self.args = args
	def flatten(self, strict, out, target):
		out = [list_flatten([x],strict,[],target) for x in self.args]
		if target=='flatten':
			out = sum(out,[])
		elif target =='str':			
			out = ''.join(out)
		return out

# def list_leaf(lst, strict=0, target='leaf'):
# 	return list_flatten(lst,strict, None, target)

def list_to_string(lst,strict=0,out=None,target='str'):
	return list_flatten(lst,strict,out,target)
def list_flatten(lst, strict=0, out=None, target='flatten' ):
	_this = list_flatten
	out = None
	out = []
	assert isinstance(lst, (tuple, list, dict)),(type(lst), lst)
	if isinstance(lst,dict):
		lst = lst.items()
	for v in lst:
		if 0:
			pass
			_this(v, strict, out, target)
		elif isinstance(v,(list,tuple)):
			vo = _this(v, strict, None, target)
		elif isinstance(v,StringUtil):
			vo = v.flatten(strict, None, target)
			# out.extend( v.flatten(strict, None, target) )
			# _this(_v, strict, out, target)
		else:
			if strict:
				assert isinstance(v, six.string_types),(type(v),v)
			if target=='str':
				vo = str(v)
			elif target=='flatten':
				vo = [v]
			else:
				assert 0,target

		if target =='str':
			out.append(vo)
		elif target =='flatten':
			out.extend(vo)

	if target =='str':
		out = ' '.join(out)
	elif target == 'flatten':
		pass
	else:
		assert 0,target
	return out

def list_flatten_strict(lst, **kw):
	return list_flatten(lst,strict=1,**kw)

def rstrip(s,suffix):
	if s.endswith(suffix):
		s = s[:-len(suffix)]
	return s

def rgetattr(obj,attr):
    _this_func = rgetattr
    sp = attr.split('.',1)
    if len(sp)==1:
        l,r = sp[0],''
    else:
        l,r = sp
        
    obj = getattr(obj,l)
    if r:
        obj = _this_func(obj,r)
    return obj

def resolve_spiper(obj, url):
	_this = resolve_spiper
	if not url:
		return obj
	else:
		sp = url.split('..',1)	
		if len(sp)==1:
			l,r = sp[0],''
		else:
			l,r = sp

		o = obj.__getitem__(l)
		o = _this(o, r)
		return o


def rgetattr_dft(obj,attr,dft):
    _this_func = rgetattr_dft
    sp = attr.split('.',1)
    if len(sp)==1:
        l,r = sp[0],''
    else:
        l,r = sp
        
    obj = getattr(obj, l, dft)
    if r:
        obj = _this_func(obj, r, dft)
    return obj       
