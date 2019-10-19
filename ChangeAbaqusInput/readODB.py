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
    def write_all_frame(self, step_name, part_name, folder):
        for file in self.odb_files:
            odb = openOdb(file)
            total_frames = len(odb.steps[step_name].frames)
            for frame_num in range(total_frames):
                args = [odb, folder, step_name, part_name, frame_num]
                positions = self.read_frame(args)
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
        
    def readpoint_specific_frame(self, args):
        odb, step_name, frame_num, node_label, part_name = args
        for name, instance in odb.rootAssembly.instances.items(): 
            if name == part_name:                 
                frame = odb.steps[step_name].frames[frame_num]   
                displacement = frame.fieldOutputs['U']  
                field_values = displacement.values  
                field_value.instance.nodes[node_label].coordinates                     
                for field_value in field_values:
                    label = field_value.nodeLabel
                    if label != node_label or len(field_value.instance.nodes) != len(instance.nodes):
                        continue
                   
                    return field_value.data                                     
    
    def readpoints(self, step_name, node_label, part_name):
        poistions = []
        for file in self.odb_files:
            odb = openOdb(file)
            total_frames = len(odb.steps[step_name].frames)
            for frame_num in range(total_frames):
                args = [odb, step_name, frame_num, node_label, part_name]
                poistions.append(self.readpoint_specific_frame(args))
        return poistions
                
if __name__ == "__main__": 
    odb_file = ['278.odb']
    breast_step = 'Step-1'
    hand_step = 'Step-1'
    tip_label = 4  # generate_all_scenario.py can find the label of hand tip
    output_folder = 'displacement files'  
    breast_part = 'PART-1-1'
    hand_part = 'PART-2-1'
    odb_reader = ReadOdb(odb_file)
   # odb_reader.write_all_frame(breast_step, breast_part, output_folder)
    odb_reader.readpoints(hand_step, tip_label, hand_part)
      
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    



