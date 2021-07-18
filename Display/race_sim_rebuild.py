import pandas as pd
import pygame
import sector_times
import team_colours
import mapPoints
import time

# ###### Constants ###### #
WINWIDTH = 800  # window width
WINHEIGHT = 800  # window width
FRAMERATE = 30
OFFSET = 50  # map offset from edge
TRACKNAME = 'Sakhir'
RACE = 'Bahrain'
YEAR = 2021
SPEEDMULT = 20  # speed sim up or down from real time
clock = pygame.time.Clock()  # used to keep track of timing and framerate
screen = pygame.display.set_mode((WINWIDTH, WINHEIGHT), vsync=True)


class Track:
    """Class for drawing a track object.
    draws track from points generated in mapPoints
    draws racing line from points generated in mapPoints"""
    def __init__(self, name):
        self.name = name
        self.track_points = mapPoints.generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME)
        self.race_line_points = mapPoints.rceline_generate_points(WINWIDTH, WINHEIGHT, OFFSET, TRACKNAME, YEAR)

    def draw_map(self, width):
        """simple function that draws the map"""
        for j in range(len(self.track_points)):
            pygame.draw.line(screen, 'blue', self.track_points[j - 1], self.track_points[j], width)

    def draw_rcing_line(self):
        """ simple function that draws the racing line"""
        for j in range(len(self.race_line_points)):
            pygame.draw.line(screen, 'red', self.race_line_points[j - 1], self.race_line_points[j], 1)

    def update(self, width=3, rce_line=False):
        """method to be called once per frame to draw track."""
        self.draw_map(width)
        if rce_line:
            self.draw_rcing_line()


class Car:
    """Object used to represent each car on an F1 track. Takes about 1 second to initialise because must process
    and get a 50k large array."""
    def __init__(self, car_name, track, car_data):
        self.name = car_name
        self.data = car_data  # position and sector time data
        self.coords, self.time_arr = self.data.race_points_times(self.name)  # TODO: Add cache to speed up

        self.x = self.coords[0][0]  # x position on map
        self.y = self.coords[0][1]  # y position on map
        self.indices_checked = 0  # variable used to ignore indices that have already been checked

        self.track = track

        self.car_colour = team_colours.team_colours[int(YEAR)][self.data.team_name(car_name)]

        self._draw()
        self.retired = False

        print(self.name, ' initialised')

    def stay(self):
        """method that keeps the car where it is"""
        self._draw()

    def update(self, runtime):
        """method that takes the given race time and calculates the position that the car is"""
        lower_index = self._return_index(runtime, self.time_arr)  # indices for the position data array
        upper_index = self._find_upper_index(lower_index)
        fraction = self._get_fraction(upper_index, lower_index, runtime)  # fraction between one point and the next

        # calculates difference between the two closest points
        delta_x = self.coords[upper_index][0] - self.coords[lower_index][0]
        delta_y = self.coords[upper_index][1] - self.coords[lower_index][1]

        # calculates the position between the two points based on the time. Makes it slightly smoother than just
        # going to the nearest point
        self.x = self.coords[lower_index][0] + delta_x * fraction
        self.y = self.coords[lower_index][1] + delta_y * fraction
        self._draw()

    def _draw(self):
        """simple method that draws the car"""
        pygame.draw.circle(screen, self.car_colour, (self.x, self.y), 5)

    def _get_fraction(self, upper_index, lower_index, runtime):
        """method that finds the fraction of the gap between two points that the car should be"""
        time_gap_btwn_points = self.time_arr[upper_index] - self.time_arr[lower_index]
        zero_var = self.time_arr[upper_index] - self.time_arr[upper_index]  # used in place of zero but of correct type
        timedelta = pd.Timedelta(runtime, 's')
        compare_time = timedelta + self.data.ref_time  # time since start of race
        frac_gap = compare_time - self.time_arr[lower_index]
        if time_gap_btwn_points != zero_var:
            fraction = frac_gap / time_gap_btwn_points
            return fraction
        else:
            return 0

    def _find_upper_index(self, lower_index):
        """Adds 1 to the index of the lower index, unless at the end of the telemetry, in which case it returns the
        lower index."""
        if lower_index == len(self.time_arr)-1:
            if not self.retired:
                print(self.name, 'finished telemetry')
                self.retired = True
            upper_index = lower_index
        else:
            upper_index = lower_index + 1
        return upper_index

    def _return_index(self, runtime, time_array):
        """finds the lower index of the telemetry that corresponds to the given runtime."""
        timedelta = pd.Timedelta(runtime, 's')
        compare_time = timedelta + self.data.ref_time  # time since start of the race
        max_indices = len(time_array)
        added_index = 0
        while time_array[self.indices_checked + added_index] < compare_time:
            if self.indices_checked + added_index < \
                    (max_indices - 1) and time_array[self.indices_checked + added_index + 1] < compare_time:
                added_index += 1
            else:
                self.indices_checked += added_index
                return self.indices_checked
        return self.indices_checked


class Race:
    """Class that controls the race"""
    def __init__(self):
        pygame.init()
        self.track_obj = Track(TRACKNAME)
        self.race_lap_data = sector_times.LapData(YEAR, RACE, 'R')
        self.drivers = self.race_lap_data.drivers_list()  # list of names of drivers # ['44']
        self.cars = []

        self.finished = False
        self.started = False
        self.draw_racing_line = False
        self.track_width = 1

    def _init_drivers_if_empty(self):
        """initilaises the cars and writes them into a list"""
        if len(self.cars) > 0:
            return
        for driver_names in self.drivers:
            self.cars.append(Car(driver_names, self.track_obj, self.race_lap_data))
            pygame.display.flip()

    def _check_if_quitting(self):
        """checks if have received a request to quit the window"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.finished = True  # quits canvas

    def _check_key_presses(self):
        """check if received a request to do something special like increase track width or draw the racing
        line"""
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            self.started = True
        elif pressed[pygame.K_UP]:
            self.track_width += 1
            print(self.track_width)
        elif pressed[pygame.K_DOWN]:
            self.track_width -= 1
            print(self.track_width)
        elif pressed[pygame.K_j]:
            self.draw_racing_line = not self.draw_racing_line

    def _wait_and_draw(self):
        """draws the map and the cars when waiting for the race to start"""
        screen.fill((0, 0, 0))
        self._check_if_quitting()
        self._check_key_presses()
        self.track_obj.update(self.track_width)
        if self.draw_racing_line:
            self.track_obj.draw_rcing_line()
        self._init_drivers_if_empty()
        for i in self.cars:
            i.stay()
        pygame.display.flip()
        clock.tick(FRAMERATE)

    def _race_and_draw(self):
        """does the race loop"""
        time_running = time.time() - self.sim_start
        screen.fill((0, 0, 0))
        self.track_obj.update()
        self._check_if_quitting()
        for i in self.cars:
            i.update(time_running * SPEEDMULT)
        pygame.display.flip()
        clock.tick(FRAMERATE)

    def race(self):
        """main race method - when run, starts drawing, and when left arrow, starts racing!"""
        while not self.started:
            self._wait_and_draw()

        self.sim_start = time.time()
        while not self.finished:
            self._race_and_draw()
        pygame.quit()


if __name__ == "__main__":
    Main_race = Race()
    Main_race.race()
