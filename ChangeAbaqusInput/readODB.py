import manipulate_abaqus_file
import numpy as np
import odbAccess
from odbAccess import openOdb
import os
import pdb
import read_tetgen

# odb file repeat displacements
# @param odb the .odb file pointer
# @param step_name the step name from Abaqus file
# @param frame_num which frame data you want to extract
# return an np array of displacement
def read_frame(odb, step_name, frame_num):
    if len(odb.steps[step_name].frames)== 0:
      return
    frame = odb.steps[step_name].frames[frame_num]
    displacement = frame.fieldOutputs['U']    
    field_values = displacement.values
    disps = []
    for v in field_values:
        temp_disp = [v.data[0], v.data[1], v.data[2]]
        disps.append(temp_disp)
    return np.array(disps)

# write displacements to txt files
# arguments:
# odb_files: a list of odb file names
# num_breastnode: how many points in the displacements belong to breast
# folder: the filder to store file
def write_all_frame(odb_files, step_name, num_breastnode, folder):
    for file in odb_files:
        odb = openOdb(file)
        total_frames = len(odb.steps[step_name].frames)
        for frame in range(total_frames):
            points = read_frame(odb, step_name, frame)
            breast_points = points[0:num_breastnode]
            f = open(folder + '\/' + file.split('.')[0] + '_' + str(frame) + '.txt', "a+")
            rows = num_breastnode
            for i in range(rows):
                f.write(str(breast_points[i][0]) + ' ' + str(breast_points[i][1]) \
                        + ' ' + str(breast_points[i][2]) + '\n')
            f.close()
# calculate coordinate after displacement
# @param node_file .node from TetGen
# @param element_file .ele from TetGen 
# return the coordination after move 
'''
def move_breast(node_file, element_file, odb_file, step_name):
    disps = read_lastframe(odb_file, step_name)
    
    content = read_tetgen.ReadTetGen(element_file, node_file)
    original_coords = content.read_coordinates()
    moved_coords = []
    for i, coord in enumerate(original_coords):
        moved_coords.append(coord + disps[i])
    return moved_coords
'''
# insert node positions to .inp
# @param file_name the .inp need to be written into
# @param positions the node positions
def insert_nodes(file_name, positions, part):
    abaqus = manipulate_abaqus_file.ReadAbaqusInput(file_name)
    abaqus.add_node(positions, file_name, part)

if __name__ == "__main__":
    odb = ['278.odb']
    step = 'Step-1'
    node = 'Skin_Layer.node'
    element = 'Skin_Layer.ele'
    inp_file = 'Jobs/surface_to_node.inp'
    part = '*Part, name=PART-1\n'
    output_folder = 'displacement files'  
    frame_num = 2
    
    abaqus = manipulate_abaqus_file.ReadAbaqusInput(inp_file)
    breast_points = abaqus.read_part(part)
    num_breastnode = len(breast_points)
    write_all_frame(odb, step, num_breastnode, output_folder)
    points = read_frame(odb, step, frame_num)
    breast_points = points[0:(num_breastnode - 1)]
    hand_points = points[num_breastnode:]
   # read_frame(odb, step, frame_num, part_instance, part)
    
    
    pdb.set_trace()
  #  positions = move_breast(node, element, odb, step)
  #  insert_nodes(output_file, positions, part)
    
      
    



