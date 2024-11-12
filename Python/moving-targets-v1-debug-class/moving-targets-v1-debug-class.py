from tkinter import *
import numpy as np
import threading
import time
from PIL import ImageTk, Image
import cv2
import sys

class MotorControl:
    @staticmethod
    def Amove(z):
        print(z, "| A motor steps")

    @staticmethod
    def Bmove(z):
        print(z, "| B motor steps")

    @staticmethod
    def deltaA(delX, delY):
        return delX + delY

    @staticmethod
    def deltaB(delX, delY):
        return delX - delY


class Sensor:
    @staticmethod
    def read():
        x = np.random.randint(0, 2)
        time.sleep(0.1)
        return x == 1


class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1500x1000")
        self.root.configure(bg="Gray30")
        self.root.title("Moving Targets Inc.")
        self.start_time = time.time()

        
        # Gamemode flags
        self.normal_gameflag = False
        self.random_gameflag = False
        self.text_box_gameflag = False

        # Position variables
        self.position_x = 0
        self.position_y = 0

        # Stepper motor next position
        self.new_position_x = 0
        self.new_position_y = 0

        # Previous position variables
        self.previous_position_x = 0
        self.previous_position_y = 0

        # Counter for position array
        self.next_position_array_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.next_position_array_y = [2, 4, 6 ,8 ,10 ,12, 14, 16, 18, 20]

        # Thread event for synchronization
        self.position_event = threading.Event()
        
        self.create_widgets()
        self.cap = cv2.VideoCapture(0)
        self.counter = 0
        self.clock_counter = 60

    def create_widgets(self):
        self.title_label = Label(self.root, text="Moving Targets inc.", font=("Comic sans", 72), fg="black", bg="red4")
        self.score_label = Label(self.root, fg="black", bg="red4" ,text="", font=("Comic sans", 48))
        self.current_position = Label(self.root, fg="black", bg="red4" , text="", font=("Comic sans", 48))
        self.clock_label = Label(self.root, fg="black", bg="red4" ,font=("Comic sans", 48))

        # Buttons that choose game mode
        self.normal_start_button = Button(self.root, fg="black", bg="red4" ,activebackground="green",text="Normal", font=("Comic sans", 32), command=lambda:[self.set_normal_flag(), self.normal_start()])
        self.random_start_button = Button(self.root, fg="black", bg="red4" ,activebackground="green",text="Random", font=("Comic sans", 32), command=lambda:[self.set_random_flag(), self.random_start()])
        self.text_box_start_button = Button(self.root, fg="black", bg="red4" ,activebackground="green",text="Text Box", font=("Comic sans", 32), command=lambda:[self.set_textbox_flag(), self.text_box_start()])


        # Single text field and button for both X and Y
        self.text_field = Entry(self.root, fg="black", bg="red4", font=("Arial", 14))
        self.text_field_button = Button(self.root, fg="black", bg="red4" ,text="Set Position", font=("Arial", 14), command=self.send_text_field)

        self.title_label.grid(row=0, column=0, pady=5, columnspan=4)
        # Column 0
        self.current_position.grid(row=1, column=0, sticky=NW)
        self.text_field.grid(row=2, column=0, sticky=NW)
        self.text_field_button.grid(row=3, column=0, sticky=NW)

        # Column 1
        self.normal_start_button.grid(row=3, column=1, pady=5, sticky=NSEW)
        self.random_start_button.grid(row=4, column=1, pady=5, sticky=NSEW)
        self.text_box_start_button.grid(row=5, column=1, pady=5, sticky=NSEW)
        

        # Column 2
        self.score_label.grid(row=1, column=2, pady=5, sticky=NW)
        self.clock_label.grid(row=1, column=3, sticky=N)
        # Column 3
        
        # Column 4
        self.app_frame = LabelFrame(self.root, fg="black", bg="red4", text="TURRET-POV", padx=10, pady=10)
        self.app_frame.grid(row=0, column=5, rowspan=7,columnspan=7, pady=15, sticky=SE)
        self.lmain = Label(self.app_frame, fg="black", bg="red4" ,)
        self.lmain.grid(row=1, column=5, sticky=NSEW)    

    def set_normal_flag(self):
        print("normal game selected")
        self.normal_gameflag = True


    def set_random_flag(self):
        print("random game selected")
        self.random_gameflag = True
        

    def set_textbox_flag(self):
        print("text_box game selected")
        self.text_box_gameflag = True

    def send_text_field(self):
        value = self.text_field.get()
        try:
            # Split the input by space and attempt to convert both parts to integers
            x, y = map(int, value.split())
            self.previous_position_x = self.position_x
            self.previous_position_y = self.position_y
            self.new_position_x = x
            self.new_position_y = y
            self.position_event.set()  # Signal the normal_game_mode thread to continue
            self.text_field.delete(0, END)  # Clear the text box after reading the input
        except ValueError:
            print("Invalid input; please enter two integers separated by a space.")

    def get_next_position(self):
        # Wait for user to click the button and set the next position
        self.position_event.wait()
        self.position_event.clear()  # Clear the event for the next wait
        return self.position_x, self.position_y

    def update_clock(self):
        if self.clock_counter > 0:
            self.clock_counter -= 1
        minute, second = divmod(self.clock_counter, 60)
        self.clock_label.config(text=f"{minute}:{second:02}")
        self.clock_label.after(1000, self.update_clock)

    def update_score(self):
        if Sensor.read():
            self.counter += 1
            self.score_label.config(text=f"{self.counter} pts")

    def video_stream(self):
        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(10, self.video_stream)

    def normal_game_mode(self):
        self.next_update_interval = 2

        while True:  # Keep running unless you have a stopping condition
            # Wait for the next X and Y positions
            #new_position_x, new_position_y = self.get_next_position()

            self.next_update = time.time() + self.next_update_interval
            # Grabs data from new_position_x & y arrays
            self.new_position_x = self.next_position_array_x[self.counter]
            self.new_position_y = self.next_position_array_y[self.counter]

            dx = self.new_position_x - self.position_x
            dy = self.new_position_y - self.position_y

            if dx != 0 or dy != 0:  # Only move if dx or dy have changed
                MotorControl.Amove(MotorControl.deltaA(dx, dy))
                MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                self.position_x, self.position_y = self.new_position_x, self.new_position_y
                self.current_position.config(
                    text=f"current position: {self.position_x}, {self.position_y}", 
                    font=("Arial", 14)
                )
                self.counter = (self.counter+1)%len(self.next_position_array_x)
            else:
                print("No position change, skipping motor movement.")
            time.sleep(self.next_update_interval)
                


    def random_game_mode(self):
        self.next_update_interval = 2
        while True:  
            self.next_update = time.time()+self.next_update_interval
            # Generate random numbers between 0, 40 for x and y positions
            self.new_position_x = np.random.randint(0,40)
            self.new_position_y = np.random.randint(0,40)                
            dx = self.new_position_x - self.position_x
            dy = self.new_position_y - self.position_y

            if dx != 0 or dy != 0:  # Only move if dx or dy have changed
                MotorControl.Amove(MotorControl.deltaA(dx, dy))
                MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                self.position_x, self.position_y = self.new_position_x, self.new_position_y
                self.current_position.config(
                text=f"current position: {self.position_x}, {self.position_y}", 
                     font=("Arial", 14)
                )
            else:
                print("No position change, skipping motor movement.")
            time.sleep(self.next_update_interval)



    def text_box_game_mode(self):
        self.next_update_interval = 2
        while True:
            # Her bør det legges inn WAIT signal
            dx = self.new_position_x - self.position_x
            dy = self.new_position_y - self.position_y
            if dx != 0 or dy != 0:  # Only move if dx or dy have changed
                MotorControl.Amove(MotorControl.deltaA(dx, dy))
                MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                self.position_x, self.position_y = self.new_position_x, self.new_position_y
                self.current_position.config(
                    text=f"current position: {self.position_x}, {self.position_y}", 
                    font=("Arial", 14)
                )
            else:
                print("No position change, skipping motor movement.")
            time.sleep(self.next_update_interval)



    def grid_remover(self):
        self.normal_start_button.grid_remove()
        self.random_start_button.grid_remove()
        self.text_box_start_button.grid_remove()

        print("start buttons removed")
        if self.normal_gameflag == True or self.random_gameflag == True:
            self.text_field.grid_remove()
            self.text_field_button.grid_remove()    
            print("text field and button removed")


        

    def normal_start(self):
        self.update_clock()
        self.video_stream()
        self.grid_remover()
        #Removes start menu buttons

        # Start threads for regular task and sensor task
        t1 = threading.Thread(target=self.normal_game_mode, daemon=True)
        t2 = threading.Thread(target=self.update_score, daemon=True)

        t1.start()
        t2.start()
        

    def random_start(self):
        self.update_clock()
        self.video_stream()
        self.grid_remover()

        # Start threads for regular task and sensor task
        t1 = threading.Thread(target=self.random_game_mode, daemon=True)
        t2 = threading.Thread(target=self.update_score, daemon=True)

        t1.start()
        t2.start()
        

    def text_box_start(self):
        #self.update_clock()
        self.video_stream()
        self.grid_remover()

        # Start threads for regular task and sensor task
        t1 = threading.Thread(target=self.text_box_game_mode, daemon=True)
        t2 = threading.Thread(target=self.update_score, daemon=True)

        t1.start()
        t2.start()

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
