import geojson
import os

"""This module is used to track the locations of the files for each of the circuits. Also gives some surface level
information about the files."""

def track_file_dict():
    """This function produces a dictionary of the the names of the tracks and which files they are in. Makes it
    easier to load in map files."""
    cwd = os.getcwd()
    circ_direct = os.path.join(cwd, 'circuits')  # used because 'circuits' is a sub-folder
    tracks = dict()
    os.chdir(circ_direct)
    for files in os.listdir(circ_direct):
        # iterates over the files and adds to dictionary with key = track name, item being ffile name
        filename = str(files)
        with open(files) as f:
            gj = geojson.load(f)
        location = gj['features'][0]['properties']['Location']
        tracks[location] = filename
    os.chdir(cwd)  # to move back to directory started in
    return tracks


def return_coords(trackname):
    """Returns the coordinates of a track given a track name. Very specific with names, use track_file_dict to search
    for names."""
    track_dict = track_file_dict()
    cwd = os.getcwd()
    circ_direct = os.path.join(cwd, 'circuits')
    os.chdir(circ_direct)
    file = track_dict[trackname]
    with open(file) as f:
        gj = geojson.load(f)
    coords = gj['features'][0]['geometry']['coordinates']
    os.chdir(cwd)
    return coords


if __name__ == '__main__':
    track_dict_output = track_file_dict()
    print(track_dict_output)