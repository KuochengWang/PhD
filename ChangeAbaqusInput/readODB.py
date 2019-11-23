from convert_tetgen_to_unity import write_to_file
import glob
import manipulate_abaqus_file
import math
import numpy as np
import odbAccess
from odbAccess import openOdb
import os
import pdb
import read_tetgen
import sys 

# to run: abaqus python readODB.py unload  or
# abaqus python readODB.py weight or
# abaqus python readODB.py tumor
# the unload is to cancle the gravity, weight is read the result .odb file and 
# added the displacement to the model,  

class ReadOdb:
    # arguments:
    # odb_files: a list of odb file names
    def __init__(self, odb_files):
        self.odb_files = odb_files
        
    # read displaements from all frames from odb files in a folder and write to text file  
    # Notice, everytime run, should delete the file already existed in the folder
    # Otherwise, it will append to the end of the same file
    # write displacements to txt files
    # arguments:
    # step_name: the step of the odb file we want to read from 
    # part_name: the specific part name
    # folder: the filder to store file
    # file_names: the file names that was written to
    def write_all_frame(self, step_name, part_name, folder):
        file_names = []
        for file in self.odb_files:
            odb = openOdb(file)
            total_frames = len(odb.steps[step_name].frames)
            for frame_num in range(total_frames):
                args = [odb, step_name, part_name, frame_num]
                positions = self.read_frame(args)
                file_name = folder + '\/' + file.split('.')[0] + '_' + \
                                   str(frame_num) + '.txt'                
                write_to_file(file_name, positions, 'write')
                file_names.append(file_name)
            odb.close()
        return file_names
    
    # read all point position of a part from each specific frame
    # arguments:
    # odb: from openOdb(file)
    # step: the step name from Abaqus
    # part: the part name from Abaqus
    # frame_num: which frame to read
    # returns:
    # a 2D list         
    def read_frame(self, args):
        odb, step, part, frame_num = args
        disps_dic = dict() # a dictionary maps displacement to its indices
        for name, instance in odb.rootAssembly.instances.items(): 
            if name == part: 
                num_nodes_total = len(instance.nodes) 
                frame = odb.steps[step].frames[frame_num]   
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
                for index in range(num_nodes_total):
                    pos = disps_dic[index + 1]
                    displacements.append(pos)
                return displacements        
    
    # read a specific point postion and displacement of a frame
    # arguments:
    # odb: from openOdb(file)
    # step_name: the step name from Abaqus
    # part_name: the part name from Abaqus
    # node_label: the label of the node we want to extract
    # returns:
    # a list of x, y z of the displacement of current point
    def readpoint_specific_frame(self, args):
        odb, step_name, frame_num, node_label, part_name = args
        for name, instance in odb.rootAssembly.instances.items(): 
            if name == part_name:                 
                frame = odb.steps[step_name].frames[frame_num]   
                displacement = frame.fieldOutputs['U']  
                field_values = displacement.values
                
                for field_value in field_values:
                    label = field_value.nodeLabel    
                    if len(field_value.instance.nodes) != len(instance.nodes) or label != node_label:
                        continue
                    pdb.set_trace()
                    return field_value.instance.nodes[node_label - 1].coordinates, \
                           field_value.data
    
    # returns the start and end position of a point of all frames 
    # returns:
    # a list of start positions, a list of end positions of all odb files
    def read_start_end_pos(self, step_name, node_label, part_name):
        start_positions = []
        end_positions = []
        for file in self.odb_files:
            odb = openOdb(file)
            total_frames = len(odb.steps[step_name].frames)
            for frame_num in range(total_frames):
                args = [odb, step_name, frame_num, node_label, part_name]
                
                pos, disp = self.readpoint_specific_frame(args)
                
                start_positions.append(pos) 
                end_positions.append(pos + disp)
               
        return start_positions, end_positions 

# add the start and end position to the end of displacement file
# args:
# start_positions: a list of hand start position
def write_hand_pos(filenames, start_positions, end_positions):    
    for file, start, end in zip(filenames, start_positions, end_positions):
        write_to_file(file, [start], 'append')
        write_to_file(file, [end], 'append')

# calculate the center of a part across frames, not working yet
# args:
# inp_file, .inp file name
# eleset, which element set does the part belong to 
# odb_reader, ReadOdb class
# step_name: step name in odb file
# part: the part name in odb file
# part_start: the starting line of the part in .inp file
def find_centers(inp_file, eleset, odb_reader, step_name, part, part_start):
    abaqus = manipulate_abaqus_file.ReadAbaqusInput(inp_file)
    elements = abaqus.read_elset_or_nset(eleset)
    element_to_node = abaqus.read_element(part_start)
    node_indices = []
    for elem in elements:
        node_indices.append(element_to_node[elem - 1])  
    nodes_unique = np.unique(np.array(node_indices))
    positions_across_frame = []
    
    for label in nodes_unique:
        start, end = odb_reader.read_start_end_pos(step_name, label, part)
        positions_across_frame.append(np.array(start) - np.array(end))
    pdb.set_trace()
    
