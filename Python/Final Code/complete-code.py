import numpy as np
import time
import cv2
import sys
import cv2
import threading
import time

from tkinter import *
from tkinter import simpledialog
from PIL import ImageTk, Image
from gpiozero import Servo, OutputDevice
from TMC_2209.TMC_2209_StepperDriver import *
from time import sleep
from adafruit_servokit import ServoKit
from math import floor

#Initialize servos to GPIO pins
kit = ServoKit(channels=16)
kit.servo[0].actuation_range = 90
kit.servo[1].actuation_range = 90
kit.servo[0].angle = 55
kit.servo[1].angle = 45

#Servo angle constraints
panMin, panMax = 0, 90
tiltMin, tiltMax = 40, 65

oldValueX = 0
oldValueY = 0

#Map angle to servo position
#Angle = 0-180, Position = -1 to +1
def angleToServoPos(angle):
    return (angle - 1)
#Camera settings
frameWidth, frameHeight = 640, 480
latestFrame = None
frameLock = threading.Lock()

#Initialize the camera
videocapture = cv2.VideoCapture(0)
videocapture.set(cv2.CAP_PROP_FRAME_WIDTH, frameWidth)
videocapture.set(cv2.CAP_PROP_FRAME_HEIGHT, frameHeight)

#Load HOG Descriptor
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

#Initialize tracker
tracker = None
primaryTargetLocked = False

#Flag to control threads
stopThreads = False

class MotorControl:    
    def __init__(self):
        self.aFlag = False
        self.bFlag = False

    def Amove(self, steps, duration=None):
        if self.aFlag is False:
            self.aFlag = True
            stepperMotorA.set_direction_reg(False)
            stepperMotorA.set_current(800)
            stepperMotorA.set_interpolation(True)
            stepperMotorA.set_spreadcycle(False)
            stepperMotorA.set_microstepping_resolution(2)
            stepperMotorA.set_internal_rsense(False)

            stepperMotorA.set_acceleration(2000)
            stepperMotorA.set_max_speed(1500)

        if duration is not None:
            print(steps, "| A motor steps")
            stepperMotorA.set_speed_fullstep (steps)
            stepperMotorA.run_to_position_steps(steps)
            print(stepperMotorA.get_current_position())
        
    def Bmove(self, steps, duration=None):            
        if self.bFlag is False:
            self.bFlag = True
            stepperMotorB.set_direction_reg(False)
            stepperMotorB.set_current(800)
            stepperMotorB.set_interpolation(True)
            stepperMotorB.set_spreadcycle(False)
            stepperMotorB.set_microstepping_resolution(2)
            stepperMotorB.set_internal_rsense(False)

            stepperMotorB.set_acceleration(2000)
            stepperMotorB.set_max_speed(1500)
        if duration is not None:
            print(steps, "| B motor steps")
            stepperMotorB.set_speed_fullstep (steps)
            stepperMotorB.run_to_position_steps(steps)
            print(stepperMotorB.get_current_position())

    @staticmethod
    def deltaA(delX, delY):
        return delX + delY

    @staticmethod
    def deltaB(delX, delY):
        return delX - delY

class TMC_StepperMotor:
    def __init__(self, step_pin, dir_pin, en_pin):
        self.tmc = TMC_2209(step_pin, dir_pin, en_pin, serialport="/dev/ttyAMA0", driver_address=0)
        self.tmc.set_direction_reg(False)
        self.tmc.set_current(300)
        self.tmc.set_interpolation(True)
        self.tmc.set_spreadcycle(False)
        self.tmc.set_microstepping_resolution(2)
        self.tmc.set_internal_rsense(False)

        self.tmc.set_acceleration(2000)
        self.tmc.set_max_speed(500)
        
    def run_to_position_steps(self, steps):
        self.tmc.run_to_position_steps(steps)

    def run_to_position_fullsteps(self, speed):
        self.tmc.set_speed_fullstep(speed)

