
# coding: utf-8

# In[ ]:
# run: abaqus python readODB.py
# in order to run abaqus simulation: abaqus j=breast int cpus=4

import numpy as np
from odbAccess import openOdb
import os
import pdb
import read_tetgen

# odb file repeat displacements, so the node number become twice as large
def read_lastframe(file_name, step_name):
    odb = openOdb(file_name)
    if len(odb.steps[step_name].frames)== 0:
      return
    last_frame = odb.steps[step_name].frames[-1]
    displacement = last_frame.fieldOutputs['U']   
    field_values = displacement.values
    disps = []
    for v in field_values:
        temp_disp = [v.data[0], v.data[1], v.data[2]]
        disps.append(temp_disp)
    return np.array(disps)

def move_breast(node_file, element_file, odb_file, step_name):
    disps = read_lastframe(odb_file, step_name)
    content = read_tetgen.ReadTetGen(element_file, node_file)
    original_coords = content.read_coordinates()
    moved_coords = []
    for i, coord in enumerate(original_coords):
        moved_coords.append(coord + disps[i])
        pdb.set_trace()
    return moved_coords

if __name__ == "__main__":
    odb = 'Job-6.odb'
    step = 'Step-2'
    node = 'Skin_Layer.node'
    element = 'Skin_Layer.ele'
    move_breast(node, element, odb, step)
      
    



