"""Scan for iBeacons.

Copyright (c) 2022 Koen Vervloesem

https://koen.vervloesem.eu/listings/ibeacon_scanner/ibeacon_scanner.py.html

SPDX-License-Identifier: MIT
"""
import time
import asyncio
from uuid import UUID

from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from datetime import datetime as t
# import datetime

# from original 
ibeacon_format = Struct(
	"type_length" / Const(b"\x02\x15"),
	"uuid" / Array(16, Byte),
	"major" / Int16ub,
	"minor" / Int16ub,
	"power" / Int8sl,
)

# not working
eddytlm_format = Struct(
	"type_length" / Const(b"\x02%"),
	"uuid" / Array(1, Byte),
#	"major" / Int16ub,
#	"minor" / Int16ub,
#	"power" / Int8sl,
)

# not working
laptop_format = Struct (
	"type_length" / Const(b"\x01"),
	"wat" / Array(16, Byte),
)

def log(s):
	# debugPrint('\n',t.now(),'')
	print('log', s)
	f = open('log.csv', 'a')
	ts = time.time()
	sttime = t.fromtimestamp(time.time()).strftime('%Y%m%d_%H:%M:%S - ')
	f.write(sttime + s + '\n')
	# f.write(str(t.now()) + s + '\n')
	f.close


def device_found(
	device: BLEDevice, advertisement_data: AdvertisementData
):
	"""Decode iBeacon."""
	try:
		print(".", end = '')

		if not len(advertisement_data.manufacturer_data) > 0:
			return
		
		# print('advert:', advertisement_data.manufacturer_data)
		processed = False
		
		if 6 in advertisement_data.manufacturer_data:
			data = advertisement_data.manufacturer_data[0x0006] # decimaal 224, eddystone?
			# print('data 6 (laptop)', data, end = '')
			# print('rssi ', advertisement_data.rssi)
			what = laptop_format.parse(data)
			# print('what ', what)
			# print(47 * "-")
			processed = True

		if 76 in advertisement_data.manufacturer_data:
			data = advertisement_data.manufacturer_data[0x004C] #  decimaal 76, apple iBeacon
			ibeacon = ibeacon_format.parse(data)
			# print('ibeacon', ibeacon)
			uuid = UUID(bytes=bytes(ibeacon.uuid))
			if uuid == UUID('00000000-1111-2222-3333-0f0f0f0f0f0f'):
				log('idle ---------')
			if uuid == UUID('00000000-1111-2222-3333-acacacacacac'):
				log('active ++++++++')
			#print('data 76 (Apple)',data)
			#print(f"UUID: {uuid}", end='')
			#print(f", Major: {ibeacon.major}", end='')
			#print(f", Minor: {ibeacon.minor}", end='')
			#print(f", TX power: {ibeacon.power} dBm", end='')
			#print(f", RSSI: {advertisement_data.rssi} dBm")
			#print(47 * "-")
			processed = True

		if 224 in advertisement_data.manufacturer_data:
			data = advertisement_data.manufacturer_data[0x00E0] # decimaal 224, eddystone?
			#print('data 224 (eddy?)',data)
			#print('manufacturer_data:', advertisement_data.manufacturer_data)
			#print('service data', advertisement_data.service_data)
			#print('service uuids', advertisement_data.service_uuids)
			#print('rssi', advertisement_data.rssi)
			#	print('uuid', advertisement_data.service_uuids)
			#	eddytmr = eddystonetmr_format.parse(data)
			#	print('eddytmr:', eddytmr)
			#	#uuid = UUID(bytes=bytes(eddytmr.uuid))
			#print(47 * "-")
			processed = True

		if not processed:
			print('unknown:', advertisement_data)

	except KeyError:
		# Apple company ID (0x004c) not found
		time.sleep(0.5)
		pass
	except ConstError:
		# No iBeacon (type 0x02 and length 0x15)
		pass


async def main():
	"""Scan for devices."""
	scanner = BleakScanner(detection_callback = device_found)
	# scanner.register_detection_callback(device_found) #  deprecated

	while True:
		await scanner.start()
		await asyncio.sleep(0.1)
		await scanner.stop()


asyncio.run(main())