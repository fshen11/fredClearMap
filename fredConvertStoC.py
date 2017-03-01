# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:11:52 2017

@author: cailab
"""

from ClearMap.Alignment.Resampling import sagittalToCoronalData
sourceFN = '/home/cailab/clearmap_ressources_mouse_brain/ClearMap_ressources/annotation_25_full.nrrd'
sinkFN = '/media/sf_Fred_Data/testClearMap/annotation_coronal.tif'


sagittalToCoronalData(sourceFN,sinkFN)