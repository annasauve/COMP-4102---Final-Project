import glob
import cv2 as cv
import numpy as np
import math

# Function which separates atlas into structures according to their pixel values

# Frontal lobe: 133
# Occipital lobe: 141
# Basal ganglia: 63
# Temporal lobe: 213
# Parietal lobe: 88
# Corpus callosum: 177

# Input:
#   img = atlas image
# Output:
#   frontal_lobe, occipital_lobe, basal_ganglia, temporal_lobe, parietal_lobe, corpus_callosum = arrays containing pixel indexes that correspond to those structures
def atlas_sections(img):
    frontal_lobe = []
    occipital_lobe = []
    basal_ganglia = []
    temporal_lobe = []
    parietal_lobe = []
    corpus_callosum = []

    # iterate through the atlas image and sort the pixels according to their color
    x, y = img.shape
    for i in range(0, x):
        for j in range(0, y):
            pixel = img[i][j]
            if pixel == 133:
                frontal_lobe.append([i,j])
            elif pixel == 141:
                occipital_lobe.append([i,j])
            elif pixel == 63:
                basal_ganglia.append([i,j])
            elif pixel == 213:
                temporal_lobe.append([i,j])
            elif pixel == 88:
                parietal_lobe.append([i,j])
            elif pixel == 177:
                corpus_callosum.append([i,j])

    return [frontal_lobe, occipital_lobe, basal_ganglia, temporal_lobe, parietal_lobe, corpus_callosum]

# Function to classify the tumor and locate it
# Input:
#   tumor = tumor contour
#   sections = array which contains the sections found in atlas_sections
# Output:
#   text = array containing strings to indicate where the tumor is located
def classify(tumor, sections):
    frontal_lobe = sections[0]
    occipital_lobe = sections[1]
    basal_ganglia = sections[2]
    temporal_lobe = sections[3]
    parietal_lobe = sections[4]
    corpus_callosum = sections[5]

    # need this so a string is only added once
    f = 0
    o = 0
    b = 0
    t = 0
    p = 0
    c = 0

    text = [] # will contain locations

    # iterate through the tumor pixels and check if they are in the predefined sections
    for x in tumor:
        if [x[0][0],x[0][1]] in frontal_lobe and f == 0:
            text.append("frontal lobe")
            f = True
        elif [x[0][0],x[0][1]] in occipital_lobe and o == 0:
            text.append("occipital lobe")
            o = True
        elif [x[0][0],x[0][1]] in basal_ganglia and b == 0:
            text.append("basal ganglia")
            b = True
        elif [x[0][0],x[0][1]] in temporal_lobe and t == 0:
            text.append("temporal lobe")
            t = True
        elif [x[0][0],x[0][1]] in parietal_lobe and p == 0:
            text.append("parietal lobe")
            p = True
        elif [x[0][0],x[0][1]] in corpus_callosum and c == 0:
            text.append("corpus callosum")
            c = True

    return text


# Function that includes all the necessary image preprocessing steps
# 1. Removing image noise to improve contrast
# 2. Bias correction: I have chosen to use histogram to find values to adjust brightness and contrast. I've done some tests and found that clipping the histogram at 10% gives the best results.
# 3. Filtering: I finish the preprocessing step by applying a sharpening filter to make some of the features stand out. This will be useful when applying edge detection later.

# Input:
#   img = original image before preprocessing
# Output:
#   img_s = image after preprocessing
def preprocessing(img):

    # denoise the image
    img_d = cv.fastNlMeansDenoising(img, None, 5, 7, 21) # did some tests with different filter numbers, 5 is the best. it conserves the most detail while removing a decent amount of noise.

    # bias correction using histogram
    histogram = cv.calcHist([img_d], [0], None, [256], [0,256]) # get histogram

    # get histogram distribution
    distribution = []
    distribution.append(float(histogram[0]))
    for i in range(1, len(histogram)):
        distribution.append(distribution[i-1] + float(histogram[i]))

    # clip the histogram at 3%
    max = distribution[-1]
    clip = (3 * max/100) / 2

    # calculate minimum and maximum gray values in the image
    min_g = 0
    while distribution[min_g] < clip:
        min_g += 1

    max_g = len(histogram) -1
    while distribution[max_g] >= (max - clip):
        max_g -= 1

    # calculate gain and bias for the image, will be used to adjust the brightness and contrast
    gain = 255 / (max_g - min_g)
    bias = -min_g * gain

    # brightness and contrast adjustment after calculating using histogram values
    img_h = cv.convertScaleAbs(img_d, alpha=gain, beta=bias)

    # sharpen the image to make features stand out - THIS IS NOT NECESSARY (it actually makes the tumors harder to find)
    # sharp_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) # use classic sharpening filter
    # img_s = cv.filter2D(img_h, -1, sharp_filter)

    return img_h

# Function that removes skull from the image. At the end we only have the brain which is easier to manipulate.

