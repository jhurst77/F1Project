import pygame

import circuit_points
import mapPoints
import sector_times
import math
import team_colours

# ###### Constants ###### #
WINWIDTH = 800  # window width
WINHEIGHT = 800  # window width
FRAMERATE = 30
OFFSET = 10  # map offset from edge
TRACKNAME = 'Spielberg'
# track = mapPoints.normCoords(circuit_points.return_coords(TRACKNAME))  # normalised coords of track
YEAR = 2020
SPEEDMULT = 10  # speed sim up or down from real time

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINWIDTH, WINHEIGHT), vsync= True)


class Track:
    mapRange = WINWIDTH - 2 * OFFSET  # width of track on screen
    vert_shift = mapPoints.vert_shiftX(track) * 0.5
    track_coords = track  # coords ranging from 0 to 1
    sec_boundary_pts = mapPoints.sectors[TRACKNAME]
    track_points = []

    def __init__(self, name):
        self.name = name
        self.generate_points()
        self.sec_dists = [self.sec_dist(1), self.sec_dist(2), self.sec_dist(3)]  # distances for each sector

    def generate_points(self):
        """Generates the points relating to the canvas width and height. Returns
        list of point pairs that are the coordinates."""
        point = 0
        while point in range(len(self.track_coords)):
            x = WINWIDTH - (OFFSET + ((self.track_coords[point][1]) * self.mapRange))
            y = WINWIDTH - (OFFSET + self.mapRange * (self.track_coords[point][0])) \
                - self.vert_shift * self.mapRange  # done because not all tracks are square
            self.track_points.append([x, y])
            point += 1

    def draw_map(self):
        """ simple function that draws the map"""
        for j in range(len(self.track_points)):
            pygame.draw.line(screen, 'blue', self.track_points[j - 1], self.track_points[j])

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

    def sector_given_point(self, pt):
        """places a point into a sector. Returns sector as an int (1-3)"""
        if 0 <= pt < self.sec_boundary_pts[0]:
            return 1
        elif self.sec_boundary_pts[0] <= pt <= self.sec_boundary_pts[1]:
            return 2
        else:
            return 3

    def update(self):
        self.draw_map()


class Car:
    def __init__(self, name, sec_times, track, data):
        self.race_lap_data = data
        self.name = name
        self.sec_times = sec_times
        self.pt = 0
        self.x = track.track_points[self.pt][0]  # starting point of car x
        self.y = track.track_points[self.pt][1]  # starting point of car y
        self.team_name = data.team_name(name)
        self.colour = team_colours.team_colours[int(YEAR)][self.team_name]
        self.Track = track
        self.lap = 0
        self.BOX = False
        self.BOX_start_time = 0
        self.outside_BOX = True
        self.retired = False
        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)

    def car_speed(self, current_sector):
        sec_index = current_sector - 1
        sec_speed = self.Track.sec_dists[sec_index] / self.sec_times[sec_index]
        sec_frame_speed = sec_speed * SPEEDMULT / FRAMERATE
        return sec_frame_speed

    def speed_components(self):
        size = len(self.Track.track_coords) - 1
        next_pt = (self.pt + 1) % size
        abs_dist = math.dist(self.Track.track_points[next_pt], self.Track.track_points[self.pt])
        x_dist = (self.Track.track_points[next_pt][0] - self.Track.track_points[self.pt][0])
        y_dist = (self.Track.track_points[next_pt][1] - self.Track.track_points[self.pt][1])
        x_prop = x_dist / abs_dist
        y_prop = y_dist / abs_dist
        return x_prop, y_prop

    def move_blocks(self):
        """function that moves the car. Input pt is the most recent point the car went through."""
        sector = Track.sector_given_point(self.Track, self.pt)
        x_prop, y_prop = self.speed_components()
        speed = self.car_speed(sector)
        x = speed * x_prop
        y = speed * y_prop
        return x, y  # speeds in x and y coordinates

    def update_if_close(self):
        """corrects the car to one of the track points if it's within a certain range. Also updates the current pt when
        it does the correction."""
        sector = self.Track.sector_given_point(self.pt)
        gap = self.car_speed(sector)
        # must be within this radius around a point to correct to a point (nominally 1 frame).
        size = len(self.Track.track_points) - 1  # mod input to loop through the track points
        new_pt = (self.pt + 1) % size
        if math.dist([self.x, self.y], self.Track.track_points[new_pt]) <= gap:
            self.pt = new_pt
            self.x = self.Track.track_points[new_pt][0]
            self.y = self.Track.track_points[new_pt][1]
            if new_pt == 0:
                self.lap += 1
                self.sec_times = self.race_lap_data.sector_times(self.lap, self.name)
                if self.sec_times == 'retired':
                    self.retired = True
                    self.x += 20
                    self.y += 20
                elif self.sec_times[3] >= 1e-9:
                    self.BOX = True
                    self.BOX_start_time = pygame.time.get_ticks()
                    self.outside_BOX = False
                    self.y += 50

    def stay(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)

    def move(self):
        if self.retired:
            self.stay()
        elif self.BOX and (pygame.time.get_ticks() - self.BOX_start_time) <= self.sec_times[3] * 1000/SPEEDMULT:
            self.stay()
        elif not self.outside_BOX:
            self.stay()
            self.outside_BOX = True
            self.y -= 50
        else:
            dx, dy = self.move_blocks()
            self.x += dx
            self.y += dy
            pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)
            self.update_if_close()


class Race:
    def __init__(self, track_name, year):
        self.track_obj = Track(TRACKNAME)
        self.track_name = track_name
        self.year = year
        self.race_lap_data = sector_times.LapData(year, track_name, 'R')
        self.drivers = self.race_lap_data.drivers_list()
        self.cars = []
        self.init_drivers()

    def init_drivers(self):
        lap1 = 1
        for driver_names in self.drivers:
            sector_times = self.race_lap_data.sector_times(lap1, driver_names)
            self.cars.append(Car(driver_names, sector_times, self.track_obj, self.race_lap_data))

    def race(self):
        done = False
        waiting = True
        while waiting:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # quits canvas
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LEFT]:
                waiting = False
            self.track_obj.update()
            for i in self.cars:
                i.stay()
            pygame.display.flip()
            clock.tick(FRAMERATE)

        while not done:
            screen.fill((0, 0, 0))
            self.track_obj.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # quits canvas
            for i in self.cars:
                i.move()
            pygame.display.flip()
            clock.tick(FRAMERATE)
        pygame.quit()


# def race():
#     done = False
#     Bahrain = Track()
#     names = ['BOT', 'HAM', 'VER']
#     times = {'BOT': [4, 5, 6], 'HAM': [2, 2, 2], 'VER': [2, 3, 2]}
#     drivers = []
#     for i in names:
#         drivers.append(Car(i, times[i], Bahrain))
#     while not done:
#         screen.fill((0,0,0))
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 done = True  # quits canvas
#         pressed = pygame.key.get_pressed()
#         if pressed[pygame.K_LEFT]:  # if left arrow key pressed
#             for i in drivers:
#                 i.move()
#         else:
#             for i in drivers:
#                 i.stay()
#         Bahrain.update()
#         pygame.display.flip()
#         clock.tick(FRAMERATE)
#     pygame.quit()


if __name__ == "__main__":
    Bahr_race = Race(TRACKNAME, YEAR)
    Bahr_race.race()
