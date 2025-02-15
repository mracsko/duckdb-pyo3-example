import requests
import pyarrow.flight as flight
import polars as pl
import time
import sys
import statistics
import os
import csv

output_dir = "../stats"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def calculate_statistics(measurements, size):
    min_value = min(measurements)
    max_value = max(measurements)
    mean = sum(measurements) / len(measurements)
    median = statistics.median(measurements)
    std_dev = statistics.stdev(measurements)
    range = max_value - min_value

    print(f"Min Duration:         {min_value:.9f} seconds")
    print(f"Max Duration:         {max_value:.9f} seconds")
    print(f"Mean Duration:        {mean:.9f} seconds")
    print(f"Median Duration:      {median:.9f} seconds")
    print(f"Standard Deviation:   {std_dev:.9f} seconds")
    print(f"Range:                {range:.9f} seconds")

    return (size, min_value, max_value, mean, median, std_dev, range)


def json_call(session, url, data_size):
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {url}")
        sys.exit(1)
    df = pl.read_json(response.text.encode())
    assert len(df) == data_size


def json_test(size,data_size):
    url = f"http://127.0.0.1:5000/data?size={size}"
    session = requests.Session()
    for i in range(0,20):
        json_call(session, url, data_size)

    sample_size = 100

    measurements = []

    for i in range(0,sample_size):
        start_time = time.time()
        json_call(session, url, data_size)
        deserialize_time = time.time() - start_time
        measurements.append(deserialize_time)

    print("")
    print(f"Url: {url}")
    return calculate_statistics(measurements, size)

def flight_call(client, size, data_size):
    reader = client.do_get(flight.Ticket(size.encode()))
    table = reader.read_all()
    df = table.to_pandas()
    assert len(df) == data_size

def flight_test(size, data_size):
    client = flight.FlightClient("grpc://127.0.0.1:8815")

    for i in range(0,20):
        flight_call(client, size, data_size)

    sample_size = 100

    measurements = []

    for i in range(0, sample_size):
        start_time = time.time()
        flight_call(client, size, data_size)
        deserialize_time = time.time() - start_time
        measurements.append(deserialize_time)

    print("")
    print(f"Flight: {size}")
    return calculate_statistics(measurements, size)

print("")
json_xxs = json_test("xxs",1)
flight_xxs = flight_test("xxs",1)

json_xs = json_test("xs",10)
flight_xs = flight_test("xs",10)

json_s = json_test("s",100)
flight_s = flight_test("s",100)

json_m = json_test("m",1000)
flight_m = flight_test("m",1000)

json_l = json_test("l",10000)
flight_l = flight_test("l",10000)

json_xl = json_test("xl",100000)
flight_xl = flight_test("xl",100000)

json_xxl = json_test("xxl",1000000)
flight_xxl = flight_test("xxl",1000000)


data = [
    ("xxs", json_xxs, flight_xxs),
    ("xs", json_xs, flight_xs),
    ("s", json_s, flight_s),
    ("m", json_m, flight_m),
    ("l", json_l, flight_l),
    ("xl", json_xl, flight_xl),
    ("xxl", json_xxl, flight_xxl),
]

for row in data:
    data = [
        ['Measurement', 'JSON', 'Flight'],
        [f"Min Duration",f"{row[1][1]:.9f}",f"{row[2][1]:.9f}"],
        [f"Max Duration",f"{row[1][2]:.9f}",f"{row[2][2]:.9f}"],
        [f"Mean Duration",f"{row[1][3]:.9f}",f"{row[2][3]:.9f}"],
        [f"Median Duration",f"{row[1][4]:.9f}",f"{row[2][4]:.9f}"],
        [f"Standard Deviation",f"{row[1][5]:.9f}",f"{row[2][5]:.9f}"],
        [f"Range",f"{row[1][6]:.9f}",f"{row[2][6]:.9f}"]
    ]

    file_name = f'{output_dir}/python_json_vs_flight_comparison_{row[0]}.csv'

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

    print(f"Data written to {file_name}")

data = [
    ['Measurement', 'JSON', 'Flight'],
    [f"xxs",f"{json_xxs[3]:.9f}",f"{flight_xxs[3]:.9f}"],
    [f"xs",f"{json_xs[3]:.9f}",f"{flight_xs[3]:.9f}"],
    [f"s",f"{json_s[3]:.9f}",f"{flight_s[3]:.9f}"],
    [f"m",f"{json_m[3]:.9f}",f"{flight_m[3]:.9f}"],
    [f"l",f"{json_l[3]:.9f}",f"{flight_l[3]:.9f}"],
    [f"xl",f"{json_xl[3]:.9f}",f"{flight_xl[3]:.9f}"],
    [f"xxl",f"{json_xxl[3]:.9f}",f"{flight_xxl[3]:.9f}"]
]

file_name = f'{output_dir}/python_json_vs_flight_mean_comparison.csv'

with open(file_name, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)

print(f"Data written to {file_name}")
