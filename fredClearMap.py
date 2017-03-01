# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 18:35:16 2017

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
#Set the Parameters Change this! 
homeDir = '/media/sf_Fred_Data/testClearMap/Douglas/'
input_fn = os.path.join(homeDir,'TDtomato_stack/Tomato6552-3R-3b0000.tif')
orientation = 'Sagittal'
######


#AutoFluorescence Image for registration/alignment
auto_fn = os.path.join(homeDir,'AutoF.tif');

#Resampled Image Filename
auto_R_fn = os.path.join(homeDir, 'AutoF_R.tif');

#Elastix points FN after resampling
points_elastix_fn = os.path.join( homeDir, 'ElastixPoints.txt');

#Points before resampling
points_fn = os.path.join(homeDir,'Points.npy');

affineParameterFile = '/home/cailab/clearmap_ressources_mouse_brain/ClearMap_ressources/Par0000affine.txt'
bSplineParameterFile= '/home/cailab/clearmap_ressources_mouse_brain/ClearMap_ressources/BsplineDefault.txt'
alignResultDir = os.path.join(homeDir,'Align')
tempDir = os.path.join(homeDir,'TempAlign')
transformResultDir = os.path.join(homeDir,'Transform');
transformFN = os.path.join(transformResultDir,'outputpoints.txt');
tableFN = os.path.join(homeDir,'ResultsTable.csv');

atlasDir = os.path.join('/media/sf_Fred_Data/testClearMap/',orientation+'Atlas');
annoDir =  os.path.join('/media/sf_Fred_Data/testClearMap/',orientation+'Annotation');
transformParameterFN = os.path.join(alignResultDir,'TransformParameters.1.txt');


img = io.readData(input_fn);
img = img[...,numpy.newaxis]
img = img.astype('int16'); # converting data to smaller integer types can be more memory efficient!

imgB = bgr.removeBackground(img, size=(8,8), verbose = True)
io.writeData(os.path.join(homeDir,'Results/BackgroundRemoval.tif'), imgB);

#image filter
imgD = filterDoG(imgB, size=(15,15,1), verbose = True)
io.writeData(os.path.join(homeDir,'Results/FilterDoG.tif'), imgD);

#Detect Maxima
imgMaxima = findExtendedMaxima(imgD, hMax = None, verbose = True, threshold =3 )
points = findCenterOfMaxima(img,imgMaxima);
points =points.astype('int16');

#threshold intensities
dataShape = detectCellShape(imgD, points, threshold = 5);
cellSizesPre = findCellSize(dataShape, maxlabel=points.shape[0])
io.writeData(os.path.join(homeDir, 'Results/CellShapes.tif'), 20*dataShape.astype('int32'));

#cintensity = findIntensity(imgD, points);

#points, intensities = thresholdPoints(points,cintensity, threshold = (5,20), row = (1,1));
points,cellSizesPost = thresholdPoints(points,cellSizesPre,threshold=(5,100),row = (3,3))

#pdb.set_trace()
#io.writeData(os.path.join(homeDir, 'Results/OverlayWatershed.tif'), overlay_Img);

overlay_Img = plt.fredOverlayPoints(input_fn, points, pointColor = [200,0,0]);
io.writeData(os.path.join(homeDir, 'Results/PointsOriginalImg.tif'), overlay_Img);

overlay_Img = plt.fredOverlayPoints(os.path.join(homeDir,'Results/FilterDoG.tif'), points, pointColor = [200,0,0]);
io.writeData(os.path.join(homeDir, 'Results/PointsFilterDoG.tif'), overlay_Img);
#################################################################################################


#Convert points from 3d to 2d
points = numpy.delete(points,2,axis=1)
io.writePoints(points_fn,points);
#Resampled Img
imgR = io.readData(auto_fn);
imgR = imgR[...,numpy.newaxis]
imgR = imgR.astype('int16');
imgR, scaleFactor = resampleData(imgR, auto_R_fn,  orientation=(1,2,3), dataSizeSink = None, resolutionSource = (2.3719,2.3719,1), resolutionSink = (25, 25,1), 
                 processingDirectory = None, processes = 4, cleanup = True, verbose = True, interpolation = 'linear');
                 
#resample Points
pointsRe = numpy.zeros(points.shape)
for i in range(len(points.shape)):
    pointsRe[:,i] = numpy.divide(points[:,i],scaleFactor[i]).round()
pointsRe = pointsRe.astype('int16');


io.writeElastixPoints(points_elastix_fn,pointsRe);

#align data
#alignData(auto_R_fn,refImg_fn, affineParameterFile, bSplineParameterFile, alignResultDir);

bestSlice = autoAlignData(imgR, atlasDir, affineParameterFile, bSplineParameterFile, resultDirectory = alignResultDir, tempDir = tempDir, sliceNum = 195 , bounds = 1,orientation = 'Sagittal')

annoImg_fn = os.path.join(annoDir, 'Anno'+str(bestSlice).zfill(3)+'.tif');
refImg_fn  = os.path.join(atlasDir, 'Ref'+str(bestSlice).zfill(3)+'.tif');

transformPoints(points_elastix_fn, sink = None, transformParameterFile = transformParameterFN, transformDirectory = None, indices = False, resultDirectory = transformResultDir, tmpFile = None)

points = parseElastixOutputPoints2d(transformFN, indices = False)
points = points.astype('int16');
pointLabels = labelPoints2d(points, labeledImage = annoImg_fn, level = None, collapse = 1)

#defField = deformationField(sink = [], transformParameterFile = transformParameterFN, transformDirectory = None, resultDirectory = transformResultDir)
#defDistance = deformationDistance(defField, sink = None, scale = None)
#print 'Mean Deformation distance= %d' %defDistance.mean()


ids,counts = countPointsInRegions(points, labeledImage = annoImg_fn, intensities = None,collapse = 1)
#Table generation
table = numpy.zeros(ids.shape,dtype=[('id','int64'),('counts','f8'),('name','a256')])
table['id'] = ids
table['counts']=counts
table['name'] = labelToName(ids)
io.writeTable(tableFN,table)

beforeTransform = plt.fredOverlayPoints(auto_R_fn, pointsRe, pointColor = [200,0,0]);
io.writeData(os.path.join(homeDir, 'Results/BeforeTransformation.tif'), beforeTransform);


afterTransform = plt.fredOverlayPoints(refImg_fn, points, pointColor = [200,0,0]);
io.writeData(os.path.join(homeDir, 'Results/AfterTransformation.tif'), afterTransform);

