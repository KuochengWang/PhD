# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:16:04 2019

@author: vr_lab
"""
import pdb

class ReadAbaqusInput:
    def __init__(self, file_name):
        self.file_name = file_name
        
    # take a list of nodes position, add to .inp file
    # @param nodes a list of numpy with 1x3, or a list of list
    # @param part the name of the part
    # @param output_file the .inp need to be written into 
    def add_node(self, nodes, output_file, part):
        contents, index = self.return_content_and_insert_position(part)
        index += 2
        for i, node in enumerate(nodes):
            pos = str(i + 1) + ',' + str(node[0]) + ',' + str(node[1]) + ',' + str(node[2]) + '\n'
            contents.insert(index + i, pos)
        contents = "".join(contents)
        f = open(output_file, "w")
        f.write(contents)
        f.close()
    
    # find index of the string of the line need to be found
    def return_content_and_insert_position(self, search_line):
        output_file = open(self.file_name, 'r')
        content = output_file.readlines()
        output_file.close()
        line_index = content.index(search_line)
        return content, line_index
    
    # read the coordinate from the contents
    # @param start_index the starting line to read the file
    def __read_coordinates__(self, contents, start_index):
        coords = []
        for index, coord in enumerate(contents[start_index:-1]):
            coord = coord.strip().split(',')
            if not coord[0].isdigit():
                break
            coords.append([float(coord[1]), float(coord[2]), float(coord[3])])
        return coords
    
    # find all content 
    def read_part(self, part):
        contents, index = self.return_content_and_insert_position(part)
        return self.__read_coordinates__(contents, index + 2)
        