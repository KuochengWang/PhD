# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:41:01 2019

@author: vr_lab
"""
import pdb
import read_tetgen


# arg:
# filename: the output file you want to write to
# points: a list of 3D points or 1D points
# write_flag: whether to rewrite ('w') or append('a')
def write_to_file(filename, points, write_flag):
    if write_flag == 'write':
        output_file = open(filename, 'w')
    elif write_flag == 'append':
        output_file = open(filename, 'a+')
    else:
        return
    for index, point in enumerate(points):
        if len(point) == 3:
            output_file.write(str(point[0]) + ' ' + str(point[1]) + 
                              ' ' + str(point[2]) + '\n')
        if len(point) == 1:
            output_file.write(str(point[0]) + '\n')
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
    write_to_file(triangles_unity, triangles, 'write')
    write_to_file(nodefile_unity, coords, 'write')