import random
from gpiozero import OutputDevice
from threading import Thread
import time

# Stepper Motor Class
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
            self.thread = Thread(target=self.run)
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

if __name__ == "__main__":
    # Example usage
    motor = StepperMotor(step_pin=8, dir_pin=10, en_pin=11)

    # Sample operations
    positions = [0, 500, 1000, 1500]
    for pos in positions:
        print(f"Moving to position: {pos}")
        motor.move_to(pos)
        time.sleep(2)  # Wait for demonstration purposes

    motor.stop()
    print("Motor stopped.")