spiper run \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup

spiper run \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  spiper_mock_flow:run_and_backup \
  "/tmp/test_remote/root, 1, 2,/tmp/test_remote/root.backup"

#### TOPLEVEL refers to the package_name 
spiper run \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  TOPLEVEL:run_and_backup \
  "/tmp/test_remote/root, 1, 2,/tmp/test_remote/root.backup"

#### in case spiper is not in $PATH
python3 -m spiper run \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  TOPLEVEL:run_and_backup \
  "/tmp/test_remote/root, 1, 2,/tmp/test_remote/root.backup"

spiper --help >/dev/null
