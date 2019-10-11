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
<<<<<<< HEAD
 - Map and lap time overlays to use with OBS when live streaming events.

### Instructions

## Starting the server

## Useful scripts

 - dbc_extract.py: Takes a DBC file and puts MQTT topics in its signal comments
 - dbc_to_json.py: Takes a DBC file with MQTT topics and dumps JSON from OpenMCT
=======
 - Map and lap time overlays to use with OBS when live streaming events.
>>>>>>> c7e7bf6e203acccec2ec1f11fc344141264d46c6
