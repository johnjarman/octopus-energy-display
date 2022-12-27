import octopusenergy
import carbonintensity
import time
import datetime
import board
import busio
import logging
import argparse
from adafruit_ht16k33 import segments

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure command line arguments
parser = argparse.ArgumentParser(
                    prog = 'display_data',
                    description = 'Display numeric data from API on 7-seg display')

parser.add_argument('api',
                    help="Which API to use ('octopus' or 'carbon')")

api = parser.parse_args().api

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the LED segment class.
# This creates a 7 segment 4 character display:
display = segments.Seg7x4(i2c)

# Display test
display.fill(1)
time.sleep(1)
display.fill(0)

if api == 'octopus':
    api_key = octopusenergy.load_api_key_from_file('api_key.txt')
    api_interface = octopusenergy.OctopusEnergy(api_key)
elif api == 'carbon':
    api_interface = carbonintensity.CarbonIntensity()
else:
    raise ValueError('Specified API {} not found'.format(api))
    

current_str = None

while True:
    try:
        price = api_interface.value
    except Exception as err:
        # Catch-all for errors
        logging.error('Error retrieving price: {}'.format(err))
        price = None

    hour = datetime.datetime.now().hour

    # Dim display at certain times
    if hour < 6 or hour >= 23:
        display.brightness = 0.1
    elif hour < 7 or hour >= 19:
        display.brightness = 0.4
    else:
        display.brightness = 0.8

    if price is None:
        display_str = "Err "
    elif api == 'carbon' and price >= -999 and price <= 9999:
        display_str = "{:4.0f}".format(price)
    elif price >= -9.99 and price <= 99.99:
        display_str = "{:4.2f}".format(price)
    elif price >= -99.9 and price <= 999.9:
        display_str = "{:4.1f}".format(price)
    elif price >= -999 and price <= 9999:
        display_str = "{:4.0f}".format(price)
    else:
        display_str = "----"

    if display_str != current_str:
        display.fill(0)
        display.print(display_str)
        current_str = display_str
    
    time.sleep(10)