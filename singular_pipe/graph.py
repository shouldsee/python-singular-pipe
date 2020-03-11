from graphviz import Digraph
# from graphviz import nohtml
import graphviz
from collections import OrderedDict as _dict

import inspect
import asciitree
from asciitree.drawing import BOX_DOUBLE
import textwrap
from path import Path
# from spiper import DEFAULT_DIR_LAYOUT
from spiper._types import list_flatten
from spiper._types import Prefix,File,HttpResponse
from spiper.runner import Caller,file_to_node

class SymbolicNode(Path):
    pass
SourceNode = SymbolicNode('SOURCE')

def _tree_as_string(d):
    if len(d)!=1:
        d=dict(ROOT=d)
    box_tr = asciitree.LeftAligned(draw=asciitree.BoxStyle(gfx=BOX_DOUBLE, horiz_len=1))(d)
    return box_tr


def nodes_only(lst):
    this = nodes_only
    out = []
    for node,node_files in (lst):
        res = []
        for file,down_nodes in node_files:
            res += this(down_nodes)
        out.append( (node, res ))
    return out


def plot_node_graph(lst,g,last=None):
    this = plot_node_graph
    if g is None:
        g = Digraph('G', strict=True)
        g.attr(rankdir='TB')
    for node, edges in lst:
        if not len(edges):
            g.edge(node.prefix_named,'SINK')
        plot_node_graph(edges, g, node)
        if last is None:
            g.edge('SOURCE', node.prefix_named)
            continue

        g.edge( last.prefix_named, node.prefix_named)
        g.node( node.prefix_named, label = node.to_table_node_label(), shape='plaintext')            

    if last is not None:
        g.node( last.prefix_named, label = last.to_table_node_label(), shape='plaintext')
    return g

def plot_simple_graph_label(x):
    x = r'\l'.join(textwrap.wrap(repr(x),width=50)) 
    x = x.replace(':','_')
    return x 
def plot_simple_graph( trees, g, is_upstream,last = None):
    this = plot_simple_graph
    _label = plot_simple_graph_label
    # revi = 2*int(is_upstream) - 1
    if g is None:
        g = Digraph('G', strict=True)
        g.attr(rankdir='TB')

    if is_upstream:
        if not trees:
            g.edge(*(_label('SOURCE'), _label(last or 'SINK')))
        for node, up_trees in trees:
            this(up_trees, g, is_upstream, node)
            g.edge(*( _label(node),  _label(last or 'SINK')))
    else:        
        if not trees:
            g.edge(*(_label(last or 'SOURCE'), _label('SINK')))
        for node, up_trees in trees:
            this(up_trees, g, is_upstream, node)
            g.edge(*( _label(last or 'SOURCE'),  _label(node)))
    return g



def graph_from_tree(lst,g = None, last=None, i=None,):
    '''
    Accept a list of shape [(node,[(file,[(node,[(file,)])]),]),]
    '''
    this = graph_from_tree
    if g is None:
        g = Digraph('G', strict=True)
        g.attr(rankdir='TB')
        # g = Digraph('G', strict=0,)

    if not i:
        i = [0]
    if last is None:
        last = Path('root')
        g.node(last,label=repr(last), shape='diamond')
    out = []
    for node,node_files in (lst):
        i[0]+=1
        g.edge( last, node.prefix_named)
        g.node( node.prefix_named, label = node.to_table_node_label(), shape='plaintext')

        with g.subgraph(name='cluster_%s'%node.prefix_named) as c:
            # c.attr(label= node.dotname)
            c.attr(color='blue')
            c.node_attr['style'] = 'filled'
            nout = []
            for file,down_nodes in node_files:
                c.node(file, label='%r'%file.basename(),style='filled')
                c.edge(node.prefix_named, file)
                # .basename())
            for file,down_nodes in node_files:
                res = this(down_nodes, g, file, i)
                nout.append((file.basename(),res))
        out.append((node.prefix_named,_dict(nout)))
    return g
    # return _dict(out)


