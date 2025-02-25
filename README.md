# PyFieldImager

![example workflow](https://github.com/nudoi/pyfieldimager/actions/workflows/python-publish.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/pyfieldimager.svg)](https://badge.fury.io/py/pyfieldimager)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nudoi/pyfieldimager/blob/main/examples/example-1.ipynb)

## A Python package for field image analysis

This is a tool for analyzing orthomosaic images. You can extract useful information for agricultural analysis from images.

## Features

- This package manages field images (such as orthophoto, Digital Surface Model (DSM) and Digital Terrain Model (DTM)) as field image object.
- This package can identify vegetation and soil extent using vegetation indices (e.g. NDVI, VARI, SCI).
- It can also calculate the height distribution (known as Canopy Height Model (CHM)) and projected/surface area of vegetation areas, save to CSV, and can create DTMs by missing value completion.

## For Example

- Select field area.

<img alt="select_field" src="https://raw.githubusercontent.com/nudoi/pyfieldimager/refs/heads/main/examples/img/select_field.png" width="300px">

- Calculate vegetation index.

<img alt="field_index" src="https://raw.githubusercontent.com/nudoi/pyfieldimager/refs/heads/main/examples/img/field_index.png" width="300px">

- Split field by grid.

<img alt="field_index" src="https://raw.githubusercontent.com/nudoi/pyfieldimager/refs/heads/main/examples/img/crop_grid.png" width="300px">

- Create DTM from Soil DSM, and CHM(=DSM-DTM).

<img alt="field_index" src="https://raw.githubusercontent.com/nudoi/pyfieldimager/refs/heads/main/examples/img/create_chm.png" width="500px">

- Plant Canopy Height

<img alt="field_index" src="https://raw.githubusercontent.com/nudoi/pyfieldimager/refs/heads/main/examples/img/plant_chm.png" width="300px">

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

Note: GDAL is required. See [here](https://pypi.org/project/GDAL/) for installation.

## License

view [LICENSE](https://raw.githubusercontent.com/nudoi/pyfieldimager/refs/heads/main/LICENSE).