# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:58:12 2019

@author: vr_lab
"""

# This file will delete the vertices based on user specification.
# TetGen detects intersect surfaces. We can delete them and regenerate using 
# Meshmixer. 

import numpy as np
import pdb
import vtk

def parse(filename):
    infile = filename
    reader = vtk.vtkSTLReader()
    reader.SetFileName(infile)
    reader.Update()
    data = reader.GetOutput()
        
    n_points = data.GetNumberOfPoints()
    n_triangles = data.GetNumberOfCells()
    mesh_points = np.zeros([n_points, 3])
    mesh_triangles = np.zeros([n_triangles, 3])
    for i in range(n_points):
        mesh_points[i][0], mesh_points[i][1], mesh_points[i][	2] = data.GetPoint(i)
    for i in range(n_triangles):
        mesh_triangles[i][0] = data.GetPolys().GetData().GetValue(i*4+1)
        mesh_triangles[i][1] = data.GetPolys().GetData().GetValue(i*4+2)
        mesh_triangles[i][2] = data.GetPolys().GetData().GetValue(i*4+3)
    return mesh_points, mesh_triangles.astype(int)

def compare_faces(face_to_delete, face):
    for temp_face_to_delete in face_to_delete:
        if (np.sort(temp_face_to_delete) == np.sort(face)).sum() == 3:
            return True
    return False

def write_to_file(filename, face_to_delete, output_filename):
    
    Points = vtk.vtkPoints()
    Triangles = vtk.vtkCellArray()
    Triangle = vtk.vtkTriangle()
    points, faces = parse(filename)
    for point in points:
        id = Points.InsertNextPoint(point[0], point[1], point[2])        
    for i, face in enumerate(faces):
      
        skip = compare_faces(face_to_delete, face)
        if not skip:
            Triangle.GetPointIds().SetId(0, int(face[0]))
            Triangle.GetPointIds().SetId(1, int(face[1]))
            Triangle.GetPointIds().SetId(2, int(face[2]))
            Triangles.InsertNextCell(Triangle)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(Points)
    polydata.SetPolys(Triangles)
    polydata.Modified()
    
    if vtk.VTK_MAJOR_VERSION <= 5:
        polydata.Update()
    writer = vtk.vtkSTLWriter();
    writer.SetFileName(output_filename);
    if vtk.VTK_MAJOR_VERSION <= 5:
        writer.SetInput(polydata)
    else:
        writer.SetInputData(polydata)
    writer.Write()

def read_intersection_faces(filename):
    file = open(filename, 'r') 
    lines = file.readlines() 
      
    count = 0
    # Strips the newline character 
    faces = np.zeros([len(lines), 3])
    for line in lines: 
        content = line.strip()
        if content[0] == '(':
            no_left_parenthesis = content.replace('(', '')
            no_right_parenthesis = no_left_parenthesis.replace(')', '')
            f1 = no_right_parenthesis.split('and')[0].replace(',', ' ')
            f1 = f1.split()
            f2 = no_right_parenthesis.split('and')[1].replace(',', ' ')
            
            f2 = f2.split()
            faces[count * 2] = [int(f1[0]), int(f1[1]), int(f1[2])]
            faces[count * 2 + 1] = [int(f2[0]), int(f2[1]), int(f2[2])]
            count += 1
    return faces     
        
if __name__ == "__main__":
    intersection_file = 'F:\Research\Breast Model\BM_Fatty_001\Left\Fat_1_Fgt_1\SolidModel\intersection.txt'
    output_filename = 'F:\Research\Breast Model\BM_Fatty_001\Left\Fat_1_Fgt_1\SolidModel\FGT_Cluster_Biggest.stl'
    input_filename = 'F:\Research\Breast Model\BM_Fatty_001\Left\Fat_1_Fgt_1\SolidModel\FGT_Cluster_Simplified.stl'
    face_to_delete = read_intersection_faces(intersection_file)
    write_to_file(input_filename, face_to_delete, output_filename)
  #  output_filename = "FGT_Cluster_1-2_modified.stl"
  #  points = write_to_file("FGT_Cluster_1-2_modified.stl", face_to_delete, output_filename)
    
    