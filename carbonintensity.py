"""
Get electricity prices from Octopus Energy API.

John Jarman johncjarman@gmail.com
"""

import logging
import json
import requests
import datetime

class CarbonIntensity:
    def __init__(self, api_url='https://api.carbonintensity.org.uk/intensity/'):
        self.api_url = api_url
        self.date_format = '%Y-%m-%dT%H:%MZ'
        self.data = None
        self.forecast = False

    @property
    def value(self):
        """ Current carbon intensity
        """
        value = None

        if self.data is not None:
            # Try and get a value from cached value in self.data
            value = self._get_current_value_from_data(self.data)
            
        if value is None:
            self.data = self._get_data_http()
            value = self._get_current_value_from_data(self.data)

        return value

    def _get_data_http(self):
        logging.info('Loading price data over HTTP')
        r = requests.get(self.api_url)
        return json.loads(r.text)

    def _get_current_value_from_data(self, data):
        utc = datetime.timezone.utc
        current_time = datetime.datetime.now(tz=utc)
        correction = datetime.timedelta(hours=0, minutes=30)
        value = None

        try:
            valid_from = datetime.datetime.strptime(data['data'][0]['from'],
                                        self.date_format).replace(tzinfo=utc)
            valid_to = datetime.datetime.strptime(data['data'][0]['to'], 
                                        self.date_format).replace(tzinfo=utc)

            if (valid_from <= current_time - correction and
                    valid_to > current_time - correction):
                value = self.data['data'][0]['intensity']['actual']
                self.forecast = False

                if value is None:
                    # Fallback to forecast data if actual not available
                    logging.warn('Actual data unavailable, falling back to forecast')
                    value = self.data['data'][0]['intensity']['forecast']
                    self.forecast = True

        except KeyError:
            logging.error("Could not get data: KeyError")

        except json.JSONDecodeError as err:
            logging.error('JSON decode error: {}'.format(err))

        return value

if __name__ == '__main__':
    intensity = CarbonIntensity()
    print(intensity.value)
