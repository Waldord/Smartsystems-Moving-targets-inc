
from tkinter import *
from tkinter import simpledialog
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
        x = np.random.randint(0, 3)
        time.sleep(0.1)
        return x == 1


class App:
    def __init__(self, root):
        # Initialization of root window
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
        self.next_position_array_y = [2, 4, 6 ,8 ,10 ,12, 14, 16, 18, 20, 12, 14, 16 ,18 ,110 ,112, 114, 116, 118, 120]

        # Thread event for synchronization
        self.position_event = threading.Event()
        
        self.create_widgets()
        self.cap = cv2.VideoCapture(0)
        self.clock_counter = 60

        self.counter = 0
        self.position_counter = 0

        # Flag for exiting some game modes
        self.running = True

        self.entered_username_flag = False
        self.username_saved_flag = False

        self.t1 = threading.Thread
        self.t2 = threading.Thread



    def create_widgets(self):
        # Title
        self.title_label = Label(
            self.root, 
            text="Moving Targets inc.", 
            font=("Comic sans", 72), 
            fg="black", 
            bg="red4")
        self.title_label.grid(row=0, column=0, pady=5, columnspan=4) 

        # Player score
        self.score_label = Label(
            self.root, 
            fg="black", 
            bg="red4" ,
            text="", 
            font=("Comic sans", 48))
        self.score_label.grid(row=1, column=2, pady=5, sticky=NW)

        # Motor stepper current position
        self.current_position = Label(
            self.root, 
            fg="black", 
            bg="red4" , 
            text="", 
            font=("Comic sans", 48))
        self.current_position.grid(row=1, column=0, sticky=NW)      

        # Clock label
        self.clock_label = Label(
            self.root, 
            fg="black", 
            bg="red4" ,
            font=("Comic sans", 48))
        self.clock_label.grid(row=1, column=3, sticky=N)


        # Button for high score list
        self.high_score_button = Button(
            self.root, 
            fg="black", 
            bg="red4", 
            text="High Score", 
            font=("Comic sans", 32), 
            command=self.show_high_score)
        self.high_score_button.grid(row=3, column=2, pady=5, sticky=NSEW)

        # Normal game mode
        self.normal_start_button = Button(
            self.root, 
            fg="black", 
            bg="red4" ,
            activebackground="green",
            text="Normal", 
            font=("Comic sans", 32), 
            command=lambda:[self.set_normal_flag(), self.normal_start()])
        self.normal_start_button.grid(row=3, column=1, pady=5, sticky=NSEW)
        
        # Random game mode
        self.random_start_button = Button(
            self.root, 
            fg="black", 
            bg="red4" ,
            activebackground="green",
            text="Random", 
            font=("Comic sans", 32), 
            command=lambda:[self.set_random_flag(), self.random_start()])
        self.random_start_button.grid(row=4, column=1, pady=5, sticky=NSEW)
        
        # Text field game mode (debug)
        self.text_box_start_button = Button(
            self.root, 
            fg="black", 
            bg="red4" ,
            activebackground="green",
            text="Text Box", 
            font=("Comic sans", 32), 
            command=lambda:[self.set_textbox_flag(), self.text_box_start()])
        self.text_box_start_button.grid(row=5, column=1, pady=5, sticky=NSEW)
        


        #Stop button for text mode        
        self.stop_button = Button(
            self.root, 
            fg="black", 
            bg="red4" ,
            activebackground="green",
            text="Quit game", 
            font=("Comic sans", 32), 
            command=lambda:[self.stop()])
        

        # Single text field for both X and Y position, enter like "342 555"
        self.text_field = Entry(
            self.root, 
            fg="black", 
            bg="red4", 
            font=("Arial", 14))
        self.text_field.grid(row=2, column=0, sticky=NW)
        
        # text field button, which sends data entered in text field to motor controller
        self.text_field_button = Button(
            self.root, 
            fg="black", 
            bg="red4" ,
            text="Set Position", 
            font=("Arial", 14), 
            command=self.send_text_field)
        self.text_field_button.grid(row=3, column=0, sticky=NW)


        # Camera frame text
        self.app_frame = LabelFrame(
            self.root, 
            fg="black", 
            bg="red4", 
            text="TURRET-POV", 
            padx=10, 
            pady=10)
        self.app_frame.grid(row=0, column=5, rowspan=7,columnspan=7, pady=15, sticky=SE)
        
        # Camera frame
        self.lmain = Label(
            self.app_frame, 
            fg="black", 
            bg="red4" ,)
        self.lmain.grid(row=1, column=5, sticky=NSEW)    

    def show_main_menu(self):
        # Clear all widgets currently displayed
        for widget in self.root.winfo_children():
            widget.destroy()

        # Recreate the main menu
        self.create_widgets()
        print("Returned to main menu")

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
        print("before wait")
        self.position_event.wait()
        print("after wait, before clear")
        self.position_event.clear()  # Clear the event for the next wait
        print("after clear")
        return self.new_position_x, self.new_position_y


    def show_high_score(self):
        # Create high score window
        high_score_window = Toplevel(self.root)
        high_score_window.title("Highscore")
        high_score_window.geometry("400x600")
        high_score_window.configure(bg="Gray30")

        title =Label(high_score_window, text="Highscore", font=("Comic sans", 32), fg="black", bg="Red4" )
        scores = self.load_highscore()

        for idx, (name, score) in enumerate(scores, start=1):
            score_label = Label(high_score_window, text=f"{idx}. {name} - {score} pts", font=("Arial", 18), bg="Gray30", fg="white")
            score_label.pack(pady=5)

    def load_highscore(self):
        try:
            with open("Highscore.txt", "r") as file:
                scores = [line.strip().split(",") for line in file.readlines()]
                return sorted([(name, int(score)) for name, score in scores], key=lambda x: x[1], reverse=True)
        except FileNotFoundError:
            return []
        
    def save_high_scores(self, name, score):
        scores = self.load_highscore()
        scores.append((name, score))
        scores = sorted(scores, key=lambda x: x[1], reverse = True)[:10] # [:10] is the amount of scores to be kept
        with open("Highscore.txt", "w") as file:
            for name, score in scores:
                file.write(f"{name},{score}\n")

    def update_clock(self):
        if self.clock_counter > 0:
            self.clock_counter -= 1
        minute, second = divmod(self.clock_counter, 60)
        self.clock_label.config(text=f"{minute}:{second:02}")
        self.clock_label.after(1000, self.update_clock)
        
        if self.clock_counter == 0:
            self.game_finished()

    def update_score(self):
        while self.clock_counter > 0:
            if Sensor.read():
                self.counter += 1
                self.score_label.config(text=f"{self.counter} pts")
                time.sleep(1) 
                #tid mellom hver gang du kan få poeng, så du ikke kan spamme. LOCKOUT funksjon
                #funker dårlig med random, men kommer nok til å funke med sensor

    def video_stream(self):
        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(10, self.video_stream)
    
    #Terminates tk window
    def stop(self):
        self.root.destroy()
        
    #deployes the stop button
    def stop_button_deploy(self):
        self.stop_button.grid(row=4, column=0, sticky=NW)

    def normal_game_mode(self):
        self.next_update_interval = 2

        while self.clock_counter > 0:  # Keep running unless you have a stopping condition
            # Wait for the next X and Y positions
            #new_position_x, new_position_y = self.get_next_position()

            self.next_update = time.time() + self.next_update_interval
            # Grabs data from new_position_x & y arrays
            self.new_position_x = self.next_position_array_x[self.position_counter]
            self.new_position_y = self.next_position_array_y[self.position_counter]

            dx = self.new_position_x - self.position_x
            dy = self.new_position_y - self.position_y
            print(self.position_counter)
            if dx != 0 or dy != 0:  # Only move if dx or dy have changed
                MotorControl.Amove(MotorControl.deltaA(dx, dy))
                MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                self.position_x, self.position_y = self.new_position_x, self.new_position_y
                self.current_position.config(
                    text=f"current position: {self.position_x}, {self.position_y}", 
                    font=("Arial", 14)
                )
                self.position_counter = (self.position_counter+1)%len(self.next_position_array_x)
            else:
                print("No position change, skipping motor movement.")
            time.sleep(self.next_update_interval)
                
    def random_game_mode(self):
        self.next_update_interval = 2
        while self.clock_counter > 0:  
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
        #self.next_update_interval = 2
        while True:
            # Keep running unless you have a stopping condition
            # Wait for the next X and Y positions
            self.new_position_x, self.new_position_y = self.get_next_position()
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
            #time.sleep(self.next_update_interval)



    def grid_remover(self):
        self.normal_start_button.grid_remove()
        self.random_start_button.grid_remove()
        self.text_box_start_button.grid_remove()

        print("start buttons removed")
        if self.normal_gameflag == True or self.random_gameflag == True:
            self.text_field.grid_remove()
            self.text_field_button.grid_remove()    
            print("text field and button removed")

    def game_finished_old(self):
        #tk kode for finished screen med poeng
        self.clock_label.grid_remove()
        self.current_position.grid_remove()
        self.score_label.config(font=("arial" , 72))

    def game_finished(self):
        self.running = False
        if self.clock_counter <= 0 and self.entered_username_flag == False:
            self.entered_username_flag = True
            name = simpledialog.askstring("Game Over", "Enter your name for the high score list:")
            print(f"Scores to save: {self.counter}")
            if name:
                self.save_high_scores(name, self.counter)
                self.username_saved_flag = True
        if self.username_saved_flag == True:
            self.game_finished_show_main_menu()
    
    def game_finished_show_main_menu(self):
        print("hello")
        self.username_saved_flag = False
        if self.t1.is_alive():
            self.t1.join(timeout=1)
        if self.t2.is_alive():
            self.t2.join(timeout=1)
        # Clear all widgets currently displayed
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
          

    def normal_start(self):
        self.update_clock()
        self.video_stream()
        self.grid_remover()
        #Removes start menu buttons

        # Start threads for regular task and sensor task
        self.t1 = threading.Thread(target=self.normal_game_mode, daemon=True)
        self.t2 = threading.Thread(target=self.update_score, daemon=True)

        self.t1.start()
        self.t2.start()

        

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
        self.stop_button_deploy()
        
        
        # Start threads for regular task and sensor task
        t1 = threading.Thread(target=self.text_box_game_mode, daemon=True)
        t2 = threading.Thread(target=self.update_score, daemon=True)

        t1.start()
        t2.start()


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
