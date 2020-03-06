'''
singular_pipe.types.Flow is preferred over recursive cache_run() when specifying a workflow.
The cache_run_deep() is more about sanity check file status 
given a boundary specified by the Flow. If no Flow is given then no tree is expanded until a
leaf node.

get_upstream_tree() already gives a tree. I need to change
the Flow execution to deposit labels into each dependent Node 
and allow the function to be terminated once this label disappear.

'''
assert 0,'[TBI]'

# def function():
#  	pass 
#  	# = models.ForeignKey()
