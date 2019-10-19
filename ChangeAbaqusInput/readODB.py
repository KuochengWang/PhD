import manipulate_abaqus_file
import numpy as np
import odbAccess
from odbAccess import openOdb
import os
import pdb
import read_tetgen

# read displaements from all frames from odb files in a folder and write to text file  

# Notice, everytime run, should delete the file already existed in the folder
# Otherwise, it will append to the end of the same file

# write displacements to txt files
# arguments:
# odb_files: a list of odb file names
# num_breastnode: how many points in the displacements belong to breast
# folder: the filder to store file
def write_all_frame(odb_files, step_name, num_breastnode, folder):
    for file in odb_files:
        odb = openOdb(file)
        total_frames = len(odb.steps[step_name].frames)
        for frame_num in range(total_frames):
            positions = read_frame(odb, folder, step_name, frame_num)
            output_file = open(folder + '\/' + file.split('.')[0] + '_' + \
                               str(frame_num) + '.txt', "a+")
            for pos in positions:
                output_file.write(str(pos[0]) + ' ' + str(pos[1]) + ' ' + \
                                  str(pos[2]) + '\n') 
            output_file.close()
        odb.close()

# read postion from each specific frame
# arguments:
# odb: from openOdb(file)
# step: the step name from Abaqus
# folder: the filder to store file 
# frame_num: which frame to read
# returns:
# a 2D list         
def read_frame(odb, folder, step, frame_num):
    disps_dic = dict() # a dictionary maps displacement to its indices
    breast_part = 'PART-1-1'
    for name, instance in odb.rootAssembly.instances.items(): 
        if name == breast_part: 
            numNodesTotal = len(instance.nodes) 
            frame = odb.steps[ 'Step-1' ].frames[frame_num]   
            displacement = frame.fieldOutputs['U']  
            field_values = displacement.values            
            index = 0            
            for field_value in field_values:
                label = field_value.nodeLabel
                if len(field_value.instance.nodes) != len(instance.nodes):
                    continue                            
                x, y, z = field_value.data       
                disps_dic[label] = [x, y, z] 
                index += 1            
    displacements = []
    for index in range(numNodesTotal):
        pos = disps_dic[index + 1]
        displacements.append(pos)
    return displacements        
        

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
    
      
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    



