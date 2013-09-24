#!/usr/bin/env python3.3
"""
Simple API for placing objects on tables according to directional spatial
relations.
"""
import pymorse
import sys
import random
import json
import math
import numpy
import errno 
import getopt
from operator import itemgetter

from contextlib import contextmanager

@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


MAX_NUM_OF_SAMPLES = 100

# Constants
# Offset for placing an object above a table 
Z_DIST = 0.005
# Offset for placing an object at the edge of the table
XY_DIST = 0.02
# Sigma allows for some variance for directional relations 
DIRECTION_SIGMA = math.pi/16
# Scale the bounding box of the object in order to prevent the object to be
# spawned close to the table edge
OBJECT_SCALE = 1.00

# epsilon for testing whether a number is close to zero
_EPS = numpy.finfo(float).eps * 4.0

def vector_norm(data, axis=None, out=None):
    """Return length, i.e. Euclidean norm, of ndarray along axis.

    >>> v = numpy.random.random(3)
    >>> n = vector_norm(v)
    >>> numpy.allclose(n, numpy.linalg.norm(v))
    True
    >>> v = numpy.random.rand(6, 5, 3)
    >>> n = vector_norm(v, axis=-1)
    >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=2)))
    True
    >>> n = vector_norm(v, axis=1)
    >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=1)))
    True
    >>> v = numpy.random.rand(5, 4, 3)
    >>> n = numpy.empty((5, 3))
    >>> vector_norm(v, axis=1, out=n)
    >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=1)))
    True
    >>> vector_norm([])
    0.0
    >>> vector_norm([1])
    1.0

    """
    data = numpy.array(data, dtype=numpy.float64, copy=True)
    if out is None:
        if data.ndim == 1:
            return math.sqrt(numpy.dot(data, data))
        data *= data
        out = numpy.atleast_1d(numpy.sum(data, axis=axis))
        numpy.sqrt(out, out)
        return out
    else:
        data *= data
        numpy.sum(data, axis=axis, out=out)
        numpy.sqrt(out, out)


def quaternion_about_axis(angle, axis):
    """Return quaternion for rotation about axis.

    >>> q = quaternion_about_axis(0.123, [1, 0, 0])
    """
    q = numpy.array([0.0, axis[0], axis[1], axis[2]])
    qlen = vector_norm(q)
    if qlen > _EPS:
        q *= math.sin(angle/2.0) / qlen
    q[0] = math.cos(angle/2.0)
    return q

class BBox():
    """ Bounding box of an object with getter functions.
    """
    def __init__(self, bbox):
        # Calc x_min and x_max for obj1
        x_sorted = sorted(bbox, key=itemgetter(0))
        self.x_min = x_sorted[0][0]
        self.x_max = x_sorted[7][0]

        # Calc y_min and y_max for obj
        y_sorted = sorted(bbox, key=itemgetter(1))
        self.y_min = y_sorted[0][1]
        self.y_max = y_sorted[7][1]

        # Calc z_min and z_max for obj
        z_sorted = sorted(bbox, key=itemgetter(2))
        self.z_min = z_sorted[0][2]
        self.z_max = z_sorted[7][2]
        
    def get_x_min(self):
        return self.x_min

    def get_x_max(self):
        return self.x_max

    def get_y_min(self):
        return self.y_min

    def get_y_max(self):
        return self.y_max

    def get_z_min(self):
        return self.z_min

    def get_z_max(self):
        return self.z_max
    

class AbstractNode():
    """ An abstract node. Captures the common aspects of RootNode and ObjectNode
    """
    def __init__(self, object):
        self.name = object
        self.local_bbox = BBox(self.get_local_bbox())
        self.calc_anchors()

    def get_local_bbox(self):
        """ Get the bounding box from the object.
        """
        return json.loads(morse.rpc('simulation','get_object_bbox',self.name))

    def calc_anchors(self):
        """ Calculate anchors on the supporting plane. Default is a 3x3 grid.
        """
        x = (self.local_bbox.get_x_max() - self.local_bbox.get_x_min()) / 6 
        y = (self.local_bbox.get_y_max() - self.local_bbox.get_y_min()) / 6

        self.x_sigma = (x) * (x)
        self.y_sigma = (y) * (y)
        
        self.north      = [self.local_bbox.get_x_min() + 1*x, self.local_bbox.get_y_min() + 3*y]
        self.north_east = [self.local_bbox.get_x_min() + 1*x, self.local_bbox.get_y_min() + 5*y]
        self.east       = [self.local_bbox.get_x_min() + 3*x, self.local_bbox.get_y_min() + 5*y]
        self.south_east = [self.local_bbox.get_x_min() + 5*x, self.local_bbox.get_y_min() + 5*y]
        self.south      = [self.local_bbox.get_x_min() + 5*x, self.local_bbox.get_y_min() + 3*y]
        self.south_west = [self.local_bbox.get_x_min() + 5*x, self.local_bbox.get_y_min() + 1*y]
        self.west       = [self.local_bbox.get_x_min() + 3*x, self.local_bbox.get_y_min() + 1*y]
        self.north_west = [self.local_bbox.get_x_min() + 1*x, self.local_bbox.get_y_min() + 1*y]
        self.center     = [self.local_bbox.get_x_min() + 3*x, self.local_bbox.get_y_min() + 3*y]

    def get_anchor(self, anchor):
        if anchor == 'north':
            return self.north
        elif anchor == 'north_east':
            return self.north_east
        elif anchor == 'east':
            return self.east
        elif anchor == 'south_east':
            return self.south_east
        elif anchor == 'south':
            return self.south
        elif anchor == 'south_west':
            return self.south_west
        elif anchor == 'west':
            return self.west
        elif anchor == 'north_west':
            return self.north_west
        else: # anchor == 'center':
            return self.center
            
