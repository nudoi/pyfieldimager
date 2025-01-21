import numpy as np
import matplotlib.pyplot as plt
import os
from osgeo import gdal
from functools import singledispatch

from .index import *
from .main import *


@singledispatch
def export_png(image: FieldImage, filename: str):

    if filename[-4:] != ".png":
        filename += ".png"

    # save imege.rgb to png
    plt.imsave(filename, image.rgb)


@export_png.register
def _(images: list, dir_name: str):

    if dir_name[-1] != "/":
        dir_name += "/"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # save imeges[i][j].rgb to png
    for i in range(len(images)):
        for j in range(len(images[i])):
            filename = dir_name + str(i) + "_" + str(j) + ".png"
            export_png(images[i][j], filename)


@singledispatch
def export_tif(image: FieldImage, filename: str):

    if filename[-4:] != ".tif":
        filename += ".tif"

    height, width = image.shape

    # save imege.rgb to tif
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(filename, width, height, 3, gdal.GDT_Byte)

    for i in range(3):
        outdata.GetRasterBand(i + 1).WriteArray(image.rgb[:, :, i])

    outdata.FlushCache()


@export_tif.register
def _(images: list, dir_name: str):

    if dir_name[-1] != "/":
        dir_name += "/"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # save imeges[i][j].rgb to tif
    for i in range(len(images)):
        for j in range(len(images[i])):
            filename = dir_name + str(i) + "_" + str(j) + ".tif"
            export_tif(images[i][j], filename)


@singledispatch
def export_dsm(image: FieldImage, filename: str):

    if image.dsm is None:
        raise ValueError("DSM not found.")

    if filename[-4:] != ".tif":
        filename += ".tif"

    height, width = image.dsm.shape

    # save imege.rgb to tif
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(filename, width, height, 1, gdal.GDT_Float32)

    outdata.GetRasterBand(1).WriteArray(image.dsm)

    outdata.FlushCache()


@export_dsm.register
def _(images: list, dir_name: str):

    if dir_name[-1] != "/":
        dir_name += "/"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # save imeges[i][j].rgb to tif
    for i in range(len(images)):
        for j in range(len(images[i])):
            filename = dir_name + str(i) + "_" + str(j) + ".tif"
            export_dsm(images[i][j], filename)


@singledispatch
def export_dtm(image: FieldImage, filename: str):

    if image.dtm is None:
        raise ValueError("DTM not found.")

    if filename[-4:] != ".tif":
        filename += ".tif"

    height, width = image.dtm.shape

    # save imege.rgb to tif
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(filename, width, height, 1, gdal.GDT_Float32)

    outdata.GetRasterBand(1).WriteArray(image.dtm)

    outdata.FlushCache()


@export_dtm.register
def _(images: list, dir_name: str):

    if dir_name[-1] != "/":
        dir_name += "/"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # save imeges[i][j].rgb to tif
    for i in range(len(images)):
        for j in range(len(images[i])):
            filename = dir_name + str(i) + "_" + str(j) + ".tif"
            export_dtm(images[i][j], filename)


@singledispatch
def export_chm(image: FieldImage, filename: str):

    if image.chm is None:
        raise ValueError("CHM not found.")

    if filename[-4:] != ".tif":
        filename += ".tif"

    height, width = image.chm.shape

    # save imege.rgb to tif
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(filename, width, height, 1, gdal.GDT_Float32)

    outdata.GetRasterBand(1).WriteArray(image.chm)

    outdata.FlushCache()


@export_chm.register
def _(images: list, dir_name: str):

    if dir_name[-1] != "/":
        dir_name += "/"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # save imeges[i][j].rgb to tif
    for i in range(len(images)):
        for j in range(len(images[i])):
            filename = dir_name + str(i) + "_" + str(j) + ".tif"
            export_chm(images[i][j], filename)


@singledispatch
def export_csv(image: FieldImage, filename: str):

    if filename[-4:] != ".csv":
        filename += ".csv"
    
    if image.chm is not None:

        try:
            with open(filename, 'w') as f:
                f.write("max, min, mean, median, std, proj, surf, square\n")
                f.write(
                    "{}, {}, {}, {}, {}, {}, {}, {}\n".format(
                        image.max_chm(),
                        image.min_chm(),
                        image.mean_chm(),
                        image.median_chm(),
                        image.std_chm(),
                        image.proj_area(),
                        image.surf_area(),
                        image.square()
                    )
                )
        except:
            raise ValueError("Failed to write csv file.")
        
    else:
        raise ValueError("No output.")
        

@export_csv.register
def _(images: list, filename: str):

    if filename[-4:] != ".csv":
        filename += ".csv"

    if images[0][0].chm is not None:

        try:
            with open(filename, 'w') as f:
                f.write("col, row, max, min, mean, median, std, proj, surf, square\n")
                for i in range(len(images)):
                    for j in range(len(images[i])):
                        f.write(
                            "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(
                                i,
                                j,
                                images[i][j].max_chm(),
                                images[i][j].min_chm(),
                                images[i][j].mean_chm(),
                                images[i][j].median_chm(),
                                images[i][j].std_chm(),
                                images[i][j].proj_area(),
                                images[i][j].surf_area(),
                                images[i][j].square()
                            )
                        )
        except:
            raise ValueError("Failed to write csv file.")
        
    else:
        raise ValueError("No output.")
        