
[![Build Status](https://travis-ci.com/shouldsee/spiper.svg?branch=master)](https://travis-ci.com/shouldsee/spiper)

## spiper: Utilities to make a pipeline, with singularity integration and caching ability.

### Dependencies:

- A pip manager compatible with PEP 508 URL requirements see [examples](https://www.python.org/dev/peps/pep-0508/#examples):
  - For python3, this means `python3 -m pip install --upgrade pip>=18.1` (see pip3 [changelog](https://pip.pypa.io/en/stable/news/#id245))
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

Usage:
	spiper <subcommand> <package> <workflow_entrypoint> <workflow_arguments>

Example:
	spiper run \
	  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
	  spiper_mock_flow:run_and_backup \
	  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup

Arguments:
	<subcommand>:
		run                  execute the workflow
		get_all_files        print all files governed by workflow
			--plain: print a newline-separated list instead of pprint
		get_changed_files    print all files changed by workflow
			--plain: print a newline-separated list instead of pprint
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
#### get a list of changed_files
spiper get_changed_files \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup

# [Flow running] mock=None
# [workflow]done
# [File('/tmp/test_remote/root.workflow.log'),
#  File('/tmp/test_remote/root.random_seq.seq'),
#  File('/tmp/test_remote/root.random_seq_const.seq'),
#  File('/tmp/test_remote/root.transcribe.fasta'),
#  File('/tmp/test_remote/root.mutate.fasta'),
#  File('/tmp/test_remote/root.source.py'),
#  File('/tmp/test_remote/root.backup.subflow.random_seq.output.seq'),
#  File('/tmp/test_remote/root.backup.subflow.random_seq_const.output.seq'),
#  File('/tmp/test_remote/root.backup.subflow.transcribe.output.fasta'),
#  File('/tmp/test_remote/root.backup.subflow.mutate.output.fasta'),
#  File('/tmp/test_remote/root.backup.output.log'),
#  File('/tmp/test_remote/root.backup.source.py'),
#  File('/tmp/test_remote/root.backup.plot_graph.deptree_json'),
#  File('/tmp/test_remote/root.backup.plot_graph.deptree_dot_txt')]


spiper run \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup

# [Flow running] mock=None
# [fn] /tmp/test_remote/root.backup.plot_graph.deptree_dot_txt.svg
# [workflow]done

spiper get_changed_files \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup
# [No files changed by this workflow]'

spiper --help >/dev/null

```

### Screenshots

![](./tests/test_downstream.node_only.dot.svg)



### ToDo
    - [x] Running a remote module
    	- [ ] add some tests for spiper._types.PythonModule()
    - [ ] Polish graph to have input-output node
    - [ ] Ability to relocate nodes.
    - [ ] Auto-backup all output files. job_backup_copy()
    - [ ] (not essential) Adding Glob() and RecursiveGlob() to allow for easy file matching
	- [x] (see config_runner(tag=DirtyKey('Some tag')))(func, prefix) must be unique within each workflow
    - [ ] Add timed_run() to print out execution times for each job.
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
