# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 16:49:18 2017

@author: cailab
"""

#Fred Batch
from string import ascii_lowercase as alphabet
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


animalPath = '/media/sf_Fred_Data/OdorInduction/cfosOdor060717';
#whichWell = 8; 
#wellDir = os.path.join(animalPath,'Well_'+str(whichWell));
cfosDir = os.path.join(animalPath,'totalC1');  #C1 folder is cfos signal
autoDir = os.path.join(animalPath,'totalC2');  #c2 folder is autofluorescence
listSections = os.listdir(cfosDir); 

for i in range(len(listSections)):
    
    if not os.path.exists(os.path.join(animalPath,'Align',listSections[i][-6:-4])):
        os.makedirs(os.path.join(animalPath,'Align',listSections[i][-6:-4]))
    if not os.path.exists(os.path.join(animalPath,'Results',listSections[i][-6:-4])):
        os.makedirs(os.path.join(animalPath,'Results',listSections[i][-6:-4]))
    if not os.path.exists(os.path.join(animalPath,'Transform',listSections[i][-6:-4])):
        os.makedirs(os.path.join(animalPath,'Transform',listSections[i][-6:-4]))        
        
if not os.path.exists(os.path.join(animalPath,'tempAlign')):
    os.makedirs(os.path.join(animalPath,'tempAlign'))


######

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


##Loop through all cfos files
for z in range(len(listSections)):
    cfos_fn = os.path.join(cfosDir,listSections[z]);
    fName = listSections[z][-6:-4];
    resultDir = os.path.join(animalPath,'Results',fName) ;     
    points_fn = os.path.join(animalPath,'Points.npy');
    transformDir = os.path.join(animalPath,'Transform',fName);
    alignDir = os.path.join(animalPath,'Align',fName);
  
    bestSliceFN = os.path.join(resultDir,'BestSlice.npy');
    if overWrite == 'No' and os.path.exists(bestSliceFN): continue;
    
    
    #AutoFluorescence Image for registration/alignment
    auto_fn = os.path.join(autoDir,listSections[z]);

    #Resampled Image Filename
    auto_R_fn = os.path.join(resultDir, 'AutoF_R.tif');
    
    #Elastix points FN after resampling
    points_elastix_fn = os.path.join(resultDir, 'ElastixPoints.txt');
    
    #Points before resampling
    points_fn = os.path.join(resultDir,'Points.npy');
    tPointsFN = os.path.join(resultDir,'Transformed_Points.npy');
    
    
    transformFN = os.path.join(transformDir,'outputpoints.txt');
    tableFN = os.path.join(resultDir,'ResultsTable.csv');
    
    #Atlas and Annotation
    transformParameterFN = os.path.join(alignDir,'TransformParameters.1.txt');  

    print(cfos_fn);
    img = io.readData(cfos_fn);
    img = img[...,numpy.newaxis]
    img = img.astype('int16'); # converting data to smaller integer types can be more memory efficient!
    
    imgB = bgr.removeBackground(img, size=backgroundSize, verbose = True)
    io.writeData(os.path.join(resultDir,fName + '_BackgroundRemoval.tif'), imgB);
    
    ##image filter
    imgD = filterDoG(img, size=DoGSize, verbose = True)
    io.writeData(os.path.join(resultDir,fName + '_FilterDoG.tif'), imgD);
    
    #Detect Maxima
    imgMaxima = findExtendedMaxima(img, hMax = None, verbose = True, threshold =maximaThresh )
    points = findCenterOfMaxima(img,imgMaxima,verbose = True);
    points =points.astype('int16');
    
    #threshold intensities
    dataShape = detectCellShape(imgD, points, threshold = cellShapeThresh, verbose = True);
    cellSizesPre = findCellSize(dataShape, maxlabel=points.shape[0])
    
    io.writeData(os.path.join(resultDir, fName+ '_CellShapes.tif'), 255*dataShape.astype('int32')/dataShape.max());
    #cintensity = findIntensity(imgD, points);
    
    #points, intensities = thresholdPoints(points,cintensity, threshold = (5,20), row = (1,1));
    points,cellSizesPost = thresholdPoints(points,cellSizesPre,threshold=pointsThresh,row = threshType)
    
    #pdb.set_trace()
    #io.writeData(os.path.join(homeDir, 'Results/OverlayWatershed.tif'), overlay_Img);
    
    overlay_Img = plt.fredOverlayPoints(cfos_fn, points, pointColor = [200,0,0]);
    io.writeData(os.path.join(resultDir, fName+ '_PointsOriginalImg.tif'), overlay_Img);
    
    overlay_Img = plt.overlayPoints(imgD, points, pointColor = [200,0,0]);
    io.writeData(os.path.join(resultDir, fName+ '_PointsFilterDoG.tif'), overlay_Img);
    
    #Convert points from 3d to 2d
    points = numpy.delete(points,2,axis=1)
    io.writePoints(points_fn,points);

##############################################################333


    imgR = io.readData(auto_fn);
    imgR = imgR[...,numpy.newaxis]
    imgR = imgR.astype('int16');
    imgR, scaleFactor = resampleData(imgR, auto_R_fn,  orientation=(1,2,3), dataSizeSink = None, resolutionSource = pixelRes , resolutionSink = (25, 25,1), 
                     processingDirectory = None, processes = 4, cleanup = True, verbose = True, interpolation = 'linear');
    
    points = numpy.load(points_fn) 
    #resample Points
    pointsRe = numpy.zeros(points.shape)
    for i in range(len(points.shape)):
        pointsRe[:,i] = numpy.divide(points[:,i],scaleFactor[i]).round()
    pointsRe = pointsRe.astype('int16');
    
    
    io.writeElastixPoints(points_elastix_fn,pointsRe);
    
    #align data
    #alignData(auto_R_fn,refImg_fn, affineParameterFile, bSplineParameterFile, alignResultDir);
#    if z==0:
#        lowB = 90; 
#        upperB = lowB + 100;
    
    bestSlice = autoAlignData(imgR, atlasDir, affineParameterFile, bSplineParameterFile, resultDirectory = alignDir, tempDir = os.path.join(animalPath,'tempAlign'), lowB =250 , upperB = 325 ,orientation = orientation)
    io.writePoints(bestSliceFN,bestSlice)
#    lowB = bestSlice;
#    upperB = lowB + 100;    
    
    annoImg_fn = os.path.join(annoDir, 'Anno'+str(bestSlice).zfill(3)+'.tif');
    refImg_fn  = os.path.join(atlasDir, 'Ref'+str(bestSlice).zfill(3)+'.tif');
    
    transformPoints(points_elastix_fn, sink = None, transformParameterFile = transformParameterFN, transformDirectory = None, indices = False, resultDirectory = transformDir, tmpFile = None)
    
    points = parseElastixOutputPoints2d(transformFN, indices = False)   
    
    points = points.astype('int16');
    io.writePoints(tPointsFN,points); 
    pointLabels = labelPoints2d(points, labeledImage = annoImg_fn, level = None, collapse = None)
    
    #defField = deformationField(sink = [], transformParameterFile = transformParameterFN, transformDirectory = None, resultDirectory = transformResultDir)
    #defDistance = deformationDistance(defField, sink = None, scale = None)
    #print 'Mean Deformation distance= %d' %defDistance.mean()
    
    
    ids,counts = countPointsInRegions(points, labeledImage = annoImg_fn, intensities = None,collapse = None)
    #Table generation
    table = numpy.zeros(ids.shape,dtype=[('id','int64'),('counts','f8'),('name','a256')])
    table['id'] = ids
    table['counts']=counts
    table['name'] = labelToName(ids)
    io.writeTable(tableFN,table)
    
    beforeAlign = plt.fredOverlayPoints(auto_R_fn, pointsRe, pointColor = [200,0,0]);
    io.writeData(os.path.join(resultDir, 'BeforeAlign.tif'), beforeAlign);
    
    
    afterAlign = plt.fredOverlayPoints(refImg_fn, points, pointColor = [200,0,0]);
    io.writeData(os.path.join(resultDir, 'AfterAlign.tif'), afterAlign);
