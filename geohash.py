#!/usr/bin/env python3
"""
Created on Tue Jun  4 15:18:03 2019

@author: clarkhs
"""
import argparse
import datetime
import dateutil.parser
import hashlib
# import webbrowser

from math import trunc

import requests

with open('alphavantage_api_key.txt') as api_keyfile:
    AV_API_KEY = api_keyfile.read().strip()
TODAYS_DATE = datetime.date.today()


class NotYetAvailable(Exception):
    """
    Exception raised when DJI data isn't yet available for a day.

    Attributes:
        date -- date with unavailable data
    """

    def __init__(self, message, failure_date):
        self.message = message
        self.failure_date = failure_date


def get_dji_data(api_key=AV_API_KEY):
    '''
    Get the DJI data provided by AlphaVantage.
    '''
    params = {'apikey': api_key,
              'function': 'TIME_SERIES_DAILY',
              'symbol': "DJI"}
    url = 'https://www.alphavantage.co/query?'

    response = requests.get(url, params)
    dji_data_json = response.json()['Time Series (Daily)']

    return dji_data_json


def select_dji_data_on_date(dji_data, request_date=TODAYS_DATE):
    '''
    Get the specific most recent opening, given a date.
    Note that it doesn't always return the most up-to-date data,
    and will only return the most recent DJI data. This means not weekends.
    '''
    day_gen = date_iterator(request_date)
    attempts = 0
    dji_data_oneday = None

    while dji_data_oneday is None and attempts < 7:
        selected_date = next(day_gen)
        print(selected_date)
        if selected_date.weekday() > 4:
            pass
        else:
            try:
                dji_data_oneday = dji_data[selected_date.isoformat()]
            except KeyError:
                raise NotYetAvailable('DJI open data not available on',
                                      selected_date.isoformat())

    return dji_data_oneday


def date_iterator(start_date=TODAYS_DATE,
                  time_change=datetime.timedelta(days=-1)):
    '''
    By default, starts counting backwards.
    You have been warned.
    (I actually don't remember what I was warning about.)
    '''
    yielded_date = start_date

    while True:
        yield yielded_date
        yielded_date += time_change


def get_latlong_by_ip():
    '''
    What it says on the tin.
    This only exists so that I can make it look neater down below.
    '''
    url = 'http://ipinfo.io/json'

    response = requests.get(url)

    loc = [float(s) for s in response.json()['loc'].split(',')]

    return loc


def get_first_matching_key(search_dictionary, search_key):
    '''
    Bullshit way to get around unordered dicts in JSON responses.
    Again, only exists because I suck and haven't found a better way.
    '''
    desired_key = [s for s in search_dictionary if search_key in s][0]
    desired_value = search_dictionary[desired_key]
    return desired_value


def geohash(location, selected_date=TODAYS_DATE, dji_open=None):
    '''
    Think from antigravity import geohash
    but like better or something.
    '''
    location = [trunc(int(f)) for f in location]
    hash_input = '-'.join([selected_date.isoformat(), str(round(dji_open, 2))])
    hash_output = hashlib.md5(bytes(hash_input, 'utf-8'))
    hex_output = hash_output.hexdigest()

    loc_hash = [hex_output[:len(hex_output)//2],
                hex_output[len(hex_output)//2:]]
    fractions = [int(s, 16) / 2 ** 64 for s in loc_hash]
    final_loc = [location[0] + fractions[0] * location[0] / abs(location[0]),
                 location[1] + fractions[1] * location[1] / abs(location[1])]

    return final_loc, fractions


def main(args):
    '''
    At runtime, goes and finds the most recent DJI open.
    Then, gets your approximate location from your IP,
    and truncates that to get just the integers.
    It picks out most recent DJI open for the day,
    and does account for weekends.
    It then runs an implementation of the XKCD geohash function,
    prints all the regular useful information,
    and opens a webpage to that location.
    '''
    if args.location is None:
        location = [trunc(s) for s in get_latlong_by_ip()]
    else:
        location = args.location

    if args.date is None:
        date = TODAYS_DATE
    else:
        date = dateutil.parser.parse(args.date).date()

    if args.dji_open is None:
        dji_data = get_dji_data()
        dji_data_oneday = select_dji_data_on_date(dji_data, date)

        dji_open = round(float(get_first_matching_key(dji_data_oneday,
                                                      "open")), 2)
    else:
        dji_open = int(args.dji_open)

    goal_loc, fractions = geohash(location, date, dji_open)

    print(location,
          date.isoformat()+'-'+str(dji_open),
          fractions,
          goal_loc,
          sep='\n')

#    webbrowser.open('https://www.google.com/maps/search/'
#                    + '+'.join([str(s) for s in goal_loc]) + '/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--location', '-l', nargs=2,
                        metavar=('LAT', 'LONG'),
                        help='Current latitude and longitude')
    parser.add_argument('--date', '-d', metavar='DATE',
                        help='''Date of desired geohash.
                                Right now only works for last 100 days''')
    parser.add_argument('--dji-open',
                        help='Specify a DJI open if you like.')
    args = parser.parse_args()
    main(args)
