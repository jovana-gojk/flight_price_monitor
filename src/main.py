import sqlite3
from datetime import datetime, timedelta
from scraper import get_sorted_flights, make_url


def setup_database():
    connection = sqlite3.connect("data/flights.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TEXT,
            flight_date TEXT,
            origin TEXT,
            destination TEXT,
            airline TEXT,
            price INTEGER,
            departure_time TEXT,
            arrival_time TEXT,
            duration TEXT)""")

    connection.commit()
    connection.close()

def save_flights(flights, flight_date, origin, destination):

    connection = sqlite3.connect("data/flights.db")
    cursor = connection.cursor()

    for flight in flights:

        cursor.execute("""
            INSERT INTO flights (
                checked_at,
                flight_date,
                origin,
                destination,
                airline,
                price,
                departure_time,
                arrival_time,
                duration
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d"),
            flight_date,
            origin,
            destination,
            flight["airline"],
            flight["price"],
            flight["departure_time"],
            flight["arrival_time"],
            flight["duration"]
        ))

    connection.commit()
    connection.close()

def main():
    departure_airport = "OOL"
    arrival_airport = "SYD"
    earliest_flight_time = "2:00 PM"

    print("Flight Price Monitor")

    setup_database()

    start_friday = datetime(2026, 9, 18)
    number_of_weekends = 5

    for i in range(number_of_weekends):

        friday = start_friday + timedelta(weeks=i)
        sunday = friday + timedelta(days=2)

        friday_date = friday.strftime("%Y-%m-%d")
        sunday_date = sunday.strftime("%Y-%m-%d")

        friday_url = make_url(departure_airport, arrival_airport, friday_date)
        sunday_url = make_url(arrival_airport, departure_airport, sunday_date)

        friday_flights = get_sorted_flights(friday_url, earliest_flight_time)
        sunday_flights = get_sorted_flights(sunday_url, earliest_flight_time)

        save_flights(friday_flights, friday_date, departure_airport, arrival_airport)
        save_flights(sunday_flights, sunday_date, arrival_airport, departure_airport)


if __name__ == "__main__":
    main()