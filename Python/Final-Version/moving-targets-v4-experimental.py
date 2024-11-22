from tkinter import *
from tkinter import simpledialog
import numpy as np
import threading
import time
from PIL import ImageTk, Image
import cv2
from TMC_2209.TMC_2209_StepperDriver import TMC_2209


class MotorControl:
    @staticmethod
    def Amove(z):
        print(z, "| A motor steps")
        steppercontroller1.move_to(z)

    @staticmethod
    def Bmove(z):
        print(z, "| B motor steps")
        steppercontroller2.move_to(z)

    @staticmethod
    def deltaA(delX, delY):
        return delX + delY

    @staticmethod
    def deltaB(delX, delY):
        return delX - delY


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
        self.next_position_array_y = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

        # Thread event for synchronization
        self.position_event = threading.Event()

        self.create_widgets()
        self.cap = cv2.VideoCapture(0)
        self.clock_counter = 0

        self.counter = 0
        self.position_counter = 0

        # Flag for exiting some game modes
        self.running = True

        self.entered_username_flag = False
        self.username_saved_flag = False

        self.t1 = None
        self.t2 = None
        self.t3 = None

    def create_widgets(self):
        self.reset_flags()
        self.counter = 0

        self.title_label = Label(
            self.root, 
            text="Moving Targets inc.", 
            font=("Comic sans", 72), 
            fg="black", 
            bg="red4"
        )
        self.title_label.grid(row=0, column=0, pady=5, columnspan=4)

        self.score_label = Label(
            self.root, 
            fg="black", 
            bg="red4", 
            text="", 
            font=("Comic sans", 48)
        )
        self.score_label.grid(row=1, column=2, pady=5, sticky=NW)

        self.current_position = Label(
            self.root, 
            fg="black", 
            bg="red4", 
            text="", 
            font=("Comic sans", 48)
        )
        self.current_position.grid(row=1, column=0, sticky=NW)

        self.clock_label = Label(
            self.root, 
            fg="black", 
            bg="red4", 
            font=("Comic sans", 48)
        )
        self.clock_label.grid(row=1, column=3, sticky=N)

        self.stop_button = Button(
            self.root, 
            fg="black", 
            bg="red4", 
            activebackground="green",
            text="Quit game", 
            font=("Comic sans", 32), 
            command=lambda: [self.game_finished_show_main_menu()]
        )
        self.stop_button.grid(row=4, column=0, sticky=NW)

        self.high_score_button = Button(
            self.root, 
            fg="black", 
            bg="red4", 
            text="High Score", 
            font=("Comic sans", 32), 
            command=self.show_high_score
        )
        self.high_score_button.grid(row=3, column=2, pady=5, sticky=NSEW)

        self.normal_start_button = Button(
            self.root, 
            fg="black", 
            bg="red4", 
            activebackground="green",
            text="Normal", 
            font=("Comic sans", 32), 
            command=lambda: [self.set_normal_flag(), self.normal_start()]
        )
        self.normal_start_button.grid(row=3, column=1, pady=5, sticky=NSEW)

        self.random_start_button = Button(
            self.root, 
            fg="black", 
            bg="red4", 
            activebackground="green",
            text="Random", 
            font=("Comic sans", 32), 
            command=lambda: [self.set_random_flag(), self.random_start()]
        )
        self.random_start_button.grid(row=4, column=1, pady=5, sticky=NSEW)

        self.text_box_start_button = Button(
            self.root, 
            fg="black", 
            bg="red4", 
            activebackground="green",
            text="Text Box", 
            font=("Comic sans", 32), 
            command=lambda: [self.set_textbox_flag(), self.text_box_start()]
        )
        self.text_box_start_button.grid(row=5, column=1, pady=5, sticky=NSEW)

        self.text_field = Entry(
            self.root, 
            fg="black", 
            bg="red4", 
            font=("Arial", 14)
        )
        self.text_field.grid(row=2, column=0, sticky=NW)

        self.text_field_button = Button(
            self.root, 
            fg="black", 
            bg="red4", 
            text="Set Position", 
            font=("Arial", 14), 
            command=self.send_text_field
        )
        self.text_field_button.grid(row=3, column=0, sticky=NW)

        self.app_frame = LabelFrame(
            self.root, 
            fg="black", 
            bg="red4", 
            text="TURRET-POV", 
            padx=10, 
            pady=10
        )
        self.app_frame.grid(row=0, column=5, rowspan=7, columnspan=7, pady=15, sticky=SE)

        self.lmain = Label(
            self.app_frame, 
            fg="black", 
            bg="red4"
        )
        self.lmain.grid(row=1, column=5, sticky=NSEW)

    # The remaining logic remains similar, focusing on utilizing `TMC_2209` for motor control.

if __name__ == "__main__":
    root = Tk()

    app = App(root)
    steppercontroller1 = TMC_2209(21, 16, 20, serialport="/dev/ttyAMA0", driver_address=0)
    steppercontroller2 = TMC_2209(25, 23, 24, serialport="/dev/ttyAMA1", driver_address=0)
    root.mainloop()
