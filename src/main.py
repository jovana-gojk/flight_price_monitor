import sqlite3
from datetime import datetime, timedelta
from scraper import get_sorted_flights, make_url

def get_next_friday():
    date_today = datetime.now()
    to_friday = (4 - date_today.weekday()) % 7

    if to_friday == 0:
        to_friday = 7

    return date_today + timedelta(days=to_friday)

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

def get_weekend_prices(start_friday, number_of_weekends, origin="OOL", destination="SYD"):

    connection = sqlite3.connect("data/flights.db")
    cursor = connection.cursor()

    weekend_prices = []

    for i in range(number_of_weekends):

        friday = start_friday + timedelta(weeks=i)
        sunday = friday + timedelta(days=2)

        friday_date = friday.strftime("%Y-%m-%d")
        sunday_date = sunday.strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT airline, price, departure_time, arrival_time, duration
            FROM flights
            WHERE flight_date = ?
            AND origin = ?
            AND destination = ?
            ORDER BY price ASC
            LIMIT 1
        """, (friday_date, origin, destination))

        friday_flight = cursor.fetchone()

        cursor.execute("""
            SELECT airline, price, departure_time, arrival_time, duration
            FROM flights
            WHERE flight_date = ?
            AND origin = ?
            AND destination = ?
            ORDER BY price ASC
            LIMIT 1
        """, (sunday_date, origin, destination))

        sunday_flight = cursor.fetchone()

        weekend_prices.append({
            "friday_date": friday_date,
            "sunday_date": sunday_date,
            "friday_flight": friday_flight,
            "sunday_flight": sunday_flight
        })

    connection.close()

    return weekend_prices


def main():
    departure_airport = "SYD"
    arrival_airport = "OOL"
    earliest_flight_time = "2:00 PM"

    print("Flight Price Monitor")

    setup_database()

    start_friday = get_next_friday()
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

    weekend_prices = get_weekend_prices(
        start_friday,
        number_of_weekends,
        origin=departure_airport,
        destination=arrival_airport
    )
    print(f"\nFrom {departure_airport} to {arrival_airport}:")
    for weekend in weekend_prices:

        print("==============================")
        print(
            f"{weekend['friday_date']} → "
            f"{weekend['sunday_date']}"
        )
        print("==============================")

        friday = weekend["friday_flight"]
        sunday = weekend["sunday_flight"]

        if friday:
            print(
                f"Friday: ${friday[1]} | "
                f"{friday[0]} | "
                f"{friday[2]} → {friday[3]}"
            )

        if sunday:
            print(
                f"Sunday: ${sunday[1]} | "
                f"{sunday[0]} | "
                f"{sunday[2]} → {sunday[3]}"
            )

        if friday and sunday:
            total = friday[1] + sunday[1]
            print(f"Weekend total: ${total}")


if __name__ == "__main__":
    main()