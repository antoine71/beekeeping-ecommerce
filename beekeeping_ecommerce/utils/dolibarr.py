import json
import requests

from django.conf import settings


class DolibarrAPIClient:

    def __init__(self):
        self.url = settings.DOLIBARR_URL
        self.token = settings.DOLIBARR_TOKEN
        self.third_party_id = 0

    def endpoint(self, endpoint):
        return f"{self.url}/api/index.php{endpoint}"

    def post(self, endpoint, data):
        headers = {
            "Content-Type": "application/json",
            'Accept': 'application/json',
            'DOLAPIKEY': self.token,
        }
        return requests.post(endpoint, data=data, headers=headers)

    def create_third_party(self, name, email, phone):
        endpoint = self.endpoint('/thirdparties')
        data = {
            'name': name,
            'email': email,
            'phone': phone,
            'client': 1,
            'code_client': -1,
        }
        response = self.post(endpoint, data=json.dumps(data))
        if response.ok:
            self.third_party_id = response.json()
        return response

    def create_shipping_address(self):
        if not self.third_party_id:
            return
        endpoint = self.endpoint('/contacts')
        data = {

        }
        response = self.post(endpoint, data=json.dumps(data))
        
        
    def create_billing_address(self):
        if not self.third_party_id:
            return

    def create_order(self):
        pass


# api = DolibarrAPIClient()

# r = api.create_third_party('Emmanuel Jallas', 'ejallas@numericbees.com', '0123456789')
# print(r.json())
# print(r.status_code)
