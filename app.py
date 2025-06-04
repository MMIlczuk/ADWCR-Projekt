import streamlit as st
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
from kafka import KafkaConsumer
import json
import math
import pandas as pd
from collections import defaultdict
from datetime import datetime

if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = False

# Ustawienia
MAP_CENTER = [52.2297, 21.0122]
bike_icon_url = "https://img.freepik.com/premium-vector/blue-icon-with-bicycle_928715-598.jpg"
min_bikes = 0
max_bikes = 20
colormap = cm.linear.RdYlGn_09.scale(min_bikes, max_bikes)


# Streamlit UI
st.set_page_config(layout="wide")
st.title("🚲 Mapa dostępnych rowerów Nextbike – Warszawa")

# Funkcje pobierające dane z Kafki
def get_kafka_data():
    consumer = KafkaConsumer(
        'nextbike-data',
        bootstrap_servers='broker:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True#,
        #group_id='streamlit-group2'
    )
    messages = []
    for _ in range(500):
        try:
            msg = next(consumer)
            messages.append(msg.value)
        except StopIteration:
            break
    return messages

def get_kafka_data_bike():
    consumer_bike = KafkaConsumer(
        'nextbike-data-bike',
        bootstrap_servers='broker:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True#,
        #group_id='streamlit-bike2'
    )
    messages = []
    for _ in range(3000):
        try:
            msg = next(consumer_bike)
            messages.append(msg.value)
        except StopIteration:
            break
    return messages

# Pobieranie danych przy starcie lub po kliknięciu przycisku
if st.button("Odśwież dane") or not st.session_state["data_loaded"]:
    st.session_state["data"] = get_kafka_data()
    st.session_state["bike_data"] = get_kafka_data_bike()
    st.session_state["data_loaded"] = True

data = st.session_state.get("data", [])
bike_data = st.session_state.get("bike_data", [])

# Logika relokacji
low_threshold = 2
high_threshold = 10
relocation = []

def distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Mapa
m = folium.Map(location=MAP_CENTER, zoom_start=13)
colormap.add_to(m)

for station in data:
    lat = station['lat']
    lng = station['lng']
    name = station['name']
    bikes = station['bikes']

    is_free_bike = 'BIKE' in name.upper()
    popup_text = f"<b>{name}</b><br>Rowery: {bikes}"

    if is_free_bike:
        icon = folium.CustomIcon(icon_image=bike_icon_url, icon_size=(30, 30))
        folium.Marker(
            location=[lat, lng],
            icon=folium.Icon(icon="bicycle", prefix="fa"),
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(m)
    else:
        color = colormap(bikes)
        folium.CircleMarker(
            location=[lat, lng],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(m)

for station in data:
    lat = station['lat']
    lng = station['lng']
    name = station['name']
    bikes = station['bikes']
    

    is_free_bike = 'BIKE' in name.upper()
    popup_text = f"<b>{name}</b><br>Rowery: {bikes}"

    if is_free_bike:
        # Wolnostojący rower – niebieskie kółko, bez ikony
        icon = folium.CustomIcon(icon_image=bike_icon_url, icon_size=(30, 30))
        folium.Marker(
            location=[lat, lng],
            icon=folium.Icon(icon="bicycle", prefix="fa"),
            popup=folium.Popup(popup_text, max_width=250)
            ).add_to(m)
    else:
        # Stacja rowerowa – kolor wg liczby rowerów
        color = colormap(bikes)

        folium.CircleMarker(
            location=[lat, lng],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(m)

#rozladowane rowery
rozladowane_rowery = []
for bike in bike_data:
    if bike['battery'] is not None and bike['battery'] < 11:
       rozladowane_rowery.append([bike['name'], bike['bike_number'], bike['battery'], str(bike['battery']) + '%'])
# Generowanie propozycji relokacji
relocation_pairs = set()
for station in data:
    if station['bikes'] >= high_threshold:
        nearest_low = None
        min_dist = float('inf')
        for target in data:
            if (
                target['bikes'] <= low_threshold and
                target['name'] != station['name'] and
                'BIKE' not in target['name'].upper()
            ):
                dist = distance(station['lat'], station['lng'], target['lat'], target['lng'])
                if dist < min_dist:
                    min_dist = dist
                    nearest_low = target
        # Dodaj tylko jeśli para nie została już dodana
        if nearest_low and min_dist < 1.501:
            pair_key = (station['name'], nearest_low['name'])
            if pair_key not in relocation_pairs:
                relocation.append([
                    station['bikes'],
                    station['name'],
                    f"{round(min_dist * 1000)}m >>>",
                    nearest_low['name'],
                    nearest_low['bikes'],
                    min_dist
                ])
                relocation_pairs.add(pair_key)

st_folium(m, width=1000, height=800)



# Wczytanie danych z pliku .jsonl
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Konwersja timestampu
def parse_timestamp(ts_str):
    return datetime.strptime(ts_str, "%Y-%m-%d_%H-%M-%S")


# Formatowanie sekund na czytelny string
def format_duration(seconds):
    seconds = int(seconds)
    h, m = divmod(seconds, 3600)
    m, s = divmod(m, 60)
    parts = []
    if h > 0:
        parts.append(f"{h}h")
    if m > 0:
        parts.append(f"{m}min")
    if s > 0 or not parts:
        parts.append(f"{s}s")
    return ' '.join(parts)
    
# Główna funkcja analizy
def analyze_station_stability(data):
    rows = []
    for bike_number, info in data.items():
        duration = info.get('duration', 0)
        if duration > 3600:
            rows.append({
                'Numer roweru': bike_number,
                'Aktualna stacja': info.get('station'),
                'sekundy': duration,
                'Długość bez zmiany': format_duration(duration)
            })
    if not rows:
        return pd.DataFrame(
            columns=['Numer roweru', 'Aktualna stacja', 'sekundy', 'Długość bez zmiany']
        )
        
    return pd.DataFrame(rows)

dane_hist = load_json('raw_nextbike_data/bike_station_status.json')
df = analyze_station_stability(dane_hist)




# Tabela relokacji
st.subheader("🚛 Propozycje relokacji")
relocation_table = pd.DataFrame(relocation, columns = [ 'Liczba rowerów','Skąd?', 'Odległość', 'Dokąd?', 'Liczba rowerów\n', 'odleg' ]).sort_values(by=['odleg']).drop(columns=['odleg'])
st.table(relocation_table)



# Rozładowane rowery
st.subheader("Rozładowane rowery")
rozladowana_table = pd.DataFrame(rozladowane_rowery, columns = [ 'Nazwa stacji','Numer roweru', 'proc', 'Procent naładowania baterii']).sort_values(by=['proc']).drop(columns=['proc'])
st.table(rozladowana_table)


#Tabela awarii

st.subheader("Tabela awarii")
awaria_table = df.sort_values(by=['sekundy'],ascending = False).drop(columns=['sekundy']).head(n=100)
st.table(awaria_table)