# Input:
#   img = original image
# Output:
#   img_b = image without skull (only brain left)
def skull_stripping(img):
    img_b = img.copy()

    thresh, img_t = cv.threshold(img, 0, 225,cv.THRESH_OTSU) # threshold with otsu, will get binary transformation
    # cv.imshow("after otsu", img_t)

    # get markers (m) for connected components of the otsu image
    comp, m = cv.connectedComponents(img_t)

    # separate image into areas according to component markers
    areas = [np.sum(m == x) for x in range(np.max(m)) if x!=0]

    # find max of the areas using np.argmax, this should be the brain since it is the largest connected component
    max = np.argmax(areas) + 1

    # make a mask which contains only the markers that are in the max areas
    mask = m == max

    # remove everything that is not part of the mask (remove skull)
    img_b[mask == False] = 0

    # cv.imshow("brain only", img_b)

    return img_b

# Apply segmentation to the image using a tozero threshold. Then color the segmented parts with different intensities.

# Input:
#   img = image with no skull
#   img_s = image with skull
# Output:
#   img_c = image after segmentation with colored parts
#   img_t = thresholded image
def segmentation(img, img_s):

    thresh, img_t = cv.threshold(img, 125, 255, cv.THRESH_TOZERO)

    # cv.imshow('thresholding', img_t)

    img_c = cv.cvtColor(img_s, cv.COLOR_GRAY2RGB)

    x, y = img.shape

    for i in range(0, x-1):
        for j in range(0, y-1):
            if img_t[i][j] != 0:
                # print(img_t[i][j])
                intensity = img_t[i][j] / 255 # getting intensity % of the grays to adjust the color
                # print(intensity)
                img_c[i][j] = (math.ceil(87*intensity), math.ceil(46*intensity), math.ceil(148*intensity)) # adjusting the color based on intensity


    # cv.imshow("color", img_c)

    return img_c, img_t

# Finds a tumor in given image and returns an image which highlights this tumor.

# Input:
#   img = thresholded image from segmentation step
#   img_c = original color image (will draw tumor contour on this)
# Output:
#   img_tumor = image with highlighted tumor
def find_tumor(img, img_c):
    # create 10 x 5 kernel to use in morphological transformations
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (10, 5))

    # use closing function to remove holes in image
    img_close = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)

    # apply erosion function to erode foreground. did some testing and 15 is a good number of iterations.
    img_erode = cv.erode(img_close, None, iterations = 15)

    # apply dilation function to dilate foreground. apply this after erosion to remove noise in the thresholded image. did some testing and 15 is a good number of iterations.
    img_dilate = cv.dilate(img_erode, None, iterations = 15)

    # use built in canny edge detector to find edges of the shapes in given image
    img_edges = cv.Canny(img_dilate, 20, 60, 3)

    # find contours from the canny edges
    contours, _ = cv.findContours(img_edges.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # find the biggest contour. I assume that this is the tumor. Draw largest contour.
    if len(contours) != 0: # if true, means that something was found (hopefully tumor)
        max_contour = max(contours, key = cv.contourArea)
        cv.drawContours(img_c, [max_contour], -1, (0, 255, 0), 2)
        return img_c.copy(), max_contour

    else: # need this condition in case no contour was found (no tumor was found)
        cv.drawContours(img_c, contours, -1, (0, 255, 0), 2)
        return img_c.copy(), []

# ------------------------ MAIN ------------------------ #
path = glob.glob("data/*.jpg") # get path

a_c = cv.imread("data/other/atlas_gray.jpg") # get brain atlas image
a = cv.cvtColor(a_c, cv.COLOR_BGR2GRAY) # make sure it is grayscale
a = cv.resize(a, (600,600))

sections = atlas_sections(a) # get sections

# loop trough image folder
for img in path:
    square = cv.imread("data/other/square.jpg") # black square where we will write stuff
    square = cv.resize(square, (700,500))

    i_color = cv.imread(img) # import brain image
    i_gray = cv.cvtColor(i_color,cv.COLOR_BGR2GRAY) # make sure it is grayscale
    i_gray = cv.resize(i_gray, (600,600))
    i_color = cv.resize(i_color, (600,600))

    # cv.imshow("original image", i_gray)

    i_gray = preprocessing(i_gray)
    # cv.imshow("after preprocessing", i_gray)

    no_skull = skull_stripping(i_gray)

    i_layers, i_thresholded = segmentation(no_skull, i_gray)
    # cv.imshow("segmentation", i_layers)
    # cv.imshow("threshold", i_thresholded)

    i_tumor, contour = find_tumor(i_thresholded, i_color)
    cv.imshow("tumor", i_tumor)

    if len(contour) != 0:
        location = classify(contour, sections)
        # print(location)
        origin = 50
        if len(location) > 0:
            square = cv.putText(square, "A tumor was detected and it affects:", (50,origin), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            for loc in location:
                origin += 50
                square = cv.putText(square, loc, (50,origin), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
        else:
            square = cv.putText(square, "A tumor was detected", (50,origin), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            square = cv.putText(square, "but could not be located.", (50,origin+50), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    else:
        square = cv.putText(square, "Nothing was detected.", (50,50), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
        print("Nothing was detected")

    cv.imshow("text", square)

    cv.waitKey()
