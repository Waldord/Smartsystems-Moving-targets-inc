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
        self.root.title("Moving Targets Inc.")
        self.start_time = time.time()
        
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
        self.title_label = Label(self.root, text="Moving Targets inc.", font=("Comic sans", 100), fg="white", bg="grey")
        self.score_label = Label(self.root, text="", font=("Comic sans", 60))
        self.current_position = Label(self.root, text="", font=("Comic sans", 60))
        self.clock_label = Label(self.root, font=("Comic sans", 80), fg="white", bg="black")
        self.start_button = Button(self.root, text="START", font=("Comic sans", 48), command=self.start)
        
        # Single text field and button for both X and Y
        self.text_field = Entry(self.root, font=("Arial", 14))
        self.text_field_button = Button(self.root, text="Set Position", font=("Arial", 14), command=self.send_text_field)

        self.title_label.grid(row=0, column=0, pady=5, columnspan=5)
        # Column 0
        self.current_position.grid(row=1, column=0)
        self.text_field.grid(row=2, column=0)
        self.text_field_button.grid(row=3, column=0)

        # Column 1
        
        self.start_button.grid(row=3, column=1, pady=5)
        self.app_frame = LabelFrame(self.root, text="TURRET-POV", padx=10, pady=10)
        self.app_frame.grid(row=4, column=4, columnspan=3, pady=15)
        self.lmain = Label(self.app_frame)
        self.lmain.grid(row=4, column=4)

        # Column 2
        self.score_label.grid(row=1, column=1, pady=5)
        self.clock_label.grid(row=1, column=3)
        # Column 3
        




    def send_text_field(self):
        value = self.text_field.get()
        try:
            # Split the input by space and attempt to convert both parts to integers
            x, y = map(int, value.split())
            self.previous_position_x = self.position_x
            self.previous_position_y = self.position_y
            self.new_position_x = x
            self.new_position_y = y
            self.position_event.set()  # Signal the regular_task thread to continue
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

    def regular_task(self):
        while True:  # Keep running unless you have a stopping condition
            # Wait for the next X and Y positions
            #new_position_x, new_position_y = self.get_next_position()

            # Grabs data from new_position_x & y arrays
            self.new_position_x = self.next_position_array_x[self.counter]
            self.new_position_y = self.next_position_array_y[self.counter]

            dx = self.new_position_x - self.position_x
            dy = self.new_position_y - self.position_y

            if dx != 0 or dy != 0:  # Only move if there's a change
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

            time.sleep(2)

    def start(self):
        self.update_clock()
        self.video_stream()

        # Start threads for regular task and sensor task
        t1 = threading.Thread(target=self.regular_task, daemon=True)
        t2 = threading.Thread(target=self.update_score, daemon=True)

        t1.start()
        t2.start()
        self.start_button.grid_remove()


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
