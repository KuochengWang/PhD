from collections import defaultdict
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
MOVE_HAND_TO_SURFACE_TOLERANCE = 2

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

# return the angle between 2 vector in degree
def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)) * 180 / math.pi
    
# find direction to move hand to palpate breast
def find_direction(hand_pos, tetrahedral_mesh):          
    keys = list(range(1, 28))
    random.shuffle(keys)    
    closest_point,  closest_point_index = tetrahedral_mesh.closest_triangle_point(hand_pos)
    direction = closest_point - hand_pos
    dist = np.sum(np.abs(direction)**2,axis=-1)**(1./2)
    return  direction, dist, closest_point_index
                    
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
                        surface_point = pos
                        surface_point_index = index
            if min_y == sys.float_info.max:
                tolerace += 1
        return surface_point, surface_point_index
    
    def find_all_surface_point(self, grid_points, surface_file):
        surface_points = []
        surface_points_indices = []
        content = read_tetgen.ReadTetGen('', '')
        surface = content.read_surface(surface_file)
        surface = np.unique(surface)
        for i, point in enumerate(grid_points):
            surface_point, surface_point_index = self.find_surface_point(point, surface.tolist())
            surface_points.append(surface_point)
            surface_points_indices.append(surface_point_index)
        return surface_points, surface_points_indices

class HandManipulate:
    # @param file_name the abaqus.inp file name
    # @param part the part name the hand represents in abaqus.inp file
    def __init__(self, file_name, part):
        self.hand_part = part
        self.abaqus = manipulate_abaqus_file.ReadAbaqusInput(file_name)
        
    def return_abaqus(self):
        return self.abaqus
        
    def __find_handtip__(self):
         
        hand_points = np.array(self.abaqus.read_part(self.hand_part))
        hand_y = hand_points[:, 1]
        result = np.where(np.max(hand_y) == hand_y)
        ymax_index = result[0][0]
        hand_tip = hand_points[ymax_index]
        
        return hand_tip
    
    # move hand to the surface based on surface points
    # @param base_y is y value of base plane
    # @param base_center the center of the 4 edges
    # return the hand move direction 
    def move_hand_to_surface(self, surface_points, base_center):
        hand_tip = self.__find_handtip__()
        move_vecs = []
        for point in surface_points:
            move_vec = point - hand_tip + MOVE_HAND_TO_SURFACE_TOLERANCE * (point -  base_center) / np.linalg.norm(point -  base_center)  
            move_vecs.append(move_vec)            
        return hand_tip, move_vecs
    
    # set the boundary condition of hand so it can move to different direction
    # @param arg[0] the line content with boundary of hand
    # @param arg[1] the line content for time period
    # @param arg[2] the direction the hand should move to
    # @param arg[3] the point of the hand should move to
    # @param arg[4] the y axis of the breast base
    # @param arg[5] the distance from 
    def set_boundary(self, arg):
        boundary_line = arg[0]
        time_period_line = arg[1]
        direction = arg[2]
        surface_point = arg[3]
        base = arg[4]
        dist = arg[5]
        depth_ratio = 0.2
        time_period = self.abaqus.read_timeperiod(time_period_line)
        depth = (base - surface_point[1]) * depth_ratio
        self.abaqus.set_boundary(boundary_line, time_period, direction, (depth + dist) / time_period)
        
    # @param assembly the content of the line that assembly start
    # @param vec is the new vector of the assembly
    def set_assembly(self, assembly, vec):
        self.abaqus.set_assembly(assembly, vec)
        
    def write_output(self, output_file):
        self.abaqus.write_output(output_file)
        
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

