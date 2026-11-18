# ICON schedule
# NAME Bude Tides
# DESC Tide state and seapool temperature for Bude

import gc
import json
import time
from presto import Presto

try:
	import requests
except ImportError:
	import urequests as requests

# Same setup as the working Word Clock example
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(200, 200, 200)

TIDES_URL = "https://playingwith.variousbits.net/utilities/tides/api.php"
POOL_URL = "https://spt.tsak.dev/api/v1/temperature"
REFRESH_SECONDS = 600


def show_message(text):
	print(text)
	display.set_pen(BLACK)
	display.clear()
	display.set_pen(WHITE)
	display.text(f"{text}", 5, 10, WIDTH, 2)
	presto.update()


display.set_pen(BLACK)
display.clear()
presto.update()

show_message("Connecting...")

try:
	wifi = presto.connect()
except ValueError as e:
	while True:
		show_message(e)
except ImportError as e:
	while True:
		show_message(e)


def get_json(url):
	gc.collect()
	try:
		r = requests.get(url, timeout=15)
	except TypeError:
		# older urequests has no timeout argument
		r = requests.get(url)
	try:
		return json.loads(r.text)
	finally:
		r.close()
		gc.collect()


def tides_text(tides):
	ct = tides.get("closest_tide", {}) or {}
	return "Bude: {}\nNext {}: {}\n({})".format(
		tides.get("human_tide", "?"),
		ct.get("type", "?"),
		ct.get("time", "?"),
		ct.get("height", "?"),
	)


while True:
	try:
		show_message("Getting tides...")
		tides = get_json(TIDES_URL)
		base = tides_text(tides)
		show_message(base + "\n\nPool: fetching...")

		pool = get_json(POOL_URL)
		show_message(base + "\n\nPool: {:.1f} C".format(float(pool["temperature"])))
	except Exception as e:
		show_message("Failed: " + str(e))

	time.sleep(REFRESH_SECONDS)