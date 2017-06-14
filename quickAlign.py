# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 17:58:28 2017

@author: cailab
"""
import os
import ClearMap.IO as io  
import ClearMap.Settings as settings
from ClearMap.ImageProcessing.CellDetection import detectCells;
import numpy
import ClearMap.Visualization.Plot as plt;
import ClearMap.ImageProcessing.BackgroundRemoval as bgr
from ClearMap.ImageProcessing.Filter.DoGFilter import filterDoG
from ClearMap.ImageProcessing.MaximaDetection import findExtendedMaxima
import pdb
from ClearMap.ImageProcessing.MaximaDetection import findCenterOfMaxima
from ClearMap.ImageProcessing.MaximaDetection import findIntensity
from ClearMap.Analysis.Statistics import thresholdPoints
from ClearMap.Alignment.Resampling import resampleData;
from ClearMap.Alignment.Resampling import resamplePoints, resamplePointsInverse

from ClearMap.Alignment.Elastix import alignData, transformPoints, deformationField, deformationDistance
from ClearMap.Alignment.Elastix import parseElastixOutputPoints2d, getMinMetric, autoAlignData
from ClearMap.Analysis.Label import countPointsInRegions, labelPoints2d
from ClearMap.Analysis.Label import LabelInfo, labelToName
from ClearMap.ImageProcessing.CellSizeDetection import detectCellShape, findCellSize,findCellIntensity

backgroundSize = (10,10,1);
DoGSize = (10,10,1)
maximaThresh = 5;
cellShapeThresh = 5;
pointsThresh = (5,50);
threshType = (3,3);
orientation = 'Coronal';
pixelRes = (2.3719,2.3719,1);
overWrite = 'No';
#####

#Elastix
affineParameterFile = '/home/cailab/clearmap_ressources_mouse_brain/ClearMap_ressources/Par0000affine.txt'
bSplineParameterFile= '/home/cailab/clearmap_ressources_mouse_brain/ClearMap_ressources/BsplineDefault.txt'
atlasDir = os.path.join('/media/sf_Fred_Data/testClearMap/',orientation+'Atlas');
annoDir =  os.path.join('/media/sf_Fred_Data/testClearMap/',orientation+'Annotation');
auto_fn = ['/media/sf_Fred_Data/OdorInduction/cfosOdor052417/Debugging/C2-MAX_8d_594.tif','/media/sf_Fred_Data/OdorInduction/cfosOdor052417/Debugging/MAX_8d_debugging_546.tif']

auto_R_fn = '/media/sf_Fred_Data/OdorInduction/cfosOdor052417/testAlign/testR.tif'
tempDir = '/media/sf_Fred_Data/OdorInduction/cfosOdor052417/testAlign'

for i in range(len(auto_fn)):
    imgR = io.readData(auto_fn[i]);
    imgR = imgR[...,numpy.newaxis]
    imgR = imgR.astype('int16');
    imgR, scaleFactor = resampleData(imgR, auto_R_fn,  orientation=(1,2,3), dataSizeSink = None, resolutionSource = pixelRes , resolutionSink = (25, 25,1), 
                     processingDirectory = None, processes = 4, cleanup = True, verbose = True, interpolation = 'linear');
                     
    bestSlice = autoAlignData(imgR, atlasDir, affineParameterFile, bSplineParameterFile, resultDirectory = alignDir, tempDir = tempDir, lowB = 250, upperB = 300,orientation = orientation)
    print(auto_fn[i]); print(bestSlice)