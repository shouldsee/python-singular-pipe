from spiper.types import Node,Flow
from spiper.types import RemotePythonObject as RPO
from spiper.types import RemotePythonObject

### Github "tarball/master" often take minutes to update,
### use the commit hash to ensure integrity. 
### package_path_with_hash = 'spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/d457426'
### package_path           = 'spiper_mock_flow@http://github.com/shouldsee/spiper_mock_flow/tarball/master'
###
### import the top-level module of the package
_mod1 = RemotePythonObject('spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/d457426')

### import a function from toplevel module
_remote_function= RemotePythonObject(
'spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/d457426',
None,  
'run_and_backup')

### import a module with different name
_mod2 = RemotePythonObject(
'luigi@https://github.com/spotify/luigi/tarball/2.8.12',
'luigi',)

##### showing many different ways of
_mod2attr = RemotePythonObject(
'luigi@https://github.com/spotify/luigi/tarball/2.8.12',
'luigi.event', 
'Event')
