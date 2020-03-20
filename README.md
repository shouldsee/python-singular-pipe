
[![Build Status](https://travis-ci.com/shouldsee/spiper.svg?branch=master)](https://travis-ci.com/shouldsee/spiper)

## spiper: Utilities to make a pipeline, with singularity integration and caching ability.

### Dependencies:

- A pip manager compatible with PEP 508 URL requirements see [examples](https://www.python.org/dev/peps/pep-0508/#examples):
  - For python3, this means `python3 -m pip install --upgrade pip>=19.0` (see pip3 [changelog](https://pip.pypa.io/en/stable/news/#id245))
  - For python2, err python2 is not yet supported 
- Optional: singularity >= 3.5.3 to use `spiper.types.LoggedSingularityExecCommand()`. (try to install with `bash install_singular.sh /opt/singularity`, assuming ubuntu and use sudo for apt packages)
- Optional: dot binary for plotting graphs with `spiper.graph.plot_simple_graph()`.(try install with `sudo apt install -y graphviz`)
- see requirements.txt

### Install

```bash
pip3 install spiper@https://github.com/shouldsee/spiper/tarball/master --user
```

### Documentation

See https://shouldsee.github.io/spiper/

### Usage:

```bash
Version:spiper-0.1.2

Usage

	``spiper <subcommand> <package> <workflow_entrypoint> <workflow_arguments>``

Example::

	spiper run \
	  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
	  spiper_mock_flow:run_and_backup \
	  /tmp/test_remote/root 1 2 /tmp/test_remote/root.backup

Arguments:
	<subcommand>:
		run                  execute the workflow
		get_all_files        print all files governed by workflow
			--plain          print a newline-separated list instead of pprint
		get_changed_files    print all files changed by workflow
			--plain          print a newline-separated list instead of pprint
		get_all_deps         print all dependencies governed by workflow
			--plain          print a newline-separated list instead of pprint
			--which_flow     printing which subflow/node requries this dependency
	<package>:
		a string compatible with pep-508
	<workflow_entrypoint>:
		a string  "<module>:<object_name>" where object is like a `spipe.types.Node()`
	<workflow_arguments>:
		a comma-separated list of arguments for the workflow

Options:
	--help: show this help

	

```

### Running a remote pipeline

Pipeline living at https://github.com/shouldsee/spiper_mock_flow

```bash
### [pybash-0.0.5]
### [sys.argv] /home/user/.local/lib/python3.5/site-packages/pybash.py --log-stdout

### ---------------
### [ command]
commit=7c317b
### 
### [  stdout]
### ---------------

### ---------------
### [ command]
spiper\
  get_changed_files\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup
### 
### [  stdout]
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]
### ---------------

### ---------------
### [ command]
spiper\
  get_changed_files\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit\
  spiper_mock_flow:run_and_backup\
  --comma\
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup
### 
### [  stdout]
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]
### ---------------

### ---------------
### [ command]
ARR=(spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup\
  )
### 
### [  stdout]
### ---------------

### ---------------
### [ command]
spiper\
  get_changed_files\
  ${ARR[@]}
### 
### [  stdout]
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]
### ---------------

### ---------------
### [ command]
spiper\
  run\
  ${ARR[@]}
### 
### [  stdout]
### 
### [Flow running] mock=None
### [workflow]done
### ---------------

### ---------------
### [ command]
spiper\
  get_changed_files\
  ${ARR[@]}
### 
### [  stdout]
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]
### ---------------

### ---------------
### [ command]
spiper\
  get_all_deps\
  ${ARR[@]}
### 
### [  stdout]
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py')]
### ---------------

### ---------------
### [ command]
spiper\
  get_all_deps\
  --which_flow\
  ${ARR[@]}
### 
### [  stdout]
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [(File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py'),
###   [File('spiper:///tmp/test_remote/root.source.py'),
###    File('spiper:///tmp/test_remote/root.backup.source.py')])]
### ---------------

### ---------------
### [ command]
spiper\
  --help\
  >/dev/null
### 
### [  stdout]
### ---------------

```


### ToDo
	- [ ] print more logs during runtime.
	- [ ] extensive tests for RPO(). 
		- [ ] Figure out how to avoid pip install
		- [ ] construct setup.py for single-file script
	- [ ] Adding wrapper for WDL.
    - [x] Running a remote module
    	- [x] `spiper.mock.test_remote()` add some tests for spiper._types.PythonModule()
    - [ ] use _header.resolve_piper(). Auto-backup all output files. job_backup_copy()
    - [ ] [need:test] Adding Glob() and RecursiveGlob() to allow for easy file matching
    - [ ] Add timed_run() to print out execution times for each job.
    - [ ] Polish graph to have input-output node
    - Ability to relocate nodes.
	- [x] (see config_runner(tag=DirtyKey('Some tag')))(func, prefix) must be unique within each workflow
    - [x] Added MyPickleSession to sniff python dependency. Use protocol 3 by default
    - [ ] adds error tests for Caller.cache and Caller.__call__
    - [ ] cache_run_deep() to compute a dynamic graph and recursively 
        cache_run() from top to bottom.
    - [x] (see `mock_run()`) Caller.method() to populate Caller.output() for constructing symbolic graphs.
	- [x] In get_upstream()/get_downstream(), how to treat File that belongs to a Prefix?
		- [x] it should come with a pointer pointing back to the Prefix.
		- Prefix in get_input_identity() will be globbed and snapshotted
		- Prefix in get_upstream() will be treated as a standalone
		- If a File has been included in a OutputPrefix(), 
	- [x] fix get_upstream() if possible 
	- [x] test_loadable_subprocess() test the outputted caller_dump is loadable from other directories
	- shellcmd
		- [x] capture stderr and stdout of subprocess.check_output(), 
		- [x] logging the command executed into .cmd file
		- [x] with optional log file.  
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



### Screenshots

![](./tests/test_downstream.node_only.dot.svg)

