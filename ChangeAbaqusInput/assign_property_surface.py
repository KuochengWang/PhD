# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 13:21:39 2019

@author: vr_lab
"""

# this script uses surface mesh (.ply) to find tetrahedral element

import numpy as np
import pdb
from plyfile import PlyData, PlyElement

def read_content(file_name):
    output_file = open(file_name, 'r')
    content = output_file.readlines()
    output_file.close()
    return content

def write_ele(elements, output_filename):
    output_file = open(output_filename, 'w')
    output_file.write(str(len(elements)) + ' 4 0\n')
    for index, elem in enumerate(elements):
        output_file.write(str(index) + ' ' + str(elem[0]) + ' ' + str(elem[1]) + 
                          ' ' + str(elem[2]) + ' ' + str(elem[3]) + '\n')

# build a data struct for a tetrahedral mesh for grid search 
class Grid:
    def __init__(self, elems, coords):
        self.map = {}
        self.elements = elems
        self.coordinates = coords
        self.x_min = -1
        self.x_max = -1
        self.y_min = -1 
        self.y_max = -1
        self.z_min = -1
        self.z_max = -1
        self.step = []
        
    def find_grid_range(self):
        x_min = min(self.coordinates[:,0])
        y_min = min(self.coordinates[:,1])
        z_min = min(self.coordinates[:,2])
        x_max = max(self.coordinates[:,0])    
        y_max = max(self.coordinates[:,1])
        z_max = max(self.coordinates[:,2])
        return x_min, x_max, y_min, y_max, z_min, z_max
    
    def grid_coord(self, coord, step):
        x_step, y_step, z_step = self.step
        grid_x = (coord[0] - self.x_min ) // x_step
        grid_y = (coord[1] - self.y_min ) // y_step
        grid_z = (coord[2] - self.z_min ) // z_step
        return grid_x, grid_y, grid_z
    
    def build_grid(self):
        num_grid = 10
        self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max = self.find_grid_range()
        x_step = (self.x_max - self.x_min) / num_grid
        y_step = (self.y_max - self.y_min) / num_grid
        z_step = (self.z_max - self.z_min) / num_grid
        self.step = [x_step, y_step, z_step]
        for index, elem in enumerate(self.elements):
            coord = (self.coordinates[elem[0]] + self.coordinates[elem[1]] + 
                    self.coordinates[elem[2]] + self.coordinates[elem[3]]) / 4
            grid_coordx, grid_coordy, grid_coordz = self.grid_coord(coord, self.step)
            key = str(grid_coordx) + ' ' + str(grid_coordy) + ' ' + str(grid_coordz)
            if key not in self.map:
                self.map[key] = [index]
            else:
                self.map[key].append(index)
    
    def __tetra_coord__(self, A,B,C,D):
      v1 = B-A ; v2 = C-A ; v3 = D-A
      mat = np.array((v1,v2,v3)).T
      # mat is 3x3 here
      M1 = np.linalg.inv(mat)
      return(M1)

    def __point_inside__(self, v1,v2,v3,v4,p):
      # Find the transform matrix from orthogonal to tetrahedron system
      m1=self.__tetra_coord__(v1,v2,v3,v4)
      # apply the transform to P (v1 isu the origin)
      newp = m1.dot(p-v1)
      return (np.all(newp>=0) and np.all(newp <=1) and np.sum(newp)<=1)

    def search_tet(self, coord):
        x, y, z = self.grid_coord(coord, self.step)
        key = str(x) + ' ' + str(y) + ' ' + str(z)
        if key in self.map:
            tet_indices = self.map[key]
            for tet_index in tet_indices:
                elem = self.elements[tet_index]
                if self.__point_inside__(self.coordinates[elem[0]], 
                                self.coordinates[elem[1]],
                                self.coordinates[elem[2]],
                                self.coordinates[elem[3]],
                                np.array([coord[0], coord[1],coord[2]])):
                    return tet_index
        return -1        
        
def assign_material(fatcoord_file, fatele_file, glandular_file):
    fatcoord_content = read_content(fatcoord_file)
    fatele_content = read_content(fatele_file)
    fat_coords = np.zeros([len(fatcoord_content) - 2, 3])
    fat_elems = np.zeros([len(fatele_content) - 2, 4])
    for index, fat_coord in enumerate(fatcoord_content[1:-1]):
        coord = fat_coord.strip().split()
        fat_coords[index] = np.array([float(coord[1]), float(coord[2]), float(coord[3])])
    for index, fatele in enumerate(fatele_content[1:-1]):
        ele = fatele.strip().split()
        fat_elems[index] = np.array([int(ele[1]), int(ele[2]), int(ele[3]), int(ele[4])])
    fat_elems = fat_elems.astype(int)
    grid = Grid(fat_elems, fat_coords)
    grid.build_grid()
    glandular_content = PlyData.read(glandular_file) 
    glandular_coords = []
    for index in range(glandular_content['vertex'].count):
        glandular_coords.append(glandular_content['vertex'][index])
    glandular_elem_index = []
    for index, glandular_coord in enumerate(glandular_coords):
        elem_index = grid.search_tet(glandular_coord)
        if elem_index != -1:
            glandular_elem_index.append(elem_index)
        print(index)
    glandular_elem_index = np.unique(glandular_elem_index)
    glandular_elem = []
    for elem in glandular_elem_index:    
        glandular_elem.append(fat_elems[elem])
    return glandular_elem

if __name__ == '__main__':
    fatcoord_file = 'Fat_Solid_hete_no_nipple.node'
    fatele_file = 'Fat_Solid_hete_no_nipple.ele'
   # glandular_file = 'glandular_filter.ply'
    glandular_file = 'FGT_Cluster_1-2.ply'
    #glandular_elems_file = 'glandular.ele'
    glandular_elems_file = 'FGT_Cluster_1-2.ele'
    glandular_elems = assign_material(fatcoord_file, fatele_file, glandular_file)
    write_ele(glandular_elems, glandular_elems_file)
    
    