class RootNode(AbstractNode):
    """ A root node must be a supporting plane, e.g. an office desk. All
    objects that are associated with the suppporting plane will be placed on
    it.
    """
    def __init__(self, object):
        super(RootNode, self).__init__(object)
        self.children = []
        self.anchors = dict()
        self.scenes = list()
        self.objects = list()
        self.positions = dict()
        self.orientations = dict()
        self.global_bboxes = dict()
        self.global_bboxes_json = dict()
        
    def add(self,node, anchor):
        """ Appends an object sub-tree to the current node
        """
        self.children.append(node)
        self.anchors[node] = anchor

    def within_root_bbox(self,object,x,y):

        min_xy_dim = \
            min(object.local_bbox.get_x_max() - object.local_bbox.get_x_min(), \
                object.local_bbox.get_y_max() - object.local_bbox.get_y_min()) \
                * OBJECT_SCALE        
        
        if (self.local_bbox.get_x_min() + min_xy_dim < x and \
            x < self.local_bbox.get_x_max() - min_xy_dim and \
            self.local_bbox.get_y_min() + min_xy_dim < y and \
            y < self.local_bbox.get_y_max()- min_xy_dim ):
            return True
        return False

    def in_collision(self,bbox):

        x_min = bbox.get_x_min()
        x_max = bbox.get_x_max()
        y_min = bbox.get_y_min()
        y_max = bbox.get_y_max()
        
        for obj in self.global_bboxes.keys():
            bbox2 = self.global_bboxes[obj]
            if (x_max >= bbox2.get_x_min() and
                x_min <= bbox2.get_x_max() and
                y_max >= bbox2.get_y_min() and
                y_min <= bbox2.get_y_max()):
                return True

        return False
        
    def place_objects(self, no):
        """ Places objects in the scene according to their specified
        relations.
        """
        for c in self.children:
            c.set_root(self)

            [x_mu, y_mu] = self.get_anchor(self.anchors[c])

            # sample as long as a valid position is found
            i = 0
            while i < MAX_NUM_OF_SAMPLES:
                x = random.gauss(x_mu, self.x_sigma)
                y = random.gauss(y_mu, self.y_sigma)
                z = self.local_bbox.get_z_max() + \
                    (c.local_bbox.get_z_max() - c.local_bbox.get_z_min()) / 2 + Z_DIST
                
                if self.within_root_bbox(c,x,y):

                    # calc pose 
                    pos =  morse.rpc('simulation','transform_to_obj_frame', self.name, str([x,y,z]))
                    orientation = list(quaternion_about_axis(c.get_yaw(), [0,0,1]))

                    # set pose
                    morse.rpc('simulation','set_object_pose',
                              c.name, str(pos), str(orientation))
                    # get global bounding box
                    json_bbox = json.loads(morse.rpc('simulation','get_object_global_bbox',c.name))
                    global_bbox = BBox(json_bbox)

                    # Second test: is object in collision with other objects?
                    if not self.in_collision(global_bbox):
                        # Hooray! Object could be placed
                        self.objects.append(c.name)
                        self.positions[c.name] = pos
                        self.orientations[c.name] = orientation
                        self.global_bboxes[c.name] = global_bbox
                        self.global_bboxes_json[c.name] = json_bbox
                        break
                i = i + 1

            if i >= MAX_NUM_OF_SAMPLES:
                raise PlacementException(c.name)
                        
            # place children
            c.place_children()


        scene = ['scene' + str(no), json.dumps({'objects' : self.objects ,
                                                'position' : self.positions,
                                                'orientation' : self.orientations,
                                                'bbox': self.global_bboxes_json})] 

        print(scene)
        self.scenes.append(scene)


