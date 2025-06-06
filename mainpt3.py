import cv2
import numpy as np
import cardData
import utils
import timeit
import time
# import pySerialTransferl
import serial
import pyfirmata2 as pyfirmata


board = pyfirmata.Arduino('COM10')  # Change this to your Arduino port
fl1 = 9
fl2 = 10
fl3 = 11
forward_pin = 1
backward_pin = 12
delay_time = 3 
flippers = [fl1, fl2, fl3]
# Set pin modes and immediately set each servo to 180 degrees
for flipper in flippers:
    board.digital[flipper].mode = pyfirmata.SERVO
    board.digital[flipper].write(180)  # Set initial position to 180 degrees
    time.sleep(0.1)  # Small delay to ensure each servo is set
board.digital[forward_pin].mode = pyfirmata.OUTPUT  # OUTPUT
board.digital[backward_pin].mode = pyfirmata.OUTPUT  # OUTPUT
def resetServos(flippers):
    for flipper in flippers:
        board.digital[flipper].write(180)

def readCard(n, cam):
    
    # phoneCamFeed = True        # Flag signaling if images are being read live from phone camera or from image file
    pathImage = 'testImages/tiltright.jpg'      # File name of image
    # print(n) # TO DO SEPARATE CAMERA INIT INTO ITS OWN DEFINED FUNCTION SO THAT CODE CAN RUN WITHOUT INITIALIZING EVERY TIME
    # if phoneCamFeed and n ==0:
    #     cam = cv2.VideoCapture(0)   # Use Video source 1 = phone; 0 = computer webcam
    #     print('I love panda ')
    # initCamstop = timeit.default_timer()
    # print('Time to init. camera' + str(initCam-initCamstop))
    # # Scaled to the IRL height and width of a Pokemon card (6.6 cm x 8.8 cm)
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
            # rot90frame = cv2.resize(rot90frame, (widthCard+50, heightCard+50))
        else:
            # Read in picture and resize it to normalize
            pic = cv2.imread(pathImage)
            rot90frame = pic.copy()
        # Background Subtractor
        background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

        # Process each frame
        # Convert the frame to grayscale
        grayFrame = cv2.cvtColor(rot90frame, cv2.COLOR_BGR2GRAY)

        # Blur the grayscale frame to reduce noise
        blurredFrame = cv2.GaussianBlur(grayFrame, (3, 3), 0)

        # Apply the background subtractor to get the foreground mask
        fg_mask = background_subtractor.apply(blurredFrame)

        # Clean up the foreground mask using morphological operations
        kernel = np.ones((5, 5), np.uint8)
        fg_mask_cleaned = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask_cleaned = cv2.morphologyEx(fg_mask_cleaned, cv2.MORPH_CLOSE, kernel)

        # Use the cleaned mask to isolate the foreground
        foreground = cv2.bitwise_and(blurredFrame, blurredFrame, mask=fg_mask_cleaned)

        # Use Canny edge detection on the foreground to get edges
        edgedFrame = cv2.Canny(foreground, threshold1=80, threshold2=150)

        # Clean up edges with dilation and erosion
        frameDial = cv2.dilate(edgedFrame, kernel, iterations=2)
        frameThreshold = cv2.erode(frameDial, kernel, iterations=1)

        # Get contours from the cleaned edge-detected image
        contourFrame = rot90frame.copy()
        bigContour = rot90frame.copy()
        contours, hierarchy = cv2.findContours(frameThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours for visualization
        cv2.drawContours(contourFrame, contours, -1, (0, 255, 0), 10)

        # Get the biggest contour and perform perspective transformation if corners are detected
        imgWarpColored = blackImg  # Set imgWarpColored
        corners, maxArea = utils.biggestContour(contours)
        matchingCard = np.zeros((heightCard, widthCard, 3), dtype=np.uint8)
        found = False #
        cardinfo = 0
        if len(corners) == 4:
            corners = [corners[0][0], corners[1][0], corners[2][0], corners[3][0]]
            corners = utils.reorderCorners(corners)  # Reorder corners
            bigContour = utils.drawRectangle(bigContour, corners)
            pts1 = np.float32(corners)
            pts2 = np.float32([[0, 0], [widthCard, 0], [0, heightCard], [widthCard, heightCard]])
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            imgWarpColored = cv2.warpPerspective(rot90frame, matrix, (widthCard, heightCard))
            section_start = timeit.default_timer()
            found, matchingCard, cardinfo = utils.findCard(imgWarpColored.copy())  # Check for a matching card
            section_end = timeit.default_timer()

        # Resize all of the images to the same dimensions
        rot90frame = cv2.resize(rot90frame, (widthCard, heightCard))
        grayFrame = cv2.resize(grayFrame, (widthCard, heightCard))
        blurredFrame = cv2.resize(blurredFrame, (widthCard, heightCard))
        edgedFrame = cv2.resize(edgedFrame, (widthCard, heightCard))
        contourFrame = cv2.resize(contourFrame, (widthCard, heightCard))
        bigContour = cv2.resize(bigContour, (widthCard, heightCard))


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

def set_flipper(n):
    board.digital[n].write(110)  # Adjust angle as needed
    print(f"Set servo on pin {n} to 110 degrees")

def sortingLogic(matchingCardData):
    # Set input value based on card type
    inp = 0
    if matchingCardData['Card Type'] == 'Pokémon':
        inp = 1
    elif matchingCardData['Card Type'] == 'Trainer':
        inp = 2
    elif matchingCardData['Card Type'] == 'Energy':
        inp = 3
    else:
        print('Card type not recognized')
        return  # If the card type is unrecognized, exit the function
    print(inp)
    print(matchingCardData['Card Name'])
    incoming_byte = inp
    # Specify the pin connected to the servo

    # Turn off all LEDs first
    
    # Set the RGB LED based on the user's input
    if incoming_byte == 1:
        # set_flipper(flippers[incoming_byte])
        # print(flippers[incoming_byte])
        set_flipper(9)
        print("Flipper 1: Pokémon")

    elif incoming_byte == 2:
        # set_flipper(flippers[incoming_byte])
        set_flipper(10)
        print(flippers[incoming_byte])

        print("Flipper 2: Trainer")

    elif incoming_byte == 3:
        set_flipper(11)
        # set_flipper(flippers[incoming_byte])
        print("Flipper 3: Energy")

    else:
        print("Other Pile")

    # time.sleep(0.6)  # Add a small delay to avoid rapid-fire toggling


if __name__ == '__main__':
    isFirst = False  # True if this is your first time running this code; will create a new database
    if isFirst:
        cardData.createDatabase()
    n = 0 #number of times read card has been ran
    phoneCamFeed = True
    cam = None
    if phoneCamFeed:
        initCam = timeit.default_timer()
        cam = cv2.VideoCapture(1)
        initCamstop = timeit.default_timer()
        print('Time to init. camera' + str(initCam-initCamstop))
    if not cam.isOpened():
        print("Error: Could not initialize camera.")
        cam = None
    if cam:     
        while True:
            starttot=  timeit.default_timer()
            board.digital[backward_pin].write(1)
            board.digital[forward_pin].write(0)

            time.sleep(delay_time)
            resetServos(flippers)
            cardinfo = readCard(n, cam)  # Finds and reads from a saved image or live feed
            board.digital[backward_pin].write(0)
            board.digital[forward_pin].write(1)
            sortingLogic(cardinfo)
            time.sleep(5)
            endtot = timeit.default_timer()
            print('Length of total loop:' + str(endtot-starttot))
            n = n + 1
    if cam:
        cam.release()
        cv2.destroyAllWindows()
            
