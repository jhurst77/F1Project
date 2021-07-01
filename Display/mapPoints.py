#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 14:37:06 2021

@author: jameshurst
"""
import math
import pygame
import circuit_points


##############################################################################
# FUNCTIONS USED LATER TO TIDY THE OUTPUTTED DATA
##############################################################################

sectors = {'Sakhir' : [23, 75, 0], 'Barcelona': [42, 94, 0], 'Spielberg': [42, 94, 0], 'Silverstone': [20, 40, 0]}

def testing_sectors(TRACKNAME, sector_to_test):
    """Function used to visually test the positions of the sector boundaries. Pretty shoddily made function but works.
    Would like to find a way to automatically have sector points."""
    CANWIDTH = 800  # window width
    CANHEIGHT = 800  # window width
    FRAMERATE = 30
    OFFSET = 10  # map offset from edge
    mapRange = CANWIDTH - 2 * OFFSET
    track = normCoords(circuit_points.return_coords(TRACKNAME))
    vert_shift = vert_shiftX(track) * 0.5
    track_coords = normCoords(track)
    track_points = []
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((CANWIDTH, CANHEIGHT))
    pt = sectors[TRACKNAME][sector_to_test - 1]
    def generate_points():
        point = 0
        while point in range(len(track_coords)):
            x = CANWIDTH - (OFFSET + ((track_coords[point][1]) * mapRange))
            y = CANWIDTH - (OFFSET + mapRange * (track_coords[point][0])) \
                - vert_shift * mapRange  # done because not all tracks are square
            point += 1
            track_points.append([x, y])
    def draw_map():
        generate_points()
        for j in range(len(track_points)):
            pygame.draw.line(screen, 'blue', track_points[j - 1], track_points[j])
    def car_stay():
        x, y = track_points[pt][0], track_points[pt][1]
        pygame.draw.circle(screen, [255, 255, 255], (x, y), 5)
    def update():
        draw_map()
        car_stay()

    def test():
        done = False
        while not done:
            screen.fill((0, 0, 0))
            update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # quits canvas
            pygame.display.flip()
            clock.tick(FRAMERATE)
        pygame.quit()
    test()

def findMinMax(coords):
    """find the minimum and maximum of the X and Y values so that the
    bounding box for the map of the circuit can be found.

    Returns
    4 float values that are:
        1. min X
        2. max X
        3. min Y
        4. max Y
    in that order"""

    minX = math.inf  # these values are the opposite and initialised here
    maxX = 0
    minY = math.inf
    maxY = 0
    for pairs in coords:
        minX = min(minX, pairs[0])  # keeps the appropriate value each loop.
        minY = min(minY, pairs[1])
        maxX = max(maxX, pairs[0])
        maxY = max(maxY, pairs[1])
    return minX, maxX, minY, maxY


def normCoords(coords):
    """Divides the X and Y values by the range of values to values between
    0 and 1, that is, a fraction of the track height they are from (0,0).

    Returns
    List of value pairs [...,[x_n, y_n],...]"""

    minX, maxX, minY, maxY = findMinMax(coords)
    rangeY = maxY - minY
    rangeX = maxX - minX
    divisor = max(rangeY, rangeX)  # maximum so that output always <1.
    normCoords = []

    for pairs in coords:
        xPart = (pairs[0] - minX) / divisor  # divides the coords by max to have between 0 and 1
        yPart = (pairs[1] - minY) / divisor
        normCoords.append([xPart, yPart])

    return normCoords


def vert_shiftX(coords):
    """function that finds how much smaller the X dimensions are than the y. This
    can then be used to center the drawing when the track is drawn."""
    extrms = findMinMax(normCoords(coords))
    return 1 - extrms[1]


def vert_shiftY(coords):
    """function that finds how much smaller the Y dimensions are than the X. This
    can then be used to center the drawing when the track is drawn."""
    extrms = findMinMax(normCoords(coords))
    return 1 - extrms[3]


def sector_distance(coords, secNumber):
    """returns the distance (in units that are the same as the coords given) of
    that sector (from the start line???)"""
    sector_distance = 0
    for points in range(secNumber - 1):
        sector_distance = sector_distance + \
                          distance(coords[points][0], coords[points][1],
                                   coords[points + 1][0], coords[points + 1][1])
    return sector_distance


def distance(x1, y1, x2, y2):
    """ simple function that returns the distance between two point pairs"""
    return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


if __name__ == '__main__':
    testing_sectors('Spielberg', 1)