class ObjectNode(AbstractNode):
    """ An object node is an element in an object tree; a hierarchical
    specification of the relations between objects with repect to its root
    element.
    """
    def __init__(self, object):
        super(ObjectNode, self).__init__(object)
        self.root = None
        self.children = []
        self.directions = dict()
        self.distances = dict()
        self.init_directions()
        self.set_yaw(0)

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root
        
    def add(self, node, direction, distance='any'):
        """ Appends a node to the current node
        """
        self.children.append(node)
        self.directions[node] = direction
        self.distances[node] = distance

    def init_directions(self):
        self.right       = 0 
        self.right_front  = math.pi / 4
        self.front         = math.pi / 2
        self.left_front   = 3 * math.pi / 4
        self.left        = math.pi;
        self.left_back  = 5 * math.pi / 4
        self.back        = 3 * math.pi / 2
        self.right_back = 7 * math.pi / 4
        
    def get_direction(self,direction):
        if direction == 'back':
            return self.back
        elif direction == 'right_back':
            return self.right_back
        elif direction == 'right':
            return self.right
        elif direction == 'right_front':
            return self.right_front
        elif direction == 'left_front':
            return self.left_front
        elif direction == 'left':
            return self.left
        elif direction == 'left_back':
            return self.left_back
        else: #elif direction == 'front':
            return self.front
        
    def calc_distance_range(self, object):
        
        [x,y,z] = self.get_root().positions[self.name]
        obj_bbox = self.get_root().global_bboxes[self.name]

        root_bbox =  BBox(json.loads(morse.rpc('simulation',
                                              'get_object_global_bbox',
                                              self.get_root().name)))

        direction = self.directions[object]

        min_xy_dim = \
            (min(object.local_bbox.get_x_max() - object.local_bbox.get_x_min(), \
                object.local_bbox.get_y_max() - object.local_bbox.get_y_min()) \
                * OBJECT_SCALE ) / 2      

        if direction == 'back':
             min_dist = x - obj_bbox.get_x_min() + min_xy_dim
             max_dist = x - root_bbox.get_x_min() - min_xy_dim

        elif direction == 'right_back':
            min_dist =  math.sqrt(2* min(x - obj_bbox.get_x_min(),
                                    obj_bbox.get_y_max() - y)**2) + min_xy_dim
            
            max_dist =  math.sqrt(2*min(x - root_bbox.get_x_min(),
                                 root_bbox.get_y_max() - y)**2)  - min_xy_dim
             
        elif direction == 'right':
            min_dist = obj_bbox.get_y_max()  - y + min_xy_dim
            max_dist = root_bbox.get_y_max() - y - min_xy_dim

        elif direction == 'right_front':
            min_dist =  math.sqrt(2*min( obj_bbox.get_x_max() - x,
                                    obj_bbox.get_y_max() - y)**2) + min_xy_dim
            
            max_dist =  math.sqrt(2*min(root_bbox.get_x_max() - x,
                                   root_bbox.get_y_max() - y)**2) - min_xy_dim

        
        elif direction == 'left_front':
            min_dist =  math.sqrt(2*min( obj_bbox.get_x_max() - x,
                                    y - obj_bbox.get_y_min())**2) + min_xy_dim
            
            max_dist =  math.sqrt(2*min(root_bbox.get_x_max() - x,
                                   y - root_bbox.get_y_min())**2) - min_xy_dim

        elif direction == 'left':
            min_dist = y - obj_bbox.get_y_min()  + min_xy_dim
            max_dist = y - root_bbox.get_y_min() - min_xy_dim
            
        elif direction == 'left_back':
            min_dist =  math.sqrt(2* min(x - obj_bbox.get_x_min(),
                                    y - obj_bbox.get_y_min() )**2) + min_xy_dim
            
            max_dist =  math.sqrt(2*min(x - root_bbox.get_x_min(),
                                   y - root_bbox.get_y_min())**2) - min_xy_dim

        else: #elif direction == 'front':
            min_dist = obj_bbox.get_x_max()  - x + min_xy_dim
            max_dist = root_bbox.get_x_max() - x - min_xy_dim

        if self.distances[object] == 'close':
            max_dist = (((max_dist + min_dist) / 2) + min_dist) /2
        
        return [min_dist,max_dist]

    def set_yaw(self,yaw):
        self.yaw = yaw

    def get_yaw(self):
        return self.yaw

    def place_children(self):

        for c in self.children:

            c.set_root(self.get_root())

            [self_x,self_y,self_z] = self.get_root().positions[self.name]

            phi_mu = self.get_direction(self.directions[c])

            root_pose = json.loads(morse.rpc('simulation','get_object_pose',
                                             self.get_root().name))

            [root_x, root_y, root_z] = root_pose[0]

            [min_dist, max_dist] = self.calc_distance_range(c)

            i = 0
            while i < MAX_NUM_OF_SAMPLES:
                
                phi = random.gauss(phi_mu, DIRECTION_SIGMA)

                if phi < 0:
                    phi = phi + 2 * math.pi
                if phi > (2 * math.pi):
                    phi = phi - (2 * math.pi)
            
                dist = random.uniform(min_dist, max_dist)

                x_rel = math.sin(phi) * dist
                y_rel = math.cos(phi) * dist  

                x =  self_x - root_x + x_rel
                y =  self_y - root_y + y_rel
                z = self.get_root().local_bbox.get_z_max() + \
                    (c.local_bbox.get_z_max() - c.local_bbox.get_z_min()) / 2 + Z_DIST 

                # First sanity check: is object position on table?
                if self.get_root().within_root_bbox(c,x,y):
            
                    pos =  morse.rpc('simulation','transform_to_obj_frame',
                                     self.get_root().name, str([x,y,z]))


                    orientation = list(quaternion_about_axis(c.get_yaw(), [0,0,1]))
                    
                    # set pose
                    morse.rpc('simulation','set_object_pose', c.name,
                              str(pos),str(orientation))

                    json_bbox = json.loads(morse.rpc('simulation','get_object_global_bbox',c.name))
                    global_bbox = BBox(json_bbox)

                    # Second test: is object in collision with other objects?
                    if not self.get_root().in_collision(global_bbox):
                        # Hooray! Object could be placed
                        self.get_root().objects.append(c.name)
                        self.get_root().positions[c.name] = pos
                        self.get_root().orientations[c.name] = orientation
                        self.get_root().global_bboxes[c.name] = global_bbox
                        self.get_root().global_bboxes_json[c.name] = json_bbox
                        break
                i = i + 1

            if i >= MAX_NUM_OF_SAMPLES:
                raise PlacementException(c.name)
            
            c.place_children()

