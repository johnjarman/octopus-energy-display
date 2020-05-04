"""
Get electricity prices from Octopus Energy API.

John Jarman johncjarman@gmail.com
"""

import logging
import json
import requests
from datetime import datetime
from dateutil import tz


def load_api_key_from_file(filename):
    with open(filename) as f:
        s = f.read()
        return s.strip()

class OctopusEnergy:
    def __init__(self, api_key, api_url='https://api.octopus.energy/v1/products/AGILE-18-02-21/electricity-tariffs/E-1R-AGILE-18-02-21-J/standard-unit-rates/'):
        self.api_key = api_key
        self.api_url = api_url
        self.date_format = '%Y-%m-%dT%H:%M:%SZ'
        self.data = None

    def get_elec_price(self, cache=True):
        """ Get current electricity price 
        @param bool cache: Allow caching of fetched values
        """
        price = None

        if cache:
            try:
                # RAM cache
                price = self._get_current_price_from_data(self.data)
            except:
                pass

        if price is None:
            logging.info('Loading price data over HTTP')
            # Get price via HTTP
            self.data = self._get_data_http()
            price = self._get_current_price_from_data(self.data)

        return price

    def _get_data_http(self):
        r = requests.get(self.api_url, auth=(self.api_key + ':', ''))
        return json.loads(r.text)

    def _get_current_price_from_data(self, data):
        current_time = datetime.now()
        utc = tz.tzutc()
        local_tz = tz.tzlocal()
        current_time.replace(tzinfo=local_tz)
        current_time = current_time.astimezone(utc)
        price = None

        try:
            for val in data['results']:
                valid_from = datetime.strptime(val['valid_from'], self.date_format).replace(tzinfo=utc)
                valid_to = datetime.strptime(val['valid_to'], self.date_format).replace(tzinfo=utc)
                if (valid_from <= current_time and
                    valid_to > current_time):
                    price = val['value_inc_vat']

        except KeyError:
            try:
                logging.error("Could not get price data: " + data['detail'])
            except:
                logging.error("Could not get price data or error info.")

        except json.JSONDecodeError as err:
            logging.error('JSON decode error: {}'.format(err))

        return price

if __name__ == '__main__':
    api_key = load_api_key_from_file('api_key.txt')
    oe = OctopusEnergy(api_key)
    print(oe.get_elec_price())
