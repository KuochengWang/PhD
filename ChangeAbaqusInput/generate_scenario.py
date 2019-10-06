import manipulate_abaqus_file
import math
import numpy as np
import pdb
import random
import read_tetgen
import sys

HAND_DIRECTION = [0, 1, -1]
VERTICLE_DIRECTION = [0, 1, 0]
HORIZONTAL_GRID_NUMER = 50
VERTICLE_GRID_NUMER = 25
BOUNDARY_INTERVAL = 5

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

# return the angle between 2 vector in degree
def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)) * 180 / math.pi
    
# find direction to move hand to palpate breast
# @param hand_pos the hand current postion
# @param edge_points the edge postion on the bottom of breast, there are 4 
# return the direct the hand is suppsosed to move
def find_direction(hand_pos, edge_points):
    find_direction = False
    while not find_direction:
        direction_key = random.randint(1, 28)
        counter = 1
        for x in HAND_DIRECTION:
            for y in HAND_DIRECTION:
                for z in HAND_DIRECTION:
                    if (x == 0 and y == 0 and z == 0) or counter != direction_key:
                        counter += 1 
                        continue                 
                    step = np.array([x, y, z])
                    for edge in edge_points:
                        if angle_between(step, VERTICLE_DIRECTION) <  angle_between(VERTICLE_DIRECTION, edge - hand_pos):
                               find_direction = True
                               break
                    if find_direction:
                        return step

class GetInfoFromBreast:
    def __init__(self, elementfile, nodefile):
        self.coordinates = self.read_coordinates(elementfile, nodefile)
        
    def read_coordinates(self, ele_file, coord_file): 
        content = read_tetgen.ReadTetGen(ele_file, coord_file)
        coordinates = content.read_coordinates()
        return coordinates
        
    # find 4 edges with largest x, z; smallest, x, z
    # @param ele_file the .ele file
    # @param ele_file the .node file
    def find_edge(self):
        x_col = self.coordinates[:, 0]
        z_col = self.coordinates[:, 2]
        result = np.where(np.max(x_col) == x_col)
        xmax_index = result[0][0]
        result = (np.where(np.min(x_col) == x_col))
        xmin_index = result[0][0]
        result = (np.where(np.max(z_col) == z_col))
        zmax_index = result[0][0]
        result = (np.where(np.min(z_col) == z_col))
        zmin_index = result[0][0] 
        return [self.coordinates[xmax_index], self.coordinates[xmin_index], self.coordinates[zmax_index], self.coordinates[zmin_index]]
    
    # find the surface point within the grid of search_pos
    # @param search_pos the grid position, contains [x,z]
    # @param coordinates_indices the indices of the coordinate 
    def find_surface_point(self, search_pos, coordinates_indices):
        tolerace = 2
        min_y = sys.float_info.max
        while min_y == sys.float_info.max:
            for index in list(coordinates_indices):
                pos = self.coordinates[index]
                temp_y = pos[1]
                if abs(pos[0]-search_pos[0]) < tolerace and abs(pos[2]-search_pos[1]) < tolerace:
                    if temp_y < min_y:
                        min_y = temp_y
            if min_y == sys.float_info.max:
                tolerace += 1
        return min_y
    
    def find_all_surface_point(self, grid_points, surface_file):
        surface_points = []
        content = read_tetgen.ReadTetGen('', '')
        surface = content.read_surface(surface_file)
        surface = np.unique(surface)
        for i, point in enumerate(grid_points):
            surface_points.append(self.find_surface_point(point, surface.tolist()))
            print(i)
        return surface_points

def change_handpos(file_name, hand_part, edge):
    abaqus = manipulate_abaqus_file.ReadAbaqusInput(file_name)
    hand_points = np.array(abaqus.read_part(hand_part))
    hand_y = hand_points[:, 1]
    result = np.where(np.max(hand_y) == hand_y)
    ymax_index = result[0][0]
    hand_point = hand_points[ymax_index]
    directions = []
    directions.append(find_direction(hand_point, edge))    
    pdb.set_trace()

# form the grid for hand to palpate
# returns a list of [x,z] as grid coord
def grid(xmax, xmin, zmax, zmin):
    xmax -= BOUNDARY_INTERVAL
    xmin += BOUNDARY_INTERVAL
    zmax -= BOUNDARY_INTERVAL
    zmin += BOUNDARY_INTERVAL
    width = (xmax - xmin) / HORIZONTAL_GRID_NUMER
    height = (zmax - zmin) / VERTICLE_GRID_NUMER
    x_start = xmin
    z_start = zmin
    grids = [] 
    
    while x_start <= xmax:
        x_start += width
        z_start = zmin + height
        while z_start <= zmax:
            grids.append([x_start, z_start])
            z_start += height
    return grids

if __name__ == "__main__":
    node = 'Skin_Layer.node'
    element = 'Skin_Layer.ele'
    surface = 'Skin_Layer.face'
    abaqus_inp = 'Jobs/Job-4.inp'
    bread_info = GetInfoFromBreast(element, node)
    edge = bread_info.find_edge()
    hand_part = '*Part, name=Part-2\n'
    grids_positions = grid(edge[0][0], edge[1][0], edge[2][2], edge[3][2])
    surface_points = bread_info.find_all_surface_point(grids_positions, surface)
    pdb.set_trace()
    change_handpos(abaqus_inp, hand_part, edge)