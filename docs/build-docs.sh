set -e
### install package first
git checkout gh-pages
sphinx-build -b html docs _html
cp -lfrv _html/* -t .
git add .; git commit . -m "$@"; git push origin gh-pages

#mv html/* .
