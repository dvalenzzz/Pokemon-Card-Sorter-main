import pyfirmata2 as pyfirmata
import time

# Initialize Arduino board on specified port
board = pyfirmata.Arduino('COM10')  # Change this to your Arduino port

# Define servo pin numbers
fl1 = 9
fl2 = 10
fl3 = 11
forward_pin = 8
backward_pin = 12
delay_time = 3 
flippers = [fl1, fl2, fl3]

# Set pin modes for servos and output pins
board.digital[fl1].mode = pyfirmata.SERVO
board.digital[fl2].mode = pyfirmata.SERVO
board.digital[fl3].mode = pyfirmata.SERVO
board.digital[forward_pin].mode = pyfirmata.OUTPUT
board.digital[backward_pin].mode = pyfirmata.OUTPUT

# Allow some time for the board to initialize
time.sleep(2)

# Function to reset servos to 180 degrees
def resetServos(flippers):
    for flipper in flippers:
        print(f"Setting servo {flipper} to 180 degrees (reset position)")
        board.digital[flipper].write(90)  # Move servo to 180 degrees
        time.sleep(0.5)  # Short delay to ensure each servo moves

# Function to set a specific flipper to 110 degrees
def set_flipper(n):
    print(f"Setting servo {n} to 110 degrees")
    board.digital[n].write(110)  # Move servo to 110 degrees

# Reset all servos
resetServos(flippers)

# Move the second flipper to 110 degrees
set_flipper(flippers[1])

# Print to verify which servo was moved
print("Moved flipper:", flippers[2])
