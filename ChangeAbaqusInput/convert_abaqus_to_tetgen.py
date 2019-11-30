# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 13:24:13 2019

@author: vr_lab
"""

import manipulate_abaqus_file
from convert_tetgen_to_unity import write_to_file

# read .inp file's part and save to node file in tetgen

if __name__ == "__main__":
    inp_file = 'Weight Jobs/reference_pos.inp'
    file_name = 'Skin_Layer_reference.node'
    abaqus = manipulate_abaqus_file.ReadAbaqusInput(inp_file)
    breast_part_start = '*Part, name=PART-1\n'
    points = abaqus.read_part(breast_part_start)
    write_to_file(file_name, points, 'write')