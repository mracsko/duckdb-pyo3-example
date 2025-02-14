import requests
import pandas as pd
import time

url = "http://127.0.0.1:5000/data"

start_time = time.time()
response = requests.get(url)
network_time = time.time() - start_time  # Time taken for network

json_response = response.json()
json_data = json_response["data"]
serialize_time = json_response["serialize_time"]

start_time = time.time()
df = pd.read_json(json_data)  # Deserialize JSON back to DataFrame
deserialize_time = time.time() - start_time

print(f"REST - Serialization Time: {serialize_time:.4f} sec")
print(f"REST - Network Time: {network_time:.4f} sec")
print(f"REST - Deserialization Time: {deserialize_time:.4f} sec")
print(f"REST - DataFrame Shape: {df.shape}")
