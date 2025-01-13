#!/usr/bin/env python

# Copyright (c) 2012 tyrok1
#
# This software is provided 'as-is', without any express or implied warranty. In
# no event will the authors be held liable for any damages arising from the use
# of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it freely,
# subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not claim
# that you wrote the original software. If you use this software in a product,
# an acknowledgment in the product documentation would be appreciated but is not
# required.
#
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
#
# 3. This notice may not be removed or altered from any source distribution.

# The license template for this license is available at:
# http://www.opensource.org/licenses/Zlib
# and is licensed under this license:
# http://creativecommons.org/licenses/by/2.5/


from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
from math import hypot
from math import atan2
import sys
from os import mkdir
from os import path
from os import sep
from math import pi


# The size of the search space - smaller is faster and less accurate
searchSize = (160, 160)
# [0...100] Percentage each pixel has to match the desired color to be considered a match
colorThreshold = 40


# Open the source file and pick out the color to search for
def GetSource(filename):
    original = Image.open(filename)
    original = ImageOps.exif_transpose(original)
    return original


# Gets a luminance channel representing the similarity to the desired color
def GetColor(im, channel):
    channels = [-0.5, -0.5, -0.5, 0]
    channels[int(channel)] = 1
    return ImageOps.autocontrast(im.convert("L", channels))


def FindMatchingPixels(im):
    # Find coordinates of pixels which match the desired color above a certain threshold
    intColorThreshold = int(colorThreshold / 100.0 * 255.0)
    matchingPixels = []
    for x in range(0, 159):
        for y in range(0, 159):
            if im.getpixel((x, y)) > intColorThreshold:
                # found one
                matchingPixels.append((x, y))

    return matchingPixels


# Find the dots in an image
# Returned values are each [strength, centerX, centerY]
def FindDots(im):
    # Search parameters
    maxDotSize = 10

    # Find all matching pixels to search
    matchingPixels = FindMatchingPixels(im)
    dots = []

    # For each matching pixel...
    for m in matchingPixels:
        # Try and find a dot which is close to it
        found = False
        for d in dots:
            # Calculate distance from the dot's center
            vec = (m[0] - d[1], m[1] - d[2])
            dist = hypot(vec[0], vec[1])

            # If it's close enough...
            if dist < maxDotSize:
                # Recalculate the average center of the dot
                d[0] = d[0] + 1
                amount = 1.0 / d[0]
                d[1] = d[1] * (1.0 - amount) + (m[0] + 0.5) * amount
                d[2] = d[2] * (1.0 - amount) + (m[1] + 0.5) * amount
                found = True
                break

        # If no close dot was found, start a new one
        if not found:
            dots.append([1, m[0], m[1]])

    return dots


# Transform dots back into source image space
def TransformDots(dots, searchImage, originalImage):
    # Transforms a single dot
    def TransformDot(dot):
        return (
            int(dot[1] * originalImage.size[0] / searchImage.size[0]),
            int(dot[2] * originalImage.size[1] / searchImage.size[1]),
        )

    return [TransformDot(dot) for dot in dots]


# Find a box given a top-left point
def FindQuad(dots, tlDotIndex):
    # Search parameters
    angles = [pi / 2, pi / 4, 0]
    tolerance = [0.25, 0.5, 0.25]
    minDists = [2, 10, 2]

    return FindDotsInRanges(dots, tlDotIndex, angles, tolerance, minDists)


# Find dots in a line
def FindDotsInLine(dots, tlDotIndex, horizontal=None):
    angles = [pi / 2]
    tolerance = [0.25]
    minDists = [2]
    if horizontal:
        angles = [0]

    points = [tlDotIndex]
    point = None
    lastPoint = tlDotIndex
    while True:
        point = FindDotsInRanges(dots, lastPoint, angles, tolerance, minDists)
        if point is None or len(point) < 2 or point[1] is None:
            break

        points.append(point[1])
        lastPoint = point[1]

    return points


