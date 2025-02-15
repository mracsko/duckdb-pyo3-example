from flask import Flask, jsonify, request
import polars as pl
import num2words
from datetime import datetime, timedelta

app = Flask(__name__)

def gen_df(length):
    start_time = datetime(2021, 1, 1)
    end_time = start_time + timedelta(seconds=length - 1)

    return pl.DataFrame({
        "number": range(1, length + 1),
        "string": [num2words.num2words(i) for i in range(1, length + 1)],
        "timestamp": pl.datetime_range(start=start_time, end=end_time, time_unit="ms", time_zone="UTC", eager=True, interval="1s")
    })

print("Generating DataFrames...")
data_frame_xxs = gen_df(1)
print("Generated: `data_frame_xxs`")
data_frame_xs = gen_df(10)
print("Generated: `data_frame_xs`")
data_frame_s = gen_df(100)
print("Generated: `data_frame_s`")
data_frame_m = gen_df(1000)
print("Generated: `data_frame_m`")
data_frame_l = gen_df(10000)
print("Generated: `data_frame_l`")
data_frame_xl = gen_df(100000)
print("Generated: `data_frame_xl`")
data_frame_xxl = gen_df(1000000)
print("Generated: `data_frame_xxl`")
print("Generated DataFrames...")

@app.route('/data', methods=['GET'])
def send_dataframe():
    size = request.args.get('size')
    match size:
        case "xxs":
            df = data_frame_xxs
        case "xs":
            df = data_frame_xs
        case "s":
            df = data_frame_s
        case "m":
            df = data_frame_m
        case "l":
            df = data_frame_l
        case "xl":
            df = data_frame_xl
        case "xxl":
            df = data_frame_xxl
        case _:
            return "Invalid size"

    json_data = df.write_json()

    return json_data

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)