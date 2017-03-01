# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 11:44:11 2017

@author: cailab
"""
import numpy
import os
import ClearMap.IO as io  
import ClearMap.Settings as settings
import ClearMap.ImageProcessing.SpotDetection as sd
fn = '/media/sf_Fred_Data/testClearMap/1741-2-5/test-z\d{4}.tif'
img = io.readData(fn);

img = img.astype('int16'); # converting data to smaller integer types can be more memory efficient!
res = sd.detectSpots(img, dogSize = (5,5,5), flatfield = None, threshold = 5, cellShapeThreshold = 1);
print 'Found %d cells !' % res[0].shape[0]