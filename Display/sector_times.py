import fastf1 as ff1
import pandas as pd
import os

ff1.Cache.enable_cache(os.path.join(os.getcwd(), '__pycache__'))  # cache to speed up


class LapData:
    """A class for the data for all drivers for a specific race session."""
    def __init__(self, year, race, session):
        self.track_session = ff1.get_session(year, race, session)
        self.track_laps = self.track_session.load_laps()

    def sector_times(self, lap_no, DriverID):
        """Produces the sector times for a driver for a given lap.
        If the driver hasn't retired, it produces a list with [time for sector 1, time for sector 2, time for sector 3,
        time for pit stop (if pitting)]"""
        lap_index = lap_no - 1
        driver = self.track_laps.pick_driver(DriverID)
        try:
            if lap_no == 1:
                # if starting the race
                start_data = driver.iloc[lap_index]  # data for lap 1
                start_time = start_data.LapStartTime  # Lap 1 start time
                sec2_fin_time = start_data.Sector2SessionTime
                sec2_time = start_data.Sector2Time
                sec1 = (sec2_fin_time - start_time - sec2_time).total_seconds()
                sec2 = driver['Sector2Time'].iloc[0].total_seconds()
                sec3 = driver['Sector3Time'].iloc[0].total_seconds()
                pit_time = 0  # you don't pit before the race lol
            elif driver.iloc[lap_index].PitOutTime is not pd.NaT:
                # if pitting
                pit_time = driver['PitOutTime'].iloc[lap_index].total_seconds() - driver['PitInTime'].iloc[lap_index - 1].total_seconds()
                sec1 = driver['Sector1Time'].iloc[lap_index].total_seconds() - pit_time
                sec2 = driver['Sector2Time'].iloc[lap_index].total_seconds()
                sec3 = driver['Sector3Time'].iloc[lap_index].total_seconds()
            else:
                sec1 = driver['Sector1Time'].iloc[lap_index].total_seconds()
                sec2 = driver['Sector2Time'].iloc[lap_index].total_seconds()
                sec3 = driver['Sector3Time'].iloc[lap_index].total_seconds()
                pit_time = 0
            return [sec1, sec2, sec3, pit_time]
        except IndexError:
            print(DriverID, ' retired from the race')
            return 'retired'

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

    def all_sectors_ordered(self, DriverID):
        """produces a list with the time (in seconds) for every sector after the start."""
        event_times = []
        driver = self.track_laps.pick_driver(DriverID)
        race_start_time = driver.iloc[0].LapStartTime
        for rows in driver.index:
            rst = race_start_time
            row_info = driver.loc[rows]

            if row_info.PitOutTime is not pd.NaT and row_info.LapNumber != 1:
                # if pitting
                s1_event_end = row_info.PitOutTime - rst
                box = True
            elif row_info.LapNumber == 1:
                # if lap 1
                s1_event_end = rst - rst
                box = False
            else:
                # if normal lap
                s1_event_end = row_info.Sector1SessionTime - rst
                box = False
            s1_event_end = s1_event_end.total_seconds()
            event_times.append([s1_event_end, 'S1', row_info.LapNumber, box])

            s2_end = row_info.Sector2SessionTime - rst
            s2_end = s2_end.total_seconds()
            event_times.append([s2_end, 'S2', row_info.LapNumber, False])

            if row_info.PitInTime is not pd.NaT:
                # if going into pits
                s3_event_end = row_info.PitInTime - rst
            else:
                # if normal lap
                s3_event_end = row_info.Sector3SessionTime - rst
            s3_event_end = s3_event_end.total_seconds()
            event_times.append([s3_event_end, 'S3', row_info.LapNumber, False])
        event_times.sort()
        return event_times




if __name__ == '__main__':
    Austria = LapData(2020, 'Austria', 'R')
    print(Austria.all_sectors_ordered('VER'))
