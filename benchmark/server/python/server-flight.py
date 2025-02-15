import pyarrow as pa
import pyarrow.flight as flight
import polars as pl
import num2words
from datetime import datetime, timedelta

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

class FlightServer(flight.FlightServerBase):
    def __init__(self):
        super().__init__("grpc://0.0.0.0:8815")

    def do_get(self, context, ticket):
        size = ticket.ticket.decode("utf-8")
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

        return flight.RecordBatchStream(df.to_arrow())

if __name__ == "__main__":
    server = FlightServer()
    print("Arrow Flight Server running on port 8815...")
    server.serve()