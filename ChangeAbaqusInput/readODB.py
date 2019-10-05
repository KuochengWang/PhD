import manipulate_abaqus_file
import numpy as np
from odbAccess import openOdb
import os
import pdb
import read_tetgen

# odb file repeat displacements, so the node number become twice as large
# @param file_name the .odb file 
# @param step_name the step name from Abaqus file
# return an np array of displacement
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

# calculate coordinate after displacement
# @param node_file .node from TetGen
# @param element_file .ele from TetGen 
# return the coordination after move 
def move_breast(node_file, element_file, odb_file, step_name):
    disps = read_lastframe(odb_file, step_name)
    content = read_tetgen.ReadTetGen(element_file, node_file)
    original_coords = content.read_coordinates()
    moved_coords = []
    for i, coord in enumerate(original_coords):
        moved_coords.append(coord + disps[i])
    return moved_coords

# insert node positions to .inp
# @param file_name the .inp need to be written into
# @param positions the node positions
def insert_nodes(file_name, positions, part):
    abaqus = manipulate_abaqus_file.ReadAbaqusInput(file_name)
    abaqus.add_node(positions, file_name, part)

if __name__ == "__main__":
    odb = 'Job-6.odb'
    step = 'Step-2'
    node = 'Skin_Layer.node'
    element = 'Skin_Layer.ele'
    output_file = 'Job-4.inp'
    part = '*Part, name=PART-1\n'
    positions = move_breast(node, element, odb, step)
    insert_nodes(output_file, positions, part)
    
      
    



