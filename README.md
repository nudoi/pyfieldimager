# PyFieldImager

![example workflow](https://github.com/nudoi/pyfieldimager/actions/workflows/python-publish.yml/badge.svg)

## A Python package for field image analysis

This is a tool for analyzing orthomosaic images. You can extract useful information for agricultural analysis from images.

## Features

- This package manages field images (such as orthophoto, Digital Surface Model (DSM) and Digital Terrain Model (DTM)) as field image object.
- This package can identify vegetation and soil extent using vegetation indices (e.g. NDVI, VARI, SCI).
- It can also calculate the height distribution (known as Canopy Height Model (CHM)) and projected/surface area of vegetation areas, and can create DTMs by missing value completion.

## How to install

from PyPI

```
pip install pyfieldimager
```

or, from GitHub

```
git clone https://github.com/nudoi/pyfieldimager.git
cd pyfieldimager
pip install -r requirements.txt
pip install .
```