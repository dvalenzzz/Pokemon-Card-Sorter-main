
import cv2
import numpy as np

img = cv2.imread('C:/Users/valen/Desktop/Taxes 2024/cuandofokenpagan.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (3, 3), 0)
edges = cv2.Canny(blurred, 80, 150)

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter and sort contours by area
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Display area and perimeter for top 3
for i, cnt in enumerate(contours[:3]):
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)
    print(f"Contour {i+1}: Area = {area}, Perimeter = {perimeter}")
    cv2.drawContours(img, [cnt], -1, (0, 255, 0), 3)

cv2.imshow("Top Contours", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Option: Instead of relying on 4 corners,
# use cv2.minAreaRect to fit the best rotated rectangle:
# rect = cv2.minAreaRect(largest_cnt)
# box = cv2.boxPoints(rect)
# box = np.int0(box)
# cv2.drawContours(img, [box], 0, (0, 0, 255), 2)

# This method handles rotated and noisy contours better.