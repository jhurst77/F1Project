import pygame
import sector_times
import team_colours
import mapPoints
import math
import time

# ###### Constants ###### #
WINWIDTH = 800  # window width
WINHEIGHT = 800  # window width
FRAMERATE = 30
OFFSET = 50  # map offset from edge
TRACKNAME = 'Spielberg'
RACE = 'Austria'
YEAR = 2020
SPEEDMULT = 15  # speed sim up or down from real time

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
    def __init__(self, car_name, track, lap_data):
        self.name = car_name
        self.data = lap_data
        # self.data = sector_times.LapData(YEAR, TRACKNAME, 'R')
        self.ord_sec_data = self.data.all_sectors_ordered(car_name)

        self.pt = 0
        # self.lap = 0
        self.current_sec = 1
        self.x = track.track_points[self.pt][0]
        self.y = track.track_points[self.pt][1]

        self.track = track

        self.team_name = self.data.team_name(car_name)
        self.colour = team_colours.team_colours[int(YEAR)][self.team_name]

        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)
        self.time = 0
        self.running_index = 0

    def stay(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)

    def update(self, time):
        self.time = time
        self.sec_index = self.data.find_sector_number(self.time, self.ord_sec_data)
        if self._find_if_moving():
            time_for_sector = self._get_sector_duration()
            current_sec = self.ord_sec_data[self.sec_index]['Sector']
            sec_frame_speed = self.track.sec_dists[current_sec-1]/(time_for_sector*FRAMERATE)
            move_x, move_y = self._calc_speed_components(sec_frame_speed)
            self.x += move_x
            self.y += move_y
            pygame.draw.circle(screen, self.colour, (self.x, self.y), 5)
            self._update_if_close(sec_frame_speed)
            # self._update_if_new_sec()
        else:
            if self._retired():
                print(self.name, ' is retired')
                before_x, before_y = self.x, self.y
                self.x = self.track.track_points[self.pt][0] + 50
                self.y = self.track.track_points[self.pt][1] + 50
                self.stay()
                self.x = before_x
                self.y = before_y
            elif self._in_box():
                print(self.name, " is boxing")
                before_x, before_y = self.x, self.y
                self.x = self.track.track_points[self.pt][0] + 20
                self.y = self.track.track_points[self.pt][1] + 20
                self.stay()
                self.x = before_x
                self.y = before_y
            else:
                print('weird stuff going on, ', self.sec_index)

    def _find_if_moving(self):
        in_box = self._in_box()
        retired = self._retired()
        on_track = not (in_box or retired)
        return on_track

    def _in_box(self):
        return self.ord_sec_data[self.sec_index]['In box']

    def _retired(self):
        return self.ord_sec_data[self.sec_index]['Retired']

    def _get_sector_duration(self):
        if self.sec_index == 0:
            prev_time = 0
        else:
            prev_time = self.ord_sec_data[self.sec_index - 1]['End time']
        next_time = self.ord_sec_data[self.sec_index]['End time']
        sec_time = next_time - prev_time
        return sec_time

    def _calc_speed_components(self, speed):
        x_prop, y_prop = self._calc_direction_proportions()
        x = speed * x_prop
        y = speed * y_prop
        return x, y

    def _calc_direction_proportions(self):
        size = len(self.track.track_points) - 1
        next_pt = (self.pt + 1) % size
        abs_dist = math.dist(self.track.track_points[next_pt], self.track.track_points[self.pt])
        x_dist = (self.track.track_points[next_pt][0] - self.track.track_points[self.pt][0])
        y_dist = (self.track.track_points[next_pt][1] - self.track.track_points[self.pt][1])
        x_prop = x_dist / abs_dist
        y_prop = y_dist / abs_dist
        return x_prop, y_prop

    def _update_if_close(self, speed):
        gap = speed
        size = len(self.track.track_points) - 1  # mod input to loop through the track points
        new_pt = (self.pt + 1) % size
        if math.dist([self.x, self.y], self.track.track_points[new_pt]) <= gap:
            self.pt = new_pt
            self.x = self.track.track_points[new_pt][0]
            self.y = self.track.track_points[new_pt][1]

    def _update_if_new_sec(self):
        if self.running_index < self.sec_index:
            new_sector = self.ord_sec_data[self.sec_index]['Sector']
            if type(new_sector) is int:
                print('new sec ', new_sector)
                self.pt = self.track.sec_boundary_pts[new_sector % 3]
                self.x = self.track.track_points[self.pt][0]
                self.y = self.track.track_points[self.pt][1]
            self.running_index += 1

class Race:
    def __init__(self):
        self.track_obj = Track(TRACKNAME)
        self.race_lap_data = sector_times.LapData(YEAR, RACE, 'R')
        self.drivers = self.race_lap_data.drivers_list()
        self.cars = []
        self.init_drivers()

    def init_drivers(self):
        for driver_names in self.drivers:
            self.cars.append(Car(driver_names, self.track_obj, self.race_lap_data))

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
                i.update(time_running)
            if updates == 0:
                pygame.display.flip()
            updates = (updates + 1) % SPEEDMULT
            # time.sleep(1/(FRAMERATE*SPEEDMULT))
            clock.tick(FRAMERATE*SPEEDMULT)
        pygame.quit()


if __name__ == "__main__":
    # Bahr_race = Race(YEAR)
    # Test_car = Car('VER', Bahr_race.track_obj, Bahr_race.race_lap_data)
    # print(Test_car._get_time_sector(100))
    Bahr_race = Race()
    Bahr_race.race()