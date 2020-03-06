import io
import pickle

class MyClass:
	my_attribute = 1

class MyPickler(pickle._Pickler):
	def __init__(self, file, protocol=None, fix_imports=True):
		super().__init__(file, protocol,fix_imports=fix_imports)
		self.modules=set()

	def save(self, obj, save_persistent_id=True):
		if isinstance(obj, type):
			# self.modules.add(obj.__module__.__module__)
			# split('.',1)[0])
			self.modules.add(obj.__module__.split('.',1)[0])
		# print('[saving]%r'%(obj,))
		# print(type(obj))
		print('[saving]',type(obj).__module__,type(obj),repr(obj))
		super().save(obj,save_persistent_id)
		

def _dump(obj,f,protocol=None):
	p = MyPickler(f,protocol)
	p.dump(obj)

def _dumps(obj, protocol=None):	
	f = io.BytesIO()
	p = MyPickler(f,protocol)
	p.dump(obj)
	return f.getvalue(), p.modules

if __name__ =='__main__':
	# del MyClass
	import json
	# print(json.dumps(list(MyPickler.dispatch_table.items()),default=repr,indent=2))
	# print(json.dumps(list(MyPickler.dispatch.items()),default=repr,indent=2))
	res = _dumps( (MyClass()),protocol=4)
	print(res)
	assert 0
	# unpickled_class = pickle.loads(f.getvalue())

	assert isinstance(unpickled_class, type)
	assert unpickled_class.__name__ == "MyClass"
	assert unpickled_class.my_attribute == 1
