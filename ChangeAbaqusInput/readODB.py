from convert_tetgen_to_unity import write_to_file
import manipulate_abaqus_file
import numpy as np
import odbAccess
from odbAccess import openOdb
import os
import pdb

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
                args = [odb, folder, step_name, part_name, frame_num]
                positions = self.read_frame(args)
                file_name = folder + '\/' + file.split('.')[0] + '_' + \
                                   str(frame_num) + '.txt'                
                write_to_file(file_name, positions, 'write')
                file_names.append(file_name)
            odb.close()
        return file_names
    # read postion from each specific frame
    # arguments:
    # odb: from openOdb(file)
    # step: the step name from Abaqus
    # part: the part name from Abaqus
    # folder: the filder to store file 
    # frame_num: which frame to read
    # returns:
    # a 2D list         
    def read_frame(self, args):
        odb, folder, step, part, frame_num = args
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
    
    # read postion and displacement of a frame
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
                    if len(field_value.instance.nodes) != len(instance.nodes):
                        continue
                    return field_value.instance.nodes[node_label - 1].coordinates, \
                           field_value.data
    
    # returns the start and end position of a point
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

if __name__ == "__main__": 
    odb_file = ['278.odb']
    breast_step = 'Step-1'
    hand_step = 'Step-1'
    tip_label = 4  # generate_all_scenario.py can find the label of hand tip
    output_folder = 'displacement files'  
    breast_part = 'PART-1-1'
    hand_part = 'PART-2-1'
    odb_reader = ReadOdb(odb_file)
    output_filenames = odb_reader.write_all_frame(breast_step, breast_part, output_folder)
    pdb.set_trace()
    hand_start, hand_end = odb_reader.read_start_end_pos(hand_step, tip_label, hand_part)
    write_hand_pos(output_filenames, hand_start, hand_end)
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    



