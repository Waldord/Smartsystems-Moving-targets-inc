# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 12:30:42 2024

It works!

@author: The sweedish Sleggosaurus rex, da ørkenen var øde pushet sleggosaur til hub og gjorde liv i systemet
"""
import numpy as np
import array as arr
import time as time
import matplotlib.pyplot as plt
import subprocess
import threading

#skal være en funskjon som aktiverer porten til motor A
def Amove(z):
    print (z ,"| A motor steps")

#skal være en funskjon som aktiverer porten til motor B
def Bmove(z):
    print (z ,"| B motor steps")

#matte greiær
def deltaA(delX, delY):
    return delX + delY

def deltaB(delX, delY):
    return delX - delY

x = 5

#Printer all type informasjon
def printall(x,y,nx,ny,xd,yd):
    print("")
    print("---------------------")
    print("")
    print("current position: ", x, " ", y)
    print("")
    print("new position: ", nx, " ", ny)
    print("")
    print("position differential: ", xd, " ", yd)
    print("")
    


def sensor():
    #Skal lese inn fra trykksensor
    x = np.random.randint(0,12)
    time.sleep(0.1)
    if (x == 1):
        return True
    else:
        return False





def poengfunction():
    Score = 0
    timeoutstart = time.time()
    while(time.time() < timeoutstart + 2):

        if (sensor() == True):
            Score = Score+2

    
            print(Score)
            time.sleep(0.2)       
            break
        time.sleep(0.1)



def start():
    #lager variabler for start/current posisjon av x og y
    position_y = 0
    position_x = 0

    #lager variabel for den posisjonen den skal til
    new_position_x = 0
    new_position_y = 0

    #variabel for antall steps motoren skal ta
    motorAmovement = 0
    motorBmovement = 0
    
    #lager variablel for forskjellen på ny posisjon og nåværende posisjon
    position_x_diff = new_position_x - position_x
    position_y_diff = new_position_y - position_y
    
    for i in range(x):
            #lager tilfeldig kordinat i felt på 40x40
            new_position_x = np.random.randint(0,40)
            new_position_y = np.random.randint(0,40)

            #oppdaterer position_diff og printer info
            position_x_diff = new_position_x - position_x
            position_y_diff = new_position_y - position_y
            printall(position_x , position_y, new_position_x, new_position_y, position_x_diff, position_y_diff)

            #bruker matte greiær for å mattifisere til hvor mange steps motoren må ta
            motorAmovement = deltaA(position_x_diff, position_y_diff)
            motorBmovement = deltaB(position_x_diff, position_y_diff)
    
            Amove(motorAmovement)
            Bmove(motorBmovement)
            print ("")
            print ("-----------------")
            print ("")

            #setter den posisjonen den skulle til, til nåværende posisjon
            position_x = new_position_x
            position_y = new_position_y
        
            time.sleep(0.5)
            poengfunction()
            i += i
start()





"""
while (True):
    print (time.time())
    time.sleep(1)
"""


  
"""
print (timeoutstart)
time.sleep(2)      
print (timeoutstart)   
"""



"""
def lw():    
 
    t1 = threading.Thread(target = start())
    t2 = threading.Thread(target = poengfunction())
   
    t1.start()
    t2.start()
    for p in range(10):
        
        t1.join()
        t2.join()
    
lw()

"""
