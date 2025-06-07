import serial
import time

serialcomm = serial.Serial('COM8', 115200)  # Use the same baud rate as Arduino
serialcomm.timeout = 1
a = 0

while True:
    i = str(2) + '\n'  # Send input as string with newline
    serialcomm.write(i.encode())  # Send to Arduino

    # Short delay to give Arduino time to process the command
    time.sleep(0.1)

    # Wait for Arduino's response
    response = ""
    while not response or response != "Command processed":
        response = serialcomm.readline().decode('ascii').strip()  # Read Arduino's response

    a += 1
    print(f'Loop {a}: {response}')  # Print Arduino's response

    time.sleep(2)  # Delay between loops