# Find dots within specified angle ranges
def FindDotsInRanges(dots, tlDotIndex, angles, tolerance, minDists):
    nearDists = []
    outPoints = [tlDotIndex]

    # Temporary points that are corrected as we run
    angleRanges = [(angles[a] - tolerance[a], angles[a] + tolerance[a]) for a in range(0, len(angles))]

    # For each dot...
    for dotIndex, dot in enumerate(dots):
        # Calculate distance from this dot to the top left
        vec = (dot[0] - dots[tlDotIndex][0], dot[1] - dots[tlDotIndex][1])
        dist = hypot(vec[0], vec[1])

        for p in range(0, len(angleRanges)):
            # Initialize nearDists if they aren't already
            if len(nearDists) <= p:
                nearDists.append(10000)

            # Initialize output points if they aren't already
            if len(outPoints) <= p + 1:
                outPoints.append(None)

            if minDists[p] <= dist <= nearDists[p]:
                angle = atan2(vec[1], vec[0])
                if angleRanges[p][0] <= angle <= angleRanges[p][1]:
                    if p != 1 or (vec[0] > 0 and vec[1] > 0):
                        outPoints[p + 1] = dotIndex
                        nearDists[p] = dist

    return outPoints


# Finds and slices squares from an image using a dot pattern
def SliceSquares(imageOriginal, channel, drawDebuggingGrid, outputSize):
    # Finds a row of images from a top-left corner
    def FindRow(dots, tlDotIndex, rowNum):
        # Find the first quad
        quadIndices = FindQuad(dots, tlDotIndex)

        # Keep track of the bottom-left point of the first quad so we can return it later
        blPoint = None
        if len(quadIndices) > 1 and quadIndices[1] is not None:
            blPoint = quadIndices[1]

        # Start looking for more of 'em
        colNum = 0
        squares = []
        while (
            len(quadIndices) > 3
            and quadIndices[0] is not None
            and quadIndices[1] is not None
            and quadIndices[2] is not None
            and quadIndices[3] is not None
        ):
            # Translate from indices into coordinates
            quad = [dots[index] for index in quadIndices]

            # Found a box - crop it out of the original
            squares.append(
                ImageOps.autocontrast(
                    imageOriginal.transform(
                        outputSize,
                        Image.QUAD,
                        (
                            quad[0][0],
                            quad[0][1],
                            quad[1][0],
                            quad[1][1],
                            quad[2][0],
                            quad[2][1],
                            quad[3][0],
                            quad[3][1],
                        ),
                        Image.BICUBIC,
                    ),
                    2,
                )
            )
            colNum = colNum + 1

            # See if we're drawing an output grid for debugging
            if drawDebuggingGrid:
                for p in range(0, 3):
                    drawDebuggingGrid.line(
                        [(quad[p][0], quad[p][1]), (quad[p + 1][0], quad[p + 1][1])],
                        fill=(0, 64 + (p * 48), 0),
                        width=3,
                    )
                drawDebuggingGrid.line([(quad[3][0], quad[3][1]), (quad[0][0], quad[0][1])], fill=(0, 255, 0), width=3)

            # Continue on to the next quad in the line
            quadIndices = FindQuad(dots, quadIndices[3])

        # Return both the first point's bottom-left corner and the squares we found
        return (blPoint, squares)

    # Get an image containing brighter areas that match the desired color
    imageLuminance = GetColor(imageOriginal, channel)

    # Downsize the search space to speed things up and make the search
    # more accurate
    imageSearch = imageLuminance.resize(searchSize, Image.LANCZOS)

    # Find all of the dots in the image
    dots = TransformDots(FindDots(imageSearch), imageSearch, imageOriginal)
    if drawDebuggingGrid:
        for d in dots:
            drawDebuggingGrid.ellipse((d[0] - 10, d[1] - 10, d[0] + 10, d[1] + 10), fill="red")

    # If we have at least one dot...
    squares = []
    if len(dots) > 0:
        # Find the top-left dot
        topLeft = 0
        topLeftDist = hypot(dots[0][0], dots[0][1])
        for d in range(0, len(dots)):
            curDist = hypot(dots[d][0], dots[d][1])
            if curDist < topLeftDist:
                topLeft = d
                topLeftDist = curDist

        # See what style of dot placement we have
        topColumnDots = FindDotsInLine(dots, topLeft, True)
        leftRowDots = FindDotsInLine(dots, topLeft, False)
        if len(dots) < len(topColumnDots) * len(leftRowDots):
            # Interpolate the dots in between
            # First, check if we have all edge dots
            bottomColumnDots = FindDotsInLine(dots, leftRowDots[len(leftRowDots) - 1], True)
            rightRowDots = FindDotsInLine(dots, topColumnDots[len(topColumnDots) - 1], False)

            # Find lengths of top, right, bottom, and left edges so we can properly weight averages
            topVec = (
                dots[topColumnDots[len(topColumnDots) - 1]][0] - dots[topColumnDots[0]][0],
                dots[topColumnDots[len(topColumnDots) - 1]][1] - dots[topColumnDots[0]][1],
            )
            topFullLength = hypot(topVec[0], topVec[1])
            rightVec = (
                dots[rightRowDots[len(rightRowDots) - 1]][0] - dots[rightRowDots[0]][0],
                dots[rightRowDots[len(rightRowDots) - 1]][1] - dots[rightRowDots[0]][1],
            )
            rightFullLength = hypot(rightVec[0], rightVec[1])
            bottomVec = (
                dots[bottomColumnDots[len(bottomColumnDots) - 1]][0] - dots[bottomColumnDots[0]][0],
                dots[bottomColumnDots[len(bottomColumnDots) - 1]][1] - dots[bottomColumnDots[0]][1],
            )
            bottomFullLength = hypot(bottomVec[0], bottomVec[1])
            leftVec = (
                dots[leftRowDots[len(leftRowDots) - 1]][0] - dots[leftRowDots[0]][0],
                dots[leftRowDots[len(leftRowDots) - 1]][1] - dots[leftRowDots[0]][1],
            )
            leftFullLength = hypot(leftVec[0], leftVec[1])

            if len(topColumnDots) > len(bottomColumnDots):
                # Not enough dots on the bottom edge
                for c in range(1, len(topColumnDots) - 1):
                    topLength = hypot(
                        dots[topColumnDots[c]][0] - dots[topColumnDots[0]][0],
                        dots[topColumnDots[c]][1] - dots[topColumnDots[0]][1],
                    )
                    topRatio = topLength / topFullLength
                    newDot = (
                        dots[bottomColumnDots[0]][0] + bottomVec[0] * topRatio,
                        dots[bottomColumnDots[0]][1] + bottomVec[1] * topRatio,
                    )
                    dots.append(newDot)
                    if drawDebuggingGrid:
                        drawDebuggingGrid.ellipse(
                            (newDot[0] - 10, newDot[1] - 10, newDot[0] + 10, newDot[1] + 10), fill="blue"
                        )

                # Update the list of bottom edge dots
                bottomColumnDots = FindDotsInLine(dots, leftRowDots[len(leftRowDots) - 1], True)

            if len(leftRowDots) > len(rightRowDots):
                # Not enough dots on the right edge
                for r in range(1, len(leftRowDots) - 1):
                    leftLength = hypot(
                        dots[leftRowDots[r]][0] - dots[leftRowDots[0]][0],
                        dots[leftRowDots[r]][1] - dots[leftRowDots[0]][1],
                    )
                    leftRatio = leftLength / leftFullLength
                    newDot = (
                        dots[rightRowDots[0]][0] + rightVec[0] * leftRatio,
                        dots[rightRowDots[0]][1] + rightVec[1] * leftRatio,
                    )
                    dots.append(newDot)
                    if drawDebuggingGrid:
                        drawDebuggingGrid.ellipse(
                            (newDot[0] - 10, newDot[1] - 10, newDot[0] + 10, newDot[1] + 10), fill="blue"
                        )

                # Update the list of right edge dots
                rightRowDots = FindDotsInLine(dots, topColumnDots[len(topColumnDots) - 1], False)

            # Interpolate middle dots based on the edges
            for row, leftDot in enumerate(leftRowDots[1:-1]):
                try:  # Generate a row-wide vector
                    rightDot = rightRowDots[row + 1]
                    rowVec = (dots[rightDot][0] - dots[leftDot][0], dots[rightDot][1] - dots[leftDot][1])
                except Exception:
                    print(f"rightRowDots: {rightRowDots}")

                for col, topDot in enumerate(topColumnDots[1:-1]):
                    # Generate a column-wide vector
                    bottomDot = bottomColumnDots[col + 1]
                    colVec = (dots[bottomDot][0] - dots[topDot][0], dots[bottomDot][1] - dots[topDot][1])

                    # Figure out how far along the top and bottom sides we are
                    topLen = hypot(
                        dots[topDot][0] - dots[topColumnDots[0]][0], dots[topDot][1] - dots[topColumnDots[0]][1]
                    )
                    topRatio = topLen / topFullLength
                    bottomLen = hypot(
                        dots[bottomDot][0] - dots[bottomColumnDots[0]][0],
                        dots[bottomDot][1] - dots[bottomColumnDots[0]][1],
                    )
                    bottomRatio = bottomLen / bottomFullLength

                    # Figure out how much of the top ratio vs. the bottom ratio we should use
                    amountOfTop = 1.0 - (float(row + 1) / float(len(leftRowDots) - 1))

                    # Figure out how far along the row line we should go by weighted averaging the top and bottom ratios
                    ratioWithinRow = (topRatio * amountOfTop) + (bottomRatio * (1 - amountOfTop))

                    # Interpolate the point
                    newDot = (
                        dots[leftDot][0] + rowVec[0] * ratioWithinRow,
                        dots[leftDot][1] + rowVec[1] * ratioWithinRow,
                    )
                    dots.append(newDot)
                    if drawDebuggingGrid:
                        drawDebuggingGrid.ellipse(
                            (newDot[0] - 10, newDot[1] - 10, newDot[0] + 10, newDot[1] + 10), fill="blue"
                        )

        # Search for a row, then search for the next based on its bottom-left
        # point, until there are no more rows
        rowNum = 0
        while topLeft is not None:
            (topLeft, newRow) = FindRow(dots, topLeft, rowNum)
            squares.append(newRow)
            rowNum = rowNum + 1

    # Return whatever we found in a [y][x] array
    return squares



