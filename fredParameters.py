# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 11:48:09 2017

@author: cailab
"""

###Parameters File####

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


#Set the Parameters Change this! 
homeDir = '/media/sf_Fred_Data/testClearMap/Douglas/';
input_fn = os.path.join(homeDir,'TDtomato_stack/Tomato6552-3R-3b0001.tif');
orientation = 'Sagittal';
pixelRes = (2.3719,2.3719,1)
sliceNum = 195
bounds = 2
######

backgroundSize = (10,10,1);
DoGSize = (10,10,1)
maximaThresh = 3;
cellShapeThresh = 5;
pointsThresh = (10,100);
threshType = (3,3);
#####

alignDir = os.path.join(homeDir,'Align');
tempDir = os.path.join(homeDir,'TempAlign');
resultDir = os.path.join(homeDir,'Results');
transformDir = os.path.join(homeDir,'Transform');


if not os.path.exists(alignDir):
    os.makedirs(alignDir)
if not os.path.exists(tempDir):
    os.makedirs(tempDir)
if not os.path.exists(resultDir):
    os.makedirs(resultDir)
if not os.path.exists(transformDir):
    os.makedirs(transformDir)
    
#AutoFluorescence Image for registration/alignment
auto_fn = os.path.join(homeDir,'AutoF.tif');

#Resampled Image Filename
auto_R_fn = os.path.join(homeDir, 'AutoF_R.tif');

#Elastix points FN after resampling
points_elastix_fn = os.path.join(resultDir, 'ElastixPoints.txt');

#Points before resampling
points_fn = os.path.join(resultDir,'Points.npy');

#Elastix
affineParameterFile = '/home/cailab/clearmap_ressources_mouse_brain/ClearMap_ressources/Par0000affine.txt'
bSplineParameterFile= '/home/cailab/clearmap_ressources_mouse_brain/ClearMap_ressources/BsplineDefault.txt'


transformFN = os.path.join(transformDir,'outputpoints.txt');
tableFN = os.path.join(resultDir,'ResultsTable.csv');

#Atlas and Annotation
atlasDir = os.path.join('/media/sf_Fred_Data/testClearMap/',orientation+'Atlas');
annoDir =  os.path.join('/media/sf_Fred_Data/testClearMap/',orientation+'Annotation');
transformParameterFN = os.path.join(alignDir,'TransformParameters.1.txt');

