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
    def __read_coordinates__(self, start_index):
        coords = []
        for index, coord in enumerate(self.contents[start_index:-1]):
            coord = coord.strip().split(',')
            if not coord[0].isdigit():
                break
            coords.append([float(coord[1]), float(coord[2]), float(coord[3])])
        return coords
    
    # find all content 
    def read_part(self, part):
        index = self.return_insert_position(part)
        return self.__read_coordinates__(index + 2)
    
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
    
    