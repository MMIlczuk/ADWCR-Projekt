# 🚲 Nextbike Warsaw – Monitoring i analiza dostępności rowerów w czasie rzeczywistym

---

## 📌 Opis projektu

Ten projekt prezentuje **system monitoringu i analizy danych w czasie rzeczywistym** oparty na danych z systemu rowerów miejskich Nextbike w Warszawie. Został stworzony jako przykład **praktycznego zastosowania analityki danych strumieniowych** oraz wizualizacji insightów dla operacyjnych decyzji biznesowych.

🔧 Projekt obejmuje:
- Pobieranie danych z **publicznego API Nextbike**
- Strumieniowanie danych do **Apache Kafka**
- Konsumpcję danych i **wizualizację na interaktywnej mapie** w Streamlit
- Analizę dostępności rowerów oraz **propozycje relokacji i identyfikację rowerów z niskim poziomem baterii**

---

## 🧠 Cele analityczne

1. **Propozycje relokacji rowerów**  
   Identyfikacja stacji, które mają nadmiar rowerów (>10) i wskazanie najbliższych stacji deficytowych (<2) w promieniu 1,5 km.  
   👉 Potencjalne zastosowanie: usprawnienie działania zespołu relokacyjnego, optymalizacja dostępności.

2. **Monitoring rozładowanych rowerów elektrycznych**  
   Wyodrębnienie rowerów z poziomem baterii <10% – mogą wymagać interwencji serwisowej lub relokacji.  
   👉 Potencjalne zastosowanie: poprawa jakości usług i zadowolenia użytkowników.

---

## 🖼️ Demo aplikacji

👉 [Wstaw link do hostowanej wersji Streamlit, jeśli posiadasz]  
Przykładowy zrzut ekranu interfejsu:  
![screenshot](screenshots/mapa_rowerow.png)

---

## ⚙️ Architektura projektu


- `producer.py` – pobiera dane z API i przesyła je do tematów Kafka: `nextbike-data` i `nextbike-data-bike`
- `app.py` – konsument danych, interfejs mapowy i analiza
- `docker-compose.yml` – definiuje środowisko wielokontenerowe (Streamlit + Kafka + Zookeeper)

---

## 🧠 Możliwości rozwoju

🔄 Integracja z danymi GPS pojazdów relokacyjnych
📈 Uczenie maszynowe do przewidywania zapotrzebowania rowerów
🧭 Rekomendacje tras relokacji i priorytetów
📊 Dashboard analityczny z metrykami operacyjnymi (średni czas stacjonowania, obłożenie stacji)
