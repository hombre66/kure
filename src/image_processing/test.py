'''
Created on Oct 10, 2016

@author: standa
'''
import cv2
import numpy as np

img = cv2.imread("/Users/standa/Image_4679.jpg", 0)

ret, thresh = cv2.threshold(img, 127, 2,0)
image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
color = img
img = cv2.drawContours(color, contours, -1, (0,255,255), 2)
cv2.imwrite('dd.jpg', img)
cv2.imshow("contours", img)
cv2.waitKey()
cv2.destroyAllWindows()


