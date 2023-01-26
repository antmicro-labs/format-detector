# Image Resolution and Format Detector

This script reads in a binary file and tries to determine the best resolution and format for the image. It uses edge detection and object detection to determine the best resolution and format.

## Description

This script reads in a binary file and tries to determine the best resolution and format for the image. It first reads in a config.json file to set threshold and height-to-width ratio values, and then uses the argparse library to take in the path of the binary file as an argument. It then reads the binary file using the from_file function and checks all possible resolutions using the possibleResolutionsFinder function. It then iterates through each possible resolution and color format, converts the image to grayscale, detects edges and objects, and appends the number of edges and objects detected, as well as the resolution and format, to corresponding lists. It then uses the evaluation list to sort by the number of edges detected and, in cases of uncertainty, by the number of objects detected. It then prints the best resolution and format, as well as the resolution and format of the next best options, and displays the final image.

## How to use

1. Make sure you have the necessary libraries installed: *`PIL`*, *`numpy`*, *`cv2`*, *`math`*, *`sys`*, *`argparse`*, and *`json`*
2. Run the script with the path to the binary file as an argument: *`python resolution_detection.py path/to/binary/file`*
3. The script will then output the best resolution and format for the image, as well as the resolution and format of the next best options.
4. The final image will also be displayed.

## Configuration

You can configure the script by creating a *`config.json`* file in the same directory as the script. This file should contain the following fields:
- *`threshold`*: a value between 0 and 255 that is used as the threshold for converting the image to grayscale
- *`heightToWidthRatio`*: a value that is used to limit the possible resolutions for the image (default is 4)

Example:

```
{
    "threshold": 100,
    "heightToWidthRatio": 4
}
```
