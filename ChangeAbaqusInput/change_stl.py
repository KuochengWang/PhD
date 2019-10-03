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
    return mesh_points, mesh_triangles

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
    pdb.set_trace()
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

        
if __name__ == "__main__":
    face_to_delete = np.zeros([46,3])
    face_to_delete[0] = [16185, 16181, 17285]
    face_to_delete[1] = [19761, 19686, 19688]
    face_to_delete[2] = [17299, 17285, 16181]
    face_to_delete[3] = [19688, 20418, 19761]
    face_to_delete[4] = [17299, 17285, 16181]
    face_to_delete[5] = [19761, 19686, 19688]
    face_to_delete[6] = [17299, 18137, 17285]
    face_to_delete[7] = [20418, 19688, 18137]
    face_to_delete[8] = [19658, 19659, 19660]
    face_to_delete[9] = [20409, 19658, 24729]
    face_to_delete[10] = [20409, 19660, 21856]
    face_to_delete[11] = [20409, 19658, 24729]
    face_to_delete[12] = [20409, 19660, 21856]
    face_to_delete[13] = [20408, 19659, 20409]
    face_to_delete[14] = [19659, 21856, 19660]
    face_to_delete[15] = [20409, 19658, 24729]
    face_to_delete[16] = [19659, 21856, 19660]
    face_to_delete[17] = [20408, 19659, 20409]
    face_to_delete[18] = [16185, 17285, 17286]
    face_to_delete[19] = [19686, 19687, 19688]
    face_to_delete[20] = [19687, 19686, 18945]
    face_to_delete[21] = [16168, 17286, 17283]
    face_to_delete[22] = [19670, 17283, 19687]
    face_to_delete[23] = [18945, 19670, 19687]
    face_to_delete[24] = [16168, 16165, 17286]
    face_to_delete[25] = [19687, 19686, 18945]
    face_to_delete[26] = [18945, 19670, 19687]
    face_to_delete[27] = [16185, 17286, 16165]
    face_to_delete[28] = [19687, 19686, 18945]
    face_to_delete[29] = [16185, 17285, 17286]
    face_to_delete[30] = [19686, 19687, 19688]
    face_to_delete[31] = [16185, 17285, 17286]
    face_to_delete[32] = [19687, 19686, 18945]
    face_to_delete[33] = [19761, 19686, 19688]
    face_to_delete[34] = [16185, 17286, 16165]
    face_to_delete[35] = [19687, 19686, 18945]
    face_to_delete[36] = [16185, 16181, 17285]
    face_to_delete[37] = [19761, 19686, 19688]
    face_to_delete[38] = [17299, 17285, 16181]
    face_to_delete[39] = [20418, 19688, 18137]
    face_to_delete[40] = [17299, 17285, 16181]
    face_to_delete[41] = [19688, 20418, 19761]
    face_to_delete[42] = [17299, 17285, 16181]
    face_to_delete[43] = [19761, 19686, 19688]
    face_to_delete[44] = [17299, 18137, 17285]
    face_to_delete[45] = [20418, 19688, 18137]
    output_filename = "FGT_Cluster_1-2_modified.stl"
    points = write_to_file("FGT_Cluster_1-2_modified.stl", face_to_delete, output_filename)
    
    