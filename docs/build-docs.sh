set -e
### install package first
cp -rfT docs _docs
git checkout gh-pages
sphinx-build -b html _docs _html
cp -lfrv _html/* -t .
git add .; git commit . -m "$@"; git push origin gh-pages

#mv html/* .
