import glob
import cv2 as cv

path = glob.glob("data/*.jpg")
data = []
for img in path:
    i = cv.imread(img)
    i = cv.cvtColor(i,cv.COLOR_BGR2GRAY) # make sure it is grayscale
    # i = cv.resize(i,(500,500)) # resize so all images are the same

    cv.imshow("img", i)
    cv.waitKey()

    data.append(i)
