import fastf1 as ff1
import pandas as pd
import os

ff1.Cache.enable_cache(os.path.join(os.getcwd(), '__pycache__'))


class LapData:
    def __init__(self, year, race, session):
        self.track_session = ff1.get_session(year, race, session)
        self.track_laps = self.track_session.load_laps()

    def sector_times(self, lap_no, DriverID):
        lap_index = lap_no - 1
        Driver = self.track_laps.pick_driver(DriverID)
        try:
            if lap_no == 1:
                # if starting the race
                start_data = Driver.iloc[lap_index]
                start_time = start_data.LapStartTime
                sec2_fin_time = start_data.Sector2SessionTime
                sec2_time = start_data.Sector2Time
                sec1 = (sec2_fin_time - start_time - sec2_time).total_seconds()
                sec2 = Driver['Sector2Time'].iloc[0].total_seconds()
                sec3 = Driver['Sector3Time'].iloc[0].total_seconds()
                pit_time = 0
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
        driver_numbers = self.track_session.drivers
        while '' in driver_numbers:
            driver_numbers.remove('')
        return driver_numbers

    def team_name(self, DriverID):
        Driver = self.track_laps.pick_driver(DriverID)
        team = Driver['Team'].iloc[0]
        return team


if __name__ == '__main__':
    Bahr_Data = LapData(2021, 'Bahrain', 'R')
    VER = Bahr_Data.track_laps.pick_driver('VER')
    PER = Bahr_Data.track_laps.pick_driver('PER')
    print(VER['LapStartTime'].iloc[0])
    print(PER['LapStartTime'].iloc[0])
