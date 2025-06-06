import cv2
import numpy as np
import cardData
import utils
import timeit
import time
# import pySerialTransfer
import serial
import pyfirmata2 as pyfirmata

board = pyfirmata.Arduino('COM8')  # Change this to your Arduino port

# Define pins
led_builtin = 13  # LED_BUILTIN is typically pin 13
red = 9
green = 10
blue = 11

def turn_off_all():
    """Turn off all LEDs (set all pins to LOW)."""
    board.digital[red].write(0)
    board.digital[green].write(0)
    board.digital[blue].write(0)
    
def readCard(n):
    
    phoneCamFeed = True        # Flag signaling if images are being read live from phone camera or from image file
    pathImage = 'testImages/tiltright.jpg'      # File name of image
    initCam = timeit.default_timer()
    print(n) # TO DO SEPARATE CAMERA INIT INTO ITS OWN DEFINED FUNCTION SO THAT CODE CAN RUN WITHOUT INITIALIZING EVERY TIME
    if phoneCamFeed and n ==0:
        cam = cv2.VideoCapture(0)   # Use Video source 1 = phone; 0 = computer webcam
        print('I love panda ')
    initCamstop = timeit.default_timer()
    print('Time to init. camera' + str(initCam-initCamstop))
    # Scaled to the IRL height and width of a Pokemon card (6.6 cm x 8.8 cm)
    widthCard = utils.getWidthCard()
    heightCard = utils.getHeightCard()

    while True:
        # Create a blank image
        blackImg = np.zeros((heightCard, widthCard, 3), np.uint8)

        # Check if using phone camera or saved picture
        if phoneCamFeed:
            # Read in frame and rotate 90 degrees b/c video comes in horizontally
            check, frame = cam.read()
            rot90frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            rot90frame = cv2.resize(rot90frame, (widthCard, heightCard))
        else:
            # Read in picture and resize it to normalize
            pic = cv2.imread(pathImage)
            rot90frame = pic.copy()

        # Make image gray scale
        grayFrame = cv2.cvtColor(rot90frame, cv2.COLOR_BGR2GRAY)
        # Blur the image to reduce noise
        blurredFrame = cv2.GaussianBlur(grayFrame, (3, 3), 0)

        # Use Canny edge detection to get edges
        edgedFrame = cv2.Canny(image=blurredFrame, threshold1=100, threshold2=200)

        # Clean up edges
        kernel = np.ones((5,5))
        frameDial = cv2.dilate(edgedFrame, kernel, iterations=2)
        frameThreshold = cv2.erode(frameDial, kernel, iterations=1)

        # Get image contours
        contourFrame = rot90frame.copy()
        bigContour = rot90frame.copy()
        contours, hierarchy = cv2.findContours(frameThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(contourFrame, contours, -1, (0, 255, 0), 10)

        imgWarpColored = blackImg  # Set imgWarpColored
        # Get biggest contour
        corners, maxArea = utils.biggestContour(contours)
        if len(corners) == 4:
            corners = [corners[0][0], corners[1][0], corners[2][0], corners[3][0]]
            corners = utils.reorderCorners(corners)  # Reorders corners to [topLeft, topRight, bottomLeft, bottomRight]
            #cv2.drawContours(bigContour, corners, -1, (0, 255, 0), 10)
            bigContour = utils.drawRectangle(bigContour, corners)
            pts1 = np.float32(corners)
            pts2 = np.float32([[0, 0], [widthCard, 0], [0, heightCard], [widthCard, heightCard]])
            # Makes a matrix that transforms the detected card to a vertical rectangle
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            # Transforms card to a rectangle widthCard x heightCard
            imgWarpColored = cv2.warpPerspective(rot90frame, matrix, (widthCard, heightCard))

        # Resize all of the images to the same dimensions
        # Note: imgWarpColored is already resized and matchingCard gets resized in utils.getMatchingCard()
        rot90frame = cv2.resize(rot90frame, (widthCard, heightCard))
        grayFrame = cv2.resize(grayFrame, (widthCard, heightCard))
        blurredFrame = cv2.resize(blurredFrame, (widthCard, heightCard))
        edgedFrame = cv2.resize(edgedFrame, (widthCard, heightCard))
        contourFrame = cv2.resize(contourFrame, (widthCard, heightCard))
        bigContour = cv2.resize(bigContour, (widthCard, heightCard))
        
        section_start = timeit.default_timer()
        # Check if a matching card has been found, and if so, display it
        found, matchingCard, cardinfo = utils.findCard(imgWarpColored.copy())  # Check to see if a matching card was found
        section_end = timeit.default_timer()
        # print(f"Time to read and rotate image: {section_end - section_start:.4f} seconds")

        # An array of all 8 images
        imageArr = ([rot90frame, grayFrame, blurredFrame, edgedFrame],
                    [contourFrame, bigContour, imgWarpColored, matchingCard])

        # Labels for each image
        labels = [["Original", "Gray", "Blurred", "Threshold"],
                  ["Contours", "Biggest Contour", "Warped Perspective", "Matching Card"]]

        # Stack all 8 images into one and add text labels
        stackedImage = utils.makeDisplayImage(imageArr, labels)

        # Display the image
        cv2.imshow("Card Finder", stackedImage)

        if not phoneCamFeed:  # If reading image file, display image until key is pressed
            if not found:  # If a matching card has not been found
                print('Please try another image. Your card could not be found.')
            # sortingLogic(cardinfo)
            cv2.waitKey(0)  # Keeps window open until any key is pressed
            break
        elif cv2.waitKey(1) & 0xFF == ord('q'):  # If reading from video, quit if 'q' is pressed
            break
        elif found:  # If the input is a video and a matching card has been found
            # print('\n\nPress any key to exit.')
            # sortingLogic(cardinfo)
            cv2.waitKey(0)
            break

    # Stops cameras and closes display window
    # if phoneCamFeed:
    #      cam.release()
    cv2.destroyAllWindows()
    return cardinfo
def set_rgb(r, g, b):
    """Set the RGB LED color by controlling red, green, and blue channels."""
    board.digital[red].write(r)
    board.digital[green].write(g)
    board.digital[blue].write(b)

def sortingLogic(matchingCardData):
    # Set input value based on card type
    inp = 0
    if matchingCardData['Card Type'] == 'Trainer':
        inp = 1
    elif matchingCardData['Card Type'] == 'Pokémon':
        inp = 2
    elif matchingCardData['Card Type'] == 'Energy':
        inp = 3
    else:
        print('Card type not recognized')
        return  # If the card type is unrecognized, exit the function
    print(inp)
    print(matchingCardData['Card Name'])
    incoming_byte = inp
    
    # Turn off all LEDs first
    turn_off_all()
    
    # Set the RGB LED based on the user's input
    if incoming_byte == 1:
        set_rgb(1, 0, 0)  # Red
        print("Red ON")

    elif incoming_byte == 2:
        set_rgb(0, 1, 0)  # Green
        print("Green ON")

    elif incoming_byte == 3:
        set_rgb(0, 0, 1)  # Blue
        print("Blue ON")

    else:
        set_rgb(1, 1, 1)  # White (Red + Green + Blue)
        print("White ON")

    # time.sleep(0.6)  # Add a small delay to avoid rapid-fire toggling

#     
# i = 3
#     serialcomm = serial.Serial('COM8', 460800, timeout=1)
#     start = timeit.default_timer()
#     while i>0:
#         # Send inp to the Arduino

#         # try:
#         # Sending the input
#         # serialcomm.write(str(inp).encode())
#         inpsend = str(inp).encode()
#         serialcomm.write(inpsend)

#         time.sleep(.6) # Wait for a moment

#         # Read and print the response from Arduino
#         response = serialcomm.readline().decode('utf-8')
                
#         print(response)
#         i = i - 1
        
# # finally:
#     end = timeit.default_timer()
#     print('Communication Time:' + str(end-start))
#     serialcomm.close()  # Ensure the serial connection is closed
# Set up your board (adjust the port based on your system)


 
if __name__ == '__main__':
    isFirst = False  # True if this is your first time running this code; will create a new database
    if isFirst:
        cardData.createDatabase()
    n = 0 #number of times read card has been ran

    while True:
        starttot=  timeit.default_timer()
        cardinfo = readCard(n)  # Finds and reads from a saved image or live feed
        sortingLogic(cardinfo)
        endtot = timeit.default_timer()
        print('Length of total loop:' + str(endtot-starttot))
        n = n + 1
    