class StepperMotor:
    def __init__(self, step_pin, dir_pin, en_pin, steps_per_rev=200):
        # Define pins
        self.step_pin = OutputDevice(step_pin)
        self.dir_pin = OutputDevice(dir_pin)
        self.en_pin = OutputDevice(en_pin)
        
        # Motor settings
        self.steps_per_rev = steps_per_rev
        self.max_speed = 1000.0
        self.acceleration = 200.0
        self.current_speed = 200.0
        self.target_position = 0
        self.current_position = 0
        self.step_delay = 0.001
        self.running = False

    def set_max_speed(self, speed):
        self.max_speed = speed

    def set_acceleration(self, acceleration):
        self.acceleration = acceleration

    def set_speed(self, speed):
        self.current_speed = min(speed, self.max_speed)
        self.step_delay = 1 / self.current_speed

    def move_to(self, position):
        self.target_position = position
        self.running = True
        if not hasattr(self, 'thread') or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def run(self):
        while self.running:
            distance_to_go = self.target_position - self.current_position
            if distance_to_go == 0:
                self.running = False
                break

            # Set direction
            self.dir_pin.value = distance_to_go > 0

            # Accelerate/decelerate logic (simplified for demonstration)
            if self.acceleration > 0:
                if abs(self.current_speed) < self.max_speed:
                    self.current_speed += self.acceleration * 0.01
                    self.set_speed(self.current_speed)
            self.step_pin.on()
            time.sleep(self.step_delay)
            self.step_pin.off()
            time.sleep(self.step_delay)

            # Update current position
            self.current_position += 1 if self.dir_pin.value else -1

    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()

class Sensor:
    # Assigns GPIO pin 27 to infrared detector
    IR_PIN = 27

    def ir_callback(channel):
        print(f"IR signal detected. Channel: {channel}, Time: {time.time()}")

    def read():
        x = np.random.randint(0, 3)
        time.sleep(0.1)
        return x == 1