# Main

class PlacementException(Exception):
    def __init__(self, msg):
        self.msg = msg
    
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def help_msg():
    return """
  Usage: object_placement.py [-h] <num_of_samples> 

    num_of_samples  number of samples to be generated 

    -h, --help for seeing this msg
"""

morse = None

if __name__ == "__main__":
    #sys.exit(main())

#def main(argv=None):
    argv = None
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error as msg:
            raise Usage(msg)

        if ('-h','') in opts or ('--help', '') in opts or len(args) != 1:
            raise Usage(help_msg())


        num_of_samples = int(args[0])
        if num_of_samples < 0:
            num_of_samples = 0
        i = 0
        while i < num_of_samples:
            with ignored(IOError):

                with pymorse.Morse() as morse:
                    
                    # Please note: all objects need to exist in the simulation beforehand!
                    
                    # Create a root note
                    table = RootNode('table')
                    
                    # Create several object nodes
                    pc1 = ObjectNode('pc1')
                    mon1 = ObjectNode('monitor1')
                    key1 = ObjectNode('keyboard1')
                    laptop1 = ObjectNode('laptop1')
                    cup1 = ObjectNode('cup1')
                    bottle = ObjectNode('bottle')
            
                    # Random rotations of objects
                    mon1.set_yaw(random.gauss(0.0,math.pi/16))
                    key1.set_yaw(random.gauss(0.0,math.pi/16))
                    cup1.set_yaw(random.uniform(0,2*math.pi))

        
                    # Add object nodes to the root node
                    table.add(pc1,'north_west')
                    #table.add(laptop1,'east')
                    table.add(mon1,'north')

                    # Add object nodes relative to other object nodes
                    mon1.add(key1,'front')

                    laptop_left_right = int(random.uniform(0,3))
                    if laptop_left_right == 0:
                        key1.add(laptop1, 'right')
                    else:
                        key1.add(laptop1, 'left')
                    
                    cup_left_right = int(random.uniform(0,2))
                    if cup_left_right == 0:
                        mon1.add(cup1, 'right_front')
                    else:
                        mon1.add(cup1,'left_front',)

                    bottle_left_right = int(random.uniform(0,4))
                    if bottle_left_right == 0:
                        mon1.add(bottle, 'right_front')
                    else:
                        mon1.add(bottle, 'left_front')


                    try:
                        table.place_objects(i+1)
                        i = i + 1
                    except PlacementException as e:
                        print(e.msg)
                        pass

    except Usage as err:
        print(err.msg)
        print("for help use --help")
        #return 2


    