import pyfieldimager as pfi
import pytest
import sys

sys.path.append('../')

orthophoto = '20231018-orthophoto.tif'
dsm        = '20231018-dsm.tif'


def test_fieldimage():

    fi = pfi.FieldImage(orthophoto=orthophoto, dsm=dsm)
    assert fi.img is not None
    assert fi.dsm is not None


def test_crop_field():

    fi = pfi.FieldImage(orthophoto=orthophoto, dsm=dsm)
    fi.crop_field(rotation=52, x_range=[1500, 3000], y_range=[2000, 3000])
    assert fi.img.size == (1500, 1000)


def test_crop_grid():

    fi = pfi.FieldImage(orthophoto=orthophoto, dsm=dsm)
    fi.crop_field(rotation=52, x_range=[1500, 3000], y_range=[2000, 3000])
    fi.crop_grid(rotation=0, x_range=[100, 1100], y_range=[100, 900], x_split=10, y_split=8, grid_num=True)
    field = fi.split()
    assert field[0][0] is not None
    assert field[0][1].x_size != 0