import cv2 #resolve
import numpy as np
# define the list of boundaries
boundaries = [
    ([65, 45, 84], [61, 36, 82])
]
image = cv2.imread("/Users/standa/Image_4679.jpg")
# loop over the boundaries
for (lower, upper) in boundaries:
    # create NumPy arrays from the boundaries
    lower = np.array(lower, dtype = "uint8")
    upper = np.array(upper, dtype = "uint8")
 
    # find the colors within the specified boundaries and apply
    # the mask
    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask = mask)
 
    # show the images
cv2.imshow("images", np.hstack([image, output]))
cv2.waitKey(0)

cv2.imwrite( 'ddd.jpg', np.hstack([image, output]))