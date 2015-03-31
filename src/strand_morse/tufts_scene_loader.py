#!/usr/bin/env python3
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
import qsr
import os
import time

from contextlib import contextmanager

@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


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

            
def remove_objects(objs):
    for o in objs:
        morse.rpc('simulation','set_object_pose', o, str([0,0,0]),str([1,0,0,0]))

def quaternion_multiply(q1, q2):
    return [q1[0]*q2[0] - q1[1]*q2[1] - q1[2]*q2[2] - q1[3]*q2[3],
            q1[0]*q2[1] + q1[1]*q2[0] + q1[2]*q2[3] - q1[3]*q2[2],
            q1[0]*q2[2] - q1[1]*q2[3] + q1[2]*q2[0] + q1[3]*q2[1],
            q1[0]*q2[3] + q1[1]*q2[2] - q1[2]*q2[1] + q1[3]*q2[0]] 

def load_pointer(scn, obj):
    
    obj_pose = json.loads(morse.rpc('simulation','get_object_pose', obj))
    [x, y, z] = obj_pose[0]
    obj_rot = obj_pose[1]

    json_bbox = json.loads(morse.rpc('simulation','get_object_global_bbox',obj))
    global_bbox = BBox(json_bbox)
    max_z = global_bbox.get_z_max()

    json_bbox = json.loads(morse.rpc('simulation','get_object_bbox','pointer'))
    local_bbox = BBox(json_bbox)
    pointer_offset = (local_bbox.get_z_max() - local_bbox.get_z_min()) / 2  

    new_pos = [x,y, max_z + pointer_offset]
    
    morse.rpc('simulation','set_object_pose','pointer', str(new_pos), str(obj_rot))

    
        
def load_scene(scn, target, offset=0):

    target_pose = json.loads(morse.rpc('simulation','get_object_pose',
                                       target))
    target_pos = target_pose[0]
    target_ori =  target_pose[1]

    
    table_pos = scn['position']['table']
    #table_ori = scn['orientation']['table'] 

    for o in scn['objects']:

        obj_pos = scn['position'][o]

        x = float(obj_pos[0]) - float(table_pos[0])
        y = float(obj_pos[1]) - float(table_pos[1])
        z = float(obj_pos[2]) - float(table_pos[2])

        pos =  morse.rpc('simulation','transform_to_obj_frame', target, str([x,y,z]))

        orientation = scn['orientation'][o]

        new_orientation = quaternion_multiply(target_ori,orientation)

        # if (o == 'monitor'):
        #     cmd = 'rosparam set /qsr_landmark/id%i/pose "[%f, %f, %f, %f, %f, %f, %f]"' % (offset+1, float(pos[0] + 1.35), float(pos[1]) - 0.65, float(pos[2]), float(new_orientation[0]), float(new_orientation[1]), float(new_orientation[2]), float(new_orientation[3]))
        #     print('Run:', cmd)
        #     os.system(cmd)

        
        # set pose
        morse.rpc('simulation','set_object_pose',obj_name(o,offset), str(pos), str(new_orientation))


    return scn['objects']

def delete_scene(scn,offset):

    objs = list()
    for o in scn['objects']:
        objs.append(obj_name(o,offset))

    objs.append('pointer')
    remove_objects(objs)

    

def obj_name(obj, offset):

    SET_SIZE = 0
    
    part = obj.split('.')

    if len(part)==1:
        postfix = SET_SIZE * offset
        if postfix == 0:
            return part[0]
        
    else:
        postfix = SET_SIZE * offset + int(part[1])

    if (postfix < 10):
        return part[0] + '.00' + str(postfix) 
    else:
        return part[0] + '.0' + str(postfix)
    
            
    
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def help_msg():
    return """
  Usage: tufts_scene_loader.py [-h] <scences_file> <output_dir> 

    scenes_file        file that contains all scenes
    output_dir         directory for screenshots 

    -h, --help for seeing this msg
"""

morse = None

if __name__ == "__main__":
    argv = None
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error as msg:
            raise Usage(msg)

        if ('-h','') in opts or ('--help', '') in opts:
            raise Usage(help_msg())

        output_dir = args[1]
        with open(args[0]) as scn_file:    
            scenes = json.load(scn_file)

            with ignored(IOError):
                    
                with pymorse.Morse() as morse:
                    vis = morse.rpc('simulation','set_object_visibility', 'Compass',False,True)
                    turk_id = 0
                    turk_meta = dict()
                    for i in range(0, len(scenes),10):

                        scn = scenes[i][1]
                        load_scene(scn, 'table', 0)

                        ### take screenshot
                        cmd = 'scrot -u -d 1 %s/scene_%i.png' % (output_dir, i)
                        print('Taking screenshot:', cmd)
                        os.system(cmd)
                        time.sleep(1)

                        
                        obj_pixel_coords = json.loads(morse.rpc('simulation','get_object_pixel_coords', 10))
                        for k in obj_pixel_coords:
                            print(k, obj_pixel_coords[k])
                        
                        for o in scn['objects']:
                            if not scn['type'][o] in ['Cup','Book','Bottle']:
                                continue

                            load_pointer(scn,o)
                            turk_id += 1
                            turk_meta[turk_id] = {"scene_id" : i, "object" : o, "pixel": obj_pixel_coords}
                        
                            #coords = morse.rpc('simulation','get_screen_pos', o)
                            #print(o, coords)

                        # take screenshot
                        #     cmd = 'scrot -u -d 1 %s/%i.png' % (output_dir, turk_id)
                        #     print('Taking screenshot:', cmd)
                        #     os.system(cmd)
                        #     time.sleep(1)
                        print("Press 'Enter' to load the next scene")
                        input()
                        
                        delete_scene(scn,int(0))
                    out = "%s/turk_meta.json" % (output_dir)
                    with open(out, "w") as outfile:
                        outfile.write(json.dumps(turk_meta, outfile, indent=2))
                            
                            
    except Usage as err:
        print(err.msg)
        print("for help use --help")
        #return 2

