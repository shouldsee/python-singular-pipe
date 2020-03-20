commit=7c317b
spiper\
  get_changed_files\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/7c317b\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]

spiper\
  get_changed_files\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/7c317b\
  spiper_mock_flow:run_and_backup\
  --comma\
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]

ARR=(spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup)

spiper\
  get_changed_files\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/7c317b\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]

spiper\
  run\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/7c317b\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup
### 
### [Flow running] mock=None
### [workflow]done

spiper\
  get_changed_files\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/7c317b\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/tmp/test_remote/root.workflow.log'),
###  File('/tmp/test_remote/root.backup.output..log')]

spiper\
  get_all_deps\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/7c317b\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py')]

spiper\
  get_all_deps\
  --which_flow\
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/7c317b\
  spiper_mock_flow:run_and_backup\
  /tmp/test_remote/root\
  1\
  2\
  /tmp/test_remote/root.backup
### 
### [Flow running] mock=None
### [workflow]done
### 
### [Flow running] mock=None
### [workflow]done
### [(File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py'),
###   [File('spiper:///tmp/test_remote/root.source.py'),
###    File('spiper:///tmp/test_remote/root.backup.source.py')])]

spiper\
  --help
