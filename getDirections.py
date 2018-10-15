import json
import os
import requests
import argparse
import urllib
from pathlib import Path
from math import ceil

# TODO:
# 1. add car line wait time option
# 2. add morning / afternoon option
# 3. add round-trip option
# 4. add store the route option


class getDirections():
    def __init__(self, args):
        self.app_id = os.environ["HERE_APP_ID"]
        self.app_code = os.environ["HERE_APP_CODE"]
        self.wake_streets_url = os.environ["WAKE_URL"]
        self.here_simple_url = os.environ["HERE_SIMPLE_URL"]
        self.here_matrix_url = os.environ["HERE_MATRIX_URL"]
        self.homes_path = Path(args.homes)
        self.schools_path = Path(args.schools)
        self.streetData = []

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
        return r.json()

    def requestSimpleRoute(self, payload):
        r = requests.get(self.here_simple_url, params=payload)
        return r.json()

    def getAddresses(self, street_name):
        call_params = {}
        call_params['where'] = f"ST_NAME=\'{street_name.upper()}\'"
        call_params['outFields'] = "ST_NUM"
        call_params['outSR'] = 4326
        call_params['f'] = 'json'
        self.streetData = self.requestStreetInfo(call_params)

    def getRoute(self, start, destination):
        call_params = {}
        call_params['app_id'] = self.app_id
        call_params['app_code'] = self.app_code
        call_params['waypoint0'] = f"geo!{start['latitude']},{start['longitude']}"
        call_params['waypoint1'] = f"geo!{destination['latitude']},{destination['longitude']}"
        call_params['departure'] = f"2018-10-10T11:30:00-04"
        call_params['mode'] = "fastest;car;traffic:enabled"
        routeData = self.requestSimpleRoute(call_params)
        return routeData


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--homes', help='JSON file with the list of neighborhoods')
    parser.add_argument('--schools', help='JSON file with the list of schools')
    arguments = parser.parse_args()

    directions = getDirections(arguments)
    print("Neighborhood,Address,TimeToDDMS,TimeToECMS")
    for key, value in directions.homes.items():
        for street in value:
            directions.getAddresses(street)
            for item in directions.streetData['features']:
                homeAddr = {}
                homeAddr['number'] = item['attributes']['ST_NUM']
                homeAddr['latitude'] = item['geometry']['y']
                homeAddr['longitude'] = item['geometry']['x']
                ddms_dir = directions.getRoute(
                    homeAddr, directions.schools['DDMS'])
                ecms_dir = directions.getRoute(
                    homeAddr, directions.schools['ECMS'])
                time_to_ddms = ceil(
                    ddms_dir['response']['route'][0]['summary']['travelTime'] / 60)
                time_to_ecms = ceil(
                    ecms_dir['response']['route'][0]['summary']['travelTime'] / 60)
                print(
                    f"{key},\'{homeAddr['number']} {street.upper()}\',{time_to_ddms},{time_to_ecms}")


if __name__ == "__main__":
    main()