class App:
    def __init__(self, root):
        # Initialization of root window
        self.root = root
        self.root.geometry("800x600")
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
        self.next_position_array_x = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        self.next_position_array_y = [100, 200, 300 ,400 , 500 , 600, 700, 800, 900, 1000]

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
        # Resets clock_counter and points
        self.counter = 0

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

        #Stop button for text mode        
        self.stop_button = Button(
            self.root, 
            fg="black", 
            bg="red4" ,
            activebackground="green",
            text="Quit game", 
            font=("Comic sans", 32), 
            command=lambda:[self.game_finished_show_main_menu()])

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
            command= lambda:[self.set_normal_flag(),self.normal_start()])
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

    def set_normal_flag(self):
        print("normal game selected")
        self.normal_gameflag = True


    def set_random_flag(self):
        print("random game selected")
        self.random_gameflag = True
        

    def set_textbox_flag(self):
        print("text_box game selected")
        self.text_box_gameflag = True

    def reset_flags(self):
        self.normal_gameflag = False
        self.random_gameflag = False
        self.text_box_gameflag = False

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

        self.position_event.wait()
        self.position_event.clear()  # Clear the event for the next wait
        return self.new_position_x, self.new_position_y


    def show_high_score(self):
        # Create high score window
        high_score_window = Toplevel(self.root)
        high_score_window.title("Highscore")
        high_score_window.geometry("400x600")
        high_score_window.configure(bg="Gray30")

        self.title =Label(high_score_window, text="Highscore", font=("Comic sans", 32), fg="black", bg="Red4" )
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
        scores = sorted(scores, key=lambda x: x[1], reverse = True)[:10] # [:10]amount of high scores kept
        with open("Highscore.txt", "w") as file:
            for name, score in scores:
                file.write(f"{name},{score}\n")

    def update_clock(self):
        if self.clock_counter > 0:
            self.clock_counter -= 1
        minute, second = divmod(self.clock_counter, 60)
        self.clock_label.config(text=f"{minute}:{second:02}")
        self.clock_label.after(1000, self.update_clock)
        
        if self.clock_counter <= 0:
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
        self.lmain.after(30, self.video_stream)

    #deployes the stop button
    def stop_button_deploy(self):
        self.stop_button.grid(row=4, column=0, sticky=NW)

    def normal_game_mode(self):
        self.next_update_interval = 2

        while self.clock_counter > 0:  # Keep running unless you have a stopping condition

            self.next_update = time.time() + self.next_update_interval
            # Grabs data from new_position_x & y arrays
            self.new_position_x = self.next_position_array_x[self.position_counter]
            self.new_position_y = self.next_position_array_y[self.position_counter]

            dx = self.new_position_x - self.position_x
            dy = self.new_position_y - self.position_y
            print(self.position_counter)
            if dx != 0 or dy != 0:  # Only move if dx or dy have changed
                #MotorControl.Amove(MotorControl.deltaA(dx, dy))
                #MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                motorController.Amove(motorController.deltaA(dx, dy), 2)
                motorController.Bmove(motorController.deltaB(dx, dy), 2)
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
                #MotorControl.Amove(MotorControl.deltaA(dx, dy))
                #MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                motorController.Amove(motorController.deltaA(dx, dy), 2)
                motorController.Bmove(motorController.deltaB(dx, dy), 2)
                self.position_x, self.position_y = self.new_position_x, self.new_position_y
                self.current_position.config(
                text=f"current position: {self.position_x}, {self.position_y}", 
                     font=("Arial", 14)
                )
            else:
                print("No position change, skipping motor movement.")
            time.sleep(self.next_update_interval)



    def text_box_game_mode(self):
        while self.running == True:
            # Wait for the next X and Y positions
            self.new_position_x, self.new_position_y = self.get_next_position()
            dx = self.new_position_x - self.position_x
            dy = self.new_position_y - self.position_y
            if dx != 0 or dy != 0:  # Only move if dx or dy have changed
                #MotorControl.Amove(MotorControl.deltaA(dx, dy))
                #MotorControl.Bmove(MotorControl.deltaB(dx, dy))
                motorController.Amove(motorController.deltaA(dx, dy), 2)
                motorController.Bmove(motorController.deltaB(dx, dy), 2)
                self.position_x, self.position_y = self.new_position_x, self.new_position_y
                self.current_position.config(
                    text=f"current position: {self.position_x}, {self.position_y}", 
                    font=("Arial", 14)
                )
            else:
                print("No position change, skipping motor movement.")


    def grid_remover(self):
        self.normal_start_button.grid_remove()
        self.random_start_button.grid_remove()
        self.text_box_start_button.grid_remove()
        self.high_score_button.grid_remove()

        if self.normal_gameflag == True or self.random_gameflag == True:
            self.text_field.grid_remove()
            self.text_field_button.grid_remove()    


    def game_finished(self):
        self.running = False
        stepperMotorA.set_motor_enabled(False)
        stepperMotorB.set_motor_enabled(False)
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
        self.running = False
        self.clock_counter = 0
        self.entered_username_flag = False
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
        self.normal_gameflag = True
        stepperMotorA.set_motor_enabled(True)
        stepperMotorB.set_motor_enabled(True)
        self.clock_counter = 60

        
        self.update_clock()
        #self.video_stream()
        self.grid_remover()
        #Removes start menu buttons

        # Start threads for regular task and sensor task
        self.t1 = threading.Thread(target=self.normal_game_mode, daemon=True)
        self.t2 = threading.Thread(target=self.update_score, daemon=True)

        self.t1.start()
        self.t2.start()


    def random_start(self):
        self.random_gameflag = True
        stepperMotorA.set_motor_enabled(True)
        stepperMotorB.set_motor_enabled(True)
        self.clock_counter = 60

        self.update_clock()
        self.video_stream()
        self.grid_remover()

        # Start threads for regular task and sensor task
        t1 = threading.Thread(target=self.random_game_mode, daemon=True)
        t2 = threading.Thread(target=self.update_score, daemon=True)
     
        t1.start()
        t2.start()

    def text_box_start(self):
        self.text_box_gameflag = True
        stepperMotorA.set_motor_enabled(True)
        stepperMotorB.set_motor_enabled(True)
        #self.update_clock()
        #self.video_stream()
        self.grid_remover()
        self.stop_button_deploy()

        #Start threads for regular task and sensor task
        t1 = threading.Thread(target=self.text_box_game_mode, daemon=True)
        t2 = threading.Thread(target=self.update_score, daemon=True)

        t1.start()
        t2.start()



