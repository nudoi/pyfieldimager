import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from osgeo import gdal
from ipywidgets import widgets, IntSlider, IntRangeSlider
import warnings
warnings.simplefilter('ignore', FutureWarning)

from .src.index import *


'''
field image class
'''
class FieldImage:

    def __init__(self, orthophoto=None, img=None, rgb=None, nir=None, re=None, dsm=None, dtm=None, gsd=None):

        if orthophoto is None and img is None and rgb is None:
            print('Image not found')
            return

        self.orthophoto = orthophoto
        self.img = gdal.Open(orthophoto) if orthophoto else img
        if rgb is not None:
            self.rgb = rgb
        elif type(self.img) == np.ndarray:
            self.rgb = self.img if self.img.shape[2] == 3 else self.img.transpose(1, 2, 0)
        else:
            self.rgb = self.img.ReadAsArray() if self.img.RasterCount == 3 else self.img.ReadAsArray().transpose(1, 2, 0)
        if nir is not None:
            self.nir = gdal.Open(nir).ReadAsArray() if type(nir) != np.ndarray else nir
        else:
            self.nir = None
        if re is not None:
            self.re = gdal.Open(re).ReadAsArray() if type(re) != np.ndarray else re
        else:
            self.re = None
        self.geo = self.img.GetGeoTransform() if self.orthophoto else None
        self.proj = self.img.GetProjection() if self.orthophoto else None
        self.x_size, self.y_size = self.rgb.shape[1], self.rgb.shape[0]
        self.shape = (self.y_size, self.x_size)
        if dsm is not None:
            self.dsm = gdal.Open(dsm).ReadAsArray() if type(dsm) != np.ndarray else dsm
        else:
            self.dsm = None
        if self.dsm is not None:
            self.dsm[self.dsm == -9999] = np.nan
        if dtm is not None:
            self.dtm = gdal.Open(dtm).ReadAsArray() if type(dtm) != np.ndarray else dtm
        else:
            self.dtm = None
        if self.dtm is not None:
            self.dtm[self.dtm == -9999] = np.nan
        self.chm = None
        self.gsd = gsd
        self._img = None
        self._rgb = None
        self._dsm = self.dsm.copy() if self.dsm is not None else None
        self._rot = 0
        self._bbox = None
        self._index = None


    def show(self, index=None, threshold=None, cmap=None):

        if index is None:
            plt.imshow(self.rgb)
            plt.show()

        else:
            i, min, max = self.calc_index(index, threshold)

            if i is not None:
                plt.imshow(i)
                plt.colorbar()
                if cmap is not None:
                    plt.set_cmap(cmap)
                if min is not None and max is not None:
                    plt.clim(min, max)
                plt.show()


    def select_index(self):

        index = widgets.Dropdown(options=FieldIndex.list(), description='Index: ')
        threshold = widgets.FloatText(value=0, description='Threshold: ')
        cmap = widgets.Dropdown(options=['viridis', 'plasma', 'inferno', 'magma', 'cividis'], description='Colormap: ')
        widgets.interact(self.show, index=index, threshold=threshold, cmap=cmap)


    def calc_index(self, index=None, threshold=None):
            
        r = self.rgb[:,:,0].astype(float)
        g = self.rgb[:,:,1].astype(float)
        b = self.rgb[:,:,2].astype(float)

        nir = self.nir.astype(float) if self.nir is not None else None
        re = self.re.astype(float) if self.re is not None else None

        min, max = None, None

        fieldindex = FieldIndex.get(index)

        if fieldindex == 1:
            i = np.sqrt((r**2 + g**2 + b**2)/3) # Brightness Index

        elif fieldindex == 2:
            i = (r - g) / (r + g - 0.0000001) # Soil Color Index
            min, max = -1, 1

        elif fieldindex == 3:
            i = (2 * g - r - b) / (2 * g + r + b - 0.0000001) # Green Leaf Index

        elif fieldindex == 4:
            i =  (2 * r - g - b) / (g - b - 0.0000001) # Primary Color Hue Index

        elif fieldindex == 5:
            i = (r - b) / (r + b - 0.0000001) # Normalized Green Red Difference Index
            min, max = -1, 1

        elif fieldindex == 6:
            i = (r - b) / (r + b - 0.0000001) # Spectral Slope Saturation Index

        elif fieldindex == 7:
            i = (g - r) / (g + r - b - 0.0000001) # Visible Atmospherically Resistant Index

        elif fieldindex == 8:
            i = np.arctan((2 * (b - g - r) ) / (30.5 * (g - r) - 0.0000001)) # Overall Hue Index

        elif fieldindex == 9:
            i = b / (g - 0.0000001) # Blue Green Index

        elif fieldindex == 10:
            i = (r - g) / (re) # Plant Senescence Reflectance Index

        elif fieldindex == 11:
            i = (nir - r) / (nir + r - 0.0000001) # Normalized Difference Vegetation Index
            min, max = -1, 1

        elif fieldindex == 12:
            i = (nir - g) / (nir + g - 0.0000001) # Green Normalized Difference Vegetation Index

        elif fieldindex == 13:
            i = nir / r # Ratio Vegetation Index

        elif fieldindex == 14:
            i = (nir - re) / (nir + re - 0.0000001) # Normalized Difference Red Edge Index
            min, max = -1, 1

        elif fieldindex == 15:
            i = 0.5 * (120 * (nir - g) - 200 * (r - g)) # Transformed Vegetation Index

        elif fieldindex == 16:
            i = (nir * r) / g**2 # Chlorophyll Vegetation Index

        elif fieldindex == 17:
            i = 2.5 * (nir - r) / (nir + 6 * r - 7.5 * b + 1) # Enhanced Vegetation Index

        elif fieldindex == 18:
            i = (nir / g) - 1 # Chlorophyll Index - Green

        elif fieldindex == 19:
            i = (nir / re) - 1 # Chlorophyll Index - Red Edge

        elif fieldindex == 20:
            i = nir - re # Difference Vegetation Index

        else:
            print('Index not available')
            return None
        
        i[(self.rgb[:,:,0] == 0) & (self.rgb[:,:,1] == 0) & (self.rgb[:,:,2] == 0) & (self.rgb[:,:,3] == 0)] = np.nan
        
        if threshold is not None:
            i[i < threshold] = np.nan

        self._index = i

        return i, min, max


    def show_hue(self, range=[0, 179]):

        min, max = range

        self.img = Image.fromarray(self.rgb)
        hsv = self.img.convert('HSV')
        hue = np.array(hsv)[:,:,0].astype(float)
        hue[(self.rgb[:,:,0] == 0) & (self.rgb[:,:,1] == 0) & (self.rgb[:,:,2] == 0) & (self.rgb[:,:,3] == 0)] = np.nan

        hue[hue < min] = np.nan
        hue[hue > max] = np.nan

        plt.imshow(hue, cmap='hsv')
        plt.colorbar()
        plt.clim(min, max)
        plt.show()


    def show_hue_hist(self):
            
        self.img = Image.fromarray(self.rgb)
        hsv = self.img.convert('HSV')
        hue = np.array(hsv)[:,:,0].astype(float)

        plt.hist(hue.flatten(), bins=180, range=(0, 179))
        plt.show()


    def select_hue(self):

        widgets.interact(self.show_hue, range=IntRangeSlider(value=[0, 179], min=0, max=179, step=1, description='Hue: ', orientation='horizontal', layout=widgets.Layout(width="auto")))


    def show_saturation(self, range=[0, 255]):
            
        min, max = range

        self.img = Image.fromarray(self.rgb)
        hsv = self.img.convert('HSV')
        sat = np.array(hsv)[:,:,1].astype(float)
        sat[(self.rgb[:,:,0] == 0) & (self.rgb[:,:,1] == 0) & (self.rgb[:,:,2] == 0) & (self.rgb[:,:,3] == 0)] = np.nan

        sat[sat < min] = np.nan
        sat[sat > max] = np.nan

        plt.imshow(sat, cmap='gray')
        plt.colorbar()
        plt.clim(min, max)
        plt.show()


    def show_saturation_hist(self):
                    
        self.img = Image.fromarray(self.rgb)
        hsv = self.img.convert('HSV')
        sat = np.array(hsv)[:,:,1].astype(float)

        plt.hist(sat.flatten(), bins=256, color='gray', alpha=0.5)
        plt.show()


    def select_saturation(self):
            
        widgets.interact(self.show_saturation, range=IntRangeSlider(value=[0, 255], min=0, max=255, step=1, description='Saturation: ', orientation='horizontal', layout=widgets.Layout(width="auto")))


    def show_value(self, range=[0, 255]):
                
        min, max = range

        self.img = Image.fromarray(self.rgb)
        hsv = self.img.convert('HSV')
        val = np.array(hsv)[:,:,2].astype(float)
        val[(self.rgb[:,:,0] == 0) & (self.rgb[:,:,1] == 0) & (self.rgb[:,:,2] == 0) & (self.rgb[:,:,3] == 0)] = np.nan

        val[val < min] = np.nan
        val[val > max] = np.nan

        plt.imshow(val, cmap='gray')
        plt.colorbar()
        plt.clim(min, max)
        plt.show()


    def show_value_hist(self):
                            
        self.img = Image.fromarray(self.rgb)
        hsv = self.img.convert('HSV')
        val = np.array(hsv)[:,:,2].astype(float)

        plt.hist(val.flatten(), bins=256, color='gray', range=(0, 255))


    def select_value(self):

        widgets.interact(self.show_value, range=IntRangeSlider(value=[0, 255], min=0, max=255, step=1, description='Value: ', orientation='horizontal', layout=widgets.Layout(width="auto")))


    def show_brightness(self, range=[0, 255]):

        self.show_value(range)


    def select_brightness(self):
                
        self.select_value()


    def show_rgb(self, band=None):

        if band is None:
            self.select_rgb()

        else:
            try:
                index = BandIndex.get(band) - 1
                if index == 0:
                    plt.imshow(self.rgb[:,:,0], cmap='Reds')
                elif index == 1:
                    plt.imshow(self.rgb[:,:,1], cmap='Greens')
                elif index == 2:
                    plt.imshow(self.rgb[:,:,2], cmap='Blues')
                elif index == 3:
                    plt.imshow(self.rgb[:,:,3], cmap='gray')

                plt.colorbar()
                plt.clim(0, 255)
                plt.show()

            except:
                print('Band number out of range')


    def select_rgb(self):
            
        band = widgets.Dropdown(options=["Red", "Green", "Blue"], description='Band: ')
        widgets.interact(self.show_rgb, band=band)


    def show_rgb_hist(self, band=None):

        if band is None:
            self.select_rgb_hist()

        else:
            try:
                index = BandIndex.get(band) - 1
                if index == 0:
                    plt.hist(self.rgb[:,:,0].flatten(), bins=256, color='red', alpha=0.5)
                elif index == 1:
                    plt.hist(self.rgb[:,:,1].flatten(), bins=256, color='green', alpha=0.5)
                elif index == 2:
                    plt.hist(self.rgb[:,:,2].flatten(), bins=256, color='blue', alpha=0.5)
                elif index == 3:
                    plt.hist(self.rgb[:,:,3].flatten(), bins=256, color='gray', alpha=0.5)

                plt.show()

            except:
                print('Band number out of range')


    def select_rgb_hist(self):
                
            band = widgets.Dropdown(options=["Red", "Green", "Blue"], description='Band: ')
            widgets.interact(self.show_rgb_hist, band=band)


    def show_nir(self):
            
        if self.nir is not None:
            plt.imshow(self.nir, cmap='gray')
            plt.colorbar()
            plt.show()

        else:
            print('NIR band not found')


    def show_re(self):
                    
            if self.re is not None:
                plt.imshow(self.re, cmap='Reds')
                plt.colorbar()
                plt.show()
    
            else:
                print('RE band not found')


    def show_field(self, rotation, x_range=[0, 0], y_range=[0, 0]):

        if rotation is not None:
            self._rot = rotation + 360 if rotation < 0 else rotation
            img = Image.fromarray(self.rgb).rotate(self._rot, expand=False)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(img)

        bbox = [x_range[0], y_range[0], x_range[1], y_range[1]]
        ax.plot([bbox[0], bbox[2]], [bbox[1], bbox[1]], color='red')
        ax.plot([bbox[0], bbox[2]], [bbox[3], bbox[3]], color='red')
        ax.plot([bbox[0], bbox[0]], [bbox[1], bbox[3]], color='red')
        ax.plot([bbox[2], bbox[2]], [bbox[1], bbox[3]], color='red')

        self._img = img.crop(bbox)
        self._bbox = bbox

        plt.show()


    def select_field(self):

        widgets.interact(self.show_field, rotation=IntSlider(min=0, max=360, step=1, value=0, description='Rotation',  layout=widgets.Layout(width="auto")), x_range=IntRangeSlider(value=[0.1*self.x_size, 0.9*self.x_size], min=0, max=self.x_size, step=1, description='X: ', orientation='horizontal', layout=widgets.Layout(width="auto")), y_range=IntRangeSlider(value=[0.1*self.y_size, 0.9*self.y_size], min=0, max=self.y_size, step=1, description='Y: ', orientation='horizontal', layout=widgets.Layout(width="auto")))


    def crop_field(self, rotation=0, x_range=[0, 0], y_range=[0, 0]):
        
        if rotation < 0 or rotation > 360:
            print('Rotation must be within 0 - 360')
        elif x_range[0] < 0 or x_range[1] > self.x_size:
            print('X range must be within 0 - ', self.x_size)
        elif y_range[0] < 0 or y_range[1] > self.y_size:
            print('Y range must be within 0 - ', self.y_size)
        else:
            self.show_field(rotation, x_range, y_range)
            self.update()


    def show_grid(self, rotation=0, x_range=[0, 0], y_range=[0, 0], x_split=10, y_split=10, grid_num=False):

        self._rot = rotation + 360 if rotation < 0 else rotation

        img = Image.fromarray(self.rgb).rotate(self._rot, expand=False)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(img)

        bbox = [x_range[0], y_range[0], x_range[1], y_range[1]]
        ax.plot([bbox[0], bbox[2]], [bbox[1], bbox[1]], color='red')
        ax.plot([bbox[0], bbox[2]], [bbox[3], bbox[3]], color='red')
        ax.plot([bbox[0], bbox[0]], [bbox[1], bbox[3]], color='red')
        ax.plot([bbox[2], bbox[2]], [bbox[1], bbox[3]], color='red')

        self._x_split = x_split
        self._y_split = y_split

        if x_split > 1:
            x_step = (bbox[2] - bbox[0]) / x_split
            for i in range(1, x_split):
                ax.plot([bbox[0] + i * x_step, bbox[0] + i * x_step], [bbox[1], bbox[3]], color='red')

        if y_split > 1:
            y_step = (bbox[3] - bbox[1]) / y_split
            for i in range(1, y_split):
                ax.plot([bbox[0], bbox[2]], [bbox[1] + i * y_step, bbox[1] + i * y_step], color='red')

        if grid_num and x_split > 1 and y_split > 1:
            x_step = (bbox[2] - bbox[0]) / x_split
            y_step = (bbox[3] - bbox[1]) / y_split
            for i in range(0, x_split):
                for j in range(0, y_split):
                    ax.text(bbox[1] + i * x_step, bbox[1] + (j+0.5) * y_step, str(j)+str(i), color='red')        
        elif grid_num and x_split > 1:
            x_step = (bbox[2] - bbox[0]) / x_split
            for i in range(0, x_split):
                ax.text(bbox[1] + i * x_step, bbox[3], str(i), color='red')
        elif grid_num and y_split > 1:
            y_step = (bbox[3] - bbox[1]) / y_split
            for i in range(0, y_split):
                ax.text(bbox[0], bbox[1] + (i+0.5) * y_step, str(i), color='red')

        self._img = img.crop(bbox)
        self._rgb = self._rgb[bbox[1]:bbox[3], bbox[0]:bbox[2]]
        self._dsm = self._dsm[bbox[1]:bbox[3], bbox[0]:bbox[2]] if self.dsm is not None else None
        self.dtm = self.dtm[bbox[1]:bbox[3], bbox[0]:bbox[2]] if self.dtm is not None else None
        self._bbox = bbox

        plt.show()


    def crop_grid(self, rotation=0, x_range=[0, 0], y_range=[0, 0], x_split=10, y_split=10, grid_num=False):
            
        if rotation < 0 or rotation > 360:
            print('Rotation must be within 0 - 360')
        elif x_range[0] < 0 or x_range[1] > self.x_size:
            print('X range must be within 0 - ', self.x_size)
        elif y_range[0] < 0 or y_range[1] > self.y_size:
            print('Y range must be within 0 - ', self.y_size)
        elif x_split < 2:
            print('X split must be > 1')
        elif y_split < 2:
            print('Y split must be > 1')
        else:
            self.show_grid(rotation, x_range, y_range, x_split, y_split, grid_num)
            self.update()


    def split(self, x_split=None, y_split=None):

        self.update()

        FIs = []

        x_split = self._x_split if x_split is None else x_split
        y_split = self._y_split if y_split is None else y_split

        if x_split > 1 and y_split > 1:
            x_step = self.img.size[0] // x_split
            y_step = self.img.size[1] // y_split
            for j in range(0, y_split):
                _ = []
                for i in range(0, x_split):
                    img = self.img.crop((i * x_step, j * y_step, (i+1) * x_step, (j+1) * y_step))
                    rgb = np.array(img)
                    dsm = self.dsm[j * y_step:(j+1) * y_step, i * x_step:(i+1) * x_step] if self.dsm is not None else None
                    dtm = self.dtm[j * y_step:(j+1) * y_step, i * x_step:(i+1) * x_step] if self.dtm is not None else None
                    nir = self.nir[j * y_step:(j+1) * y_step, i * x_step:(i+1) * x_step] if self.nir is not None else None
                    re = self.re[j * y_step:(j+1) * y_step, i * x_step:(i+1) * x_step] if self.re is not None else None
                    FI = FieldImage(rgb=rgb, dsm=dsm, dtm=dtm, nir=nir, re=re, gsd=self.gsd)
                    _rgb = self._rgb[j * y_step:(j+1) * y_step, i * x_step:(i+1) * x_step] if self._rgb is not None else None
                    FI._rgb = _rgb
                    _dsm = self._dsm[j * y_step:(j+1) * y_step, i * x_step:(i+1) * x_step] if self._dsm is not None else None
                    FI._dsm = _dsm
                    _.append(FI)
                FIs.append(_)

        return FIs
                

    def select_grid(self):
            
            widgets.interact(self.show_grid, rotation=IntSlider(min=0, max=360, step=1, value=0, description='Rotation',  layout=widgets.Layout(width="auto")), x_range=IntRangeSlider(value=[0.1*self.x_size, 0.9*self.x_size], min=0, max=self.x_size, step=1, description='X: ', orientation='horizontal', layout=widgets.Layout(width="auto")), y_range=IntRangeSlider(value=[0.1*self.y_size, 0.9*self.y_size], min=0, max=self.y_size, step=1, description='Y: ', orientation='horizontal', layout=widgets.Layout(width="auto")), x_split=widgets.IntText(step=1, value=10, description='X Grid: '), y_split=widgets.IntText(step=1, value=10, description='Y Grid: '), grid_num=widgets.Checkbox(value=True, description='Grid No.'))


    def set_nir(self, nir):
                
        self.nir = nir.ReadAsArray()


    def set_re(self, re):

        self.re = re.ReadAsArray()

    
    def set_dsm(self, dsm):
            
        self.dsm = dsm.ReadAsArray()
        self.dsm[self.dsm == -9999] = np.nan

        self._dsm = self.dsm.copy()


    def set_dtm(self, dtm):
                        
        self.dtm = dtm.ReadAsArray()
        self.dtm[self.dtm == -9999] = np.nan

    
    def delete_nir(self):
            
        self.nir = None

    
    def delete_re(self):

        self.re = None


    def delete_dsm(self):
                    
        self.dsm = None


    def delete_dtm(self):

        self.dtm = None

    
    def show_dsm(self, min=None, max=None, cmap=None, threshold=None):

        if self.dsm is not None:
            dsm = self.dsm.copy()
            if threshold is not None:
                dsm[self.dsm < threshold] = np.nan
            plt.imshow(dsm)
            plt.colorbar()
            if cmap is not None:
                plt.set_cmap(cmap)
            if min is not None and max is not None:
                plt.clim(min, max)
            plt.show()

        else:
            print('DSM not found')

    
    def show_dtm(self, min=None, max=None, cmap=None, threshold=None):

        if self.dtm is not None:
            dtm = self.dtm.copy()
            if threshold is not None:
                dtm[self.dtm < threshold] = np.nan
            plt.imshow(dtm)
            plt.colorbar()
            if cmap is not None:
                plt.set_cmap(cmap)
            if min is not None and max is not None:
                plt.clim(min, max)
            plt.show()

        else:
            print('DTM not found')


    def select_dsm(self):

        if self.dsm is not None:
            min = widgets.FloatText(value=np.nanmin(self.dsm), description='Min: ')
            max = widgets.FloatText(value=np.nanmax(self.dsm), description='Max: ')
            cmap = widgets.Dropdown(options=['terrain', 'viridis', 'plasma', 'inferno', 'magma', 'cividis'], description='Colormap: ')
            threshold = widgets.FloatSlider(value=np.nanmin(self.dsm), min=np.nanmin(self.dsm), max=np.nanmax(self.dsm), description='Threshold: ', orientation='horizontal', layout=widgets.Layout(width="auto"))
            widgets.interact(self.show_dsm, min=min, max=max, cmap=cmap, threshold=threshold)

        else:
            print('DSM not found')


    def select_dtm(self):
            
        if self.dtm is not None:
            min = widgets.FloatText(value=np.nanmin(self.dtm), description='Min: ')
            max = widgets.FloatText(value=np.nanmax(self.dtm), description='Max: ')
            cmap = widgets.Dropdown(options=['terrain', 'viridis', 'plasma', 'inferno', 'magma', 'cividis'], description='Colormap: ')
            threshold = widgets.FloatSlider(value=np.nanmin(self.dtm), min=np.nanmin(self.dtm), max=np.nanmax(self.dtm), description='Threshold: ', orientation='horizontal', layout=widgets.Layout(width="auto"))
            widgets.interact(self.show_dtm, min=min, max=max, cmap=cmap, threshold=threshold)

        else:
            print('DTM not found')


    def show_dsm_hist(self):

        if self.dsm is not None:
            plt.hist(self.dsm.flatten(), bins=256, color='gray', alpha=0.5)
            plt.show()

        else:
            print('DSM not found')


    def show_dtm_hist(self):
                    
        if self.dtm is not None:
            plt.hist(self.dtm.flatten(), bins=256, color='gray', alpha=0.5)
            plt.show()

        else:
            print('DTM not found')


    def show_dsm_grad(self, threshold=None, cmap='gray', min=None, max=None):

        if self.dsm is not None:
            grad = np.gradient(self.dsm)
            if threshold is not None:
                grad[0][grad[0] < threshold] = np.nan
            plt.imshow(grad[0], cmap=cmap)
            plt.colorbar()
            if min is not None and max is not None:
                plt.clim(min, max)
            plt.show()

        else:
            print('DSM not found')


    def select_dsm_grad(self):
                
        if self.dsm is not None:
            threshold = widgets.FloatText(value=np.nanmin(np.gradient(self.dsm)[0]), description='Threshold: ')
            cmap = widgets.Dropdown(options=['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis'], description='Colormap: ')
            min = widgets.FloatText(value=np.nanmin(np.gradient(self.dsm)[0]), description='Min: ')
            max = widgets.FloatText(value=np.nanmax(np.gradient(self.dsm)[0]), description='Max: ')
            widgets.interact(self.show_gradient, threshold=threshold, cmap=cmap, min=min, max=max)

        else:
            print('DSM not found')


    def offset_dsm(self, offset=0):

        if self.dsm is not None:
            self.dsm += offset
        else:
            print('DSM not found')


    def offset_dtm(self, offset=0):
            
        if self.dtm is not None:
            self.dtm += offset
        else:
            print('DTM not found')


    def create_dtm(self, axis=0, method='linear', order=1):

        if self.dsm is None:
            print('DSM not found')
            return

        self.dtm = self.dsm.copy()

        import pandas as pd

        df = pd.DataFrame(self.dsm)
        df = df.interpolate(axis=axis, limit_direction='both', method=method, order=order)
        self.dtm = df.to_numpy()


    def show_full(self):
                
        if self._rgb is not None:
            plt.imshow(self._rgb)
            plt.show()
        else:
            print('Image not found')


    def show_dsm_full(self, min=None, max=None, cmap=None):
                
        if self._dsm is not None:
            plt.imshow(self._dsm)
            if cmap is not None:
                plt.colorbar(cmap=cmap)
            else:
                plt.colorbar()
            if min is not None and max is not None:
                plt.clim(min, max)
            elif min is not None:
                plt.clim(min, np.nanmax(self._dsm))
            elif max is not None:
                plt.clim(np.nanmin(self._dsm), max)
            plt.show()
        else:
            print('DSM not found')


    def create_chm(self, zerofill=False):

        if self.dsm is not None and self.dtm is not None:
            diff = self._dsm - self.dtm if self._dsm is not None else self.dsm - self.dtm
            if zerofill:
                pass
            else:
                diff[diff == 0] = np.nan
            self.chm = diff
        else:
            print('DSM and/or DTM not found')


    def show_chm(self, threshold=None, min=None, max=None, cmap=None):

        if self.chm is not None:
            chm = self.chm.copy()
            if threshold is not None:
                chm[chm < threshold] = np.nan
            plt.imshow(chm)
            if cmap is not None:
                plt.colorbar(cmap=cmap)
            else:
                plt.colorbar()
            if min is not None and max is not None:
                plt.clim(min, max)
            elif min is not None:
                plt.clim(min, np.nanmax(chm))
            elif max is not None:
                plt.clim(np.nanmin(chm), max)
            plt.show()
        else:
            print('CHM not found')


    def max_chm(self):
            
        if self.chm is not None:
            return np.nanmax(self.chm)
        else:
            print('CHM not found')
            return None
        

    def min_chm(self):
                    
        if self.chm is not None:
            return np.nanmin(self.chm)
        else:
            print('CHM not found')
            return None
        

    def mean_chm(self):
                            
        if self.chm is not None:
            return np.nanmean(self.chm)
        else:
            print('CHM not found')
            return None
            

    def median_chm(self):

        if self.chm is not None:
            return np.nanmedian(self.chm)
        else:
            print('CHM not found')
            return None
        
            
    def std_chm(self):
                                    
        if self.chm is not None:
            return np.nanstd(self.chm)
        else:
            print('CHM not found')
            return None


    def proj_area(self):

        if self.gsd is None:
            print('GSD is not specified.')
            gsd = 1
        else:
            gsd = self.gsd
        
        return np.count_nonzero(~np.isnan(self.chm)) * gsd ** 2
    

    def surf_area(self):

        if self.gsd is None:
            print('GSD is not specified.')
            gsd = 1
        else:
            gsd = self.gsd

        if self.chm is not None:
            grad = np.gradient(self._dsm)
            surf = np.sqrt(1 + grad[0]**2 + grad[1]**2)
            surf = surf[~np.isnan(self.chm)]
            return np.nansum(surf) * gsd ** 2
        else:
            print('CHM not found')
            return None
        

    def square(self):

        if self.gsd is None:
            print('GSD is not specified.')
            gsd = 1
        else:
            gsd = self.gsd

        return self.shape[0] * self.shape[1] * gsd


    def clear_cache(self):

        self._img = None
        self._rot = 0
        self._bbox = None
        self._index = None


    def update(self):
        
        if self._img is not None:
            self.orthophoto = None
            self.img = self._img
            self.rgb = np.array(self._img)
            self.geo = None
            self.proj = None
            self.x_size, self.y_size = self._img.size
            if self.dsm is not None:
                if self._rot != 0:
                    dsm = Image.fromarray(self.dsm)
                    dsm = dsm.rotate(self._rot, expand=False)
                    self.dsm = np.array(dsm)
                    self.dsm[self.dsm == 0] = np.nan
                    self._rot = 0 if self.dtm is not None else self._rot
                if self._bbox is not None:
                    self.dsm = self.dsm[self._bbox[1]:self._bbox[3], self._bbox[0]:self._bbox[2]]
                    self._bbox = None if self.dtm is not None else self._bbox
            if self.dtm is not None:
                if self._rot != 0:
                    dtm = Image.fromarray(self.dtm)
                    dtm = dtm.rotate(self._rot, expand=False)
                    self.dtm = np.array(dtm)
                    self.dtm[self.dtm == 0] = np.nan
                    self._rot = 0
                if self._bbox is not None:
                    self.dtm = self.dtm[self._bbox[1]:self._bbox[3], self._bbox[0]:self._bbox[2]]
                    self._bbox = None
            self._img = None

        if self._index is not None:
            rgb = self.rgb.copy()
            self._rgb = self.rgb.copy()
            self._dsm = self.dsm.copy() if self.dsm is not None else None
            for j in range(self.y_size):
                for k in range(self.x_size):
                    if np.isnan(self._index[j, k]):
                        rgb[j, k] = [0, 0, 0, 0] if self.rgb.shape[2] == 4 else [0, 0, 0]
                        if self.dsm is not None:
                            self._dsm[j, k] = self.dsm[j, k]
                            self.dsm[j, k] = np.nan
            self.img = Image.fromarray(rgb)
            self.rgb = np.array(self.img)
            self._index = None

