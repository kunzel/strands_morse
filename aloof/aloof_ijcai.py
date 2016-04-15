#! /usr/bin/env morseexec

"""
Simple environemnt with ScitosA5.
"""

import sys
import subprocess
import os
import random

from morse.builder import *
from strands_sim.builder.robots import Scitosa5
import threading

class SimSetup():
    #from bham.builder.robots import Elevator

    def __init__(self):
        self.trigger()


    def trigger(self):
        # Set the environment
        model_file=os.path.join(os.path.dirname(os.path.abspath( __file__ )),'data/aloof.blend')
        env = Environment(model_file,fastmode=False)
        env.place_camera([10, -6.0, 15.0])
        env.aim_camera([0, 0, 0.00])

        monitor_table_top = 1.15 #higher value: higher off the table, default: 2
        object_table_top = 0.95 #higher value: higher off the table, default: 2

        #robot = Scitosa5()
        robot = Scitosa5(with_cameras = Scitosa5.WITH_OPENNI)
        robot.translate(x=10,y=-6,z=0.0)
        robot.rotate(z=0) #3.14)

        ## NORTH ROOM
        table1 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table1.properties(Object = True, Type = 'Table')
        table1.translate(x=6.75, y=-1.1, z=0.0)
        table1.rotate(0,0,math.pi)

        table2 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table2.properties(Object = True, Type = 'Table')
        table2.translate(x=8.5,y=-0.7,z=0.0)
        table2.rotate(0,0,math.pi/2)
        
        table3 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table3.properties(Object = True, Type = 'Table')
        table3.translate(x=10.75,y=-0.7,z=0.0)
        table3.rotate(0,0,math.pi/2)

        table4 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table4.properties(Object = True, Type = 'Table')
        table4.translate(x=13,y=-0.7,z=0.0)
        table4.rotate(0,0,math.pi/2)

                
        # CENTER
        # table5 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        # table5.properties(Object = True, Type = 'Table')
        # table5.translate(x=6.5,y=-6,z=0.0)

        # table6 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        # table6.properties(Object = True, Type = 'Table')
        # table6.translate(x=13.5,y=-6,z=0.0)

        ## SOUTH ROOM
        table7 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table7.properties(Object = True, Type = 'Table')
        table7.translate(x=6.75, y=-10.82913, z=0.0)
        table7.rotate(0,0,math.pi)

        table8 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table8.properties(Object = True, Type = 'Table')
        table8.translate(x=8.5,y=-11.22913,z=0.0)
        table8.rotate(0,0,math.pi/2)

        table9 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table9.properties(Object = True, Type = 'Table')
        table9.translate(x=10.75,y=-11.22913,z=0.0)
        table9.rotate(0,0,math.pi/2)
        
        table10 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table10.properties(Object = True, Type = 'Table')
        table10.translate(x=13,y=-11.22913,z=0.0)
        table10.rotate(0,0,math.pi/2)

        # SOUTH WEST ROOM
        table11 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table11.properties(Object = True, Type = 'Table')
        table11.translate(x=0.8, y=-10.82913, z=0.0)
        table11.rotate(0,0,math.pi)

        table12 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table12.properties(Object = True, Type = 'Table')
        table12.translate(x=2.5,y=-11.22913,z=0.0)
        table12.rotate(0,0,math.pi/2)

        table13 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table13.properties(Object = True, Type = 'Table')
        table13.translate(x=0.8, y=-8.55, z=0.0)
        table13.rotate(0,0,math.pi)

        table14 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table14.properties(Object = True, Type = 'Table')
        table14.translate(x=1.15,y=-6.75,z=0.0)
        table14.rotate(0,0,math.pi/2)

        # NORTH WEST ROOM
        table15 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table15.properties(Object = True, Type = 'Table')
        table15.translate(x=0.8, y=-1.1, z=0.0)
        table15.rotate(0,0,math.pi)

        table16 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table16.properties(Object = True, Type = 'Table')
        table16.translate(x=2.5,y=-0.7,z=0.0)
        table16.rotate(0,0,math.pi/2)

        table17 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table17.properties(Object = True, Type = 'Table')
        table17.translate(x=0.8, y=-3.3, z=0.0)
        table17.rotate(0,0,math.pi)

        table18 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table18.properties(Object = True, Type = 'Table')
        table18.translate(x=1.15,y=-5.3,z=0.0)
        table18.rotate(0,0,math.pi/2)

        # SOUTH EAST ROOM
        table19 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table19.properties(Object = True, Type = 'Table')
        table19.translate(x=19, y=-10.82913, z=0.0)
        table19.rotate(0,0,math.pi)

        table20 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table20.properties(Object = True, Type = 'Table')
        table20.translate(x=17.3,y=-11.22913,z=0.0)
        table20.rotate(0,0,math.pi/2)

        table21 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table21.properties(Object = True, Type = 'Table')
        table21.translate(x=19, y=-8.55, z=0.0)
        table21.rotate(0,0,math.pi)

        table22 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table22.properties(Object = True, Type = 'Table')
        table22.translate(x=18.65,y=-6.75,z=0.0)
        table22.rotate(0,0,math.pi/2)

        # NORTH EAST ROOM
        table23 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table23.properties(Object = True, Type = 'Table')
        table23.translate(x=19, y=-1.1, z=0.0)
        table23.rotate(0,0,math.pi)

        table24 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table24.properties(Object = True, Type = 'Table')
        table24.translate(x=17.3,y=-0.7,z=0.0)
        table24.rotate(0,0,math.pi/2)

        table25 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table25.properties(Object = True, Type = 'Table')
        table25.translate(x=19, y=-3.3, z=0.0)
        table25.rotate(0,0,math.pi)

        table26 = PassiveObject('environments/human_tut/tutorial_scene','Table')
        table26.properties(Object = True, Type = 'Table')
        table26.translate(x=18.65,y=-5.3,z=0.0)
        table26.rotate(0,0,math.pi/2)


        
        
        # OBJECT
        XY = [
            # NORTH CENTER
            (6.75, -1.1),
            (8.5,-0.7),
            (10.75,-0.7),
            (13,-0.7),
            # SOUTH CENTER
            (6.75,-10.82913),
            (8.5,-11.22913),
            (10.75,-11.22913),
            (13,-11.22913),
            # SOUTH WEST
            (0.8,-10.82913),
            (2.5,-11.22913),
            (0.8,-8.55),
            (1.15,-6.75),
            # NORTH WEST
            (0.8,-1.1),
            (2.5,-0.7),
            (0.8,-3.3),
            (1.15,-5.3),
            # SOUTH EAST
            (19,-10.82913),
            (17.3,-11.22913),
            (19,-8.55),
            (18.65,-6.75),
            # NORTH EAST
            (19,-1.1),
            (17.3,-0.7),
            (19,-3.3),
            (18.65,-5.3)
        ] 

        YAW = [math.pi,math.pi/2,math.pi/2,math.pi/2, # CENTER
               math.pi,math.pi/2,math.pi/2,math.pi/2,  # CENTER
               math.pi,math.pi/2,math.pi,math.pi/2,
               math.pi,math.pi/2,math.pi,math.pi/2,
               math.pi,math.pi/2,math.pi,math.pi/2,
               math.pi,math.pi/2,math.pi,math.pi/2
        ]

        
        laser = -0.5
        #table = 0 0...9
        mug =[]
        ghost =[]
        for i in range(0,len(XY)):
            print(i)
            mug.append(PassiveObject('strands_sim/robots/strands_objects.blend','cup'))
            mug[i].properties(Object = True, Type = 'cup')
            mug[i].translate(x=XY[i][0],y=XY[i][1],z=object_table_top)
            mug[i].rotate(0,0,0)

            ghost = PassiveObject('environments/human_tut/tutorial_scene','Table')
            ghost.properties(Object = True, Type = 'Table')
            ghost.translate(x=XY[i][0],y=XY[i][1],z=laser)
            ghost.rotate(0,0,YAW[i])





if __name__ == "__main__":
    s = SimSetup()
