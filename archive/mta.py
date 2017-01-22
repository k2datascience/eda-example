# mta.py

#################
#### imports ####
#################

from __future__ import division
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

def process_file(file):
    with open(file) as f:
        reader = csv.reader(f)
        rows = [[cell.strip() for cell in row] for row in reader]
    assert rows.pop(0) == ['C/A', 'UNIT', 'SCP', 'STATION', 'LINENAME',
                       'DIVISION', 'DATE', 'TIME', 'DESC', 'ENTRIES',
                       'EXITS']
    return rows

def format_file(format):
    raw_readings = {}
    for row in rows:
        raw_readings.setdefault(tuple(format), []).append(tuple(row[4:]))

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

    key,val = day_counts.items()[0]
    for i in val:
        dates.append(i[0])
        counts.append(i[1])

    return dates, counts

####################
#### challenges ####
####################

def challenge_1():
    """
    Make a python dict where there is a key for each (C/A, UNIT, SCP, STATION). These are the first four columns. The value for this key should be a list of lists. Each list in the list is the rest of the columns in a row. For example, one key-value pair should look like
    { ('A002','R051','02-00-00','LEXINGTON AVE'): [ ['NQR456', 'BMT', '01/03/2015', '03:00:00', 'REGULAR', '0004945474', '0001675324'], ['NQR456', 'BMT', '01/03/2015', '07:00:00', 'REGULAR', '0004945478', '0001675333'], ['NQR456', 'BMT', '01/03/2015', '11:00:00', 'REGULAR', '0004945515', '0001675364'], ... ] }
    """
    rows = process_file('turnstile_150627.txt')
    raw_readings = format_file(row[:4])
    return raw_readings

def challenge_2():
    """
    Let's turn this into a time series. For each key (basically the control area, unit, device address and station of a specific turnstile), have a list again, but let the list be comprised of just the point in time and the count of entries.
    """
    rows = process_file('turnstile_150627.txt')
    raw_readings = format_file(row[:4])
    datetime_counts = normalize_time_and_exits(raw_readings)
    return datetime_counts

def challenge_3():
    """
    These counts are for every n hours. (What is n?) We want total daily entries.
    Now make it that we again have the same keys, but now we have a single value for a single day, which is the total number of passengers that entered through this turnstile on this day.
    """
    rows = process_file('turnstile_150627.txt')
    raw_readings = format_file(row[:4])
    datetime_counts = normalize_time_and_exits(raw_readings)
    day_counts = convert_to_daily_counts(datetime_counts)
    return day_counts

def challenge_4():
    "We will plot the daily time series for a turnstile."

    rows = process_file('turnstile_150627.txt')
    raw_readings = format_file(row[:4])
    datetime_counts = normalize_time_and_exits(raw_readings)
    day_counts = convert_to_daily_counts(datetime_counts)
    dates, counts = prepare_single_station_graph(day_counts)

    plt.figure(figsize=(10,3))
    plt.title("Daily Time Series for a Single Turnstile")
    plt.plot(dates,counts)

def challenge_5():
    """
    So far we've been operating on a single turnstile level, let's combine turnstiles in the same ControlArea/Unit/Station combo. There are some ControlArea/Unit/Station groups that have a single turnstile, but most have multiple turnstilea-- same value for the C/A, UNIT and STATION columns, different values for the SCP column. We want to combine the numbers together -- for each ControlArea/UNIT/STATION combo, for each day, add the counts from each turnstile belonging to that combo.
    """

    rows = process_file('turnstile_150627.txt')
    raw_readings = format_file((row[0], row[1], row[3]))
    datetime_counts = normalize_time_and_exits(raw_readings)
    day_counts = convert_to_daily_counts(datetime_counts)
    return day_counts

