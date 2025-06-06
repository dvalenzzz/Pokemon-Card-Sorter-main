import time

from pyfirmata2 import Arduino, util
 
# Set up the board and pins

board = Arduino('COM8')  # Change this to your Arduino's port (e.g., 'COM3' on Windows)

forward_pin = 8

backward_pin = 12

delay_time = 3  # Time delay in seconds (3000 ms = 3 seconds)
 
# Set pins to output mode

board.digital[forward_pin].mode = 1  # OUTPUT

board.digital[backward_pin].mode = 1  # OUTPUT
 
try:

    while True:

        # Spin motor forward

        board.digital[forward_pin].write(1)

        board.digital[backward_pin].write(0)

        time.sleep(delay_time)
 
        # Spin motor backward

        board.digital[forward_pin].write(0)

        board.digital[backward_pin].write(1)

        time.sleep(1)  # 1000 ms = 1 second
 
except KeyboardInterrupt:

    # Reset the board on exit

    board.digital[forward_pin].write(0)

    board.digital[backward_pin].write(0)

    board.exit()

 