class TetrahedralMesh:
    class Node:
        def __init__(self, node):
            self.x, self.y, self.z = node
            self.neighbors = []
        
        def set_neighbor(self, node_index):
            self.neighbors.add(node_index)            
            
    # @param index the index of triangle
    # @param triangle the 3 vertex indexes in a triangle
    class Triangle:
        def __init__(self, triangle, index):
            self.index = index
            self.triangle = triangle
            self.neighbors = []
            
    class Graph:
        def __init__(self):  
            self.graph = defaultdict(list) 
                      
            
        def add_edge(self,u,v): 
            self.graph[u].append(v) 
            self.graph[v].append(u)
    
        def BFS(self, s): 
            queue = [] 
            queue.append(s) 
            nodes = []
            visited = dict() 
            visited[s] = True
            point_limit = 1000
            while queue: 
                s = queue.pop(0)
                if len(nodes) > point_limit:
                    break
                nodes.append(s) 
                for i in self.graph[s]:
                    if i not in visited.keys() or (visited[i] == False):                    
                        queue.append(i) 
                        visited[i] = True
            return nodes
            
    def __init__(self, tet_file, triangle_file, node_file):
        content = read_tetgen.ReadTetGen(tet_file, node_file)
        self.triangles = content.read_surface(triangle_file)
        self.nodes = content.read_coordinates()
        self.tetrahedrons = content.read_elements()
        self.graph = self.Graph()
        self.point_to_tet = dict() # the point index to all tetrahedrons that contain it
        
    # this method is copied from https://www.erikrotteveel.com/category/python/
        # Tests if a ray starting at point p0, in the direction
        # p1 - p0, will intersect with the triangle.
        #
        # arguments:
        # p0, p1: numpy.ndarray, both with shape (3,) for x, y, z.
        # triangle: numpy.ndarray, shaped (3,3), with each row
        #     representing a vertex and three columns for x, y, z.
        #
        # returns: 
        #    0.0 if ray does not intersect triangle, 
        #    1.0 if it will intersect the triangle,
        #    2.0 if starting point lies in the triangle.
    def ray_intersect_triangle(self, p0, p1, triangle):
        v0, v1, v2 = triangle
        u = v1 - v0
        v = v2 - v0
        normal = np.cross(u, v)
        b = np.inner(normal, p1 - p0)
        a = np.inner(normal, v0 - p0)
    
        if (b == 0.0):
            # ray is parallel to the plane
            if a != 0.0:
                # ray is outside but parallel to the plane
                return 0
            else:
                # ray is parallel and lies in the plane
                rI = 0.0
        else:
            rI = a / b
        if rI < 0.0:
            return 0
        w = p0 + rI * (p1 - p0) - v0
        denom = np.inner(u, v) * np.inner(u, v) - \
            np.inner(u, u) * np.inner(v, v)
        si = (np.inner(u, v) * np.inner(w, v) - \
            np.inner(v, v) * np.inner(w, u)) / denom
        
        if (si < 0.0) | (si > 1.0):
            return 0
        ti = (np.inner(u, v) * np.inner(w, u) - \
            np.inner(u, u) * np.inner(w, v)) / denom
        
        if (ti < 0.0) | (si + ti > 1.0):
            return 0
        if (rI == 0.0):
            # point 0 lies ON the triangle. If checking for 
            # point inside polygon, return 2 so that the loop 
            # over triangles can stop, because it is on the 
            # polygon, thus inside.
            return 2
        return 1
    
    # find which triangle is the line colliding with
    # arguments:
    # p0, p1: numpy.ndarray, both with shape (3,) for x, y, z.
    # returns:
    # None or the position of triangel, numpy.ndarray shape (3,3)
    def triangle_collision_dection(self, p0, p1):
        for tri in self.triangles:
            triangle_point = np.array([self.nodes[tri[0]], \
                                       self.nodes[tri[1]], self.nodes[tri[2]]])
            if self.side_of_triangle(triangle_point, p0) and self.side_of_triangle(triangle_point, p1):
                continue
            if self.ray_intersect_triangle(p0, p1, triangle_point):
                return triangle_point
        return 
    
    def closest_triangle_point(self, point):
        unique_tri_points = list(np.unique(self.triangles))
        triangle_points = [] 
        for tri in unique_tri_points: 
            triangle_points.append(self.nodes[tri])
        temp_dist = np.array(triangle_points) - point
        dist = np.sum(np.abs(temp_dist)**2,axis=-1)**(1./2)
        min_dist_index = (list(dist)).index(min(dist))
        return self.nodes[min_dist_index], min_dist_index
    
    # find which side of the triangle the point lies in
    # arguments:
    # tri: numpy.ndarray, shape (3, 3), 3 point position of triangle
    # point, numpy.ndarray, with shape (3,) for x, y, z
    # returns: 
    # whether the point is in postive side of plane
    def side_of_triangle(self, tri, point):
        p1 = tri[0,:]
        p2 = tri[1,:]
        p3 = tri[2,:]
        normal = np.cross(p2 - p1, p3 - p1)
        return np.dot(normal, point - p1) > 0
    
    def __build_triangle_graph__(self):
        for tri in self.triangles:
            self.graph.add_edge(tri[0], tri[1])
            self.graph.add_edge(tri[0], tri[2])
            self.graph.add_edge(tri[1], tri[2])
            
    # arguments:
    # point: the index of the point in contact triangle
    # returns:
    # a list of points on the contact surface in breast    
    def contact_points(self, point):
        self.__build_triangle_graph__()
        self.__point_to_tetrahedral__()
        return self.graph.BFS(point)
    
    # find all tetrhedrons contain the point
    # arguments:
    # point: the index of the point in contact triangle
    # returns:
    # a list of tetrahedral indices
    def surface_tetrahedral(self, point):
        points = self.contact_points(point)
        tetrahedral_indices = []
        for point in points:
            tetrahedral_indices.append(self.point_to_tet[point])  
        return [j for sub in tetrahedral_indices for j in sub] 
    
    # set the mapping between a point and all tetreherons containt it
    # arguments:
    # point: the index of the point in contact triangle
    def __point_to_tetrahedral__(self):
        tetrahedrons = self.tetrahedrons.tolist()
        for tet_index, tet in enumerate(tetrahedrons):
            for node_index in tet:
                if node_index not in self.point_to_tet.keys():
                    self.point_to_tet[node_index] = []
                else:
                    self.point_to_tet[node_index].append(tet_index)
                    
    # exclude nodeset n2 from n1
    # arguments:
    # n1, n2, both are a list of int
    def exclude_node_set(self, n1, n2):
        return list(set(n1) - set(n2))
                        
