import pandas as pd
import pygame
import sector_times
import team_colours
import mapPoints
import math
import time

# ###### Constants ###### #
WINWIDTH = 800  # window width
WINHEIGHT = 800  # window width
FRAMERATE = 60
OFFSET = 50  # map offset from edge
TRACKNAME = 'Sakhir'
RACE = 'Bahrain'
YEAR = 2020
SPEEDMULT = 2.5  # speed sim up or down from real time

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINWIDTH, WINHEIGHT), vsync= True)

class Track:
    def __init__(self, name):
        self.sec_boundary_pts = mapPoints.sectors[TRACKNAME]
        self.name = name
        self.track_points = mapPoints.generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME)
        self.race_line_points = mapPoints.rceline_generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME, YEAR)
        self.sec_dists = [self.sec_dist(1), self.sec_dist(2), self.sec_dist(3)]  # distances for each sector

    def draw_map(self, width):
        """ simple function that draws the map"""
        for j in range(len(self.track_points)):
            pygame.draw.line(screen, 'blue', self.track_points[j - 1], self.track_points[j], width)

    def draw_rcing_line(self):
        """ simple function that draws the map"""
        for j in range(len(self.race_line_points)):
            pygame.draw.line(screen, 'red', self.race_line_points[j - 1], self.race_line_points[j], 1)

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

    def rce_line(self):
        self.draw_rcing_line()

    def update(self, width):
        self.draw_map(width)

class Car:
    def __init__(self, car_name, track, lap_data):
        self.name = car_name
        self.data = lap_data
        before_time = time.time()
        self.coords, self.time_arr = self.data.race_points_times(self.name)
        after_time = time.time()
        print('race_point_times took, ', after_time - before_time)

        self.x = self.coords[0][0]
        self.y = self.coords[0][1]
        self.indices_checked = 0

        self.track = track

        self.team_name = self.data.team_name(car_name)
        self.colour = team_colours.team_colours[int(YEAR)][self.team_name]
        print(self.name, ' init')

        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)

    def stay(self):
        self._draw()

    def update(self, runtime):
        lower_index = self._return_index(runtime, self.time_arr)
        upper_index = self._find_upper_index(lower_index)
        fraction = self._get_fraction(upper_index, lower_index, runtime)

        delta_x = self.coords[upper_index][0] - self.coords[lower_index][0]
        delta_y = self.coords[upper_index][1] - self.coords[lower_index][1]

        self.x = self.coords[lower_index][0] + delta_x * fraction
        self.y = self.coords[lower_index][1] + delta_y * fraction
        self._draw()

    def _draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)

    def _get_fraction(self, upper_index, lower_index, runtime):
        points_gap = self.time_arr[upper_index] - self.time_arr[lower_index]
        zero_var = self.time_arr[upper_index] - self.time_arr[upper_index]  # just so i can get the type right
        timedelta = pd.Timedelta(runtime, 's')
        compare_time = timedelta + self.data.ref_time
        frac_gap = compare_time - self.time_arr[lower_index]
        if points_gap != zero_var:
            fraction = frac_gap/points_gap
            return fraction
        else:
            return 0

    def _find_upper_index(self, lower_index):
        """if at end, then just same, so will be still"""
        if lower_index == len(self.time_arr)-1:
            upper_index = lower_index
        else:
            upper_index = lower_index + 1
        return upper_index

    def _return_index(self, runtime, time_array):
        timedelta = pd.Timedelta(runtime, 's')
        compare_time = timedelta + self.data.ref_time
        max_indices = len(time_array)
        added_index = 0
        while time_array[self.indices_checked + added_index] < compare_time:
            if self.indices_checked + added_index < \
                    (max_indices - 1) and time_array[self.indices_checked + added_index + 1] < compare_time:
                added_index += 1
            else:
                self.indices_checked += added_index
                return self.indices_checked
        return self.indices_checked  # hi


class Race:
    def __init__(self):
        self.track_obj = Track(TRACKNAME)
        self.race_lap_data = sector_times.LapData(YEAR, RACE, 'R')
        self.drivers = ['44']  # self.race_lap_data.drivers_list()
        self.cars = []
        self.init_drivers()

    def init_drivers(self):
        for driver_names in self.drivers:
            self.cars.append(Car(driver_names, self.track_obj, self.race_lap_data))

    def race(self):
        done = False
        waiting = True
        draw_racing_line = False
        width = 5

        while waiting:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # quits canvas
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LEFT]:
                waiting = False
            elif pressed[pygame.K_UP]:
                width += 1
                print(width)
            elif pressed[pygame.K_DOWN]:
                width -= 1
                print(width)
            elif pressed[pygame.K_j]:
                draw_racing_line = not draw_racing_line
            self.track_obj.update(width)
            if draw_racing_line:
                self.track_obj.draw_rcing_line()
            for i in self.cars:
                i.stay()
            pygame.display.flip()
            clock.tick(FRAMERATE*SPEEDMULT)

        time_running = 0
        while not done:
            screen.fill((0, 0, 0))
            self.track_obj.update(width)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # quits canvas
            for i in self.cars:
                i.update(time_running)
            pygame.display.flip()
            time_running += 1*SPEEDMULT/(FRAMERATE)
            clock.tick(FRAMERATE*SPEEDMULT)
        pygame.quit()


if __name__ == "__main__":
    # Bahr_race = Race()
    # Test_car = Car('VER', Bahr_race.track_obj, Bahr_race.race_lap_data)
    # Test_car.update(1)
    Bahr_race = Race()
    Bahr_race.race()