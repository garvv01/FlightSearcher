import requests, smtplib
from flight_search import FlightSearch

class FlightData:
    def __init__(self, data):
        self.data = data
        self.flightsearch = FlightSearch(self.data)
        self.token = self.flightsearch.req_token()

    def search_flight(self, dep_date, amt, email_list):
        amt = float(amt)
        message_body = f"Flight Deals for {dep_date} under ₹{amt}:\n\n"
        for row in self.data:
            flight_headers = {
                "Authorization": f"Bearer {self.token}"
            }
            flight_params = {
                "originLocationCode": "DEL",
                "destinationLocationCode": row["iataCode"],
                "departureDate": dep_date,
                "adults": 1,
                "currencyCode": "INR",
                "max": 5,
                "nonstop": "False"
            }

            try:
                response = requests.get(
                    url="https://test.api.amadeus.com/v2/shopping/flight-offers",
                    headers=flight_headers,
                    params=flight_params
                )
                response.raise_for_status()
                data = response.json()
                offers = data.get("data", [])

                if not offers:
                    message_body += f"No flights for {row['city']} ({row['iataCode']})\n"
                    continue

            except Exception as e:
                message_body += f"API error for {row['city']} ({row['iataCode']}): {e}\n"
                continue

            min_price = float('inf')
            cheapest_offer = None

            for offer in offers:
                try:
                    price = float(offer["price"]["total"])
                    if price <= amt and price < min_price:
                        min_price = price
                        cheapest_offer = offer
                except (KeyError, TypeError, ValueError):
                    continue

            if cheapest_offer:
                airline = cheapest_offer["validatingAirlineCodes"][0] if "validatingAirlineCodes" in cheapest_offer else "Unknown"
                dep_airport = cheapest_offer["itineraries"][0]["segments"][0]["departure"]["iataCode"]
                arr_airport = cheapest_offer["itineraries"][0]["segments"][-1]["arrival"]["iataCode"]
                dep_time = cheapest_offer["itineraries"][0]["segments"][0]["departure"]["at"]
                message_body += f"✅ {row['city']}: ₹{min_price} with {airline} from {dep_airport} to {arr_airport} at {dep_time}\n"
            else:
                message_body += f"❌ No flight to {row['city']} under ₹{amt}\n"
        self.send_email(email_list, f"Flight Deals for {dep_date}", message_body)

    def send_email(self, email_list, subject, body):
        from_email = "flightclub@gmail.com"
        from_password = "flightclubpass"

        for email in email_list:
            message = f"Subject: {subject}\n\n{body}"
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(from_email, from_password)
                    server.sendmail(from_email, email, message)
                    print(f"Sent to {email}")
            except Exception as e:
                print(f"Failed to send to {email}: {e}")
