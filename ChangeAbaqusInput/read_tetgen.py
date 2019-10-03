# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 14:21:27 2019

@author: vr_lab
"""
import numpy as np

class ReadTetGen:
    def __init__(self, elefile, nodefile):
        self.elefile_name = elefile
        self.nodefile_name = nodefile
        
    def read_content(self, file_name):
        output_file = open(file_name, 'r')
        content = output_file.readlines()
        output_file.close()
        return content
    
    def read_coordinates(self):
        coord_content = self.read_content(self.nodefile_name)
        coords = np.zeros([len(coord_content) - 2, 3])
        for index, coord in enumerate(coord_content[1:-1]):
            coord = coord.strip().split()
            coords[index] = np.array([float(coord[1]), float(coord[2]), float(coord[3])])
        return coords
        
    def read_elements(self):
        ele_content = self.read_content(self.elefile_name)
        elems = np.zeros([len(ele_content) - 2, 4])
        for index, ele in enumerate(ele_content[1:-1]):
            ele = ele.strip().split()
            elems[index] = np.array([int(ele[1]), int(ele[2]), int(ele[3]), int(ele[4])])
        return elems.astype(int)