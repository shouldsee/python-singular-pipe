# DEFAULT_DIR_LAYOUT = 'clean'
DEFAULT_DIR_LAYOUT = 'flat'

def get_version():
    VERSION = (     # SEMANTIC
        0,          # major
        0,          # minor
        1,          # patch
        None,       # pre-release
        None        # build metadata
    )

    version = "%i.%i.%i" % (VERSION[0], VERSION[1], VERSION[2])
    if VERSION[3]:
        version += "-%s" % VERSION[3]
    if VERSION[4]:
        version += "+%s" % VERSION[4]
    return version
VERSION = get_version()

todo = '''
    - [ ] In get_upstream()/get_downstream(), how to treat File that belongs to a Prefix?
        - [x] it should come with a pointer pointing back to the Prefix.
        - Prefix in get_input_identity() will be globbed and snapshotted
        - Prefix in get_upstream() will be treated as a standalone
        - If a File has been included in a OutputPrefix(), 
    - [ ] fix get_upstream() if possible 
    - [ ] Caller.method() to populate Caller.output() for constructing symbolic graphs.
    - [x] test_loadable_subprocess() test the outputted caller_dump is loadable from other directories
    - shellcmd
        - [x] capture stderr and stdout of subprocess.check_output(), 
        - [x] logging the command executed into .cmd file
        - [ ] with optional log file.  
    - [x] adding an outward_pk file to complement input_pk and auto-sync
        - the outward_pk should record identity of the output file and input file.
        - the input_ident is useful 
    - [x] produce a dependency graph
        - get_upstream_files()
        - get_downstream_nodes()
    - [x] (Done as HttpResponse(),  ) Adding InputHTTP() 
        - [ ] better subclassing requests.Request()?
    - [ ] implements version_check when reading input_json / output_json
    - [ ] Adding OutputHTTP() object 
    - [ ] (abandoned)import module from online.
    - [ ] migrate valid cache folder and preserving inner dependency and re-connect cutted dependency
    - [ ] implementing checks for output nodes to make sure Files.to_ident() are changed
'''
template = '''
[![Build Status](https://travis-ci.com/shouldsee/python-singular-pipe.svg?token=f6G1tkP8yesCfYdyDVrj&branch=master)](https://travis-ci.com/shouldsee/python-singular-pipe)

## singular_pipe: Utilities to make a pipeline, with singularity integration and caching ability.

### Dependencies:

- Optional: singularity >= 3.5.3 to use singular_pipe.base.singularity_run(). (try to install with `bash install_singular.sh /opt/singularity`, assuming ubuntu and use sudo for apt packages)
- Optional: dot binary for plotting DAG.(try install with `sudo apt install -y graphviz`)
- see requirements.txt

### Install

```bash
pip3 install singular_pipe@https://github.com/shouldsee/python-singular-pipe/tarball/master --user
```

### ToDo
{todo}
'''

todo2 = '''
[ToDo]
    - adding tests for Prefix InputPrefix OutputPrefix
in get_idenity()
    InputPrefix should not match nothing
    OutputPrefix could match empty 
in bind_files()
    InputPrefix should not match nothing
    OutputPrefix could match empty
these two functions are kind of similar, but treat OutputPrefix differently
    in get_identity(), An empty OutputPrefix would reduce to []
    in bind_files(), An empty OutputPreix would cause the whole directory to be mounted
additionally, 
    get_identity() needs to expand objects other than Prefix and File, including Params
    bind_files() only consider local files for now

[ToDo]capturing get_identity() of Static params
[ToDo]illustrating the different between vars
static:    argname starts with '_' --> value is static constant of function,            must not override
temporary: argname endswith '_'    --> value is a type, discarded for cache-validation, necessary arg  
validated: argname otherwise       --> value is a type, kept for cache-validation,      ncessary

### [add-test] for  
def test_tempvar_change()  --> assert input_change == 0 
def test_statvar_change()  --> raise tma error
def test_validvar_change() --> assert input_change == 1

[add-test] for get_output_files() to preserve types from the original _output list.
  e.g. dont cast File into Prefix through namedtuple() in job_from_func()

### [ToDo] get_output_files(), 
### currently the returned _output consider all _output object as Prefix, 
because _output is a list and there isn't a way of specifying their type.
'''

def make_readme(fn,todo=todo,template=template):
    # with open(f,'w'):
    f = open(fn,'w+')
    s = template.format(**locals())
    f.write(s)
    f.flush()
    f.seek(0)
    return f
    # return tempalte.format(**locals())
