#!/opt/local/bin/perl -w

# Velocity Painting by [Mark Wheadon](https://github.com/MarkWheadon) is licensed under a [Creative Commons Attribution 4.0
# International License](http://creativecommons.org/licenses/by/4.0/).
# Based on a work at https://github.com/MarkWheadon/velocity-painting.

#Nathans notes
#Install python. Go to the python scripts folder to find pip.exe. Run pip install Pillow.


import sys
from PIL import Image
import re
import math

#if not ((len(sys.argv) > 0 and
#   ((sys.argv[1] == '-projectX' and len(sys.argv) >= 10) or
#   (ARGV[0] == '-cylinderZ' and sys.argv >= 9)))
#   sys.exit("""Arguments incorrect. Correct usage:
#Usage:
#  0 -projectX  printCentreX printCentreY imageWidth imageHeight zOffset targetSpeed lowSpeed highSpeed imageFile [sourceGcodeFile] > paintedGcodeFile
#  0 -cylinderZ printCentreX printCentreY            imageHeight zOffset targetSpeed lowSpeed highSpeed imageFile [sourceGcodeFile] > paintedGcodeFile
#  
"""
printCentre{X,Y} is the centre of the print in the printer's coordinate space, in mm.
When the print in centred on the bed then printCentre{X,Y} is 0,0 for most (all?) detas. 125,125 for the Prusa i3 MK2.
imageWidth and imageHeight are also in mm.
Specifying an imageWith of '-' sets it to the correct width for the specified height.
Specifying an imageHeight of '-' sets it to the correct height for the specified width.
targetSpeed is the speed of the vectors you wish to manipulate
(so slice the model with all speeds set to this value).
lowSpeed is the required speed for the slow parts of the print
highSpeed is the required speed for the quick parts of the print
imageFile is the image to be mapped onto the print.

All speeds above are in mm/min.
END
"""

sys.argv.pop(0)
projectionMode = sys.argv.pop(0)
projectedImageWidth = None

printCentreX = int(sys.argv.pop(0))
printCentreY = int(sys.argv.pop(0))

if (projectionMode  == '-projectX'):
    projectedImageWidth = sys.argv.pop(0)

projectedImageHeight = sys.argv.pop(0)

zOffset = int(sys.argv.pop(0))
targetSpeed = int(sys.argv.pop(0))
lowSpeed = int(sys.argv.pop(0))
highSpeed = int(sys.argv.pop(0))
imageFile = sys.argv.pop(0)
gCodeFile = sys.argv.pop(0)
outputFile = sys.argv.pop(0)

image = Image.open(imageFile)
pixels = image.convert('RGB')
#Get image width and height
imageWidth = image.width
imageHeight = image.height

print('Image width, height: %s, %s' % (imageWidth, imageHeight))

if (((projectionMode == '-cylinderZ') or projectedImageWidth == '-') and projectedImageHeight == '-'):
    sys.exit('You must set either the image width or its height, or both.')

if projectedImageWidth:
    if (projectedImageWidth == '-'):
        projectedImageWidth = projectedImageHeight * imageWidth / imageHeight
    else:
        projectedImageWidth = int(projectedImageWidth)

if (projectedImageHeight == '-'):
    projectedImageHeight = projectedImageWidth * imageHeight / imageWidth
else:
    projectedImageHeight = int(projectedImageHeight)

maxVecLength = .1 # Longest vector in mm. Splits longer vectors. Very small -> long processing times.

oldX = None
oldY = None
oldZ = None
currentZ = None
lastZOutput = -1

outputFile = open(outputFile, 'w')

def surfaceSpeed(x, y, z):
    if (projectionMode == '-cylinderZ'):
        return surfaceSpeedCylinderZ(x, y, z)
    elif (projectionMode == '-projectX'):
        return surfaceSpeedProjectX(x, y, z)

def surfaceSpeedCylinderZ(x, y, z):
    global pixels
    zNormalized = (z - zOffset) / projectedImageHeight

    theta = math.atan2(y - printCentreY, x - printCentreX) + math.pi # 0 to 2pi
    xNormalized = theta / (2 * math.pi)

    imageX = xNormalized * imageWidth
    imageY = imageHeight - zNormalized * imageHeight

    if (imageX < 0 or imageX >= imageWidth or imageY < 0 or imageY >= imageHeight):
        return highSpeed
        # return lowSpeed

    # return highSpeed - image->GetPixel(x=>imageX, y=>imageY)  * (highSpeed - lowSpeed)
    #Returns a 'normalized' pixel from 0 to 1. Is this equivelant to (R/255 + G/255 + B/255) / 3? (0 would be black and 1 for white)
    pixel = pixels.getpixel((imageX, imageY))
    pixel_intensity = (pixel[0] / 255 + pixel[1] / 255 + pixel[2] / 255) / 3 #This wont work for single band images, needs to be addressed. Also a better intensity for color images based on the human eye is (red * 0.299) + (green * 0.587) + (blue * 0.114)
    return lowSpeed + pixel_intensity  * (highSpeed - lowSpeed)

