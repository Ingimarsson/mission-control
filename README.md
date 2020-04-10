# Mission Control

Mission Control is a frontend component of the Team Spark telemetry stack. It consists of a background service that parses data from MQTT, and a web-based frontend with the following features.

- A dashboard for accumulator measurements
- A list of all sensors along with latest measurements and frequencies
- Ability to upload the DBC file that is used to decode measurements

## Installation

This service is intended to run in a Docker container.

## Development

You can set up a development environment with the following commands. First you need to set up a virtual environment.

    sudo apt update
    sudo apt install python3-venv

Now you can create and enter a virtual environment

    cd mission-control
    python3 -m venv env
    source env/bin/activate

Now you can install dependencies and run a development server

    pip3 install -r requirements.txt
    python3 manage.py runserver

## Utilities

 - `dbc_extract.py`: Takes a DBC file and puts MQTT topics in its signal comments
 - `dbc_to_json.py` Takes a DBC file with MQTT topics and dumps JSON from OpenMCT
