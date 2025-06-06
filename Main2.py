import cv2
import numpy as np
import cardData
import utils
import timeit
import time
import pyfirmata2 as pyfirmata

# Initialize Arduino
board = pyfirmata.Arduino('COM8')  # Change this to your Arduino port
fl1, fl2, fl3 = 9, 10, 11
forward_pin, backward_pin = 8, 12
delay_time = 3 
flippers = [fl1, fl2, fl3]

# Set pin modes and initial positions
for flipper in flippers:
    board.digital[flipper].mode = pyfirmata.SERVO
    board.digital[flipper].write(180)
    time.sleep(0.1)
board.digital[forward_pin].mode = pyfirmata.OUTPUT
board.digital[backward_pin].mode = pyfirmata.OUTPUT

def resetServos(flippers):
    for flipper in flippers:
        board.digital[flipper].write(180)

def readCard(n, cam):
    widthCard = utils.getWidthCard()
    heightCard = utils.getHeightCard()
    
    while True:
        blackImg = np.zeros((heightCard, widthCard, 3), np.uint8)
        check, frame = cam.read()
        if not check:
            print("Failed to capture image")
            break

        rot90frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        grayFrame = cv2.cvtColor(rot90frame, cv2.COLOR_BGR2GRAY)
        blurredFrame = cv2.GaussianBlur(grayFrame, (3, 3), 0)
        edgedFrame = cv2.Canny(blurredFrame, threshold1=80, threshold2=150)
        
        contours, _ = cv2.findContours(edgedFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        corners, maxArea = utils.biggestContour(contours)
        
        imgWarpColored = blackImg
        if len(corners) == 4:
            corners = utils.reorderCorners([corner[0] for corner in corners])
            pts1 = np.float32(corners)
            pts2 = np.float32([[0, 0], [widthCard, 0], [0, heightCard], [widthCard, heightCard]])
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            imgWarpColored = cv2.warpPerspective(rot90frame, matrix, (widthCard, heightCard))
            found, matchingCard, cardinfo = utils.findCard(imgWarpColored.copy())
        else:
            found = False
            matchingCard = np.zeros((heightCard, widthCard, 3), dtype=np.uint8)
            cardinfo = None

        imageArr = ([rot90frame, grayFrame, blurredFrame, edgedFrame],
                    [blackImg, blackImg, imgWarpColored, matchingCard])
        for image in imageArr:
            print(imageArr[image].size)
        labels = [["Original", "Gray", "Blurred", "Edges"],
                  ["Blank", "Blank", "Warped", "Matching"]]

        stackedImage = utils.makeDisplayImage(imageArr, labels)
        cv2.imshow("Card Finder", stackedImage)

        if cv2.waitKey(1) & 0xFF == ord('q') or found:
            break

    cv2.destroyAllWindows()
    return cardinfo

def set_flipper(n):
    board.digital[n].write(110)
    print(f"Set servo on pin {n} to 110 degrees")

def sortingLogic(matchingCardData):
    inp = {"Pokémon": 1, "Trainer": 2, "Energy": 3}.get(matchingCardData['Card Type'], 0)
    if inp == 1:
        set_flipper(fl1)
        print("Flipper 1: Pokémon")
    elif inp == 2:
        set_flipper(fl2)
        print("Flipper 2: Trainer")
    elif inp == 3:
        set_flipper(fl3)
        print("Flipper 3: Energy")
    else:
        print("Other Pile")

if __name__ == '__main__':
    try:
        isFirst = False
        if isFirst:
            cardData.createDatabase()

        n = 0
        phoneCamFeed = True
        cam = cv2.VideoCapture(1) if phoneCamFeed else None
        if not cam or not cam.isOpened():
            print("Error: Could not initialize camera.")
            cam = None

        if cam:
            while True:
                board.digital[backward_pin].write(1)
                board.digital[forward_pin].write(0)
                time.sleep(delay_time)
                resetServos(flippers)

                cardinfo = readCard(n, cam)
                if cardinfo:
                    sortingLogic(cardinfo)
                time.sleep(5)
                board.digital[backward_pin].write(0)
                board.digital[forward_pin].write(1)
                
                n += 1

    except KeyboardInterrupt:
        print("Process interrupted by user.")

    finally:
        if cam:
            cam.release()
        cv2.destroyAllWindows()
        board.exit()
        print("Closed camera and Arduino connection.")
