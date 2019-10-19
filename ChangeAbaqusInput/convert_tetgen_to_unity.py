# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:41:01 2019

@author: vr_lab
"""
import read_tetgen
from random_select_point_from_organ import write_to_file  

# arg:
# filename: the output file you want to write to
# points: a list of 3D points
def write_to_file(filename, points):
    output_file = open(filename, 'w')
    for index, point in enumerate(points):
        output_file.write(str(point[0]) + ' ' + str(point[1]) + 
                          ' ' + str(point[2]) + '\n')
    output_file.close()

if __name__ == "__main__":
    elefile = ''
    nodefile = 'Skin_Layer.node'
    surfacefile = 'Skin_Layer.face'
    triangles_unity = 'Skin_Layer_unity.face'
    nodefile_unity = 'Skin_Layer_unity.node'
    tet_gen = read_tetgen.ReadTetGen(elefile, nodefile)
    triangles = tet_gen.read_surface(surfacefile)
    coords = tet_gen.read_coordinates()
    write_to_file(triangles_unity, triangles)
    write_to_file(nodefile_unity, coords)