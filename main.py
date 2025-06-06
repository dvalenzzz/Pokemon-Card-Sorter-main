import cv2
import numpy as np
import cardData
import utils
import timeit
import time
import pyfirmata2 as pyfirmata

def select_crop_area(image):
    print("Click and drag to select crop area, press 'c' to confirm")
    roi = cv2.selectROI("Select Card Area", image, False)
    cv2.destroyAllWindows()
    return roi  # Returns (x, y, w, h)

board = pyfirmata.Arduino('COM8')  # Change this to your Arduino port
fl1 = 9 # Defines port pin variables
fl2 = 10
fl3 = 11
forward_pin = 8
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
def resetServos(flippers): #Iterates through each flipper and resets their position
    for flipper in flippers: 
        board.digital[flipper].write(180)

def readCard(n, cam): #Scans the card using a computer vision and hashing comparison to scan the card. The output of this function returns card information needed for sorting algorithm full program can be found on github
    
    pathImage = 'testImages/tiltright.jpg'      # File name of image
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
            rot90frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # rot90frame = cv2.resize(rot90frame, (widthCard+50, heightCard+50))
        else:
            # Read in picture and resize it to normalize
            pic = cv2.imread(pathImage)
            rot90frame = pic.copy()
        
        # Make image gray scale


        

        crop_x, crop_y = 100, 50  # Top-left corner of crop
        crop_w, crop_h = 400, 500  # Width and height of crop
        






        grayFrame =  cv2.cvtColor(rot90frame, cv2.COLOR_BGR2GRAY)
        grayFrame = cv2.equalizeHist(grayFrame)
        # Blur the image to reduce noise
        blurredFrame = cv2.GaussianBlur(grayFrame, (5, 5), 0)

        # # Background Remover 
        # background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)
        # fg_mask = background_subtractor.apply(blurredFrame)
        # foreground = cv2.bitwise_and(blurredFrame, blurredFrame, mask=fg_mask)
        #FINDING BY BRIGHTNESS
        # _, thresh = cv2.threshold(blurredFrame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # # Find contours on this thresholded image instead
        # contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Use Canny edge detection to get edges
        edgedFrame = cv2.Canny(blurredFrame, threshold1=80, threshold2=150)
        kernel = np.ones((3,3), np.uint8)
        frameThreshold = cv2.dilate(edgedFrame, kernel, iterations=2) 


        # edgedFrame = cv2.adaptiveThreshold(blurredFrame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 303, 56)
        # Clean up edges
        # kernel = np.ones((5,5))

        # frameClosed = cv2.morphologyEx(edgedFrame, cv2.MORPH_CLOSE, kernel)
        # frameClean = cv2.morphologyEx(frameClosed, cv2.MORPH_OPEN, np.ones((3,3)))
        # # frameDial = cv2.dilate(edgedFrame, kernel, iterations=1)
        # frameThreshold = cv2.erode(frameDial, kernel, iterations=1)

        # Get image contours

        contours, hierarchy = cv2.findContours(edgedFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contourFrame = rot90frame.copy()
        bigContour = rot90frame.copy()
        # DEBUG: Print contour details for the first frame only
        # if n == 0:
        #     print(f"Number of contours found: {len(contours)}")
        #     contour_data= []
        #     for i, contour in enumerate(contours):
        #         area = cv2.contourArea(contour)
        #         perimeter = cv2.arcLength(contour, True)
        #         contour_data.append((i, area, perimeter))

        #         print(f"Contour {i}: Area = {area}, Perimeter = {perimeter}")
                            
        #         # Sort contours by area in descending order and print top 3
        #     print("\nTop 3 contours by area:")
        #     top_area = sorted(contour_data, key=lambda x: x[1], reverse=True)[:3]
        #     for idx, area, perimeter in top_area:
        #         print(f"Contour {idx}: Area = {area}, Perimeter = {perimeter}")

        #     # Sort contours by perimeter in descending order and print top 3
        #     print("\nTop 3 contours by perimeter:")
        #     top_perim = sorted(contour_data, key=lambda x: x[2], reverse=True)[:3]
        #     for idx, area, perimeter in top_perim:
        #         print(f"Contour {idx}: Perimeter = {perimeter}, Area = {area}")
                



        cv2.drawContours(contourFrame, contours, -1, (0, 255, 0), 10)

        imgWarpColored = blackImg  # Set imgWarpColored
        # Get biggest contour
        
        corners, maxArea = utils.biggestContour(contours)
        areas = [cv2.contourArea(c) for c in contours]
        areas.sort(reverse=True)
        print(f"Largest 20 contour areas: {areas[:20]}")
        print(f"Total contours: {len(contours)}")
        print(f"Max area: {max(areas)}")
        print(f"Areas > 100: {len([a for a in areas if a > 100])}")
        print(f"Areas > 1000: {len([a for a in areas if a > 1000])}")

        # Initialize values for matching card and found to ensure loop works even though no values are found. 
        matchingCard = np.zeros((heightCard, widthCard, 3), dtype=np.uint8)
        found = False #
        cardinfo = 0
        print(f"Image shape: {rot90frame.shape}")
        print(f"widthCard: {widthCard}, heightCard: {heightCard}")
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
            section_start = timeit.default_timer()
            # Check if a matching card has been found, and if so, display it
            found, matchingCard, cardinfo = utils.findCard(rot90frame.copy())  # Check to see if a matching card was found
            section_end = timeit.default_timer()            

        # Resize all of the images to the same dimensions
        # Note: imgWarpColored is already resized and matchingCard gets resized in utils.getMatchingCard()
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
    if phoneCamFeed:
         cam.release()
    return cardinfo

def set_flipper(n):
    board.digital[n].write(110)  # Adjust angle as needed
    print(f"Set servo on pin {n} to 110 degrees")

def sortingLogic(matchingCardData):
    inp = 0 #initialize variable
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
        cardData.createDatabase()# Creates database according to saved card attributes. 
    n = 0 #number of times readCard has been ran
    phoneCamFeed = True#Set to true if camera is being used
    cam = None#Initializes the cam variable 
    if phoneCamFeed:
        initCam = timeit.default_timer()
        cam = cv2.VideoCapture(1)
        initCamstop = timeit.default_timer()
        print('Time to init. camera' + str(initCam-initCamstop))
    if not cam.isOpened():
        print("Error: Could not initialize camera.")
        cam = None
    if cam and cam.isOpened():     
        while True:
            starttot=  timeit.default_timer() # Begins timers to estimate the duration of a loop which was used to measure program efficiency
            board.digital[backward_pin].write(1) #Sets the DC motor direction backward to prevent card from advancing until it is scanned.
            board.digital[forward_pin].write(0) #Sets forward pin to 0 

            time.sleep(delay_time) 
            resetServos(flippers)
            select_crop_area
            cardinfo = readCard(n, cam)  # Finds and reads from a saved image or live feed
            board.digital[backward_pin].write(0)
            board.digital[forward_pin].write(1)
            sortingLogic(cardinfo)
            time.sleep(3) #Delay time included so card has time to reach its destination before resetting. 
            endtot = timeit.default_timer()
            print('Length of total loop:' + str(endtot-starttot)) #Prints duration of loop for one card then loop restarts.
            n = n + 1
    if cam:
        cam.release()
        cv2.destroyAllWindows()
            
