import requests

class FlightSearch:
    def __init__(self, data):
        self.key = "{your_api_key}"
        self.secret = "{your_api_secret}"
        self.token=""
        self.data = data
    def req_token(self):
        params = {
            "grant_type": "client_credentials",
            "client_id": f"{self.key}",
            "client_secret": f"{self.secret}"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response_bearer_token = requests.post(url="https://test.api.amadeus.com/v1/security/oauth2/token", data=params, headers=headers)
        self.token = response_bearer_token.json()["access_token"]
        return self.token
    def update_iata(self):
        for row in self.data:
            row_id = row["id"]
            city = row["city"]
            manual_iata_map = {
                "Tokyo": "TYO",
                "Hong Kong": "HKG",
                "Kuala Lumpur": "KUL"
            }
            if city in manual_iata_map:
                iata_code = manual_iata_map[city]
            else:
                flight_params = {
                    "keyword": city,
                    "subType": "CITY"
                }
                flight_headers = {
                    "Authorization": f"Bearer {self.token}"
                }
                response_flight = requests.get(url="https://test.api.amadeus.com/v1/reference-data/locations", params=flight_params, headers=flight_headers)
                iata_code = response_flight.json()['data'][0]['iataCode']
            url = f"https://api.sheety.co/{your_project_id}/flightDeals/prices/{row_id}"
            body = {
                "price": {
                    "iataCode": f"{iata_code}"
                }
            }
            response = requests.put(url=url, json=body)