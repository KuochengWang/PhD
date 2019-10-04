# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:16:04 2019

@author: vr_lab
"""
import pdb

class ReadAbaqusInput:
    def __init__(self, file_name):
        self.file_name = file_name
    
    def insert(self, section_name, content, output_file):
        f = open(self.output_file, "w")
        contents = f.readlines()
        index = self.find_line_index(section_name)
        contents.insert(index, content)
        contents = "".join(contents)
        f.write(contents)
        f.close()
        
    # take a list of nodes position, add to .inp file
    # @param nodes a list of numpy with 1x3, or a list of list
    # @param output_file the .inp need to be written into 
    def add_node(self, nodes, output_file):
        contents, index = self.return_content_and_insert_position('*Node\n')
        for i, node in enumerate(nodes):
            pos = str(i + 1) + ',' + str(node[0]) + ',' + str(node[1]) + ',' + str(node[2]) + '\n'
            contents.insert(index + i, pos)
        contents = "".join(contents)
        f = open(output_file, "w")
        f.write(contents)
        f.close()
            
    def return_content_and_insert_position(self, search_line):
        output_file = open(self.file_name, 'r')
        content = output_file.readlines()
        output_file.close()
        line_index = content.index(search_line)
        return content, line_index + 1

    def find_line_index(self, section_name):
        index = 0
        with open(self.file_name, "r") as file:
             for line in file:
                 if line.strip() == section_name:
                     return index
                 index += 1
        return index + 1