def main(inputFilename: str, channel: int, outputDir: str, outputSize: tuple[int, int]):
    # Create the output directory if it doesn't already exist
    if not path.exists(outputDir):
        mkdir(outputDir)

    # Downsize the search area to something a little more reasonable
    imageOriginal = GetSource(inputFilename)
    imageDebuggingGrid = GetColor(imageOriginal, channel).convert("RGB")
    drawDebuggingGrid = ImageDraw.Draw(imageDebuggingGrid)

    # Find all squares within the image
    squares = SliceSquares(GetSource(inputFilename), channel, drawDebuggingGrid, outputSize)

    # Save them all out
    numSlices = 0
    for y in range(0, len(squares)):
        for x in range(0, len(squares[y])):
            squares[y][x].save(outputDir + sep + "out-" + str(x) + "-" + str(y) + ".jpg")
            numSlices = numSlices + 1

    # Save out a debugging image
    imageDebuggingGrid.save(outputDir + sep + "lines.png")
    # Return the number of images saved
    return numSlices


if __name__ == "__main__":
    # Parse parameters
    if len(sys.argv) <= 1 or sys.argv[1] == "--help":
        print("Usage: slice.py inputfile [color [outputdir [width height]]]")
        print()
        print("inputfile = The input image file")
        print("color     = The dot color to search for: 0 = Red, 1 = Green, 2 = Blue")
        print("outputdir = The directory to output slices to.  Defaults to")
        print("            a directory with the same name as the input file.")
        print("width     = Desired width, in pixels, of output image.")
        print("height    = Desired height, in pixels, of output image.")
        print()
        print("Exit status for this  script is the number of slices output.")
        exit(0)

    # Input filename argument
    inputFilename = sys.argv[1]

    # Color argument
    if len(sys.argv) <= 2:
        channel = 2
    else:
        channel = sys.argv[2]

    # Output directory argument
    if len(sys.argv) <= 3:
        outputDir = inputFilename[:-4] + sep
    else:
        outputDir = sys.argv[3] + sep

    # Width/height
    if len(sys.argv) >= 5:
        outputSize = (int(sys.argv[4]), int(sys.argv[5]))
    else:
        outputSize = (320, 207)

    exit(main(inputFilename, channel, outputDir, outputSize))
