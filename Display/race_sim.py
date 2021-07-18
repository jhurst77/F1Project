import pygame

import mapPoints
import sector_times
import math
import team_colours
import time

# ###### Constants ###### #
WINWIDTH = 800  # window width
WINHEIGHT = 800  # window width
FRAMERATE = 120
OFFSET = 10  # map offset from edge
TRACKNAME = 'Sakhir'
RACE = 'Bahrain'
YEAR = 2021
SPEEDMULT = 50  # speed sim up or down from real time

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINWIDTH, WINHEIGHT), vsync= True)


class Track:
    def __init__(self, name):
        self.sec_boundary_pts = mapPoints.sectors[TRACKNAME]
        self.name = name
        self.track_points = mapPoints.generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME)
        self.sec_dists = [self.sec_dist(1), self.sec_dist(2), self.sec_dist(3)]  # distances for each sector

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
    def __init__(self, name, track_obj, data):
        self.race_lap_data = data
        self.ordered_sector_data = data.all_sectors_ordered(name)
        self.name = name

        self.pt = 0
        self.lap = 0
        self.current_sector = 1
        self.x = track_obj.track_points[self.pt][0]  # starting point of car x
        self.y = track_obj.track_points[self.pt][1]  # starting point of car y

        self.team_name = data.team_name(name)
        self.colour = team_colours.team_colours[int(YEAR)][self.team_name]
        self.track = track_obj

        self.BOX = False
        self.BOX_start_time = 0
        self.outside_BOX = True
        self.retired = False

        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)

    def stay(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)

    def _get_car_speed(self, time):
        sec_time, current_sec, retired = self._get_time_sector(time)
        sec_speed = self.track.sec_dists[current_sec-1] / sec_time
        sec_frame_speed = sec_speed / FRAMERATE
        return sec_frame_speed

    def _get_time_sector(self, time):
        sectors_done = 0
        lower_time = 0
        current_sector = 0
        while self.ordered_sector_data[sectors_done][0] < time:
            lower_time = self.ordered_sector_data[sectors_done][0]
            current_sector = self.ordered_sector_data[sectors_done][1]
            sectors_done += 1
        higher_time = self.ordered_sector_data[sectors_done][0]
        sector_time = higher_time - lower_time
        retired = self.ordered_sector_data[sectors_done][4]
        return sector_time, current_sector, retired

    def move(self, time):
        sec_time, current_sec, retired = self._get_time_sector(time)
        if retired:
            self.retired = True

        if self.retired:
            self.stay()
        elif current_sec == 'PitOut':
            self.stay()
        else:
            dx, dy = self._calc_speed_components(time)
            self.x += dx
            self.y += dy
            pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)
            self._update_if_close(time)

    def _calc_direction_proportions(self):
        size = len(self.track.track_points) - 1
        next_pt = (self.pt + 1) % size
        abs_dist = math.dist(self.track.track_points[next_pt], self.track.track_points[self.pt])
        x_dist = (self.track.track_points[next_pt][0] - self.track.track_points[self.pt][0])
        y_dist = (self.track.track_points[next_pt][1] - self.track.track_points[self.pt][1])
        x_prop = x_dist / abs_dist
        y_prop = y_dist / abs_dist
        return x_prop, y_prop

    def _calc_speed_components(self, time):
        """function that moves the car. Input pt is the most recent point the car went through."""
        x_prop, y_prop = self._calc_direction_proportions()
        speed = self._get_car_speed(time)
        x = speed * x_prop
        y = speed * y_prop
        return x, y  # speeds in x and y coordinates

    def _update_if_close(self, time):
        """corrects the car to one of the track points if it's within a certain range. Also updates the current pt when
        it does the correction."""
        gap = self._get_car_speed(time)
        # must be within this radius around a point to correct to a point (nominally 1 frame).
        size = len(self.track.track_points) - 1  # mod input to loop through the track points
        new_pt = (self.pt + 1) % size
        if math.dist([self.x, self.y], self.track.track_points[new_pt]) <= gap:
            self.pt = new_pt
            self.x = self.track.track_points[new_pt][0]
            self.y = self.track.track_points[new_pt][1]
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


class Race:
    def __init__(self):
        self.track_obj = Track(TRACKNAME)
        # self.track_name = TRACKNAME
        # self.year = YEAR
        # self.race_lap_data = sector_times.LapData(YEAR, TRACKNAME, 'R')
        self.drivers = self.race_lap_data.drivers_list()
        self.cars = []
        self.init_drivers()

    def init_drivers(self):
        for driver_names in self.drivers:
            self.cars.append(Car(driver_names, self.track_obj)) #, self.race_lap_data))

    def race(self):
        done = False
        waiting = True

        updates = 0
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
            if updates == 0:
                pygame.display.flip()
            updates = (updates + 1) % SPEEDMULT
            clock.tick(FRAMERATE*SPEEDMULT)

        start_time = time.time()
        updates = 0
        while not done:
            time_now = time.time()
            time_running = time_now - start_time
            screen.fill((0, 0, 0))
            self.track_obj.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # quits canvas
            for i in self.cars:
                i.move(time_running)
            if updates == 0:
                pygame.display.flip()
            updates = (updates + 1) % SPEEDMULT
            clock.tick(FRAMERATE*SPEEDMULT)
        pygame.quit()


# def race():
#     done = False
#     Bahrain = track()
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
    # Bahr_race = Race(YEAR)
    # Test_car = Car('VER', Bahr_race.track_obj, Bahr_race.race_lap_data)
    # print(Test_car._get_time_sector(100))
    Bahr_race = Race()
    Bahr_race.race()
