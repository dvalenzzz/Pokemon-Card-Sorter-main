import cv2

# Initialize video capture
cap = cv2.VideoCapture(0)  # or replace 0 with the video file path
background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Apply background subtraction
    fg_mask = background_subtractor.apply(frame)
    
    # Optional: clean up the mask with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        # Filter out small contours (noise)
        if cv2.contourArea(contour) < 1000:
            continue

        # Draw contours on the original frame
        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
    
    # Display the result
    cv2.imshow('Foreground Mask', fg_mask)
    cv2.imshow('Detected Objects', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