def surfaceSpeedProjectX(x, y, z):
    global pixels
    xNormalized = (x - printCentreX + projectedImageWidth / 2) / projectedImageWidth
    zNormalized = (z - zOffset) / projectedImageHeight

    imageX = xNormalized * imageWidth
    imageY = imageHeight - zNormalized * imageHeight

    if (imageX < 0 or imageX >= imageWidth or imageY < 0 or imageY >= imageHeight):
            # return highSpeed
        return lowSpeed

    # return highSpeed - image->GetPixel(x=>imageX, y=>imageY)  * (highSpeed - lowSpeed)
    pixel = pixels.getpixel((imageX, imageY))
    pixel_intensity = (pixel[0] / 255 + pixel[1] / 255 + pixel[2] / 255) / 3 #This wont work for single band images, needs to be addressed. Also a better intensity for color images based on the human eye is (red * 0.299) + (green * 0.587) + (blue * 0.114)
    return lowSpeed + pixel_intensity  * (highSpeed - lowSpeed)

def outMove(x, y, z, e, extra):
    global lastZOutput
    zCommand = ''
    if (z != lastZOutput):
        zCommand = ' Z%.3f' % z

    added = ''
    if (extra):
        added = ' ; added'

    outputFile.write("G1 X%.3f Y%.3f%s E%.3f F%.3f%s\n" % (x, y, zCommand, e, surfaceSpeed(x, y, z), added))
    lastZOutput = z

with open(gCodeFile) as f:
    for line in f:
        try:
            x = y = z = e = f = None
            line = line.rstrip()

            #Replace /r with nothing
            #line =~ s/\r//g
            line = line.replace('/r', '')

            #(x, y, z, e, f) =line =~ /G1 X([^\s]+) Y([^\s]+) Z([^\s]+) E([^\s]+) F(targetSpeed)/
            #The /.../ mean search for the inside. [^\s]+ = at least one of anything but whitespace

            #This could be cleaner. For one the groups() can be given names and made optional so this can be combined into a single matching group
            mo = re.search(r'G1 X([^\s]+) Y([^\s]+) Z([^\s]+) E([^\s]+) F(%s)' % targetSpeed, line)
            if mo:
                x, y, z, e, f = [float(s) for s in mo.groups()]
            else:
                mo = re.search(r'G1 X([^\s]+) Y([^\s]+) E([^\s]+) F(%s)' % targetSpeed, line)
                if mo:
                    x, y, e, f = [float(s) for s in mo.groups()]
                else:
                    mo = re.search(r'G1 X([^\s]+) Y([^\s]+) Z([^\s]+) E([^\s]+)', line)
                    if mo:
                        x, y, z, e = [float(s) for s in mo.groups()]
                    else:
                        mo = re.search(r'G1 X([^\s]+) Y([^\s]+) E([^\s]+)', line)
                        if mo:
                            x, y, e = [float(s) for s in mo.groups()]

            if (z):
                currentZ = z
            else:
                z = currentZ

            if x:
                if not oldZ:
                    outMove(x, y, z, e, 0)
                else:
                    
                    xd = x - oldX
                    yd = y - oldY
                    zd = z - oldZ
                    ed = e - oldE

                    length = math.sqrt(xd * xd + yd * yd + zd * zd)

                    if (length <= maxVecLength):
                        outMove(x, y, z, e, 0)
                    else:
                        lastSegOut = -1

                        #Get speed: Slow speed outside the image, higher speed based on pixel intensity
                        oSlow = surfaceSpeed(oldX, oldY, oldZ)

                        #Split GCode move into parts. Length of move / maxVectorLength
                        nSegs = int(length / maxVecLength + 0.5)

                        xDelta = xd / nSegs
                        yDelta = yd / nSegs
                        zDelta = zd / nSegs
                        eDelta = ed / nSegs

                        for i in range(1, nSegs+1):
                            nx = oldX + xDelta * i
                            ny = oldY + yDelta * i
                            nz = oldZ + zDelta * i

                            slow = surfaceSpeed(nx, ny, nz)

                            if ((slow != oSlow) and (i > 1)):
                                    # pattern has changed. Time to output the vector so far
                                    outMove(oldX + xDelta * (i - 1),
                                            oldY + yDelta * (i - 1),
                                            oldZ + zDelta * (i - 1),
                                            oldE + eDelta * (i - 1),
                                            1)
                                    oSlow = slow
                                    lastSegOut = i
                        if (lastSegOut != nSegs):
                                outMove(x, y, z, e, 0)
                oldX = x
                oldY = y
                oldZ = z
                oldE = e
            else:
                mo = re.search(r'G1 X([^\s]+) Y([^\s]+) Z([^\s]+)', line)
                if mo:
                    oldX, oldY, oldZ = [float(s) for s in mo.groups()]
                else:
                    mo = re.search(r'G1 X([^\s]+) Y([^\s]+)', line)
                    if mo:
                        oldX, oldY = [float(s) for s in mo.groups()]
                mo = re.search(r'Z([\d\.]+)', line)
                if mo:
                    currentZ = oldZ = [float(s) for s in mo.groups()][0]
                mo = re.search(r'E([\d\.]+)', line)
                if mo:
                    oldE = [float(s) for s in mo.groups()][0]
                outputFile.write("%s\n" % line)
        except:
            print('Error on line: %s' % line)
            raise

outputFile.close()
