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
        self.last_checked = None

    @property
    def value(self):
        """ Current carbon intensity
        """

        value = self._get_current_value()

        return value

    def _get_data_http(self):
        logging.info('Loading carbon intensity data over HTTP')
        r = requests.get(self.api_url)

        # Clear invalid flags, update last checked time
        self.forecast = False
        self.last_checked = datetime.datetime.now(tz=datetime.timezone.utc)
        return json.loads(r.text)

    def _get_current_value(self):
        utc = datetime.timezone.utc
        current_time = datetime.datetime.now(tz=utc)
        correction = datetime.timedelta(hours=0, minutes=30)
        recheck_time = datetime.timedelta(hours=0, minutes=5)
        
        value = None

        try:
            if self.data is None:
                self.data = self._get_data_http()
            
            valid_from = datetime.datetime.strptime(self.data['data'][0]['from'],
                                        self.date_format).replace(tzinfo=utc)
            valid_to = datetime.datetime.strptime(self.data['data'][0]['to'], 
                                        self.date_format).replace(tzinfo=utc)
            if (self.forecast and (current_time-self.last_checked > recheck_time)) or not\
               (valid_from <= current_time - correction and
                    valid_to > current_time - correction):
                # Get data from HTTP if needed.
                self.data = self._get_data_http()

            value = self.data['data'][0]['intensity']['actual']

            if value is None:
                # Fallback to forecast data if actual not available
                if not self.forecast:
                    logging.warning('Actual data unavailable, falling back to forecast')
                value = self.data['data'][0]['intensity']['forecast']
                self.forecast = True
            else:
                self.forecast = False

        except KeyError as err:
            logging.error("Could not get data: {}".format(err))

        except json.JSONDecodeError as err:
            logging.error('JSON decode error: {}'.format(err))

        return value

if __name__ == '__main__':
    intensity = CarbonIntensity()
    print(intensity.value)
