import pyfirmata2 as pyfirmata
from pyfirmata import Arduino, SERVO, util
import time

# Set up your board (adjust the port based on your system)
board = pyfirmata.Arduino('COM8')  # Change this to your Arduino port
board.digital[2].mode =SERVO 
# Define pins
led_builtin = 13  # LED_BUILTIN is typically pin 13
led1 = 2
led2 = 3
led3 = 12



def turn_off_all():
    """Turn off all LEDs."""
    # board.digital[led1].write(0)
    board.digital[led2].write(0)
    board.digital[led3].write(0)
    board.digital[led_builtin].write(0)

while True:
    try:
        incoming_byte = input("Enter a command (1, 2, 3, or anything else): ").strip()
        
        # Turn off all LEDs first
        turn_off_all()

        if incoming_byte == "1":
            board.digital[led1].write(90)
            print("Led 1 ON")

        elif incoming_byte == "2":
            board.digital[led2].write(1)
            print("Led 2 ON")

        elif incoming_byte == "3":
            board.digital[led3].write(1)
            print("Led 3 ON")

        else:
            board.digital[led_builtin].write(1)
            print("Invalid input")

        time.sleep(0.6)  # Add a small delay to avoid rapid-fire toggling

    except KeyboardInterrupt:
        print("Exiting...")
        break

# Cleanup
board.exit()
