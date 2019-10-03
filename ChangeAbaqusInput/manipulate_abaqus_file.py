# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:16:04 2019

@author: vr_lab
"""

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
    
    def find_line_index(self, section_name):
        index = 0
        with open(self.file_name, "r") as file:
             for line in file:
                 if line.strip() == section_name:
                     return index
                 index += 1
        return index + 1