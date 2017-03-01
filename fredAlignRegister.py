# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:07:31 2017

@author: cailab
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 12:45:31 2017

@author: cailab
"""

execfile('/home/cailab/ClearMap/fredParameters.py')

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

bestSlice = autoAlignData(imgR, atlasDir, affineParameterFile, bSplineParameterFile, resultDirectory = alignDir, tempDir = tempDir, sliceNum = sliceNum , bounds = bounds,orientation = orientation)

annoImg_fn = os.path.join(annoDir, 'Anno'+str(bestSlice).zfill(3)+'.tif');
refImg_fn  = os.path.join(atlasDir, 'Ref'+str(bestSlice).zfill(3)+'.tif');

transformPoints(points_elastix_fn, sink = None, transformParameterFile = transformParameterFN, transformDirectory = None, indices = False, resultDirectory = transformDir, tmpFile = None)

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

beforeAlign = plt.fredOverlayPoints(auto_R_fn, pointsRe, pointColor = [200,0,0]);
io.writeData(os.path.join(resultDir, 'BeforeAlign.tif'), beforeAlign);


afterAlign = plt.fredOverlayPoints(refImg_fn, points, pointColor = [200,0,0]);
io.writeData(os.path.join(resultDir, 'AfterAlign.tif'), afterAlign);