if 1:
    from spiper.runner import *

    def _get_upstream_tree( lst,strict,dir_layout):
        verbose = 0
        out = []
        for x in list_flatten(lst):
            up_nodes = _get_upstream(x, strict,dir_layout)
            up_trees = _get_upstream_tree(up_nodes, strict,dir_layout)
            print('[11]',repr(x),up_nodes) if verbose else None
            out.append( [x, up_trees])
        return out

    def get_upstream_tree(x,strict,dir_layout=None,flat=0):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        tree = _get_upstream_tree(x,strict,dir_layout)
        tree = list_flatten(tree) if flat else tree
        return tree
        
    def get_upstream_files(x,strict,dir_layout=None,flat=0):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        tree = _get_upstream_tree(x,strict,dir_layout)
        tree = tree_filter(tree,(File,Prefix))
        tree = list_flatten(tree) if flat else tree
        return tree

    def get_upstream_nodes(x,strict,dir_layout=None,flat=0):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        tree = _get_upstream_tree(x,strict,dir_layout)
        tree = tree_filter(tree,(Caller,))
        tree = list_flatten(tree) if flat else tree
        return tree

    def get_upstream(x,strict,dir_layout=None):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        return _get_upstream(x,strict,dir_layout)
    def _get_upstream(x, strict, dir_layout):
        this = _get_upstream
        out = []
        if isinstance( x,(Prefix,File)):
            x = file_to_node(x,strict, dir_layout)
            if x is None:
                out += []
            else:
                out += [ x ]
        elif isinstance( x , (HttpResponse,)):
            out += []
            # out += [ SourceNode ]
        elif isinstance(x, Caller):
            out += [ v for v in x.arg_values[1:] if isinstance( v,(File,Prefix,HttpResponse))]
        else:
            raise UndefinedTypeRoutine("not defined for type:%s %r"%( type(x), x))
        return out    
    def tree_filter(tree, allowed):
        '''
        return a filtered tree with allowed classes only.
            params:
                tree: a list of shape [(node,up_trees),(node,uptrees)]
        '''
        out = []
        for node,up_trees in tree:
            res = tree_filter(up_trees,allowed)
            if isinstance(node,allowed):
                out += [(node,res)]
            else:
                out += res
        return out


if 1:
    import json
    from spiper._types import IdentFile,UndefinedTypeRoutine
    from spiper.runner import _get_outward_json_file, _loads

    def get_downstream_files(x,strict,dir_layout=None,flat=0,verbose=0):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        tree = _get_downstream_tree(x, strict,dir_layout,verbose)
        tree = tree_filter(tree,(File,Prefix))
        tree = list_flatten(tree) if flat else tree
        return tree

    def get_downstream_nodes(x,strict,dir_layout=None,flat=0,verbose=0):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        tree = _get_downstream_tree(x,strict,dir_layout,verbose)
        tree = tree_filter(tree,(Caller,))
        tree = list_flatten(tree) if flat else tree
        return tree

    def get_downstream_tree(x,strict,dir_layout=None,flat=0,verbose=0):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        tree = _get_downstream_tree(x,strict,dir_layout,verbose)
        if flat:
            tree = list_flatten(tree)
        return tree
    def _get_downstream_tree( lst,strict,dir_layout, verbose):
        # verbose = 0
        out = []
        for x in list_flatten(lst):
            up_nodes = _get_downstream(x, strict,dir_layout,verbose)
            up_trees = _get_downstream_tree(up_nodes, strict,dir_layout,verbose)
            print('[_get_downstream_tree]',repr(x),up_nodes) if verbose else None
            out.append( [x, up_trees])
        return out

    def get_downstream(obj,strict,dir_layout=None,verbose=0):
        dir_layout = rcParams['dir_layout'] if dir_layout is None else dir_layout
        return _get_downstream(obj,strict,dir_layout,verbose)

    def _get_downstream(obj,strict,dir_layout,verbose):
        this = _get_downstream
        out = []
        if isinstance(obj, (File,Prefix)):
            outward_dir = _get_outward_json_file(obj, strict, dir_layout)[0]
            print('[downstream]outward_dir=%r,dir_layout=%r'%(outward_dir,dir_layout)) if verbose else None
            # if verbose:
            #     print()
            # print()
            for outward_file in outward_dir.glob('*.json'):
                buf = json.load(open(outward_file,'r'))
                x_ident = _loads(buf['ident'])
                try:
                    _ = '''[TBC] fragile '''
                    x  =_loads(buf['caller_dump'])
                    input_ident_file  = IdentFile(dir_layout, x.prefix_named, [] , 'input_json')
                    x2 = _loads(json.load(open(input_ident_file,'r'))['ident'])
                except:
                    x2 = ''
                x1 = x_ident
                if x1 == x2:
                    out += [ x ]
                    pass
                else:
                    if strict==1:
                        buf = json.dumps([outward_file,obj,x.prefix,],indent=2,default=repr)
                        raise Exception('Broken edge exists between nodes. set get_downstream_nodes(strict=0) to auto-remove outdated edge files %s'%buf)
                    elif strict == -1:
                        os.unlink(outward_file)
                    else:
                        buf = json.dumps([outward_file,obj,x.prefix,],indent=2,default=repr)
                        # if 0:
                        if verbose:
                            print('[SKIPPING]Outdated %s'%buf)
                        pass
        elif isinstance(obj, Caller):
            out += list( obj.get_output_files() )
        else:
            raise UndefinedTypeRoutine("%r not defined for type:%s %r"%(this.__code__, type(obj),obj))
        return out
