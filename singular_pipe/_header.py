import six


def list_flatten(lst, strict=0, out=None, ):
	_this = list_flatten
	if out is None:
		out = []
	assert isinstance(lst, (tuple, list, dict)),(type(lst), lst)
	if isinstance(lst,dict):
		lst = lst.items()
	for v in lst:
		if 0:
			pass
		# elif isinstance(v,dict):
		# 	v = v.items()
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
