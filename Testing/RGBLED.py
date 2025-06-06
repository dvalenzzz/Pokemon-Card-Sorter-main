import pyfirmata2 as pyfirmata
from pyfirmata import Arduino
import time

# Set up your board (adjust the port based on your system)
board = pyfirmata.Arduino('COM8')  # Change this to your Arduino port

# Define RGB LED pins
red = 9
green = 10
blue = 11

def turn_off_all():
    """Turn off all LEDs (set all pins to LOW)."""
    board.digital[red].write(0)
    board.digital[green].write(0)
    board.digital[blue].write(0)

def set_rgb(r, g, b):
    """Set the RGB LED color by controlling red, green, and blue channels."""
    board.digital[red].write(r)
    board.digital[green].write(g)
    board.digital[blue].write(b)

while True:
    try:
        # Get input from user to select color
        incoming_byte = input("Enter a command (1=Red, 2=Green, 3=Blue, 4=Yellow, 5=Cyan, 6=Magenta, or anything else for White): ").strip()
        
        # Turn off all colors first
        turn_off_all()

        # Set the RGB LED based on the user's input
        if incoming_byte == "1":
            set_rgb(1, 0, 0)  # Red
            print("Red ON")

        elif incoming_byte == "2":
            set_rgb(0, 1, 0)  # Green
            print("Green ON")

        elif incoming_byte == "3":
            set_rgb(0, 0, 1)  # Blue
            print("Blue ON")

        elif incoming_byte == "4":
            set_rgb(1, 1, 0)  # Yellow (Red + Green)
            print("Yellow ON")

        elif incoming_byte == "5":
            set_rgb(0, 1, 1)  # Cyan (Green + Blue)
            print("Cyan ON")

        elif incoming_byte == "6":
            set_rgb(1, 0, 1)  # Magenta (Red + Blue)
            print("Magenta ON")

        else:
            set_rgb(1, 1, 1)  # White (Red + Green + Blue)
            print("White ON")

        time.sleep(0.6)  # Add a small delay to avoid rapid-fire toggling

    except KeyboardInterrupt:
        print("Exiting...")
        break

# Cleanup
board.exit()
