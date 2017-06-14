# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 12:45:31 2017

@author: cailab
"""

execfile('/home/cailab/ClearMap/fredParameters.py')


img = io.readData(input_fn);
img = img[...,numpy.newaxis]
img = img.astype('int16'); # converting data to smaller integer types can be more memory efficient!

imgB = bgr.removeBackground(img, size=backgroundSize, verbose = True)
io.writeData(os.path.join(resultDir,fName+ 'BackgroundRemoval.tif'), imgB);

##image filter
imgD = filterDoG(img, size=DoGSize, verbose = True)
io.writeData(os.path.join(resultDir,fName+ 'FilterDoG.tif'), imgD);

#Detect Maxima
imgMaxima = findExtendedMaxima(img, hMax = None, verbose = True, threshold =maximaThresh )
points = findCenterOfMaxima(img,imgMaxima,verbose = True);
points =points.astype('int16');

#threshold intensities
dataShape = detectCellShape(imgD, points, threshold = cellShapeThresh, verbose = True);
cellSizesPre = findCellSize(dataShape, maxlabel=points.shape[0])

io.writeData(os.path.join(resultDir, fName+ 'CellShapes.tif'), 255*dataShape.astype('int32')/dataShape.max());
#cintensity = findIntensity(imgD, points);

#points, intensities = thresholdPoints(points,cintensity, threshold = (5,20), row = (1,1));
points,cellSizesPost = thresholdPoints(points,cellSizesPre,threshold=pointsThresh,row = threshType)

#pdb.set_trace()
#io.writeData(os.path.join(homeDir, 'Results/OverlayWatershed.tif'), overlay_Img);

overlay_Img = plt.fredOverlayPoints(input_fn, points, pointColor = [200,0,0]);
io.writeData(os.path.join(resultDir, fName+ 'PointsOriginalImg.tif'), overlay_Img);

overlay_Img = plt.overlayPoints(imgD, points, pointColor = [200,0,0]);
io.writeData(os.path.join(resultDir, fName+ 'PointsFilterDoG.tif'), overlay_Img);
#################################################################################################

#Convert points from 3d to 2d
points = numpy.delete(points,2,axis=1)
io.writePoints(points_fn,points);