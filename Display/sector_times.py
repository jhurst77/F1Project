import fastf1 as ff1
import pandas as pd
import os
import numpy as np
import mapPoints
import time as t

ff1.Cache.enable_cache(os.path.join(os.getcwd(), '__pycache__'))  # cache to speed up


class LapData:
    """A class for the data for all drivers for a specific race session."""
    def __init__(self, year, race, session):
        self.track_session = ff1.get_session(year, race, session)
        self.track_laps = self.track_session.load_laps(with_telemetry=True)
        self.ref_time = self.get_reference_time()

    def get_reference_time(self):
        """gets the reference time for the race start"""
        ref_driver = self.drivers_list()[0]
        ref_driver_laps = self.track_laps.pick_driver(ref_driver)
        ref_tel = ref_driver_laps.get_telemetry()
        ref_time = ref_tel.iloc[0].Date
        return ref_time

    def drivers_list(self):
        """produces a list of all the drivers in a race. Returns their driver numbers and not their names."""
        driver_numbers = self.track_session.drivers
        while '' in driver_numbers:
            driver_numbers.remove('')
        return driver_numbers

    def team_name(self, DriverID):
        """returns the team name of a driver"""
        Driver = self.track_laps.pick_driver(DriverID)
        team = Driver['Team'].iloc[0]
        return team

    def race_points_times(self, DriverID):
        driver = self.track_laps.pick_driver(DriverID)
        tel = driver.get_telemetry()
        x = np.array(tel['X'].values)
        y = np.array(tel['Y'].values)
        time_array = np.array(tel['Date'])
        points = np.array([x, y]).T
        points = mapPoints.normCoords(points)
        points = mapPoints.make_track(points, 800, 800, 50)
        return points, time_array
    
    def return_index(self, runtime, time_array):
        point1 = t.time()
        timedelta = pd.Timedelta(runtime, 's')
        compare_time = timedelta + self.ref_time
        max_indices = len(time_array)
        lower_index = 0
        point2 = t.time()
        print('setup took, ', point2-point1)
        for indices in range(max_indices):
            if time_array[indices] < compare_time:
                lower_index = indices
        point3 = t.time()
        print('for loop took, ', point3 - point2)
        return lower_index


if __name__ == '__main__':
    Austria = LapData(2020, 'Austria', 'R')
    points, time_array = Austria.race_points_times('VER')
    index = Austria.return_index(5000, time_array)
    print(points[index])
