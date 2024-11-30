# PyFieldImager

![example workflow](https://github.com/nudoi/pyfieldimager/actions/workflows/python-publish.yml/badge.svg)

## A Python package for field image analysis

This is a tool for analyzing orthomosaic images. You can extract useful information for agricultural analysis from images.

## Features

- This package manages field images (such as orthophoto, Digital Surface Model (DSM) and Digital Terrain Model (DTM)) as field image object.
- This package can identify vegetation and soil extent using vegetation indices (e.g. NDVI, VARI, SCI).
- It can also calculate the height distribution (known as Canopy Height Model (CHM)) and projected/surface area of vegetation areas, and can create DTMs by missing value completion.

## For Example

- Select field area.

<img alt="select_field" src="examples/img/select_field.png" width="300px">

- Calculate vegetation index.

<img alt="field_index" src="examples/img/field_index.png" width="300px">

- Create DTM from Soil DSM, and CHM(=DSM-DTM).

<img alt="field_index" src="examples/img/create_chm.png" width="500px">

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

view [LICENSE](LICENSE).