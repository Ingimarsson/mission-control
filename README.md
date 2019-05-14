## Mission Control

Mission Control is a component of Team Spark's telemetry system. It consists of a backend that listens to all measurements from the car over the MQTT protocol, and a web-based frontend to manage the system.

### Features

 - Saves timestamped measurements to a csv file when recording mode is enabled
 - Data is saved with comments, driver and track info
 - Overview of system status, displays values per second from each subsystem
 - Live map of car position on track
 - Ability to define tracks with starting gates by a list of gps coordinates
 - When recording with a defined track, lap times and other statistics are shown
 
### To be implemented

 - Ability to upload DBC files to automatically update CAN database
 - Live feed from cameras on the car
 - Compression of csv files to save space
 - Map and lap time overlays to use with OBS when live streaming events.