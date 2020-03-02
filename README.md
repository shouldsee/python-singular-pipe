[![Build Status](https://travis-ci.com/shouldsee/python-singular-pipe.svg?token=f6G1tkP8yesCfYdyDVrj&branch=master)](https://travis-ci.com/shouldsee/python-singular-pipe)

## singular_pipe: Utilities to make a pipeline, with singularity integration and caching ability.

### Requirement

- singularity >= 3.5.3 (try to install with `bash install_singular.sh /opt/singularity`, assuming ubuntu and use sudo for apt packages)
- see requirements.txt

### Install

```bash
pip3 install singular_pipe@https://github.com/shouldsee/python-singular-pipe/tarball/master --user
```


### Capabilities:

- [x] check valid cache by verifying input and output file mtime and sizes
- [ ] (abandoned)import module from online.
- [ ] migrate valid cache folder and preserving inner dependency and re-connect cutted dependency
- touch
