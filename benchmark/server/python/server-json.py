from flask import Flask, jsonify
import pandas as pd
import time

app = Flask(__name__)

# Generate a sample DataFrame
def create_dataframe():
    return pd.DataFrame({
        "id": range(1, 100001),
        "value": [x * 2 for x in range(1, 100001)]
    })

@app.route('/data', methods=['GET'])
def send_dataframe():
    df = create_dataframe()
    start_time = time.time()
    json_data = df.to_json(orient="records")  # Serialize DataFrame
    serialize_time = time.time() - start_time
    return jsonify({"data": json_data, "serialize_time": serialize_time})

if __name__ == '__main__':
    app.run(port=5000, debug=True)