from kafka import KafkaProducer
import requests
import json
import time
from datetime import datetime
from pathlib import Path

API_URL = "https://api.nextbike.net/maps/nextbike-live.json?city=812"

# Zapis danych do folderu
DATA_DIR = Path("raw_nextbike_data")
DATA_DIR.mkdir(exist_ok=True)
STATUS_FILE = DATA_DIR / "bike_station_status.json"

producer = KafkaProducer(
    bootstrap_servers='broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_and_send():
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = {}
    try:
        response = requests.get(API_URL)
        data = response.json()
        timestamp = time.time()
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        for country in data['countries']:
            for city in country['cities']:
                for place in city['places']:
                    station_name = place.get("name")
                    message = {
                        'name': place.get('name'),
                        'bikes': place.get('bikes', 0),
                        'lat': place.get('lat'),
                        'lng': place.get('lng'),
                        'timestamp': timestamp_str
                    }
                    
                    producer.send('nextbike-data', message)
                        #print("Wyslano do Kafka:", message)

                    bike_list = place['bike_list']
                    if bike_list:
                        for bike in bike_list:
                            bike_msg = {
                                'name': place.get('name'),
                                'bike_number': bike.get('number'),
                                'bike_type': bike.get('bike_type'),
                                'timestamp': timestamp_str,
                                'battery': bike.get('pedelec_battery')  # może być None
                            }
                            producer.send('nextbike-data-bike', bike_msg)
                            bike_number = bike.get("number")    
                            if bike_number in old_data:
                                prev = old_data[bike_number]
                                prev_station = prev["station"]
                                prev_timestamp = datetime.strptime(prev["last_seen"], "%Y-%m-%d %H:%M:%S")

                                if prev_station == station_name:
                                    duration = prev["duration"] + (timestamp_dt - prev_timestamp).total_seconds()
                                else:
                                    duration = 0
                            else:
                                duration = 0

                            old_data[bike_number] = {
                                "station": station_name,
                                "duration": duration,
                                "last_seen": timestamp_str
                            }
                                #print("Wysłano do Kafka:", bike_msg)
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(old_data, f, ensure_ascii=False, indent=2)
                            
    except Exception as e:
        print("Blad podczas pobierania danych:", e)

if __name__ == "__main__":
    while True:
        fetch_and_send()
        time.sleep(30)

                    

        
    

