from setuptools import setup, find_packages

setup(
    name='pyfieldimager',
    version='0.9.3.1',
    license='LGPLv2',
    description='A Python package for field image analysis.',

    author='doi',
    author_email='doi@doilab.open.ad.jp',
    url='https://github.com/nudoi/pyfieldimager',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)