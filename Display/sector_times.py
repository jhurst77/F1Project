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

    # def sector_times(self, lap_no, DriverID):
    #     """Produces the sector times for a driver for a given lap.
    #     If the driver hasn't retired, it produces a list with [time for sector 1, time for sector 2, time for sector 3,
    #     time for pit stop (if pitting)] -- NOW REDUNDANT"""
    #     lap_index = lap_no - 1
    #     driver = self.track_laps.pick_driver(DriverID)
    #     try:
    #         if lap_no == 1:
    #             # if starting the race
    #             start_data = driver.iloc[lap_index]  # data for lap 1
    #             start_time = start_data.LapStartTime  # Lap 1 start time
    #             sec2_fin_time = start_data.Sector2SessionTime
    #             sec2_time = start_data.Sector2Time
    #             sec1 = (sec2_fin_time - start_time - sec2_time).total_seconds()
    #             sec2 = driver['Sector2Time'].iloc[0].total_seconds()
    #             sec3 = driver['Sector3Time'].iloc[0].total_seconds()
    #             pit_time = 0  # you don't pit before the race lol
    #         elif driver.iloc[lap_index].PitOutTime is not pd.NaT:
    #             # if pitting
    #             pit_time = driver['PitOutTime'].iloc[lap_index].total_seconds() - driver['PitInTime'].iloc[lap_index - 1].total_seconds()
    #             sec1 = driver['Sector1Time'].iloc[lap_index].total_seconds() - pit_time
    #             sec2 = driver['Sector2Time'].iloc[lap_index].total_seconds()
    #             sec3 = driver['Sector3Time'].iloc[lap_index].total_seconds()
    #         else:
    #             sec1 = driver['Sector1Time'].iloc[lap_index].total_seconds()
    #             sec2 = driver['Sector2Time'].iloc[lap_index].total_seconds()
    #             sec3 = driver['Sector3Time'].iloc[lap_index].total_seconds()
    #             pit_time = 0
    #         return [sec1, sec2, sec3, pit_time]
    #     except IndexError:
    #         print(DriverID, ' retired from the race')
    #         return 'retired'

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

    # def all_sectors_ordered(self, DriverID):
    #     """produces a list with the time (in seconds) for every sector after the start. --- NOW REDUNDANT"""
    #     event_times = []
    #     driver = self.track_laps.pick_driver(DriverID)
    #     race_start_time = driver.iloc[0].LapStartTime
    #     retired = False
    #     for rows in driver.index:
    #         rst = race_start_time
    #         row_info = driver.loc[rows]
    #
    #         ## Sector 1 ##
    #         sec1 = dict()
    #         if row_info.LapNumber == 1:
    #             # if lap 1
    #             s1_event_end = row_info.Sector2SessionTime - row_info.Sector2Time - rst
    #         else:
    #             # if normal lap
    #             s1_event_end = row_info.Sector1SessionTime - rst
    #
    #         s1_event_end = s1_event_end.total_seconds()
    #         sec1['End time'] = s1_event_end
    #         sec1['Sector'] = 1
    #         sec1['Lap number'] = row_info.LapNumber
    #         sec1['In box'] = False
    #         sec1['Retired'] = retired
    #
    #         event_times.append(sec1)
    #
    #         ## Sector 2 ##
    #         sec2 = dict()
    #         s2_event_end = row_info.Sector2SessionTime - rst
    #         s2_event_end = s2_event_end.total_seconds()
    #
    #         sec2['End time'] = s2_event_end
    #         sec2['Sector'] = 2
    #         sec2['Lap number'] = row_info.LapNumber
    #         sec2['In box'] = False
    #         sec2['Retired'] = retired
    #         event_times.append(sec2)
    #
    #         ## Sector 3 ##
    #         if row_info.PitInTime is not pd.NaT and row_info.LapNumber != 1:
    #             sec3 = dict()
    #             # if going into pits
    #             s3_event_end = row_info.PitInTime - rst  # pit in time
    #             s3_event_end = s3_event_end.total_seconds()
    #
    #             sec3['End time'] = s3_event_end
    #             sec3['Sector'] = 3
    #             sec3['Lap number'] = row_info.LapNumber
    #             sec3['In box'] = False
    #             sec3['Retired'] = retired
    #             event_times.append(sec3)
    #
    #             ## Pitting ##
    #             pit = dict()
    #             try:
    #                 PitOutTime = driver.loc[rows+1].PitOutTime - rst
    #                 PitOutTime = PitOutTime.total_seconds()
    #
    #                 pit['End time'] = PitOutTime
    #                 pit['Sector'] = 'BOX'
    #                 pit['Lap number'] = row_info.LapNumber
    #                 pit['In box'] = True
    #                 sec3['Retired'] = retired
    #                 event_times.append(pit)
    #             except KeyError:
    #                 retired = True
    #
    #                 PitOutTime = row_info.Sector3SessionTime - rst
    #                 PitOutTime = PitOutTime.total_seconds()
    #
    #                 pit['End time'] = PitOutTime
    #                 pit['Sector'] = 'BOX'
    #                 pit['Lap number'] = row_info.LapNumber
    #                 pit['In box'] = True
    #                 sec3['Retired'] = retired
    #                 event_times.append(pit)
    #         else:
    #             # if normal lap
    #             sec3 = dict()
    #             s3_event_end = row_info.Sector3SessionTime - rst
    #             s3_event_end = s3_event_end.total_seconds()
    #
    #             sec3['End time'] = s3_event_end
    #             sec3['Sector'] = 3
    #             sec3['Lap number'] = row_info.LapNumber
    #             sec3['In box'] = False
    #             sec3['Retired'] = retired
    #             event_times.append(sec3)
    #
    #     event_times_sorted = sorted(event_times, key = lambda item: item['End time'])
    #     return event_times_sorted

    # def find_sector_number(self, runtime, secs_ordered):
    #     """finds the sector number for a given time. -- NOW REDUNDANT"""
    #     sec_number = 0
    #     try:
    #         while secs_ordered[sec_number]['End time'] <= runtime:
    #             sec_number += 1
    #
    #         return sec_number
    #     except IndexError:
    #         return 'Finished'

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

