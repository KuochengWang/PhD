# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 14:53:43 2019

@author: vr_lab
"""

import numpy as np
import pdb
import random
import vtk

def select_points(filename):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    data = reader.GetOutput()    
    n_points = data.GetNumberOfPoints()
    mesh_points = np.zeros([n_points, 3])
    for i in range(n_points):
        mesh_points[i][0], mesh_points[i][1], mesh_points[i][	2] = data.GetPoint(i)
    point_indices = []
    for i in range(0,20):
        point_index = random.randint(1, n_points)
        point_indices.append(mesh_points[point_index, :])    
    return point_indices

def write_to_file(filename, points):
    output_file = open(filename, 'w')
    for index, point in enumerate(points):
        output_file.write(str(index) + ' ' + str(point[0]) + ' ' + str(point[1]) + 
                          ' ' + str(point[2]) + '\n')
    output_file.close()
    
if __name__ == '__main__':
    input_file = 'FGlandular.stl'
    output_file = "Fat_Solid_32837pointspoints.a.node"
    points = select_points(input_file)
    write_to_file(output_file, points)