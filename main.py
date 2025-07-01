import cv2
import numpy as np
import cardData
import utils
import timeit
import time
from ultralytics import YOLO
import pyfirmata2 as pyfirmata

def select_crop_area(image):
    print("Click and drag to select crop area, press 'c' to confirm")
    roi = cv2.selectROI("Select Card Area", image, False)
    cv2.destroyAllWindows()
    return roi  # Returns (x, y, w, h)

yolo = YOLO('yolov8s.pt')
# board = pyfirmata.Arduino('COM8')  # Change this to your Arduino port 
fl1 = 9 # Defines port pin variables
fl2 = 10
fl3 = 11
forward_pin = 8
backward_pin = 12
delay_time = 3 
flippers = [fl1, fl2, fl3]
# Comment Out for Arduino
# # Set pin modes and immediately set each servo to 180 degrees
# for flipper in flippers:
#     board.digital[flipper].mode = pyfirmata.SERVO
#     board.digital[flipper].write(180)  # Set initial position to 180 degrees
#     time.sleep(0.1)  # Small delay to ensure each servo is set
# board.digital[forward_pin].mode = pyfirmata.OUTPUT  # OUTPUT
# board.digital[backward_pin].mode = pyfirmata.OUTPUT  # OUTPUT
# def resetServos(flippers): #Iterates through each flipper and resets their position
#     for flipper in flippers: 
#         board.digital[flipper].write(180)

def find_object_by_name(result, target_class_name, min_confidence=0.3):
    """
    Find the first object with the specified class name
    Returns the box if found, None otherwise
    """
    if result.boxes is None or len(result.boxes) == 0:
        return None
    
    classes_names = result.names
    
    for box in result.boxes:
        if box.conf[0] > min_confidence:
            cls = int(box.cls[0])
            class_name = classes_names[cls]
            
            if class_name == target_class_name:
                print('pog')
                return box
    
    return None


