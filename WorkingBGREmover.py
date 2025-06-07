import cv2
import numpy as np
# import timeit
from IPython.display import display, clear_output
import PIL.Image
import io
import utils

widthCard = 330
heightCard = 440
cam = cv2.VideoCapture(1)
background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, 
                                                           varThreshold=20, detectShadows=False)

blackImg = np.zeros((heightCard, widthCard, 3), np.uint8)

def biggestContour(contours, min_area=100000): ###10000 might be too large?
    largest = None
    max_area = 0
    approx_corners = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:  # Only consider contours with area larger than min_area
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(approx) == 4 and area > max_area:
                largest = contour
                max_area = area
                approx_corners = approx

    return approx_corners, max_area
def readCard(n, cam): #Scans the card using a computer vision and hashing comparison to scan the card. The output of this function returns card information needed for sorting algorithm full program can be found on github

    try:
        while True:
            check, frame = cam.read()
            if not check:
                break
            
            rot90frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            grayFrame = cv2.cvtColor(rot90frame, cv2.COLOR_BGR2GRAY)
            
            # Adaptive Histogram Equalization for contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhancedGray = clahe.apply(grayFrame)
            
            # Gaussian Blur to reduce noise
            blurredFrame = cv2.GaussianBlur(enhancedGray, (27, 27), 0)

            # Background Subtraction
            fg_mask = background_subtractor.apply(blurredFrame)
            foreground = cv2.bitwise_and(blurredFrame, blurredFrame, mask=fg_mask)

            # Edge Detection (Canny)
            edgedFrame = cv2.Canny(foreground, threshold1=50, threshold2=150)
            
            # Morphological Operations for cleaner edges
            kernel = np.ones((5, 5))
            frameDial = cv2.dilate(edgedFrame, kernel, iterations=2)
            frameThreshold = cv2.erode(frameDial, kernel, iterations=1)

            # Contour Detection
            contours, _ = cv2.findContours(frameThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contourFrame = rot90frame.copy()
            cv2.drawContours(contourFrame, contours, -1, (0, 255, 0), 10)

            # Find the biggest contour
            corners, maxArea = biggestContour(contours, min_area=5000)  # Adjust min_area as needed
            imgWarpColored = np.zeros((heightCard, widthCard, 3), np.uint8)
            matchingCard= np.zeros((heightCard, widthCard, 3), np.uint8)
            found = False
            if len(corners) == 4:
                corners = [corners[0][0], corners[1][0], corners[2][0], corners[3][0]]
                corners = utils.reorderCorners(corners)
                bigContour = utils.drawRectangle(contourFrame, corners)
                pts1 = np.float32(corners)
                pts2 = np.float32([[0, 0], [widthCard, 0], [0, heightCard], [widthCard, heightCard]])

                # Perspective Transform
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                imgWarpColored = cv2.warpPerspective(rot90frame, matrix, (widthCard, heightCard))

                # Match the card
                found, matchingCard, cardinfo = utils.findCard(imgWarpColored.copy())

            else:
                bigContour = rot90frame.copy()  # If no contour is found, show original frame

            # Display results (resize images as needed)
            cv2.imshow("All Contours", contourFrame)

            cv2.imshow("Contours", bigContour)
            cv2.imshow("Warped", imgWarpColored)
            cv2.imshow("Found", matchingCard)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if found:  # If the input is a video and a matching card has been found
                # print('\n\nPress any key to exit.')
                # sortingLogic(cardinfo)
                cv2.waitKey(0)
                break

        # Stops cameras and closes display window
        # if phoneCamFeed:
        #      cam.release()


    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        cam.release()
        cv2.destroyAllWindows()
    return cardinfo
n = 0         
cardinfo = readCard(n,cam)  # Finds and reads from a saved image or live feed
