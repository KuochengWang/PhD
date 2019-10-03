# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 16:39:13 2019

@author: vr_lab
"""

# python convert_tetgen_to_abaqus.py –-mode= write_mesh


import argparse
import numpy as np
import os
import pdb
import read_tetgen

TOLERANCE = 0.5

# abaqus starts with index 1
# mesh_type is either NODE or ELEMENT
# boundary_condition mode is outdataded. We can assign in Abaqus directly

def write_mesh(input_file_name, output_file_name, mesh_type):
    output_file = open(output_file_name, 'a+')
    with open(input_file_name, "r") as file:
        line_num = 0
        for line in file:
            if line_num == 0:
                num_mesh = int(line.split()[0])
                if mesh_type.lower() == 'element':
                    output_file.write('*ELEMENT, TYPE = C3D4,ELSET=breast' + '\n')
                elif mesh_type.lower() == "node":
                    output_file.write('*NODE' + '\n')
                else:
                    return
                line_num += 1
                continue
            if line_num > num_mesh:
                return
            li = line.strip().split()
            li_new = ''
            for index, temp_li in enumerate(li):
                if index == 0:
                    li_new += str(int(temp_li) + 1) + ','
                elif index == len(li) - 1:
                    if mesh_type.lower() == 'element':
                        li_new += str(int(temp_li) + 1)
                    else:
                        li_new += temp_li
                else:
                    if mesh_type.lower() == 'element':
                        li_new += str(int(temp_li) + 1) + ','
                    else:
                        li_new += temp_li + ','
            output_file.write(li_new + '\n')
            line_num += 1
    output_file.close()             

def read_y_value(node_file):
    y_axes = []
    with open(node_file, "r") as file:
        line_num = 0
        for line in file:
            if line_num == 0:
                num_mesh = int(line.split()[0])
                line_num += 1
                continue
            if line_num > num_mesh:
                return y_axes
            li = line.strip().split()
            y_axes.append(float(li[2]))
            line_num += 1
    return y_axes

def return_content_and_insert_position(file_name, search_line):
    output_file = open(file_name, 'r')
    content = output_file.readlines()
    output_file.close()
   # pdb.set_trace()
    line_index = content.index(search_line)
    return content, line_index

def combine_insert_content(content, file_name):
    content = ''.join(content)
    output_file = open(file_name, 'w')
    output_file.write(content)
    output_file.close()  

def reformat_node_indices(node_indices):
    nums = sorted(set(node_indices))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))

'''    
def add_node_set(file_name, node_indices):
    search_line = '*End Assembly\n'
    content, insert_pos = return_content_and_insert_position(file_name, search_line)
    node_indices_range = reformat_node_indices(node_indices)
    for count, node_index in enumerate(node_indices_range):
        content.insert(insert_pos + 2 * count - 1, '*Nset, nset' + '=' + 'n' + str(count) + ', instance=PART-1-2, generate\n')
        content.insert(insert_pos + 2 * count, str(node_index[0]) + ',' + str(node_index[1]) + '\n')
    combine_insert_content(content, file_name)
'''

# input is a list of numbers that needs to be written
def write_sixteen_num_perline(numbers, file_name):
    write_file = open(file_name, 'a+')
    line = []
    for num in numbers:
        if len(line) == 16:
            for index, word in enumerate(line):
                if index == 15:
                    write_file.write(str(word) + '\n') 
                else:
                    write_file.write(str(word) + ',') 
            line = []     
        line.append(num)
    for index, li in enumerate(line):
        if index != len(line) - 1:
            write_file.write(str(li) + ',') 
        else:
            write_file.write(str(li) + '\n')
    write_file.close()
    
def add_node_set(file_name, node_indices):
    search_line = '*End Assembly\n'
    content, insert_pos = return_content_and_insert_position(file_name, search_line)
    content.insert(insert_pos, '*Nset, nset' + '=' + 'n0' + ', instance=PART-1-2\n')
    line = []
    count = 0
    for node_index in node_indices:
        if len(line) == 16:
            content.insert(insert_pos + count + 1, str(line).strip('[]') + '\n')
            line = []
            count += 1
        else:
            line.append(node_index)
    if len(line) != 0:
        content.insert(insert_pos + count, str(line).strip('[]') + '\n')
    combine_insert_content(content, file_name)
        
# the fixed vertices are those who has largest y value
def fixed_boundary_condition(file_name, y_axes):
    search_line = '*Step, name=Step-1, nlgeom=YES, inc=1000\n'
    content, step_index = return_content_and_insert_position(file_name, search_line)
    max_y = max(y_axes)
    
    content.insert(step_index + 4, '*BOUNDARY\n')
    node_indices = []
    for index, y in enumerate(y_axes):
        if abs(y - max_y) < TOLERANCE:
            node_indices.append(index + 1)    
    content.insert(step_index + 5, 'n0' + ',ENCASTRE' + '\n')
    combine_insert_content(content, file_name)  
    add_node_set(file_name, node_indices) 

def element_to_index(elementfile, nodefile):
    elem_to_index = {}
    content = read_tetgen.ReadTetGen(elementfile, nodefile)
    elems = content.read_elements()
    for i in range(elems.shape[0]):
        content = str(elems[i][0] + 1) + ',' + str(elems[i][1] + 1) + ',' \
                  + str(elems[i][2] + 1) + ',' + str(elems[i][3] + 1)
        elem_to_index[content] = i + 1
    return elem_to_index

# layer order should be from innermost to outermost
def add_element_set(output_file, all_layer_elemfile, 
                 all_layer_nodefile):
    assigned_elem = {''}
    outmost_elefile = all_layer_elemfile[-1]
    outmost_nodefile = all_layer_nodefile[-1]
    elem_to_index = element_to_index(outmost_elefile, outmost_nodefile)
    
    for (elem_file, node_file) in zip(all_layer_elemfile, all_layer_nodefile):
        content = read_tetgen.ReadTetGen(elem_file, node_file)
        elems = content.read_elements()
        write_file = open(output_file_name, 'a+')
        pdb.set_trace()
        write_file.write('*Elset, elset=' + os.path.splitext(elem_file)[0] + ', instance=PART-1-1\n')
        write_file.close()
        current_layer_elem = []
        for i in range(elems.shape[0]):
            content = str(elems[i][0] + 1) + ',' + str(elems[i][1] + 1) + ',' \
                      + str(elems[i][2] + 1) + ',' + str(elems[i][3] + 1)
            if content in assigned_elem:
                continue        
            current_layer_elem.append(elem_to_index[content])
            assigned_elem.add(content)
        write_sixteen_num_perline(current_layer_elem, output_file)
    
def write_to_eof(content, output_file):
    write_file = open(output_file, 'a+')
    for line in content:
        write_file.write(line)
    write_file.close()
        
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--mode', help='What are you trying to do? write_mesh or boundary_condition', type=str)
    args = arg_parser.parse_args()
    mode = args.mode
  #  output_file_name = 'Fat_Solid_hete_no_nipple.inp'
    output_file_name = 'skin_no_nipple.inp'
    if mode == 'write_mesh':
     #   input_file_name = 'Fat_Solid_hete_no_nipple.node'
        input_file_name = 'Skin_Layer.node'
        write_mesh(input_file_name, output_file_name, 'node') 
     #   input_file_name = 'Fat_Solid_hete_no_nipple.ele'  
        input_file_name = 'Skin_Layer.ele'     
        write_mesh(input_file_name, outpcut_file_name, 'element') 
        
    #####################################
    #### This mode is depricated, Abaqus can assign boundary directly
    if mode == 'boundary_condition':
     #   node_file = 'Fat_Solid_hete.1.node'
     #   output_file_name = 'breast_hete.inp'
        y_axes = read_y_value(node_file)
        fixed_boundary_condition(output_file_name, y_axes)
        
    if mode == 'add_elemset':
        first_layer_node = 'Skin_Layer.node'
        first_layer_ele = 'Skin_Layer.ele'
        second_layer_ele = 'fat_fromskin.ele'
        third_layer_ele = 'FGT_Cluster_1-2.ele'
        fourth_layer_ele = 'tumor_fromskin.ele'
        add_element_set(output_file_name, [fourth_layer_ele, third_layer_ele, 
                        second_layer_ele, first_layer_ele], [first_layer_node, 
                        first_layer_node, first_layer_node, first_layer_node])
        
    if mode == 'add_material':
        first_layer_property = '*Material, name=skin\n \
                                *Density\n \
                                9.996e-10,\n \
                                *Hyperelastic, mooney-rivlin\n \
                                0.002, 0.004,  3.36\n'
        second_layer_property = '*Material, name=fat\n \
                                *Density\n \
                                9.21e-10,\n \
                                *Hyperelastic, mooney-rivlin\n \
                                0.0013, 0.002,  6.04\n'
        third_layer_property = '*Material, name=glandular\n \
                                *Density\n \
                                9.485e-10,\n \
                                *Hyperelastic, mooney-rivlin\n \
                                0.0023, 0.0035,  3.45\n'
        fourth_layer_property = '*Material, name=tumor \
                                 *Density\n \
                                 9.21e-10,\n \
                                 *Elastic \
                                 0.7193, 0.4531\n'
        write_to_eof([first_layer_property, second_layer_property, 
                      third_layer_property, fourth_layer_property], 
                    output_file_name)