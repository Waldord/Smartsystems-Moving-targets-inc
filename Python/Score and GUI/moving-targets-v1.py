# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 12:01:47 2024

@author: Helten fra larvik som tok på seg monstere av å skaffe threading i en U-kode, for å gjøre det om til en I-kode
"""
from tkinter import *
import numpy as np
import threading
import time
from PIL import ImageTk, Image
import cv2

start_time = time.time()




def Amove(z):
    print (z ,"| A motor steps")
    
def Bmove(z):
    print (z ,"| B motor steps")

def deltaA(delX, delY):
    return delX + delY

def deltaB(delX, delY):
    return delX - delY

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
    x = np.random.randint(0,2)
    time.sleep(0.1)
    if (x == 1):
        return True
    else:
        return False

def regular_task():
    position_y = 0
    position_x = 0
    
    new_position_x = 0
    new_position_y = 0
    
    motorAmovement = 0
    motorBmovement = 0
    
    
    position_x_diff = new_position_x - position_x
    position_y_diff = new_position_y - position_y
    
    for i in range(10):
            
        new_position_x = np.random.randint(0,40)
        new_position_y = np.random.randint(0,40)
        position_x_diff = new_position_x - position_x
        position_y_diff = new_position_y - position_y
        printall(position_x , position_y, new_position_x, new_position_y, position_x_diff, position_y_diff)
        
        motorAmovement = deltaA(position_x_diff, position_y_diff)
        motorBmovement = deltaB(position_x_diff, position_y_diff)
            
        Amove(motorAmovement)
        Bmove(motorBmovement)
        print ("")
        print ("-----------------")
        print ("")
                
        position_x = new_position_x
        position_y = new_position_y
        current_position.config(text="current position:"+str(position_x)+", "+str(position_y))
        time.sleep(2)


def daemon_task():
    while True:
        if (time.time() > start_time + 70): # her kan man bestemme når den skal være av å på
            print("daemontask finished")    
            break
        if (sensor() == True):
            daemon_task.counter += 1
            score_label.config(text=str(daemon_task.counter) + " pts")
            if (daemon_task.counter < 10):    
                empty.config(text="        ")
            else:
                empty.config(text="          ")
        time.sleep(1)

daemon_task.counter = 0           

def clock():
    minute = 0
    clock.counter -= 1
    if (clock.counter < 0):
        clock.counter = 0
    if (clock.counter < 10):
        clock_label.config(text=str(minute) + ":0" + str(clock.counter))
    else:    
        clock_label.config(text=str(minute) + ":" + str(clock.counter))
    clock_label.after(1000, clock)

clock.counter = 60

def send_text_field():
    value_to_send = text_field.get()
    try:
        target_position = int(value_to_send)
        text.set(value_to_send)
        motorA.move_to(target_position)
    except ValueError:
        print("Invalid input; please enter an integer.")

def current_position_x():
    return position_x

def current_position_y():
    return position_y
    

cap = cv2.VideoCapture(0)

def video_stream():
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(1, video_stream) 
        
    
#en funksjon til å starte alle funksjoner som må startes når spille skal begynne
def start():
    clock()
    t1 = threading.Thread(target=regular_task)
    t1.deamon = True
    # Daemon thread
    t2 = threading.Thread(target=daemon_task)
    t2.daemon = True

    t2.start()
    t1.start()
    
    start_Button.grid_remove()
    clock_label.grid(row=0, column=0)
    app.grid(row=4, column=0, columnspan=3, pady=15)
    lmain.grid()
    video_stream()
    #t1.join()
    return        

root = Tk()
root.geometry("1167x800")
root.title("Moving Targets Inc.")

frame = LabelFrame(root, text="TIMER", padx=10, pady=10)

title_label = Label(root, text="Moving Targets inc.", font=("Comic sans", 100), fg="white", bg="grey")
score_label = Label(root, text="", font=("Comic sans", 60))
current_position = Label(root, text="", font=("Comic sans", 60))
clock_label = Label(frame, text="", font=("Comic sans", 80), fg="white", bg="black")
start_Button = Button(root, text="START", font=("Comic sans", 48), padx=10, pady=10, command=start)

text_field = Entry(root, font=("Arial", 14))
text_field_button = Button(root, text="Set Position", font=("Arial", 14), command=send_text_field)

app = LabelFrame(root, text="TURRET-POV",padx=10,pady=10)

lmain = Label(app)


empty = Label(root, text="", font=("Comic sans", 60))

title_label.grid(row=0, column=0, pady=5, columnspan=3)
score_label.grid(row=2, column=2, pady=5)
empty.grid(row=2, column=0, pady=5)
frame.grid(row=2, column=1, pady=5)
start_Button.grid(row=3, column=1, pady=5)
text_field.grid(row=4, column=0)
text_field_button.grid(row=5, column=0)
current_position.grid(row=6, column=0)

root.mainloop()


"""
KILDER
https://docs.python.org/3/library/threading.html
https://www.geeksforgeeks.org/regular-threads-vs-daemon-threads-in-python/?ref=oin_asr1
https://www.geeksforgeeks.org/python-daemon-threads/
"""
