from math import sin, cos, sqrt, atan2, radians
import time
import json
import sqlite3

class gps(object):
    def __init__(self):
        # Lap time calculation variables

        self.gate = None                # Two GPS points that define a starting gate, if None lap times won't be calculated
        self.laps = []                  # Values for each lap are stored as a dictionary in this list
        self.gps_current = [0,0]        # Latest received GPS coordinate, used to check if path intersects starting gate
        self.gps_last = [0,0]           # Second latest received GPS coordinate
        self.track = 0                  # Primary key of track in sqlite database
        self.distance = 0               # Distance of current recording in kilometers, is incremented when GPS is received

        self.track_range = 3            # The distance in km the client has to be from a track to auto ditect the track ID

        self.start_time = 0
        self.current_time = 0

        self.sqlite_path = "D:\dev\mission-control-github\db.sqlite3"

    def gps_gather(self, data):   # Collect GPS coordinates to calculate lap times
        if data[0] == 'ts/gps/longitudinal':
            self.gps_current[0] = float(data[1])

        if data[0] == 'ts/gps/lateral':
            self.gps_current[1] = float(data[1])

        both_received = (self.gps_current[0] != self.gps_last[0]) and (self.gps_current[1] != self.gps_last[1])

        if both_received:
            self.current_time = time.time() - self.start_time

        return both_received # returnes true if both axis have been received

    def get_distance_traveled(self):
        if self.gps_last[0] != 0:
            self.distance += self.calc_distance(self.gps_current, self.gps_last)

    def calc_lap_time(self):
        # Check if GPS path intersects the starting line
        if self.gate is not None and self.gate != 0:

            if self.intersect(self.gps_current, self.gps_last, self.gate[0], self.gate[1]):

                # Get the lap number and append the latest lap
                i = len(self.laps)

                if i == 0:
                    self.laps.append({
                        'id': i+1,
                        'total_time': round(self.current_time,2),
                        'distance': round(self.distance,3),
                        'lap_time': 0
                    })

                else:
                    time_delta = round(self.current_time - self.laps[i-1]['total_time'],2)

                    self.laps.append({
                        'id': i+1,
                        'total_time': round(self.current_time,2),
                        'distance': round(self.distance,3),
                        'lap_time': time_delta
                    })

    def set_start(self):
        self.start_time = time.time()
        self.gate = None
        self.laps = []
        self.gps_current = [0,0]
        self.gps_last = [0,0]
        self.track = 0
        self.distance = 0


    # Findes track in data base from gps location
    # returnes True if track has ben found
    def finde_track(self):
        status = False
        conn = sqlite3.connect(self.sqlite_path)
        c = conn.cursor()

        c.execute("select points from control_track")
        nr_of_tracks = len(c.fetchall())
        #print("number of tracks in database"+str(nr_of_tracks))

        for i in range(1,nr_of_tracks):
            c.execute("select points from telemetry_track where id=%i" % i)

            try:
                gate = json.loads(c.fetchone()[0])['gate']
                distance = self.calc_distance(gate[0], self.gps_current)
                if distance < self.track_range:
                    self.track = i
                    self.gate = gate
                    status = True
                    print("Track found with ID: " + str(self.track))
                    break
            except Exception as e:
                print("Could not load gate points")
                gate = None

        return status


    def get_track(self):
        return self.track

    def publish (self, client):
        gps_packet = {
            'track': self.track,
            'gps_lon': self.gps_current[0],
            'gps_lat': self.gps_current[1],
            'laps': self.laps
        }
        client.publish('control/gps',json.dumps(gps_packet))

        self.gps_last[0] = self.gps_current[0]
        self.gps_last[1] = self.gps_current[1]


    def calc_distance(self,x,y):
        dlon = radians(x[0]) - radians(y[0])
        dlat = radians(x[1]) - radians(y[1])

        # Calculate distance traveled
        a = sin(dlat / 2)**2 + cos(y[1]) * cos(x[1]) * sin(dlon / 2)**2
        return 2 * 6373 * atan2(sqrt(a), sqrt(1 - a))

    # Takes in endpoints of two lines as lists [x,y] and checks if the lines intersect or not
    def intersect(self, a1, a2, b1, b2):
        def f(x,y):
            return (x-a1[0])*(a2[1]-a1[1])-(y-a1[1])*(a2[0]-a1[0])

        def g(x,y):
            return (x-b1[0])*(b2[1]-b1[1])-(y-b1[1])*(b2[0]-b1[0])

        u = f(b1[0], b1[1])*f(b2[0], b2[1])
        v = g(a1[0], a1[1])*g(a2[0], a2[1])

        return (u < 0 and v < 0)
