from singular_pipe.test.base import debugTestRunner,SharedObject
from singular_pipe.test.base import prefix_job,http_job2
import unittest2
self = SharedObject
from singular_pipe.runner import force_run,cache_run,cache_run_verbose
from singular_pipe.types import *
import singular_pipe.runner
import json
from singular_pipe.graph import graph_from_tree, nodes_only
import singular_pipe.graph
def dimple_job(self,prefix,
	s=str,  
	digitFile=InputFile, 
	letterFile=InputFile,
	_output=[File('out_txt')]):
	[x for x in range(10)]
	with open( self.output.out_txt, 'w') as f:
		print(s*10)
		f.write(s*10)
	return self
class SharedObject(SharedObject):
	def get_tree1(self,http=0):
		if http:
			tups = ( http_job2, self.DIR/'root',)
			res0 = cache_run(*tups,verbose=0)
			tups = (dimple_job, self.DIR/'root', 'ATG', res0.output.cache, '/tmp/letter.txt')
		else:
			tups = (dimple_job, self.DIR/'root', 'ATG',  '/tmp/digit.txt', '/tmp/letter.txt')

		res1 = force_run(*tups,verbose=0)

		tups = (dimple_job, self.DIR/'job2', 'ATG',res1.output.out_txt, '/tmp/digit.txt')
		res2 = force_run(*tups,verbose=0)

		tups = (dimple_job, self.DIR/'job3', 'ATG',res1.output.out_txt, res2.output.out_txt)
		res3 = force_run(*tups,verbose=0)

		fn = File('/tmp/digit.txt')
		f2 = res3.output.out_txt
		tree = None
		# tree = singular_pipe.runner.get_downstream_tree(fn, flat=0,strict=0)	
		return fn, f2, tree
class Case(unittest2.TestCase, SharedObject):
	# DIR = SharedObject.DIR
	# DATA_DIR = SharedObject.DATA_DIR

	# def test_graph_nodes_only(self):
	# 	from singular_pipe.graph import nodes_only
	# 	from singular_pipe.graph import plot_node_graph
	# 	fn,fo,tree = self.get_tree1()

	# 	g = graph_from_tree(tree,last = fn)
	# 	g.render(filename= 'tests/test_graph_1.dot',format='svg')

	# 	tree = nodes_only(tree)
	# 	g = plot_node_graph(tree,None)
	# 	g.render(filename='tests/test_graph_nodes_only.dot',format='svg')

	# 	# import json
	# 	# assert 0,json.dumps(tree,default=lambda x:x.prefix_named,indent=2)

	# def test_graph1(self):
	# 	fn, fo, tree = self.get_tree1()
	# 	g = graph_from_tree(tree,last = fn)
	# 	g.render(filename= self.DIR / 'graphs'/ fn,format='svg')
	# 	# assert 0,out
	# 	# len(out)

	def test_graph_2(self):
		THREADS = 2
		DATA_DIR = Path(__file__).dirname().realpath()/'tests/data'

		fn = File('/tmp/pjob.txt'); fn.touch() if not fn.isfile() else None
		tups =(prefix_job, self.DIR/'root','/tmp/pjob',)
		job1 = job = force_run(*tups)

		tups =(prefix_job, self.DIR/'root2', job.output.out_prefix,)
		job = force_run(*tups)
		fn = File( job1.output.out_prefix  + '.1')
		fn = File('/tmp/pjob.txt')

		##### dependency is to Prefix, not to File
		# fn = Prefix(fn[:-4])
		print('###### [TBI]test_graph_2 fix this')		
		return 
		tree = singular_pipe.graph.get_downstream_tree([fn], flat=0,strict=0)
		g = graph_from_tree(tree,last = fn)
		g.render(filename= self.DIR / 'graphs'/ fn,format='svg')
		print(json.dumps(tree,indent=2,default=repr))

		# assert 0,(g,out)

	def test_ascii_tree(self):
		from singular_pipe.graph import _tree_as_string
		pass
	def test_upstream(self):
		fn, fo, tree = self.get_tree1(http=1)
		from singular_pipe.graph import plot_simple_graph,plot_node_graph,tree_filter
		from singular_pipe.graph import get_upstream_tree

		res = get_upstream_tree([fo],0,)
		g = plot_simple_graph(res,None,1)
		g.render(filename='tests/test_upstream.dot',format='svg')

		from singular_pipe.runner import Caller

		filtered = tree_filter( res, (Caller,))
		g = plot_node_graph(filtered,None)
		g.render(filename='tests/test_upstream.node_only.dot',format='svg')

		print('######## test_upstream ############')
		print(res)
		print(filtered)

	def test_downstream(self):
		fn, fo, tree = self.get_tree1(http=1)
		from singular_pipe.graph import plot_simple_graph,plot_node_graph,tree_filter
		from singular_pipe.graph import get_downstream_tree

		res = get_downstream_tree([fn],0,)
		g = plot_simple_graph(res,None,1)
		g.render(filename='tests/test_downstream.dot',format='svg')

		from singular_pipe.runner import Caller
		filtered = tree_filter( res, (Caller,))
		g = plot_node_graph(filtered,None)
		g.render(filename='tests/test_downstream.node_only.dot',format='svg')

		print('######## test_downstream ###############')
		print(res)
		print(filtered)
		# print(res2)
		# import pdb;pdb.set_trace()
		# print(_tree_as_string(res))
	# print

if __name__ == '__main__':

	print('[testing]%s'%__file__)
	# with SharedObject.DIR:
	if '--pdb' in sys.argv:
		del sys.argv[sys.argv.index('--pdb')]
		unittest2.main(testRunner=debugTestRunner())
	else:
		unittest2.main(testRunner=None)

