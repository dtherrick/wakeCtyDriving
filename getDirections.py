import json
import os
import requests
import argparse
import urllib
from pathlib import Path
from math import ceil


class getDirections():
    def __init__(self, args):
        self.app_id = os.environ["HERE_APP_ID"]
        self.app_code = os.environ["HERE_APP_CODE"]
        self.wake_streets_url = os.environ["WAKE_URL"]
        self.here_simple_url = os.environ["HERE_SIMPLE_URL"]
        self.here_matrix_url = os.environ["HERE_MATRIX_URL"]
        self.homes_path = Path(args.homes)
        self.schools_path = Path(args.schools)
        self.latitude = 0
        self.longitude = 0

        with open(self.homes_path.as_posix()) as f:
            self.homes = json.load(f)

        with open(self.schools_path.as_posix()) as f:
            self.schools = json.load(f)

    def print_metadata(self):
        print(f"APP ID:             {self.app_id}")
        print(f"APP CODE:           {self.app_code}")
        print(f"HOMES JSON PATH:    {self.homes_path.as_posix()}")
        print(f"SCHOOLS JSON PATH:  {self.schools_path.as_posix()}")
        print(f"HOMES DATA:         {self.homes}")
        print(f"SCHOOLS DATA:       {self.schools}")
        for key, value in self.homes.items():
            if len(value) > 0:
                for street in value:
                    print(f"Neighborhood: {key} :: Street: {street}")
                print(f"\n----------\n")
            else:
                print(f"{key} is empty")

    def requestStreetInfo(self, payload):
        params = urllib.parse.urlencode(
            payload, safe="=", quote_via=urllib.parse.quote)
        r = requests.get(self.wake_streets_url, params=params)
        print(f"{r.url}")
        return r.json()

    def requestSimpleRoute(self, payload):
        r = requests.get(self.here_simple_url, params=payload)
        print(f"{r.url}")
        return r.json()

    def getAddresses(self):
        call_params = {}
        call_params['where'] = f"ST_NAME=\'{self.homes['FentonEstates'][0].upper()}\'"
        call_params['outFields'] = "ST_NUM"
        call_params['outSR'] = 4326
        call_params['f'] = 'json'
        streetData = self.requestStreetInfo(call_params)
        self.latitude = streetData['features'][0]['geometry']['y']
        self.longitude = streetData['features'][0]['geometry']['x']
        print(f"LATITUDE:   {self.latitude}")
        print(f"LONGITUDE:  {self.longitude}")

    def getRoute(self, destination):
        call_params = {}
        call_params['app_id'] = self.app_id
        call_params['app_code'] = self.app_code
        call_params['waypoint0'] = f"geo!{self.latitude},{self.longitude}"
        call_params['waypoint1'] = f"geo!{destination['latitude']},{destination['longitude']}"
        call_params['mode'] = "fastest;car;traffic:enabled"
        routeData = self.requestSimpleRoute(call_params)
        print(
            f"Travel Time: {ceil(routeData['response']['route'][0]['summary']['travelTime'] / 60)} minutes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--homes', help='JSON file with the list of neighborhoods')
    parser.add_argument('--schools', help='JSON file with the list of schools')
    arguments = parser.parse_args()

    directions = getDirections(arguments)
    directions.getAddresses()
    directions.getRoute(directions.schools['DDMS'])
    directions.getRoute(directions.schools['ECMS'])


if __name__ == "__main__":
    main()
