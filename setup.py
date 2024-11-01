from setuptools import setup, find_packages

setup(
    name='pyfieldimager',
    version='0.9',
    description="""A tool for field image analysis""",
    author='doi',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'gdal',
        'Pillow',
    ],
    license="LGPL-2.1",
)