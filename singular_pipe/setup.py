#!/usr/bin/env python
#from setuptools import setup

from singular_pipe import get_version,make_readme

config = dict(
	name='singular_pipe',
	version = get_version(),
    packages=['.',],
	include_package_data=True,
	license='MIT',
	author='Feng Geng',
	author_email='shouldsee.gem@gmail.com',
	long_description = make_readme('README.md').read(),
	# long_description=open('README.md').read(),
	# python_requires = '>=3.6',
	classifiers = [
	'Programming Language :: Python :: 3.5',
	],
	install_requires=[
		x.strip() for x in open("requirements.txt","r")
        	if x.strip() and not x.strip().startswith("#")
	],

)


if __name__ == '__main__':
	from distutils.core import setup
	import os,glob,sys
	make_readme('README.md').read()
	assert sys.version_info >= (3,5),('Requires python>=3.5, found python==%s'%('.'.join([str(x) for x in sys.version_info[:3]])))
	setup(**config)