def challenge_6():
    """
    Similarly, combine everything in each station, and come up with a time series of [(date1, count1),(date2,count2),...] type of time series for each STATION, by adding up all the turnstiles in a station.
    """

    rows = process_file('turnstile_150627.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    day_counts = convert_to_daily_counts(datetime_counts)
    return day_counts

def challenge_7():
    "Plot the time series for a station."

    rows = process_file('turnstile_150627.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    day_counts = convert_to_daily_counts(datetime_counts)
    dates, counts = prepare_single_station_graph(day_counts)

    plt.figure(figsize=(10,3))
    plt.title("Daily Time Series for Individual Station")
    plt.plot(dates,counts)

def challenge_8():
    """
    Make one list of counts for one week for one station. Monday's count, Tuesday's count, etc. so it's a list of 7 counts. Make the same list for another week, and another week, and another week. plt.plot(week_count_list) for every week_count_list you created this way. You should get a rainbow plot of weekly commute numbers on top of each other.
    """

    rows = process_file('turnstile_150620.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    x_dict = convert_to_daily_counts(datetime_counts)
    x1, x2 = prepare_single_station_graph(day_counts)

    rows = process_file('turnstile_150613.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    y_dict = convert_to_daily_counts(datetime_counts)
    y1, y2 = prepare_single_station_graph(day_counts)

    rows = process_file('turnstile_150606.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    z_dict = convert_to_daily_counts(datetime_counts)
    z1, z2 = prepare_single_station_graph(day_counts)

    x2 = np.array(x2)
    y2 = np.array(y2)
    z2 = np.array(z2)

    x1 = [i.weekday() for i in x1]
    y1 = [i.weekday() for i in y1]
    z1 = [i.weekday() for i in z1]

    width = .25
    p1 = plt.bar(x1,x2,width,color='r')
    p2 = plt.bar(y1,y2,width,color='g', bottom = x2)
    p3 = plt.bar(z1,z2,width,color='b', bottom = x2+y2)

    plt.xticks(x1, days, rotation='vertical')
    plt.xticks(y1, days, rotation='vertical')
    plt.title("3 Weeks")
    ax = plt.gca()

def challenge_9():
    """
    Over multiple weeks, sum total ridership for each station and sort them, so you can find out the stations with the highest traffic during the time you investigate
    """
    rows = process_file('turnstile_150620.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    x_dict = convert_to_daily_counts(datetime_counts)
    x1, x2 = prepare_single_station_graph(day_counts)

    rows = process_file('turnstile_150613.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    y_dict = convert_to_daily_counts(datetime_counts)
    y1, y2 = prepare_single_station_graph(day_counts)

    rows = process_file('turnstile_150606.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    z_dict = convert_to_daily_counts(datetime_counts)
    z1, z2 = prepare_single_station_graph(day_counts)

    # summation of all stations and counts
    massive_dict = {}

    for station, rows in x_dict.items():
        for time, count in rows:
            massive_dict[station[0]] = massive_dict.get(station, 0) + count

    for station, rows in y_dict.items():
        for time, count in rows:
            massive_dict[station[0]] = massive_dict.get(station, 0) + count

    for station, rows in z_dict.items():
        for time, count in rows:
            massive_dict[station[0]] = massive_dict.get(station, 0) + count

    sorted_massive_dict = sorted(massive_dict.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_massive_dict

def challenge_10():
    """
    Make a single list of these total ridership values and plot it with
    plt.hist(total_ridership_counts)
    to get an idea about the distribution of total ridership among different stations.
    This should show you that most stations have a small traffic, and the histogram bins for large traffic volumes have small bars.
    """

    rows = process_file('turnstile_150620.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    x_dict = convert_to_daily_counts(datetime_counts)
    x1, x2 = prepare_single_station_graph(day_counts)

    rows = process_file('turnstile_150613.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    y_dict = convert_to_daily_counts(datetime_counts)
    y1, y2 = prepare_single_station_graph(day_counts)

    rows = process_file('turnstile_150606.txt')
    raw_readings = format_file([row[3]])
    datetime_counts = normalize_time_and_exits(raw_readings)
    z_dict = convert_to_daily_counts(datetime_counts)
    z1, z2 = prepare_single_station_graph(day_counts)

    # summation of all stations and counts
    massive_dict = {}

    for station, rows in x_dict.items():
        for time, count in rows:
            massive_dict[station[0]] = massive_dict.get(station, 0) + count

    for station, rows in y_dict.items():
        for time, count in rows:
            massive_dict[station[0]] = massive_dict.get(station, 0) + count

    for station, rows in z_dict.items():
        for time, count in rows:
            massive_dict[station[0]] = massive_dict.get(station, 0) + count

    sorted_massive_dict = sorted(massive_dict.items(), key=operator.itemgetter(1), reverse=True)

    stations = []
    counts = []

    for x in sorted_massive_dict[:10]:
        stations.append(x[0])
        counts.append(x[1])

    stations = list(reversed(stations))
    counts = list(reversed(counts))

    plt.figure(figsize=(10,3))
    indices = range(len(counts))
    plt.title("Top 10 Station Ridership over June 2015")
    plt.xticks(indices,stations, rotation=45)
    plt.bar(indices, counts)