def test_graph(surface, node):
    g = TetrahedralMesh(surface, node).Graph()
    g.add_edge(1, 2) 
    g.add_edge(1, 3) 
    g.add_edge(8, 3) 
    g.add_edge(4, 1) 
    g.add_edge(5, 4) 
    g.add_edge(4, 6) 
    g.add_edge(7, 6)
    g.add_edge(8, 7)
      
    print ("Following is Breadth First Traversal"
                      " (starting from vertex 2)") 
    g.BFS(2) 

def test_ReadAbaqusInput_delete_elset(filename, start_line):
    delete_elset(start_line)
    
if __name__ == "__main__":
    node = 'Skin_Layer.node'
    element = 'Skin_Layer.ele'
    surface = 'Skin_Layer.face'
    abaqus_inp = 'Jobs/surface_to_node.inp'    
    
    breast_info = GetInfoFromBreast(element, node)
    edge = breast_info.find_edge()

    hand_part = '*Part, name=PART-2\n'
    grids_positions = grid(edge[0][0], edge[1][0], edge[2][2], edge[3][2])
    surface_points, surface_points_indices = breast_info.find_all_surface_point(grids_positions, surface)     
    hand = HandManipulate(abaqus_inp, hand_part)
    base = max([edge[0][1], edge[1][1], edge[2][1], edge[3][1]])
    hand_tip, trans_vector = hand.move_hand_to_surface(surface_points, (edge[0] + edge[1] + edge[2] + edge[3]) / 4)
    
    boundary = '*Boundary, amplitude=AMP-1\n'
    time_period = '*Amplitude, name=AMP-1, time=TOTAL TIME, definition=EQUALLY SPACED, fixed interval=1.\n'
    assembly = '*Instance, name=PART-2-1, part=PART-2\n'
    index = 0
    
    directions = []
    distances = []
    closest_point_indices = []
    tetrahedral_mesh = TetrahedralMesh(element, surface, node)
   
    for i, vec in enumerate(trans_vector):
        direc, dist, closest_point_index = find_direction(hand_tip + vec, tetrahedral_mesh)
        directions.append(direc)
        distances.append(dist)
        closest_point_indices.append(closest_point_index)
        print(i)
    
    r_input = hand.return_abaqus()
    nset = '*Nset, nset=s_Set-12, instance=PART-1-1\n'
    encastre = '*Nset, nset=SET-4, instance=PART-1-1\n' 
    encastre_points = r_input.read_elset_or_nset(encastre)
    for vec, direction, surface_point, distance, closest_point_index in zip(trans_vector, directions, surface_points, distances, closest_point_indices):
        hand.set_assembly(assembly, vec)
        boundary_arg = [boundary, time_period, direction, surface_point, base, distance]
        hand.set_boundary(boundary_arg)
        contact_ps = tetrahedral_mesh.contact_points(closest_point_index)
        r_input.delete_elset_or_nset(nset)
        r_input.add_to_elset_or_nset(nset, contact_ps)
        hand.write_output('Jobs/' + str(index) + '.inp')
        index += 1
        