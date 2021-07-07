import math
import pygame
import circuit_points


##############################################################################
# FUNCTIONS USED LATER TO TIDY THE OUTPUTTED DATA
##############################################################################

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
    return normCoords


def vert_shiftX(coords):
    """function that finds how much to move coordinates in."""
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

def sec_dist(self, sec_no):
    """"Function that calculates the distance of a sector (ranging from 1-3). Can produce a list of all the
    distances using lists."""
    sec_index = sec_no - 1  # indices start from 0 not 1
    sec_dist_output = 0
    start_pt = self.sec_boundary_pts[sec_index - 1]
    end_pt = self.sec_boundary_pts[sec_index]
    pt = start_pt
    amt_pts = len(self.track_points)
    while (pt % amt_pts) != end_pt:  # while not at end point of sector
        sec_dist_output += math.dist(self.track_points[pt], self.track_points[pt - 1])
        pt += 1
    return sec_dist_output  # returns float value


def distance(x1, y1, x2, y2):
    """ simple function that returns the distance between two point pairs"""
    return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME):
    point = 0
    track = normCoords(circuit_points.return_coords(TRACKNAME))
    minX, maxX, minY, maxY = findMinMax(track)
    X_ave_pos = (minX + maxX)/2
    Y_ave_pos = (minY + maxY)/2
    print(X_ave_pos, Y_ave_pos)
    mapRangeX = WINWIDTH - 2 * OFFSET
    mapRangeY = WINHEIGHT - 2 * OFFSET
    mapReach = min(mapRangeX, mapRangeY)/2
    rotation = '2Clockwise'
    track_points = []
    while point in range(len(track)):
        x = (0.5 * WINWIDTH * (X_ave_pos+1)) + (mapReach * track[point][0])
        y = (0.5 * WINHEIGHT * (Y_ave_pos+1)) - (mapReach * track[point][1])
        track_points.append([x,y])
        # if rotation == '1Clockwise':
        #     track_points.append([WINWIDTH - y, x - .25*WINHEIGHT])
        # elif rotation == 'OG':
        #     track_points.append([x, y])
        # elif rotation == '2Clockwise':
        #     track_points.append([WINWIDTH - x, WINHEIGHT - y])
        # elif rotation == '1AntiClock':
        #     track_points.append([y, WINHEIGHT - x])
        point += 1
    return track_points

if __name__ == '__main__':
    testing_sectors('Spielberg', 2)