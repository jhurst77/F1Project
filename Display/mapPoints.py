import math
import pygame
import circuit_points
import fastf1 as ff1
import os
import numpy as np
from pyproj import Transformer

TRAN_4326_TO_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")
TRAN_3857_TO_4326 = Transformer.from_crs("EPSG:3857", "EPSG:4326")

sectors = {'Sakhir' : [23, 75, 0], 'Barcelona': [42, 94, 0], 'Spielberg': [13, 50, 0], 'Silverstone': [20, 50, 0]}

def testing_sectors(TRACKNAME, sector_to_test):
    """Function used to visually test the positions of the sector boundaries. Pretty shoddily made function but works.
    Would like to find a way to automatically have sector points."""
    CANWIDTH = 850  # window width
    CANHEIGHT = 850  # window width
    FRAMERATE = 30
    OFFSET = 30  # map offset from edge

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((CANWIDTH, CANHEIGHT))
    sec_index = sector_to_test - 1

    pt = sectors[TRACKNAME][sec_index]
    track_points = generate_points(CANWIDTH, CANHEIGHT, OFFSET, TRACKNAME)

    def draw_map():
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

    def draw_box():
        minX, maxX, minY, maxY = findMinMax(track_points)
        bleft = (minX, maxY)
        bright = (maxX, maxY)
        tleft = (minX, minY)
        tright = (maxX, minY)
        pygame.draw.line(screen, 'green', bleft, bright)
        pygame.draw.line(screen, 'blue', bright, tright)
        pygame.draw.line(screen, 'yellow', tright, tleft)
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
    -1 and 1, that is, a fraction of the track height they are from (0.5,0.5).

    Returns
    List of value pairs [...,[x_n, y_n],...]"""
    minX, maxX, minY, maxY = findMinMax(coords)
    rangeY = maxY - minY
    rangeX = maxX - minX
    divisor = max(rangeY, rangeX)
    normCoords = []

    for pairs in coords:
        xPart = (((pairs[0] - minX) / divisor) - 0.5) * 2
        yPart = (((pairs[1] - minY) / divisor) - 0.5) * 2
        normCoords.append([xPart, yPart])
    return normCoords  # hi

def rceline_generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME, YEAR):
    ff1.Cache.enable_cache(os.path.join(os.getcwd(), '__pycache__'))  # cache to speed up
    session = ff1.get_session(YEAR, TRACKNAME, 'Q')
    laps = session.load_laps(with_telemetry=True)
    lap = laps.pick_fastest()
    tel = lap.get_telemetry()
    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)
    points = np.array([x,y]).T
    track = normCoords(points)
    return make_track(track, WINWIDTH, WINHEIGHT, OFFSET)

def make_track(track, WINWIDTH, WINHEIGHT, OFFSET):
    minX, maxX, minY, maxY = findMinMax(track)
    X_ave_pos = (minX + maxX) / 2
    Y_ave_pos = (minY + maxY) / 2
    print(X_ave_pos, Y_ave_pos)
    mapRangeX = WINWIDTH - 2 * OFFSET
    mapRangeY = WINHEIGHT - 2 * OFFSET
    mapReach = min(mapRangeX, mapRangeY) / 2
    rotation = 'OG'  # TODO: integrate this into function better, make not strings, make not hardcoded.
    track_points = []
    point = 0
    while point in range(len(track)):
        x = (0.5 * WINWIDTH * (-X_ave_pos + 1)) + (mapReach * track[point][0])
        y = (0.5 * WINHEIGHT * (Y_ave_pos + 1)) - (mapReach * track[point][1])
        # track_points.append([x,y])
        if rotation == '1Clockwise':
            track_points.append([WINWIDTH - y, x - WINHEIGHT])
        elif rotation == 'OG':
            track_points.append([x, y])
        elif rotation == '2Clockwise':
            track_points.append([WINWIDTH - x, WINHEIGHT - y])
        elif rotation == '1AntiClock':
            track_points.append([y, WINHEIGHT - x])
        point += 1
    return track_points

def transform_coords(lon, lat):
    return TRAN_4326_TO_3857.transform(lon, lat)

def generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME):
    point = 0
    geocoords = circuit_points.return_coords(TRACKNAME)
    for indices in range(len(geocoords)):
        x, y = transform_coords(geocoords[indices][1], geocoords[indices][0])
        geocoords[indices] = (x, y)
    track = normCoords(geocoords)
    minX, maxX, minY, maxY = findMinMax(track)
    X_ave_pos = (minX + maxX)/2
    Y_ave_pos = (minY + maxY)/2
    print(X_ave_pos, Y_ave_pos)
    mapRangeX = WINWIDTH - 2 * OFFSET
    mapRangeY = WINHEIGHT - 2 * OFFSET
    mapReach = min(mapRangeX, mapRangeY)/2
    rotation = 'OG'  # TODO: integrate this into function better, make not strings, make not hardcoded.
    track_points = []
    while point in range(len(track)):
        x = (0.5 * WINWIDTH * (-X_ave_pos+1)) + (mapReach * track[point][0])
        y = (0.5 * WINHEIGHT * (Y_ave_pos+1)) - (mapReach * track[point][1])
        # track_points.append([x,y])
        if rotation == '1Clockwise':
            track_points.append([WINWIDTH - y, x - WINHEIGHT])
        elif rotation == 'OG':
            track_points.append([x, y])
        elif rotation == '2Clockwise':
            track_points.append([WINWIDTH - x, WINHEIGHT - y])
        elif rotation == '1AntiClock':
            track_points.append([y, WINHEIGHT - x])
        point += 1
    return track_points

if __name__ == '__main__':
    rceline_generate_points(800, 800, 50, 'Austria', 2020)