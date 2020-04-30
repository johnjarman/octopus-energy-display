import octopusenergy
import time
import datetime
import board
import busio
from adafruit_ht16k33 import segments

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the LED segment class.
# This creates a 7 segment 4 character display:
display = segments.Seg7x4(i2c)

# Display test
display.fill(1)
time.sleep(1)
display.fill(0)

api_key = octopusenergy.load_api_key_from_file('api_key.txt')

oe = octopusenergy.OctopusEnergy(api_key)

current_str = None

while True:
    try:
        price = oe.get_elec_price()
    except:
        price = None

    hour = datetime.datetime.now().hour

    # Dim display at certain times
    if hour < 7 or hour >= 23:
        display.brightness = 0.1
    elif hour >= 19:
        display.brightness = 0.4
    else:
        display.brightness = 0.8

    if price is None:
        display_str = "E"
    elif price >= -9.99 and price <= 99.99:
        display_str = "{:.2f}".format(price)
    else:
        display_str = "----"

    if display_str != current_str:
        display.fill(0)
        display.print(display_str)
        current_str = display_str
    
    time.sleep(10)