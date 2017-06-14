# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 16:03:31 2017

@author: cailab
"""


from string import ascii_lowercase as alphabet
import os
import ClearMap.IO as io  
import ClearMap.Settings as settings
import numpy
import pdb
from ClearMap.Alignment.Elastix import parseElastixOutputPoints2d, getMinMetric, autoAlignData
from ClearMap.Analysis.Label import countPointsInRegions, labelPoints2d
from ClearMap.Analysis.Label import LabelInfo, labelToName
import pandas as pd


animalPath = '/media/sf_Fred_Data/OdorInduction/cfosOdor052417';
whichWell = 8; 
wellDir = os.path.join(animalPath,'Well_'+str(whichWell));
cfosDir = os.path.join(animalPath,'totalC1');  #C1 folder is cfos signal
tableFN = os.path.join(animalPath,'ResultsTable.csv');

listSections = os.listdir(cfosDir); 

section = '8'
outTableName = '052417-8.csv';


def combineSections(animalPath, section, outTableName):
    alph = ['a','b','c','d','e','f'];
    for z in range(len(alph)):
        fName = section+alph[z];
        resultDir = os.path.join(animalPath,'Results',fName);             
        tableFN = os.path.join(resultDir,'ResultsTable.csv');
        if z == 0:
            table= pd.read_csv(tableFN,names = ['id','counts','name','subname']);
        else:
            temp_table = pd.read_csv(tableFN,names = ['id','counts','name','subname']);
            table = pd.DataFrame.append(table,temp_table);

        #Table generation
    totTable = table.groupby(['id','name'],as_index=False).sum();
    totTableFN = os.path.join(animalPath,outTableName);
    io.writeTable(totTableFN,totTable.values);
    print('success!')
def combineAnimals(listAnimals):  
#This function combines the data across multiple animals into one single table    

    for z in range(len(listAnimals)):
        if z==0:
            tab = pd.read_csv(listAnimals[z],names = ['id','name','counts'],usecols = ['id','name','counts']); 
            colNames = ['id','name',listAnimals[z]]
        else:
            tempTab = pd.read_csv(listAnimals[z],names = ['id','name','counts','subname']);
            tab = pd.merge(tab,tempTab[['id','counts']], how = 'outer', on = 'id')
            colNames.append(listAnimals[z])
    tab.columns = colNames
    return tab
def getSectionCSV(animalPath, sections):
#This function takes an input of section name ('052417-1') and creates a list of relavent CSV filse
    out = [];
    for i in range(len(sections)):
        out.append(os.path.join(animalPath,sections[i]));
    return out


combineSections(animalPath,section,outTableName)
sections = ['052417-1.csv','052417-2.csv','052417-3.csv','052417-4.csv','052417-5.csv','052417-6.csv','052417-7.csv','052417-8.csv']
sections =getSectionCSV(animalPath,sections)

#
#listAnimals = ['/media/sf_Fred_Data/OdorInduction/cfosOdor060717/060717-1_2MT.csv','/media/sf_Fred_Data/OdorInduction/cfosOdor060717/060717-2_2MT.csv',\
#              '/media/sf_Fred_Data/OdorInduction/cfosOdor060717/060717-3_2MT.csv','/media/sf_Fred_Data/OdorInduction/cfosOdor060717/060717-5_2MT.csv','/media/sf_Fred_Data/OdorInduction/cfosOdor060717/060717-6_2MT.csv']
outTableName = 'CombinedTables.csv';
a = combineAnimals(sections); 
totTableFN = os.path.join(animalPath,outTableName);
io.writeTable(totTableFN,a.values);