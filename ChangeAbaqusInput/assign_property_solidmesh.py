# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 13:21:39 2019

@author: vr_lab
"""

# this script uses surface mesh (.ply) to find tetrahedral element

import numpy as np
import pdb
from plyfile import PlyData, PlyElement
import read_tetgen

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
        
def assign_material(outer_coord_file, outer_ele_file, inner_coord_file, inner_ele_file):    
    outer_content = read_tetgen.ReadTetGen(outer_ele_file, outer_coord_file)
    outer__coords = outer_content.read_coordinates()
    outer_elems = outer_content.read_elements()
    inner_content = read_tetgen.ReadTetGen(inner_ele_file, inner_coord_file) 
    inner_coords = inner_content.read_coordinates()
    inner_elems = inner_content.read_elements()
    grid = Grid(outer_elems, outer__coords)
    grid.build_grid()
    inner_elem_index = []
    inner_elem_centers = []
    for elem in inner_elems:
        center = (inner_coords[elem[0]] + inner_coords[elem[1]] +
                  inner_coords[elem[2]] + inner_coords[elem[3]]) / 4
        inner_elem_centers.append(center)
    
    for index, inner_coord in enumerate(inner_elem_centers):
        elem_index = grid.search_tet(inner_coord)
        if elem_index != -1:
            inner_elem_index.append(elem_index)
        print(index)
    inner_elem_index = np.unique(inner_elem_index)
    inner_elem = []
    for elem in inner_elem_index:    
        inner_elem.append(outer_elems[elem])
    return inner_elem

if __name__ == '__main__':   
    '''
    fatcoord_file = 'Fat_Solid_hete_no_nipple.node'
    fatele_file = 'Fat_Solid_hete_no_nipple.ele'
    glandularcoord_file = 'FGT_Cluster_1-2_modified.node'
    glandularele_file = 'FGT_Cluster_1-2_modified.ele'
    glandular_output_file = 'FGT_Cluster_1-2.ele'
    glandular_elems = assign_material(fatcoord_file, fatele_file, 
                                      glandularcoord_file, glandularele_file)
    write_ele(glandular_elems, glandular_output_file)
    '''  
  
    '''
    skincoord_file = 'Skin_Layer.node'
    skinele_file = 'Skin_Layer.ele'
    fatcoord_file = 'Fat_Solid_hete_no_nipple.node'
    fatele_file = 'Fat_Solid_hete_no_nipple.ele'
    fat_output_file = 'fat_fromskin.ele'
    fat_elems = assign_material(skincoord_file, skinele_file, 
                                      fatcoord_file, fatele_file)
    write_ele(fat_elems, fat_output_file)
    '''
    
    '''
    skincoord_file = 'Skin_Layer.node'
    skinele_file = 'Skin_Layer.ele'
    glandularcoord_file = 'FGT_Cluster_1-2_modified.node'
    glandularele_file = 'FGT_Cluster_1-2_modified.ele'
    glandular_output_file = 'FGT_Cluster_1-2.ele'
    glandular_elems = assign_material(skincoord_file, skinele_file, 
                                      glandularcoord_file, glandularele_file)
    write_ele(glandular_elems, glandular_output_file)
    '''
    
    skincoord_file = 'Skin_Layer.node'
    skinele_file = 'Skin_Layer.ele'
    tumorcoord_file = 'tumor.1.node'
    tumorele_file = 'tumor.1.ele'
    tumor_output_file = 'tumor_fromskin.ele'
    tumor_elems = assign_material(skincoord_file, skinele_file, 
                                      tumorcoord_file, tumorele_file)
    write_ele(tumor_elems, tumor_output_file)