def readCard(n, cam): #Scans the card using a computer vision and hashing comparison to scan the card. The output of this function returns card information needed for sorting algorithm full program can be found on github
    
    pathImage = 'testImages/Boss3.jpg'      # File name of image
    # # Scaled to the IRL height and width of a Pokemon card (6.6 cm x 8.8 cm)
    widthCard = utils.getWidthCard()
    heightCard = utils.getHeightCard()
    while True:
        # Create a blank image
        blackImg = np.zeros((heightCard, widthCard, 3), np.uint8)
        
        # Check if using phone camera or saved picture
        if camFeed:
            # Read in frame and rotate 90 degrees b/c video comes in horizontally
            if cam == None:
                print('No Frame Received from Camera')
            check, frame = cam.read()
            results = yolo(frame, conf=0.25)
            # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # frame = cv2.resize(frame, (960, 540))
        
        else:
            # Read in picture and resize it to normalize
            pic = cv2.imread(pathImage)
            # pic = cv2.resize(pic, (960,540))
            frame = cv2.rotate(pic, cv2.ROTATE_90_COUNTERCLOCKWISE)
            results = yolo(frame, conf=0.25)

        
        
        cardFrame = blackImg.copy()        

        for result in results:
            # Find the first 'book' object
            book_box = find_object_by_name(result, 'book', min_confidence=0.3)
            
            if book_box is not None:
                # Get coordinates
                bbox = book_box.xyxy[0].tolist()
                x1, y1, x2, y2 = map(int, bbox)
                confidence = float(book_box.conf[0])
                
                print(f"Found book with confidence: {confidence:.2f}")
                
                # Ensure coordinates are within bounds
                h, w = frame.shape[:2]
                x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
                
                if x2 > x1 and y2 > y1:
                    cardFrame = frame[y1:y2, x1:x2]
                    cardFrame = cv2.rotate(cardFrame, cv2.ROTATE_90_COUNTERCLOCKWISE) 

        #crop frame
        x1, x2 = round(140*.95), round(850*1.05) #
        y1, y2= round(190*.95), round(1130*1.05)  # Top-left corner of crop
        # frame = frame[y1:y2, x1:x2]
        # Make image gray scale
        grayFrame =  cv2.cvtColor(cardFrame, cv2.COLOR_BGR2GRAY)
        grayFrame = cv2.equalizeHist(grayFrame)
        # Blur the image to reduce noise
        blurredFrame = cv2.GaussianBlur(grayFrame, (3, 3), 0)
        
        # # Background Remover 
        # background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)
        # fg_mask = background_subtractor.apply(blurredFrame)
        # foreground = cv2.bitwise_and(blurredFrame, blurredFrame, mask=fg_mask)
        #FINDING BY BRIGHTNESS
        # _, thresh = cv2.threshold(blurredFrame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # # Find contours on this thresholded image instead
        # contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Use Canny edge detection to get edges
        edgedFrame = cv2.Canny(blurredFrame, threshold1=50, threshold2=150)
        
        # kernel = np.ones((3,3), np.uint8)
        # frameThreshold = cv2.dilate(edgedFrame, kernel, iterations=2) 


        # edgedFrame = cv2.adaptiveThreshold(blurredFrame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 303, 56)
        # Clean up edges
        kernel = np.ones((5,5))
        frameThreshold = cv2.dilate(edgedFrame, kernel, iterations=1)
        frameThreshold = cv2.erode(frameThreshold, kernel, iterations=1)

        # Get image contours

        contours, hierarchy = cv2.findContours(frameThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contourFrame = frame.copy()
        bigContour = frame.copy()
        
        refinedcontours = []
        for cont in contours:
            if cv2.arcLength(cont,True) > 1000:
                refinedcontours.append(cont)
        # contours = refinedcontours
        cv2.drawContours(contourFrame, contours, -1, (0, 255, 0), 10)

        imgWarpColored = blackImg  # Set imgWarpColored

        # areas = [cv2.contourArea(c) for c in contours]
        # arcs = [cv2.arcLength(c, True) for c in contours]
        # areas.sort(reverse=True)
        # print(f"Largest 20 contour areas: {areas[:20]}")
        # print(f"Total contours: {len(contours)}")
        # # print(f"Max area: {max(areas)}")
        # print(f"Areas > 100: {len([a for a in areas if a > 100])}")
        # print(f"Areas > 1000: {len([a for a in areas if a > 1000])}")
        # print(f"Arc > 1000: {len([a for a in arcs if a > 1000])}")
        # # corners()

        boxes = []
        maxbox = [0,0,0,0]
        
        for cont in contours:
            if cv2.arcLength(cont, True) > 1000 or cv2.arcLength(cont, False) > 1000:
                x,y,w,h = cv2.boundingRect(cont)
                # cv2.drawContours(contourFrame, cont, -1, (0, 255, 0), 10)

                if h > 50:
                    boxes.append([x,y,w,h])
                if w*h > maxbox[2]*maxbox[3] and h > 500: #nifty
                    maxbox = [x,y,w,h]
        for (x,y,w,h) in boxes:
            cv2.rectangle(contourFrame, (x,y), (x+w,(y+h)), (255,0,0), 5)
        print(boxes)
        # Initialize values for matching card and found to ensure loop works even though no values are found. 
        maxBoxFrame = blackImg.copy()
        matchingCard = np.zeros((heightCard, widthCard, 3), dtype=np.uint8)
        maxBoxFrame = frameThreshold[ maxbox[1]: maxbox[1]+maxbox[3], maxbox[0]:maxbox[0]+maxbox[2]]
        maxBoxEdge = cv2.Canny(maxBoxFrame, threshold1=50, threshold2=150)
        # pogtours, hierarchy = cv2.findContours(maxBoxEdge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
         # Get biggest contour   
        corners, maxArea = utils.biggestContour(contours)
        print(maxArea)
        print(6666666666666666666666666)
        found = False #
        cardinfo = 0
        hamburger = True
        print(f"Image shape: {frame.shape}")
        print(f"widthCard: {widthCard}, heightCard: {heightCard}")
        if len(corners) == 4 and not cardFrame.any==None:
            print("4 Corners Detected")
            corners = [corners[0][0], corners[1][0], corners[2][0], corners[3][0]]
            corners = utils.reorderCorners(corners)  # Reorders corners to [topLeft, topRight, bottomLeft, bottomRight]
            bigContour = utils.drawRectangle(bigContour, corners)
            pts1 = np.float32(corners)
            pts2 = np.float32([[0, 0], [widthCard, 0], [0, heightCard], [widthCard, heightCard]])
            # Makes a matrix that transforms the detected card to a vertical rectangle
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            # Transforms card to a rectangle widthCard x heightCard
            imgWarpColored = cv2.warpPerspective(cardFrame, matrix, (widthCard, heightCard))
            section_start = timeit.default_timer()
            # Check if a matching card has been found, and if so, display it
            found, matchingCard, cardinfo = utils.findCard(imgWarpColored.copy())  # Check to see if a matching card was found
            section_end = timeit.default_timer()            
        cv2.imwrite("dario.jpg", contourFrame)
        # if hamburger == True: #force findcard
        #     found, matchingCard, cardinfo = utils.findCard(frame.copy())  # Check to see if a matching card was found




        maxBoxContours = frame.copy()
        # maxBoxContours = cv2.drawContours(maxBoxContours, pogtours, -1, (0, 255, 0), 10)




        # Resize all of the images to the same dimensions
        # Note: imgWarpColored is already resized and matchingCard gets resized in utils.getMatchingCard()
        frame = cv2.resize(frame, (widthCard, heightCard))
        grayFrame = cv2.resize(grayFrame, (widthCard, heightCard))
        blurredFrame = cv2.resize(blurredFrame, (widthCard, heightCard))
        edgedFrame = cv2.resize(edgedFrame, (widthCard, heightCard))
        contourFrame = cv2.resize(contourFrame, (widthCard, heightCard))
        bigContour = cv2.resize(bigContour, (widthCard, heightCard))
        cardFrame = cv2.resize(cardFrame, (widthCard, heightCard))

        if maxBoxFrame.size > 0:
            maxBoxFrame = cv2.resize(maxBoxFrame, (widthCard, heightCard))
        else:
            # Create a blank frame if maxBoxFrame is empty
            maxBoxFrame = np.zeros((heightCard, widthCard), dtype=np.uint8)
        maxBoxContours = cv2.resize(maxBoxContours, (widthCard, heightCard))
        # print(f"Time to read and rotate image: {section_end - section_start:.4f} seconds")

        # An array of all 8 images
        imageArr = ([frame, maxBoxFrame, cardFrame, edgedFrame],
                    [contourFrame, bigContour, imgWarpColored, matchingCard])

        # Labels for each image
        labels = [["Original", "MaxBox", "Blurred", "Threshold"],
                  ["Contours", "Biggest Contour", "Warped Perspective", "Matching Card"]]

        # Stack all 8 images into one and add text labels
        stackedImage = utils.makeDisplayImage(imageArr, labels)

        # Display the image
        cv2.imshow("Card Finder", stackedImage)

        if not camFeed:  # If reading image file, display image until key is pressed
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
    if camFeed:
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
    camFeed = False#Set to true if camera is being used
    cam = None#Initializes the cam variable 
    select_crop_area
    if camFeed:
        initCam = timeit.default_timer()
        cam = cv2.VideoCapture(1)
        initCamstop = timeit.default_timer()
        print('Time to init. camera' + str(initCam-initCamstop))
    if camFeed:
        if not cam.isOpened():
            print("Error: Could not initialize camera.")
            cam = None
    if cam and cam.isOpened() or cam == None:     
        while True:
            starttot=  timeit.default_timer() # Begins timers to estimate the duration of a loop which was used to measure program efficiency
            # board.digital[backward_pin].write(1) #Sets the DC motor direction backward to prevent card from advancing until it is scanned.
            # board.digital[forward_pin].write(0) #Sets forward pin to 0 

            time.sleep(delay_time) 
            # resetServos(flippers)
            cardinfo = readCard(n, cam)  # Finds and reads from a saved image or live feed
            # board.digital[backward_pin].write(0)    
            # board.digital[forward_pin].write(1)
            # sortingLogic(cardinfo)
            time.sleep(3) #Delay time included so card has time to reach its destination before resetting. 
            endtot = timeit.default_timer()
            print('Length of total loop:' + str(endtot-starttot)) #Prints duration of loop for one card then loop restarts.
            n = n + 1
    if cam:
        cam.release()
        cv2.destroyAllWindows()
            
