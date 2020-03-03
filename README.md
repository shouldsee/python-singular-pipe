
[![Build Status](https://travis-ci.com/shouldsee/python-singular-pipe.svg?token=f6G1tkP8yesCfYdyDVrj&branch=master)](https://travis-ci.com/shouldsee/python-singular-pipe)

## singular_pipe: Utilities to make a pipeline, with singularity integration and caching ability.

### Dependencies:

- Optional: singularity >= 3.5.3 to use singular_pipe.base.singularity_run(). (try to install with `bash install_singular.sh /opt/singularity`, assuming ubuntu and use sudo for apt packages)
- see requirements.txt

### Install

```bash
pip3 install singular_pipe@https://github.com/shouldsee/python-singular-pipe/tarball/master --user
```

### ToDo

    - [ ] implements version_check when reading input_json / output_json
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
    - [ ] Adding OutputHTTP() object 
    - [ ] (abandoned)import module from online.
    - [ ] migrate valid cache folder and preserving inner dependency and re-connect cutted dependency
    - [ ] implementing checks for output nodes to make sure Files.to_ident() are changed

