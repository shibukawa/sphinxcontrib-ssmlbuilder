# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the Amazon Polly adaptor Sphinx extension.

This builder generates SSML files and kick AWS Polly API and creates MP3 files.
'''

requires = [
    'Sphinx>=1.5',
    'boto3>=1.4.4',
    'awscli>=1.11.41'
]

setup(
    name='sphinxcontrib-ssmlbuilder',
    version='0.1.2',
    url='https://github.com/shibukawa/sphinxcontrib-ssmlbuilder',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-ssmlbuilder',
    license='BSD',
    author='Yoshiki Shibukawa',
    author_email='yoshiki@shibu.jp',
    description='Sphinx "SSMLBuilder" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Sphinx :: Extension',
        'Programming Language :: Python :: 3.6',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
