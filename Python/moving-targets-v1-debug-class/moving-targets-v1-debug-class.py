from tkinter import *
import numpy as np
import threading
import time
from PIL import ImageTk, Image
import cv2

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
        self.root.geometry("1167x800")
        self.root.title("Moving Targets Inc.")
        self.pos_x_set = False
        self.pos_y_set = False
        self.start_time = time.time()
        self.position_x = 0
        self.position_y = 0

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
        self.text_field_x = Entry(self.root, font=("Arial", 14))
        self.text_field_y = Entry(self.root, font=("Arial", 14))
        self.text_field_button_x = Button(self.root, text="Set Position", font=("Arial", 14), command=self.send_text_field_x)
        self.text_field_button_y = Button(self.root, text="Set Position", font=("Arial", 14), command=self.send_text_field_y)

        self.title_label.grid(row=0, column=0, pady=5, columnspan=3)
        self.score_label.grid(row=2, column=2, pady=5)
        self.current_position.grid(row=9, column=0)
        self.start_button.grid(row=3, column=1, pady=5)
        self.text_field_x.grid(row=4, column=0)
        self.text_field_button_x.grid(row=5, column=0)
        self.text_field_y.grid(row=6, column=0)
        self.text_field_button_y.grid(row=7, column=0)
        self.app_frame = LabelFrame(self.root, text="TURRET-POV", padx=10, pady=10)
        self.app_frame.grid(row=4, column=2, columnspan=3, pady=15)
        self.lmain = Label(self.app_frame)

    def send_text_field_x(self):
        
        return int(self.text_field_x.get())
    
    def send_text_field_y(self):
        
        return int(self.text_field_y.get())
        


    """def send_text_field(self):
        try:
            return int(self.text_field.get())
        except ValueError:
            print("Invalid input; please enter an integer.")
"""
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
        for _ in range(10):
            new_position_x = self.send_text_field_x()
            new_position_y = self.send_text_field_y()

            if new_position_x is not None and new_position_y is not None:
                dx = new_position_x - self.position_x
                dy = new_position_y - self.position_y
                MotorControl.Amove(MotorControl.deltaA(dx, dy))
                MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                self.position_x, self.position_y = new_position_x, new_position_y
                self.current_position.config(text=f"current position: {self.position_x}, {self.position_y}")
                time.sleep(2)

    def start(self):
        self.update_clock()
        self.video_stream()

        # Regular Task Thread
        t1 = threading.Thread(target=self.regular_task)
        t1.daemon = True

        # Sensor Task Thread
        t2 = threading.Thread(target=self.update_score)
        t2.daemon = True

        t1.start()
        t2.start()
        self.start_button.grid_remove()
        

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
