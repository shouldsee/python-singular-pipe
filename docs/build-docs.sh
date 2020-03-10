set -e
sphinx-build -b html docs _html
cp -lfrv _html/* -t .
#mv html/* .
