# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 10:45:19 2020

@author: vr_lab

This file check which tetrahedrons in the outer layer are inside the triangle 
mesh
 
"""

import change_stl
import numpy as np
import pdb
import read_tetgen

SMALL_NUM = 0.00000001

# arguments:
#    triangle: 2D array, size 3 * 3
#    ray: 2D array, size 2 * 3
# return: 
#    whether the ray intersect with triangle, the ray is a line segment (not infinite)
def ray_intersect_triangle(triangle, ray):
    u = triangle[1] - triangle[0]
    v = triangle[2] - triangle[0]
    n = np.cross(u, v)
    if n[0] == 0 and  n[1] == 0 and n[2] == 0:
        return False
    
    ray_dir = ray[1] - ray[0]
    w0 = ray[0] - triangle[0]
    a = -np.dot(n, w0)
    b = np.dot(n, ray_dir)
    if (abs(b) < SMALL_NUM):        
        if a == 0:                 
            return True
        else: 
            return False

    r = a / b
    if r < 0:
        return False
    I = ray[0] + r * ray_dir
    uu = np.dot(u,u)
    uv = np.dot(u,v)
    vv = np.dot(v,v)
    w = I - triangle[0]
    wu = np.dot(w,u)
    wv = np.dot(w,v)
    D = uv * uv - uu * vv

    s = (uv * wv - vv * wu) / D
    if s < 0.0 or s > 1.0:         
        return False
    t = (uv * wu - uu * wv) / D
    if t < 0.0 or (s + t) > 1.0:
        return False

    if (np.linalg.norm(ray[1] - ray[0]) < np.linalg.norm(I - ray[0])):
            return False
        
    return True                                     
    
# arguments:
    # elements: a list of list (4 numbers)
    # a list of points on the contact surface in breast
def write_element(elements, output_file_name):
    output_file = open(output_file_name, 'a+') 
    for index, elem in enumerate(elements):
        output_file.write(str(index) + ' ' + str(elem[0]) + ' ' + str(elem[1]) + 
                          ' ' + str(elem[0]) + ' ' + str(elem[1]) + '\n')

# arguments:
    # returns:
    # a list of points on the contact surface in breast
def find_tet(tet_elefile, tet_coordfile, triangle_stlfile):
    tet_content = read_tetgen.ReadTetGen(tet_elefile, tet_coordfile) 
    tet_coords = tet_content.read_coordinates()
    tet_elems = tet_content.read_elements()
    tri_coords, tri_faces = change_stl.parse(triangle_stlfile)
    element_inside = []
    
    for ele_num, tet_elem in enumerate(tet_elems):
        center = (tet_coords[tet_elem[0]] + tet_coords[tet_elem[1]] +
                  tet_coords[tet_elem[2]] + tet_coords[tet_elem[3]]) / 4
       
        ray = np.array([center,[100000000, 0, 0]])
        num = 0
        for tri_face in tri_faces:
            if ray_intersect_triangle(np.array(
                    [tri_coords[tri_face[0]], tri_coords[tri_face[1]], 
                     tri_coords[tri_face[2]]]), ray):
                num += 1
        if num%2 == 1:
            print('true')
            element_inside.append(tet_elem)
       #     temp1 = np.array([[-113.3,46.2,138.1], [-77.1,46.2,138.1], [-89.9,70.2,138.1]])
       #     temp2 = np.array([[-88.01642,61.29,133.04],[-88.01642,60.93483,127.87]])
       #     if ray_intersect_triangle(temp1, temp2):
       #         pdb.set_trace()
        print(ele_num)
    
    write_element(element_inside, 'F:\Research\Breast Model\BM_Fatty_001\Left\Fat_1_Fgt_1\SolidModel\FGT_fromskin.ele')
    pdb.set_trace()
    
    
if __name__ == "__main__":
    ele_file = 'F:\Research\Breast Model\BM_Fatty_001\Left\Fat_1_Fgt_1\SolidModel\Skin_Layer_Simplified.ele'
    node_file = 'F:\Research\Breast Model\BM_Fatty_001\Left\Fat_1_Fgt_1\SolidModel\Skin_Layer_Simplified.node'
    triangle_file = 'F:\Research\Breast Model\BM_Fatty_001\Left\Fat_1_Fgt_1\SolidModel\FGT_Cluster_Coarse.stl'
    find_tet(ele_file, node_file, triangle_file)