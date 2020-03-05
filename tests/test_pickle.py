import io
import pickle

class MyClass:
    my_attribute = 1

class MyPickler(pickle.Pickler):
    def reducer_override(self, obj):
        """Custom reducer for MyClass."""
        print(obj.__class__)
        if getattr(obj, "__name__", None) == "MyClass":
            return type, (obj.__name__, obj.__bases__,
                          {'my_attribute': obj.my_attribute})
        else:
            # For any other object, fallback to usual reduction
            return NotImplemented

def _dump(obj,f,protocol=None):
	p = MyPickler(f,protocol)
	p.dump(obj)

def _dumps(obj, protocol=None):	
	f = io.BytesIO()
	p = MyPickler(f,protocol)
	p.dump(obj)
	return f.getvalue()

del MyClass

unpickled_class = pickle.loads(f.getvalue())

assert isinstance(unpickled_class, type)
assert unpickled_class.__name__ == "MyClass"
assert unpickled_class.my_attribute == 1
