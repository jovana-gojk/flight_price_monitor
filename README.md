# Flight Price Monitor
A Python application that monitors flight prices from SYD to OOL on the weekend and tracks the prices in a database. It then sends an email with the next coming weeks cheapest flight options.


## Features
- Scrapes flight data from the internet
- Stores the data in a database
- Retrieves the cheapest flight from the database
- Compares these flights to previously retrieved data
- Send email alerts with the price of every weekend trip within the next 2 months
- To be run continuously on a home server with Docker and cron for scheduling

## Technologies
- Python
- Git
- SQLite
- Docker