# calculate the center of displacement of an element set 
# args:
# inp_file, tumor_eleset, tumor_part, odb_file, breast_part, odb_step
def center_disp(args):
    inp_file, tumor_eleset, odb_file, breast_part_start, step, breast_part = args
    abaqus = manipulate_abaqus_file.ReadAbaqusInput(inp_file)
    node_indices = abaqus.get_node_from_elemset(tumor_eleset, breast_part_start)
    disp = read_lastframe(odb_file, step, breast_part)
    disp_eleset = []
    for index in node_indices:
        disp_eleset.append(disp[index - 1])
    return np.mean(np.array(disp_eleset), axis=0)       

# read displacement of last frame
# return:
# a list of 3D displacements
def read_lastframe(file_name, step, part):
    odb = openOdb(file_name)
    frame_num = -1
    odb_reader = ReadOdb(file_name)
    args = [odb, step, part, frame_num]
    disps = odb_reader.read_frame(args) 
    return disps

if __name__ == "__main__": 
    odb_files = ['278.odb']
    breast_step = 'Step-1'
    hand_step = 'Step-1'
    tip_label = 4  # generate_scenario.py can find the label of hand tip
    output_folder = 'displacement files'  
    hand_part = 'PART-2-1'
    tumor_elset = '*Elset, elset=TUMOR_FROMSKIN\n'
    inp_file = 'Palpation Jobs/surface_to_node.inp' 
    odb_reader = ReadOdb(odb_files)
    breast_part = 'PART-1-1'
    breast_part_start = '*Part, name=PART-1\n'
  #  find_centers(inp_file, tumor_elset, odb_reader, breast_step, breast_part, breast_part_start)
  #  output_filenames = odb_reader.write_all_frame(breast_step, breast_part, output_folder)
  #  for name in output_filenames:
        
  #  hand_start, hand_end = odb_reader.read_start_end_pos(hand_step, tip_label, hand_part)
  #  write_hand_pos(output_filenames, hand_start, hand_end)
    
    purpose = sys.argv[1]  # purpose can be unload (unload breat with weight)
    if purpose == 'unload':
        odb_files = ['Abaqus_outputs/reference_pos.odb']
        inp_output_folder = 'Weight Jobs'
        inp_file = 'F:/Research/Breast with weight/real_skin/reference_pos.inp'
        for file in odb_files:
            disps = read_lastframe(file, breast_step, breast_part) 
            file_name = file.split('/')[-1]
            file_name = output_folder + '\/' + file_name.split('.')[0] + '.txt'                
            write_to_file(file_name, disps, 'write')
            abaqus = manipulate_abaqus_file.ReadAbaqusInput(inp_file)
            points = abaqus.read_part(breast_part_start)
            for index, disp in enumerate(disps):
                new_pos = np.array(points[index]) + np.array([float(disp[0]),float(disp[1]),float(disp[2])])
                abaqus.edit_part(breast_part_start, index, str(new_pos[0]) + ',' + str(new_pos[1]) + ',' + str(new_pos[2]) + '\n')
                file_name = file.split('/')[-1]
                file_name = inp_output_folder + '/' + file_name.split('.')[0] + '.inp'
            abaqus.write_output(file_name)
    
    if purpose == 'weight':  # read the result .odb file and added the displacement to the model 
        odb_files = glob.glob('F:/Research/FEA simulation for NN/stl/Abaqus_outputs/weight/glandular_fat_90_10/*odb')
        for file in odb_files:
            output_folder = 'F:/Research/FEA simulation for NN/train_patient_specific/disps/glandular_fat_90_10'
            disps = read_lastframe(file, breast_step, breast_part) 
            file_name = os.path.basename(file)   
            file_name = os.path.join(output_folder, file_name.split('.')[0] + '.txt')
            write_to_file(file_name, disps, 'write')
            
    if purpose == 'tumor':
        odb_files = glob.glob('F:/Research/FEA simulation for NN/stl/Abaqus_outputs/weight/glandular_fat_90_10/*odb')       
        for file in odb_files:
            output_folder = 'F:/Research/FEA simulation for NN/train_patient_specific/tumor/glandular_fat_90_10'
            inp_file = 'Weight Jobs/reference_pos.inp'
            args = [inp_file, tumor_elset, file, breast_part_start, breast_step, breast_part]
            
               
            file_name = os.path.basename(file)  
          #  if file_name == 'reference_pos_x_y_0.odb':
          #      pdb.set_trace()
         #   else:
         #       continue
            file_name = os.path.join(output_folder, file_name.split('.')[0] + '.txt')
            disp = center_disp(args)  
            output_file = open(file_name, 'w')
            output_file.write(str(disp[0]) + ' ' + str(disp[1]) + ' ' + str(disp[2]))
            output_file.close()