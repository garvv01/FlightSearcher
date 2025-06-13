import requests
from flight_search import FlightSearch
from flight_data import FlightData

response_excel = requests.get(url="{your_url}")
print(response_excel.json())
sheet_data = response_excel.json()["prices"]
email_data = response_excel.json()["Users"]
email_list = []
for email in email_data:
    email_list.append(email["What is your email address?"])

flight_search = FlightSearch(sheet_data)
flight_search.req_token()
flight_search.update_iata()

flight_data = FlightData(sheet_data)

dep_date = input("Enter your desired departure date in YYYY-MM-DD format:\n")
amt = input("Enter your desired amount willing to pay:\n")

flight_data.search_flight(dep_date=dep_date, amt=amt, email_list=email_list)
