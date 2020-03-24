
[![Build Status](https://travis-ci.com/shouldsee/spiper.svg?branch=master)](https://travis-ci.com/shouldsee/spiper)

## spiper: Utilities to make a pipeline, with singularity integration and caching ability.

### Documentation

Written with sphinx. See https://shouldsee.github.io/spiper/

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


### Usage:

```bash
Version:spiper-0.1.4

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

		caller_show_deps     print all dependencies governed by workflow (legacy: get_all_deps)
			--plain          print a newline-separated list instead of pprint
			--which_flow     printing which subflow/node requries this dependency

		caller_show_log      print details of a call, including `arg_tuples,sourcecode,sourcefile`
			--plain

		file_show_deps       print dependencies of parent caller for a file
			--plain
			--which_flow

		file_show_log        print details of parent caller
			--plain

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
set\
  -euo\
  pipefail;
### 
### [  stdout]
### ---------------

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
  caller_show_deps\
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
  caller_show_deps\
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
  file_show_deps\
  /tmp/test_remote/root.transcribe.fasta
### 
### [  stdout]
### /tmp/test_remote/root.transcribe.fasta
### [File('/tmp/test_remote/root.random_seq.seq')]
### ---------------

### ---------------
### [ command]
spiper\
  caller_show_log\
  ${ARR[@]}\
  --plain
### 
### [  stdout]
### node:
###     prefix_named:
###         /tmp/test_remote/root.run_and_backup
###     job_type:
###         FlowFunction
###     will_change:
###         True, FlowFunction will always be executed
###     dotname:
###         spiper_mock_flow:run_and_backup
###     sourcefile:
###         /home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py
###     info_dict:
###         OrderedDict([('args_tuples',
###                       ["['prefix'       ,spiper._types.File            "
###                        ",File('/tmp/test_remote/root')]",
###                        "['seed'         ,builtins.int                  ,1]",
###                        "['L'            ,builtins.int                  ,2]",
###                        "['backup_prefix',builtins.str                  "
###                        ",'/tmp/test_remote/root.backup']",
###                        "['_output'      ,builtins.list                 ,[]]"]),
###                      ('code',
###                       '<code object run_and_backup at 0x7fe09f8a3ae0, file '
###                       '"/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py", '
###                       'line 133>')])
###     sourcecode:
###         @Flow
###         def run_and_backup(
###                 self, prefix,
###                 seed=int, L=int,
###                 backup_prefix=str,  # we don't want to track backup_prefix
###                 _output=[
###                 # File('log'),
###                 ]):
### 
###             # execute the flow
###             flow = self.runner(workflow, prefix, seed, L)
### 
###             # perform backup
###             backup_result = self.runner(backup, backup_prefix, flow)
### 
###             # plot a dependency graph into the backup directory
###             graph_out = self.runner(plot_graph, backup_prefix, backup_result)
###             print('[workflow]done')
###             return self
### ---------------

### ---------------
### [ command]
spiper\
  file_show_log\
  /tmp/test_remote/root.transcribe.fasta\
  --plain
### 
### [  stdout]
### file:
###     name:
###         /tmp/test_remote/root.transcribe.fasta
###     node:
###         prefix_named:
###             /tmp/test_remote/root.transcribe
###         job_type:
###             NodeFunction
###         will_change:
###             NA when viewing a node image
###         dotname:
###             spiper_mock_flow:transcribe
###         sourcefile:
###             /home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py
###         info_dict:
###             {'args_tuples': ["['prefix'       ,spiper._types.File            "
###                              ",File('/tmp/test_remote/root')]",
###                              "['input'        ,spiper._types.File            "
###                              ",File('/tmp/test_remote/root.random_seq.seq')]",
###                              "['_output'      ,builtins.list                 ,['fasta']]"],
###              'code': '<code object transcribe at 0x7f7520f10390, file '
###                      '"/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py", '
###                      'line 23>'}
###         sourcecode:
###             def transcribe(self, prefix, input=File, _output=['fasta']):
###                 with open(input, 'r') as fi:
###                     with open(self.output.fasta, 'w') as fo:
###                         fo.write(fi.read().replace('T', 'U'))
###                 return self
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
	- [ ] Adding definition for other file operation:
		- node_clone     duplicate a node
		  - node_detach    cache all dependencies of a node to local
          - node_cplink    create a spiper-synced sopy
        - node_mv        move a node and link meta to another location
        - file_clone      create a hardlink
          - file_cplink    create a spiper-synced copy
  		  - file_mirror    
  	    - file_mv        move a file to another location
  	    - file_commit    commit manual changes to a file
  	    - file_pull
  	    - node_pull      
	- [ ] Adding file pointers between flow and subflow.
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