if 1:
    def tree_call(call,tree,):
        lst = []
        for node,edges in tree:
            lst.append( [call(node),tree_call(call, edges)])
        return lst

    def plot_simple_graph_lr(fs,g,strict,is_upstream):
        if is_upstream:
            tree = get_upstream_tree( fs, strict)
        else:
            tree = get_downstream_tree(fs, strict)
        if g is None:
            g = Digraph('G', strict=True,engine='dot')
            g.attr(rankdir='RL',)
            g = plot_simple_graph(tree, g, is_upstream)
        rank  = -1
        ranks = {}
        while True:
            rank += 1
            for f in fs:
                ranks[f] = rank
            fs = sum([get_upstream(f,0) for f in fs],[]) 
            fs = list(set(fs))
                # ranks[f] = max(ranks.get(f,0), rank)
            if not fs:
                break
        import collections
        nodes_by_rank = collections.defaultdict(lambda:[])
        [nodes_by_rank[rk].append(n) for n,rk in ranks.items()]
        for rk,ns in nodes_by_rank.items():
            # nodes_by_rank = sorted([(rk,n) for n,rk in ranks.items()])
            with g.subgraph(name='cluster_%d'%rk) as c:
                c.attr(rank='same'); 
                for f in ns: 
                    c.node(plot_simple_graph_label(f))
        return g
# def _get_upstream_tree(lst):
#     fmt = lambda x:"%s:%s"%(x.__class__.__name__,x.recordId,)
#     d = _dict([(fmt(x), 
#         _get_upstream_tree(x.input_kw.values())) for x in lst])
#     return d            # print()


# _ID = lambda x:(x.index,x)
# def _get_root_nodes(self,exclude=None):
#     if exclude is None:
#         exclude = set()
#     exclude = set(_ID(x) for x in exclude)
    
#     it = _get_upstream_graph(self,)
#     it = [x for x in it if x[0] not in exclude]
#     rootNodes, leafNodes = zip(*it)
#     # print set(rootNodes),set(leafNodes)
#     return set(rootNodes)  - set(leafNodes) 

# def _get_upstream_graph(self, edgelist=None):
#     if edgelist is None:
#         edgelist = []
#     for x in self.input_kw.values():
#         edgelist.append(( _ID(self),  _ID(x)))
#         _get_upstream_graph(x, edgelist)
#     return edgelist


# class cached_property(object):
#     """
#     Descriptor (non-data) for building an attribute on-demand on first use.
#     Source: https://stackoverflow.com/a/4037979/8083313
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

# def _shell(cmd,debug=0,silent=0,
#               executable=None,
#               encoding='utf8',error='raise',
# #               env = None,
#               shell = 1,
#               getSuccessCode = False,
#               raw = False,
#               **kwargs
#              ):
#     if executable is None:
#         executable = "bash"
#     if not silent:
#         buf = '[CMD]{cmd}\n'.format(**locals())
#         sys.stderr.write(buf)

#     # if debug:
#     #     return 'dbg'
#     try:
#         res = subprocess.check_output(cmd,shell=shell,
# #                                           env=_env,
#                                      executable=executable,
#                                      **kwargs)

#         if encoding is not None:
#             res=  res.decode(encoding)
#         res = res.rstrip() if not raw else res
#         suc = True
#     except subprocess.CalledProcessError as e:
#         errMsg = u"command '{}' return with error (code {}): {}\
#             ".format(e.cmd, e.returncode, e.output)
#         e = RuntimeError(
#                 errMsg)
#         if error=='raise':
#             raise e
#         elif error=='ignore':
#             res = (errMsg)
#             suc = False
#      #### allow name to be returned
#     if getSuccessCode:
#         return suc,res
#     else:
#         return res

# def frame_default(frame=None):
#     '''
#     return the calling frame unless specified
#     '''
#     if frame is None:
#         frame = inspect.currentframe().f_back.f_back ####parent of caller by default
#     else:
#         pass    
#     return frame
# frame__default = frame_default






# def _dbgf():        
#     import pdb,traceback
#     print(traceback.format_exc())
#     import traceback
#     traceback.print_stack()
#     traceback.print_exc()
#     pdb.set_trace()    
# def _dbgfs():        
#     import pdb,traceback
#     pdb.set_trace()    

# def dict_flatten(d,k0='',sep='.',idFunc = lambda x:x,out=None):
#     if out is None:
#         out= []
#     for _k,v in d.iteritems():
#         k = idFunc(_k)
#         k = sep.join((k0,k))
#         out.append((k+'_KEY', _k))
#         if isinstance(v,dict) and len(v):
#             dict_flatten(v,k,sep, idFunc, out)
#         else:
#             out.append((k,v))

#     return _dict(out)
