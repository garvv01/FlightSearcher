import requests
from flight_search import FlightSearch

class FlightData:
    def __init__(self, data):
        self.data = data
        self.flightsearch = FlightSearch(self.data)
        self.token = self.flightsearch.req_token()

    def search_flight(self, dep_date, amt):
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
                "max": 5
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
                    print(f"❌ No flights available for {row['city']} ({row['iataCode']})")
                    continue

            except Exception as e:
                print(f"🚨 API error for {row['city']} ({row['iataCode']}): {e}")
                continue

            # Find cheapest flight under budget
            min_price = float('inf')
            cheapest_offer = None

            for offer in offers:
                try:
                    price = float(offer["price"]["total"])
                    if price <= amt and price < min_price:
                        min_price = price
                        cheapest_offer = offer
                except (KeyError, TypeError, ValueError):
                    print(f"⚠️ Invalid offer format: {offer}")
                    continue

            if cheapest_offer:
                airline = cheapest_offer["validatingAirlineCodes"][
                    0] if "validatingAirlineCodes" in cheapest_offer else "Unknown"
                dep_airport = cheapest_offer["itineraries"][0]["segments"][0]["departure"]["iataCode"]
                arr_airport = cheapest_offer["itineraries"][0]["segments"][-1]["arrival"]["iataCode"]
                dep_time = cheapest_offer["itineraries"][0]["segments"][0]["departure"]["at"]
                print(f"✅ {row['city']}: ₹{min_price} with {airline} from {dep_airport} to {arr_airport} at {dep_time}")
            else:
                print(f"❌ No flight to {row['city']} under ₹{amt}")
