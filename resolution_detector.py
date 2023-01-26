from PIL import Image, ImageFilter
import numpy as np
import cv2
import math
import sys
import argparse
import json


#read raw byte data
def from_file(file_path):

        data_buffer = None

        try:
            with open(file_path, "rb") as file:
                data_buffer = file.read()
                return data_buffer

        except EnvironmentError as err:
            raise Exception(
                "Error occured while trying to read from file {}.\nReason: {}".
                format(file_path, err))


#find every possible resolution, limited to 1/4 height to width ratio by default
def possibleResolutionsFinder(byteString,componentsPerPixel):
    allPixels = len(byteString)/componentsPerPixel
    calculatedResolution=[]
    result = []
    for i in range(math.floor((allPixels/heightToWidthRatio)**0.5), int(allPixels**0.5)+1):
        if allPixels % i == 0:
            calculatedResolution.append(i)
            calculatedResolution.append(int(allPixels//i))
            result.append(calculatedResolution)
            calculatedResolution=[]
            if i != int(allPixels//i):
                calculatedResolution.append(int(allPixels//i))
                calculatedResolution.append(i)
                result.append(calculatedResolution)
                calculatedResolution=[]
    return reversed(result)


try:
    with open('config.json', 'r') as f:
        config = json.load(f)

    threshold = config['threshold']
    heightToWidthRatio = config['heightToWidthRatio']

except: 
    print("Couldn't open config.json, proceeding with default values")
    threshold = 100
    heightToWidthRatio = 4


parser = argparse.ArgumentParser()
parser.add_argument('path', type=str, help='Path to the binary file')
args = parser.parse_args()

try:
        rawImageData = from_file(args.path)
except Exception as e:
    print("Error:", e, file=sys.stderr)
    sys.exit(1)


rawImageData = from_file(sys.argv[1])

#3 and 4 byte formats handling, TODO 2 and 1,5
colorFormats=[
             ['RGB',3],
             ['RGBA',4]
             ]

edgesDetected=[]
objectsDetected=[]
imageColorFormat=[]
allPossibleResolutions=[]

for id in range(len(colorFormats)):
    
    possibleResolutions = list(possibleResolutionsFinder(rawImageData,colorFormats[id][1]))

    for resolution in possibleResolutions:

        currentFormat=colorFormats[id][0]
        printableImage = Image.frombytes(currentFormat,resolution,rawImageData)
        #conversion to grayscale
        printableImage = printableImage.convert("L")
        printableImage = printableImage.point( lambda p: 255 if p > threshold else 0)
        #conversion to numpy array for object detection
        np_printableImage = np.array(printableImage)
        thresh, binaryImage = cv2.threshold(np_printableImage, 128, 255, cv2.THRESH_BINARY)
        # Find contours
        contours, _ = cv2.findContours(binaryImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Append the number of contours
        objectsDetected.append(len(contours))
        # Edge detecting filter
        printableImage = printableImage.convert('1')
        printableImage = printableImage.filter(ImageFilter.Kernel((3, 3), (-1, -1, -1, -1, 8, -1, -1, -1, -1), 1, 0))
        # Append the number of edge pixels
        edgePixels = np.sum(printableImage)
        edgesDetected.append(edgePixels)
        imageColorFormat.append(currentFormat)
        allPossibleResolutions.append(resolution)


evaluation = [list(a) for a in zip(allPossibleResolutions, edgesDetected, objectsDetected, imageColorFormat)]
#sorting by the number of detected edge pixels
evaluation.sort(key=lambda a: a[1])

#sorting by detected objects in uncertain cases
if(evaluation[1][1]<evaluation[0][1]*2):
    if(evaluation[1][2]<evaluation[0][2]):
        buffer = evaluation[0]
        evaluation[0]=evaluation[1]
        evaluation[1]=buffer

best_resolution = evaluation[0][0]
best_format = evaluation[0][3]

#printing final results
for id, result in enumerate(evaluation):
    if id == 0:
        print(best_resolution, ' <--  best resolution')
    else:
        badness = round((100*((evaluation[id][1]-evaluation[0][1])/evaluation[0][1])), 2)
        if(badness<0):
            print(evaluation[id][0], ' <-- ',badness,'% worse fit, result rejected due to abnormal object detection')
        #printing information about relatively close cases
        elif(badness<500):
            print(evaluation[id][0], ' <-- ',badness,'% worse fit')

#printing final image
printableImage = Image.frombytes(best_format,best_resolution,rawImageData)
printableImage.show()