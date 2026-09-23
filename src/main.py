import sqlite3
from datetime import datetime, timedelta
from scraper import get_eligible_flights, make_url
from email_sender import send_email

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

def query_flights(cursor, flight_date, origin, destination, checked_at):

    cursor.execute("""
        SELECT airline, price, departure_time, arrival_time
        FROM flights
        WHERE flight_date = ?
        AND origin = ?
        AND destination = ?
        AND checked_at = ?
        ORDER BY price ASC
        LIMIT 1
    """, (flight_date, origin, destination, checked_at))

    return cursor.fetchone()

def query_comparison_flight(cursor, flight_date, origin, destination, checked_at):

    cursor.execute("""
        SELECT airline, price, departure_time, arrival_time, checked_at
        FROM flights
        WHERE flight_date = ?
        AND origin = ?
        AND destination = ?
        AND checked_at < ?
        ORDER BY checked_at DESC, price ASC
        LIMIT 1
    """, (flight_date, origin, destination, checked_at))

    return cursor.fetchone()

def get_weekend_prices(start_friday, number_of_weekends, origin, destination):
    connection = sqlite3.connect("data/flights.db")
    cursor = connection.cursor()

    weekend_prices = []

    for i in range(number_of_weekends):

        friday = start_friday + timedelta(weeks=i)
        sunday = friday + timedelta(days=2)

        friday_date = friday.strftime("%Y-%m-%d")
        sunday_date = sunday.strftime("%Y-%m-%d")

        friday_flight =query_flights(cursor, friday_date, origin, destination, datetime.now().strftime("%Y-%m-%d"))
        sunday_flight = query_flights(cursor, sunday_date, destination, origin, datetime.now().strftime("%Y-%m-%d"))

        weekend_prices.append({"friday_date": friday_date, "sunday_date": sunday_date, 
                               "friday_flight": friday_flight, "sunday_flight": sunday_flight})

    connection.close()

    return weekend_prices

def get_comparison_prices(start_friday, number_of_weekends, origin, destination):
    connection = sqlite3.connect("data/flights.db")
    cursor = connection.cursor()

    comparison_prices = []

    for i in range(number_of_weekends):

        friday = start_friday + timedelta(weeks=i)
        sunday = friday + timedelta(days=2)

        friday_date = friday.strftime("%Y-%m-%d")
        sunday_date = sunday.strftime("%Y-%m-%d")

        friday_flight =query_comparison_flight(cursor, friday_date, origin, destination, datetime.now().strftime("%Y-%m-%d"))
        sunday_flight = query_comparison_flight(cursor, sunday_date, destination, origin, datetime.now().strftime("%Y-%m-%d"))

        comparison_prices.append({"friday_date": friday_date, "sunday_date": sunday_date, 
                                  "friday_flight": friday_flight, "sunday_flight": sunday_flight})

    connection.close()

    return comparison_prices

def create_email_body(weekend_prices, comparison_prices, departure_airport, arrival_airport):
    email_body = f"Flight Price Monitor\n\nFrom {departure_airport} to {arrival_airport}:\n"

    for weekend, comparison_weekend in zip(weekend_prices, comparison_prices):

        email_body += "==============================\n"
        email_body += f"{weekend['friday_date']} → {weekend['sunday_date']}\n"
        email_body += "==============================\n"

        friday = weekend["friday_flight"]
        comparison_friday = comparison_weekend["friday_flight"]
        sunday = weekend["sunday_flight"]
        comparison_sunday = comparison_weekend["sunday_flight"]

        if friday:
            email_body += (
                f"Friday: ${friday[1]} | "
                f"{friday[0]} | "
                f"{friday[2]} → {friday[3]}"
            )
        if comparison_friday:
            price_change = friday[1] - comparison_friday[1]

            if price_change > 0:
                change_text = f"↑ ${price_change}"
            elif price_change < 0:
                change_text = f"↓ ${abs(price_change)}"
            else:
                change_text = "No change"

            email_body += f" | Previously: ${comparison_friday[1]} | Price change: {change_text}\n"

        if sunday:
            email_body += (
                f"Sunday: ${sunday[1]} | "
                f"{sunday[0]} | "
                f"{sunday[2]} → {sunday[3]}"
            )

        if comparison_sunday:
            price_change = sunday[1] - comparison_sunday[1]

            if price_change > 0:
                change_text = f"↑ ${price_change}"
            elif price_change < 0:
                change_text = f"↓ ${abs(price_change)}"
            else:
                change_text = "No change"

            email_body += f" | Previously: ${comparison_sunday[1]} | Price change: {change_text}\n"

        if friday and sunday:
            total = friday[1] + sunday[1]
            email_body += f"Weekend total: ${total}\n" 
            email_body += "==============================\n\n"

    return email_body

def main():
    departure_airport = "SYD"
    arrival_airport = "OOL"
    earliest_flight_time = "2:00 PM"

    setup_database()

    start_friday = get_next_friday()
    number_of_weekends = 8

    for i in range(number_of_weekends):

        friday = start_friday + timedelta(weeks=i)
        sunday = friday + timedelta(days=2)

        friday_date = friday.strftime("%Y-%m-%d")
        sunday_date = sunday.strftime("%Y-%m-%d")

        friday_url = make_url(departure_airport, arrival_airport, friday_date)
        sunday_url = make_url(arrival_airport, departure_airport, sunday_date)

        friday_flights = get_eligible_flights(friday_url, earliest_flight_time)
        sunday_flights = get_eligible_flights(sunday_url, earliest_flight_time)

        save_flights(friday_flights, friday_date, departure_airport, arrival_airport)
        save_flights(sunday_flights, sunday_date, arrival_airport, departure_airport)

    weekend_prices = get_weekend_prices(start_friday, number_of_weekends, departure_airport, arrival_airport)
    comparison_prices = get_comparison_prices(start_friday, number_of_weekends, departure_airport, arrival_airport)

    email_body = create_email_body(weekend_prices, comparison_prices, departure_airport, arrival_airport)
    send_email(email_body)
    print(email_body)


if __name__ == "__main__":
    main()