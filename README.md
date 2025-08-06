# 🚲 Nextbike Warsaw – Monitoring i analiza dostępności rowerów w czasie rzeczywistym

**Autor**: [Twoje Imię i Nazwisko]  
**Rola**: Analityk danych / Data Analyst  
**Typ projektu**: Portfolio – rekrutacja  
**Technologie**: Python, Kafka, Streamlit, Docker, Folium, API REST, Pandas  

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

