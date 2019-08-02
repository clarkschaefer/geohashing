#!/usr/bin/env python3
"""
Created on Tue Jun  4 15:18:03 2019

@author: clarkhs
"""
import argparse
import datetime
import hashlib
import webbrowser

from math import trunc


import dateutil.parser
import requests

TODAYS_DATE = datetime.date.today()
CHANGE_DATE_30W = datetime.date(2008,5,26)


class NotYetAvailable(Exception):
    """
    Exception raised when DJI data isn't yet available for a day.

    Attributes:
        failure_date -- date with unavailable data
        message
    """

    def __init__(self, message, failure_date):
        self.message = message
        self.failure_date = failure_date
        Exception.__init__(self, ' '.join([self.message, self.failure_date]))


def get_crox_dji_data(request_date):
    '''
    Get the most commonly referenced DJI open from geo.crox.net
    '''
    url = ''.join(['http://geo.crox.net/djia/',
                   request_date.isoformat().replace('-', '/')])

    response = requests.get(url)

    return response.text


def get_av_dji_data(api_key):
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


def select_av_dji_data_on_date(dji_data, request_date=TODAYS_DATE):
    '''
    Get the specific most recent opening, given a date.
    Note that it doesn't always return the most up-to-date data,
    and will only return the most recent DJI data. This means not weekends.
    Also throws an error if you run the code before the DJIA opens.
    '''
    day_gen = _date_iterator(request_date)
    attempts = 0
    dji_data_oneday = None

    while dji_data_oneday is None and attempts < 7:
        selected_date = next(day_gen)
        if selected_date.weekday() > 4:
            pass
        else:
            try:
                dji_data_oneday = dji_data[selected_date.isoformat()]
            except KeyError:
                raise NotYetAvailable('DJI open data not yet available on',
                                      selected_date.isoformat())

    return dji_data_oneday


def _date_iterator(start_date=TODAYS_DATE,
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


def get_latlong_by_ip(ip=None):
    '''
    What it says on the tin.
    This only exists so that I can make it look neater down below.
    In the future there may be more implementations of this,
    and I'll stuff them all into their own submodule.
    '''
    if ip is None:
        payload = '/json'
    else:
        payload = '/' + ip + '/json'

    url = 'http://ipinfo.io' + payload

    response = requests.get(url)

    loc = [float(s) for s in response.json()['loc'].split(',')]

    return loc


def _get_first_matching_key(search_dictionary, search_key):
    '''
    Bullshit way to get around unordered dicts in JSON responses.
    Again, only exists because I suck and haven't found a better way.
    '''
    desired_key = [s for s in search_dictionary if search_key in s][0]
    desired_value = search_dictionary[desired_key]
    return desired_value


def _two_decimal_places(number_string):
    '''
    Does ugly things to get a two-decimal-place float.
    Also probably doesn't work quite right,
    I need to adjust how I'm passing along the DJI open.
    '''
    return trunc(float(number_string)*100)/100


def geohash(location, selected_date=TODAYS_DATE, dji_open=None):
    '''
    Think from antigravity import geohash but like better or something.
    Location is an iterable lat/long coordinate pair, tuple/list/etc.
    selected_date is a datetime.date object
    dji_open should be the matched DJIA open as a string with two decimals
    '''
    location = [trunc(int(float(f))) for f in location]
    hash_input = '-'.join([selected_date.isoformat(), dji_open])
    hash_output = hashlib.md5(bytes(hash_input, 'utf-8'))
    hex_output = hash_output.hexdigest()

    loc_hash = [hex_output[:len(hex_output)//2],
                hex_output[len(hex_output)//2:]]
    fractions = [int(s, 16) / 2 ** 64 for s in loc_hash]
    final_loc = [location[0] + fractions[0] * location[0] / abs(location[0]),
                 location[1] + fractions[1] * location[1] / abs(location[1])]

    return final_loc, fractions, hash_input


def main():
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
    parser = argparse.ArgumentParser()

    parser.add_argument('--location', '-l', nargs=2,
                        metavar=('LAT', 'LONG'),
                        help='Current latitude and longitude')
    parser.add_argument('--date', '-d', metavar='DATE',
                        help='''Date of desired geohash.
                                Right now only works for last 100 days''')
    parser.add_argument('--dji-open',
                        help='Specify a DJI open')
    parser.add_argument('--browser', '-b', action='store_true',
                        help='Open result in a browser')
    parser.add_argument('--source', '-s',
                        help='''
                        Select source of DJIA\n
                        Unset = geo.crox.net\n
                        'crox' = geo.crox.net\n
                        'av'  = AlphaVantage
                        ''')

    args = parser.parse_args()

    if args.location is None:  # get location by IP or provided
        location = [trunc(s) for s in get_latlong_by_ip()]
    else:
        location = args.location

    if args.date is None:  # Get date, automatically or provided
        date = TODAYS_DATE
    else:
        date = dateutil.parser.parse(args.date).date()

    # East of 30W and in 30W rule era
    if location[1] > -30 and date > CHANGE_DATE_30W:
        date -= datetime.timedelta(days=1)

    if args.dji_open is None:
        if args.source == 'av':  # Originally implemented data source
            with open('alphavantage_api_key.txt') as api_keyfile:
                av_api_key = api_keyfile.read().strip()

            av_data = get_av_dji_data(av_api_key)

            av_data_oneday = select_av_dji_data_on_date(av_data, date)

            av_dji_open_raw = _get_first_matching_key(av_data_oneday, 'open')

            dji_open = _two_decimal_places(av_dji_open_raw)

        elif args.source == 'crox' or args.source is None:
            dji_open = get_crox_dji_data(date)  # Default data source

    else:
        dji_open = _two_decimal_places(args.dji_open)

    goal_loc, _, hash_input = geohash(location, date, dji_open)

    print(hash_input,
          goal_loc,
          sep='\n')

    if args.browser:
        print('Opening browser...')
        webbrowser.open('https://www.google.com/maps/search/'
                        + '+'.join([str(s) for s in goal_loc]) + '/')


if __name__ == '__main__':
    main()
