import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

departure_airport = "OOL"
arrival_airport = "SYD"
earliest_flight_time = "2:00 PM"

def make_url(origin, destination, date):
    url = f"https://www.google.com/travel/flights?hl=en&curr=AUD&q=One%20way%20flights%20from%20{origin}%20to%20{destination}%20on%20{date}"
    return url

def parse_flight(flight):

    flight_link = flight.find(attrs={"role": "link"})

    if not flight_link:
        return None

    aria_label = flight_link.get("aria-label")

    price = re.search(r"(\d+) Australian dollars", aria_label)
    airline = re.search(r"flight with (.*?)\. Leaves", aria_label)
    departure_time = re.search(r"at ([\d:]+)\s*([AP]M)", aria_label)
    arrival_time = re.search(r"arrives .*? at ([\d:]+)\s*([AP]M)", aria_label)
    duration = re.search(r"Total duration (.*?)\.", aria_label)

    return {
        "price": int(price.group(1)) 
            if price else None,

        "airline": (airline.group(1)
            if airline else None),

        "departure_time": (departure_time.group(1) + " " + departure_time.group(2)
            if departure_time else None),

        "arrival_time": (arrival_time.group(1) + " " + arrival_time.group(2)
            if arrival_time else None),

        "duration": (duration.group(1)
            if duration else None)
    }

def get_response_for_flights(flight_day):
    
    response = requests.get(
        flight_day,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        }
    )
    return response

def get_sorted_flights(flight_day, earliest_flight_time):
    response = get_response_for_flights(flight_day)
    soup = BeautifulSoup(response.text, "html.parser")

    flights = soup.find_all("li", class_="pIav2d")

    flight_data = []

    for flight in flights:

        data = parse_flight(flight)

        if data:
            flight_data.append(data)

    unique_flights = []

    for flight in flight_data:

        if flight not in unique_flights:
            unique_flights.append(flight)

    flight_data = unique_flights

    # Convert earliest flight time to a time object
    earliest_time = datetime.strptime(earliest_flight_time,"%I:%M %p").time()


    # Filter flights after the earliest allowed time
    eligible_flights = []

    for flight in flight_data:
        departure_time = datetime.strptime(flight["departure_time"],"%I:%M %p").time()

        if departure_time >= earliest_time:
            eligible_flights.append(flight)


    # Sort eligible flights by price
    eligible_flights.sort(key=lambda flight: flight["price"])

    return eligible_flights
