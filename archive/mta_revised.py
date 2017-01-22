# mta.py

#################
#### imports ####
#################

import wget
from glob import glob
import pickle
import csv
import random
from datetime import datetime
from pprint import pprint
from collections import Counter, defaultdict
from operator import itemgetter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import numpy as np

##########################
#### global variables ####
##########################

DATA_PATH = None
FILENAME = None

##########################
#### helper functions ####
##########################

def download_file(date):
    url_template = 'http://web.mta.info/developers/data/nyct/turnstile/turnstile_%s.txt'
    url = url_template % date
    wget.download(url)
    print(date, 'file downloaded')

def process_file(file):
    with open(file) as f:
        reader = csv.reader(f)
        rows = [[cell.strip() for cell in row] for row in reader]
    assert rows.pop(0) == ['C/A', 'UNIT', 'SCP', 'STATION', 'LINENAME',
                       'DIVISION', 'DATE', 'TIME', 'DESC', 'ENTRIES',
                       'EXITS']

    raw_readings = defaultdict(list)

    for row in rows:
        raw_readings[tuple(row[:4])].append(row[4:])

    return raw_readings

def normalize_time_and_exits(raw_readings):
    datetime_cumulative = {turnstile: [(datetime.strptime(date + time, '%m/%d/%Y%X'),
                                        int(in_cumulative))
                                       for _, _, date, time,
                                           _, in_cumulative, _ in rows]
                           for turnstile, rows in raw_readings.items()}

    for rows in datetime_cumulative.values():
        assert rows == sorted(rows)

    datetime_count_times = {turnstile: [[rows[i][0],
                                     rows[i+1][1] - rows[i][1],
                                     rows[i+1][0] - rows[i][0]]
                                    for i in range(len(rows) - 1)]
                        for turnstile, rows in datetime_cumulative.items()}

    datetime_counts = {turnstile: [(time, count)
                               for (time, count, _) in rows
                               if 0 <= count <= 5000]
                   for turnstile, rows in datetime_count_times.items()}

    return datetime_counts

def convert_to_daily_counts(datetime_counts):
    day_counts = {}
    for turnstile, rows in datetime_counts.items():
        by_day = {}
        for time, count in rows:
            day = time.date()
            by_day[day] = by_day.get(day, 0) + count
        day_counts[turnstile] = sorted(by_day.items())

    return day_counts

def prepare_single_station_graph(day_counts):
    dates = []
    counts = []

    key, val = list(day_counts.items())[0]
    for i in val:
        dates.append(i[0])
        counts.append(i[1])

    return dates, counts

####################
#### exercises #####
####################

def exercise_1(turnstile_date):
    """
    Make a python dict where there is a key for each (C/A, UNIT, SCP, STATION). These are the first four columns. The value for this key should be a list of lists. Each list in the list is the rest of the columns in a row. For example, one key-value pair should look like
    { ('A002','R051','02-00-00','LEXINGTON AVE'): [ ['NQR456', 'BMT', '01/03/2015', '03:00:00', 'REGULAR', '0004945474', '0001675324'], ['NQR456', 'BMT', '01/03/2015', '07:00:00', 'REGULAR', '0004945478', '0001675333'], ['NQR456', 'BMT', '01/03/2015', '11:00:00', 'REGULAR', '0004945515', '0001675364'], ... ] }
    """
    raw_readings = process_file('turnstile_%s.txt' % turnstile_date)
    pickle.dump(raw_readings, open('exercise_1', 'wb'))
    print('Exercise 1 complete. Data saved as pickle object.')
    return raw_readings

def exercise_2(turnstile_date):
    """
    Let's turn this into a time series. For each key (basically the control area, unit, device address and station of a specific turnstile), have a list again, but let the list be comprised of just the point in time and the count of entries.
    """
    raw_readings = process_file('turnstile_%s.txt' % turnstile_date)
    datetime_counts = normalize_time_and_exits(raw_readings)
    pickle.dump(datetime_counts, open('exercise_2', 'wb'))
    print('Exercise 2 complete. Data saved as pickle object.')
    return datetime_counts

def exercise_3(turnstile_date):
    """
    These counts are for every n hours. (What is n?) We want total daily entries.
    Now make it that we again have the same keys, but now we have a single value for a single day, which is the total number of passengers that entered through this turnstile on this day.
    """
    raw_readings = process_file('turnstile_%s.txt' % turnstile_date)
    datetime_counts = normalize_time_and_exits(raw_readings)
    day_counts = convert_to_daily_counts(datetime_counts)
    pickle.dump(day_counts, open('exercise_3', 'wb'))
    print('Exercise 3 complete. Data saved as pickle object.')
    return day_counts

def exercise_4(turnstile_date):
    "We will plot the daily time series for a turnstile."

    raw_readings = process_file('turnstile_%s.txt' % turnstile_date)
    datetime_counts = normalize_time_and_exits(raw_readings)
    day_counts = convert_to_daily_counts(datetime_counts)
    dates, counts = prepare_single_station_graph(day_counts)

    plt.figure(figsize=(10,3))
    plt.title("Daily Time Series for a Single Turnstile")
    plt.plot(dates, counts)
    plt.show()
    plt.savefig('exercise4.png')

    print('Exercise 4 complete. Plot saved as PNG.')


##############
#### main ####
##############

def mta():
    turnstile_date = input('Enter the turnstile date (yy/mm/dd):  ')
    download_file(turnstile_date)
    exercise_1(turnstile_date)
    exercise_2(turnstile_date)
    exercise_3(turnstile_date)
    exercise_4(turnstile_date)

if __name__ == '__main__':
    mta()