#Camera Thread
def cameraThread():
    global latestFrame, stopThreads
    while not stopThreads:
        ret, frame = videocapture.read()
        if not ret:
            print("Failed to capture")
            break
        #Update latest frame with locking for thread safety
        with frameLock:
            latestFrame = frame.copy()

# Processing Thread
def processingThread():
    global latestFrame, stopThreads, tracker, primaryTargetLocked, oldValueY, oldValueX
    confirmFrames = 10 #Amount of frames used to confirm tracking
    detectHistory = []
    while not stopThreads:
        with frameLock:
            if latestFrame is None:
                continue
            frame = latestFrame.copy()

        #HOG only runs if tracker is not active
        if not primaryTargetLocked:
            # Convert frame to grayscale (optional for performance)
            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect humans in frame
            boxes, _ = hog.detectMultiScale(grayscale, winStride=(8, 8), scale=1.05)

            if len(boxes) > 0:
                # Select one target, e.g., the first detected person
                primaryBox = boxes[0]
                detectHistory.append(primaryBox)

                #If detection history contains more frames than neeeded for confirmation, delete them
                if len(detectHistory) > confirmFrames:
                    detectHistory.pop(0)
                
                #Check that the marked target stays consistent trough several frames
                if len(detectHistory) == confirmFrames and all(
                    abs(detectHistory[0][0] - box[0]) < 10 and
                    abs(detectHistory[0][1] - box[1]) < 10 and
                    abs(detectHistory[0][2] - box[2]) < 10 and
                    abs(detectHistory[0][3] - box[3]) < 10
                    for box in detectHistory
                ):
                    time.sleep(2)

                    # Initialize the tracker
                    tracker = cv2.TrackerCSRT_create()
                    tracker.init(frame, tuple(primaryBox))

                    # Lock on the target
                    primaryTargetLocked = True
                    #Once target is found, detection is no longer necessary
                    detectHistory.clear()

                    # Draw rectangle around the person
                    x, y, w, h = primaryBox
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        else:
            # Make the tracker follow the primary target
            success, box = tracker.update(frame)
            
            if success:
                x, y, w, h = map(int, box)
                # Draw a rectangle on the person when in tracking mode
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
            else:
                # Reset tracker if the target is lost
                primaryTargetLocked = False
                tracker = None
                
            #Get coordinates of the detected person
            x, y, w, h = boxes[0]
            personCenterX = box[0] + w // 2
            personCenterY = box[1] + h // 2
            
            #Convert coordinates to servo angles
            panAngle = 90-int(panMin + (personCenterX / frameWidth) * (panMax - panMin))
            tiltAngle = 90-int(tiltMin + (personCenterY / frameHeight) * (tiltMax - tiltMin))
            
            #Move servos to position 
            kit.servo[1].angle = (floor(angleToServoPos(panAngle)))
            kit.servo[0].angle = (floor(angleToServoPos(tiltAngle)))
            print(f"Pan: {panAngle}, Tilt: {tiltAngle}")

        # Display video
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('X'):
            stopThreads = True
            break

#Start the threads for camera and frame processing
cameraT = threading.Thread(target = cameraThread, daemon = True)
processingT = threading.Thread(target = processingThread, daemon = True)

cameraT.start()
processingT.start()

#Wait for the threads to complete
try:
    while not stopThreads:
        sleep(0.1) #Keeps main thread alive
finally:
    #Signal the threads to stop and release resources
    stopThreads = True
    cameraT.join()
    processingT.join()
    videocapture.release()
    cv2.destroyAllWindows()
    print("Program stopped!")

if __name__ == "__main__":
    root = Tk()

    app = App(root)
    # Pin 17 og 18 til servo
    # StepperMotor(step_pin, dir_pin, en_pin) uart
    #steppercontroller1 = StepperMotor(21, 16, 20)
    #steppercontroller2 = StepperMotor(25, 23, 24)
    stepperMotorA = TMC_2209(21, 16, 20, serialport="/dev/ttyAMA0", driver_address=0)
    stepperMotorB = TMC_2209(25, 23, 24, serialport="/dev/ttyAMA3", driver_address=1)
    motorController = MotorControl()
    root.mainloop()