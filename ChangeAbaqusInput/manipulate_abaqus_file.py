# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:16:04 2019

@author: vr_lab
"""
import numpy as np
import pdb

class ReadAbaqusInput:
    def __init__(self, file_name):
        self.contents = self.set_content(file_name) 
        
    # take a list of nodes position, add to .inp file
    # @param nodes a list of numpy with 1x3, or a list of list
    # @param part the name of the part
    # @param output_file the .inp need to be written into 
    def add_node(self, nodes, output_file, part):
        index = self.return_insert_position(part)
        index += 2
        for i, node in enumerate(nodes):
            pos = str(i + 1) + ',' + str(node[0]) + ',' + str(node[1]) + ',' + str(node[2]) + '\n'
            self.contents.insert(index + i, pos)
        self.write_output(output_file)
    
    def write_output(self, output_file):
        f = open(output_file, "w")         
        f.write(''.join(self.contents))
        f.close()
    
    # find index of the string of the line need to be found
    def return_insert_position(self, search_line):
        line_index = self.contents.index(search_line)
        return line_index
    
    def set_content(self, file_name):
        output_file = open(file_name, 'r')
        contents = output_file.readlines()
        output_file.close()
        return contents
    
    # read the coordinate from the contents
    # @param start_index the starting line to read the file
    # @param elem_or_coord a flag starting whether reading coord or element
    # return:
    # a list of 3D points
    def __read_coordinates__(self, start_index, elem_or_coord):
        coords = []
        for index, coord in enumerate(self.contents[start_index:-1]):
            coord = coord.strip().split(',')
            if not coord[0].isdigit():
                break
            if elem_or_coord == 'coordinate':
                coords.append([float(coord[1]), float(coord[2]), float(coord[3])])
            elif elem_or_coord == 'element':
                coords.append([int(coord[1]), int(coord[2]), int(coord[3]), int(coord[4])])
        return coords
    
    # find all node coordi
    # return:
    # a list of 3D points
    def read_part(self, part):
        index = self.return_insert_position(part)
        return self.__read_coordinates__(index + 2, 'coordinate')
    
    # read all the node indexes from element
    #reutrun:
    # a list of list with 4 numbers
    def read_element(self, part):
        part_index = self.return_insert_position(part)
        coords = self.read_part(part)
        elem_index = part_index + len(coords) + 3
        elems = self.__read_coordinates__(elem_index, 'element')
        return elems
    
    # change the boundary condition
    # @param start_line the enrire line string that boundary start with 
    # #param time_period the time period set from Abaqus
    def set_boundary(self, start_line, time_period, direction, magnitude): 
        index = self.return_insert_position(start_line)
        direction = direction / np.linalg.norm(direction) * magnitude
        self.contents[index + 1] = 'Set-6, 1, 1, ' + str(direction[0]) + '\n'
        self.contents[index + 2] = 'Set-6, 2, 2, ' + str(direction[1]) + '\n'
        self.contents[index + 3] = 'Set-6, 3, 3, ' + str(direction[2]) + '\n'
    
    # return the translation vector, x, y, z, and the index of the line
    def read_assembly(self, start_line):
         index = self.return_insert_position(start_line)
         x_str, y_str, z_str = self.contents[index + 1].strip().split(',')
         return float(x_str), float(y_str), float(z_str), index
    
    # set the new position in assembly
    # @param translation the translation vector from current to new position 
    def set_assembly(self, start_line, translation):
        x, y, z, index = self.read_assembly(start_line)
        x = translation[0]
        y = translation[1]
        z = translation[2]
        self.contents[index + 1] = str(x) + ',' + str(y) + ',' + str(z) + '\n'
    
    # read time period from .inp    
    def read_timeperiod(self, start_line):
        index = self.return_insert_position(start_line)
        return float(self.contents[index + 1].strip().split(',')[1])
    
    # return:
    # a list of strings
    def add_to_elset_or_nset(self, start_line, numbers):
        index = self.return_insert_position(start_line)
        start = index + 1
        line = []
        for num in numbers:
            if len(line) == 16:
                line_str = ''
                for index, word in enumerate(line):
                    if index == 15:
                        line_str = line_str + ',' + str(word + 1) + '\n'
                        line_str = line_str[1:]
                        self.contents.insert(start, line_str)
                        start += 1
                    else:
                        line_str = line_str + ',' + str(word + 1)
                line = []     
            line.append(num)
        line_str = ''
        for index, li in enumerate(line):
            if index != len(line) - 1:
                line_str = line_str + ',' + str(li + 1) 
            else:
              #  line_str = line_str[1:]
                line_str = line_str + ',' + str(li + 1) + '\n'
                line_str = line_str[1:]
                self.contents.insert(start, line_str)
            
    
    # returns:
    # line : a list of strings
    # index: the index of the first line that contain numbers
    def firstline_elset_or_nset(self, start_line):
        index = self.return_insert_position(start_line)
        end = index + 1
        line = self.contents[end].strip().split(',')
        return line, end
    
    # delete the element set, but maintain the start line of the elset or nset    
    def delete_elset_or_nset(self, start_line):
        line, end = self.firstline_elset_or_nset(start_line)
        while line[0].isdigit():
            self.contents.pop(end)
            line = self.contents[end].strip().split(',')
    
    def read_elset_or_nset(self, start_line):
        line, index = self.firstline_elset_or_nset(start_line)
        values = []
        while line[0].isdigit():
            for num in line:
                values.append(int(num))
            index += 1
            line = self.contents[index].strip().split(',')
        return values
    
    # change the part position based on the index of the point
    # args:
    # part: the start line of the part 
    # point_index: the index of the point, index start from 0
    # point: the 3D position of the new point, string format
    def edit_part(self, part, point_index, point):
        index = self.return_insert_position(part) + 2 + point_index
        self.contents[index] = str(point_index + 1) + ',' + point
        
    # change the direction of gravity
    # args:
    # gravity: the start line of gravity
    # direction: the 3D vector that describle the gravity direction 
    # magnitude: the magnitude of the gravity
    def change_gravity(self, gravity, direction, magnitude):
        index = self.return_insert_position(gravity) + 2
        line = self.contents[index].strip().split(',')
        x, y, z = direction
        new_line = line[0] + ',' + line[1] + ','+ str(magnitude) + ',' + \
                   str(x) + ',' + str(y) + ',' + str(z) + '\n'
        self.contents[index] = new_line