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
        Driver = self.track_laps.pick_driver(DriverID)
        try:
            if lap_no == 1:
                # if starting the race
                start_data = Driver.iloc[lap_index]  # data for lap 1
                start_time = start_data.LapStartTime  # Lap 1 start time
                sec2_fin_time = start_data.Sector2SessionTime
                sec2_time = start_data.Sector2Time
                sec1 = (sec2_fin_time - start_time - sec2_time).total_seconds()
                sec2 = Driver['Sector2Time'].iloc[0].total_seconds()
                sec3 = Driver['Sector3Time'].iloc[0].total_seconds()
                pit_time = 0  # you don't pit before the race lol
            elif Driver.iloc[lap_index].PitOutTime is not pd.NaT:
                # if pitting
                pit_time = Driver['PitOutTime'].iloc[lap_index].total_seconds() - Driver['PitInTime'].iloc[lap_index-1].total_seconds()
                sec1 = Driver['Sector1Time'].iloc[lap_index].total_seconds() - pit_time
                sec2 = Driver['Sector2Time'].iloc[lap_index].total_seconds()
                sec3 = Driver['Sector3Time'].iloc[lap_index].total_seconds()
            else:
                sec1 = Driver['Sector1Time'].iloc[lap_index].total_seconds()
                sec2 = Driver['Sector2Time'].iloc[lap_index].total_seconds()
                sec3 = Driver['Sector3Time'].iloc[lap_index].total_seconds()
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


if __name__ == '__main__':
    Bahr_Data = LapData(2021, 'Bahrain', 'R')
    VER = Bahr_Data.track_laps.pick_driver('VER')
    PER = Bahr_Data.track_laps.pick_driver('PER')
    print(VER['LapStartTime'].iloc[0])
    print(PER['LapStartTime'].iloc[0])
