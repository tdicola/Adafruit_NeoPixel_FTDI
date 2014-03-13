"""Port of the Adafruit NeoPixel library to python using the FTDI MPSSE.

Learn more about NeoPixels here:
  http://learn.adafruit.com/adafruit-neopixel-uberguide/overview

This library is meant to be used with a FT232H USB to MPSSE chip or cable, like
the C232HM-EDHSL-0 here:
  http://www.ftdichip.com/Products/Cables/USBMPSSE.htm

This library requires the libmpsse library to be installed with python support:
  https://code.google.com/p/libmpsse/

Created by Tony DiCola (tony@tonydicola.com)
Released under an MIT license (http://opensource.org/licenses/MIT)

"""

import itertools
import operator
import time


# Bit values which represent the zero and one bit pulses.
_ZERO = bytearray([0b11100000])
_ONE  = bytearray([0b11111000])


def _build_byte_lookup():
	"""Return lookup table to map from every byte value 0-255 and the associated
	raw SPI data."""
	lookup = {}
	for i in range(256):
		value = bytearray()
		for j in range(7, -1, -1):
			if ((i >> j) & 1) == 0:
				value += _ZERO
			else:
				value += _ONE
		lookup[i] = value
	return lookup

_byte_lookup = _build_byte_lookup()

def get_default_mpsse(speed_mhz):
	"""Open the first MPSSE device found and return it.  Throws an exception if 
	no MPSSE device is found."""
	from mpsse import MPSSE
	mpsse = MPSSE(SPI0, speed_mhz, MSB)
	if mpsse is None:
		RuntimeError('Could not find a connected MPSSE device!')
	return mpsse

def color(r, g, b):
	"""Convert an RGB triplet of 0-255 values to a 24 bit representation."""
	if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
		raise ValueError('Color values must be 0 to 255.')
	return (r << 16) | (g << 8) | b

def color_to_rgb(c):
	"""Convert a 24 bit color to RGB triplets."""
	return ((c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF)

def _encode_color_grb(c):
	"""Encode an RGB tuple into NeoPixel GRB 24 byte SPI bit stream."""
	return _byte_lookup[c[1]] + _byte_lookup[c[0]] + _byte_lookup[c[2]]

def _encode_color_rgb(c):
	"""Encode an RGB tuple into NeoPixel RGB 24 byte SPI bit stream."""
	return _byte_lookup[c[0]] + _byte_lookup[c[1]] + _byte_lookup[c[2]]


class Adafruit_NeoPixel(object):
	
	def __init__(self, n, mpsse=None, neo_rgb=False, neo_khz400=False):
		"""Create set of NeoPixels.

		The only required parameter is the number of NeoPixels.  By default the
		first MPSSE device found will be used, and it is assumed to be NeoPixels
		which support 800khz GRB signals.  Set either neo_rgb or neo_khz400
		keywoard parameters to True to use RGB or 400 khz NeoPixels respectively.

		"""
		self._n = n
		self._pixels = [0] * n
		# Initialize the mpsse to a default one if not explicitly set.
		if mpsse is None:
			# Default to 6mhz, unless overridden to 3mhz.
			speed = 3000000 if neo_khz400 else 6000000
			mpsse = get_default_mpsse(speed)
		self.setMPSSE(mpsse)
		# Default to GRB encoding, unless overridden to RGB.
		self._encode = _encode_color_rgb if neo_rgb else _encode_color_grb
		self._brightness = 1.0
		self._lastupdate = 0

	def close(self):
		"""Close the NeoPixel MPSSE connection."""
		if self._mpsse is not None:
			self._mpsse.Close()

	def show(self):
		"""Write the current pixel data to the NeoPixels."""
		# Ensure there's at least a 50 micro-second delay between show calls.
		delta = time.time() - self._lastupdate
		if delta < 0.00005:
			time.sleep(0.00005 - delta)
		self._mpsse.Start()
		# Scale pixels based on brightness and accumulate raw SPI bitstream.
		rgb = itertools.imap(color_to_rgb, self._pixels)
		scaled = itertools.imap(lambda c: (int(c[0] * self._brightness),
						   int(c[1] * self._brightness),
						   int(c[2] * self._brightness)),
					rgb)
		encoded = itertools.imap(self._encode, scaled)
		# Send data to the wire.
		self._mpsse.Write(str(reduce(operator.add, encoded)))
		self._mpsse.Stop()
		self._lastupdate = time.time()

	def setMPSSE(self, mpsse):
		"""Change the MPSSE device associated with this NeoPixel instance."""
		if mpsse is None:
			raise ValueError('MPSSE is null.')
		self._mpsse = mpsse

	def setPixelColorRGB(self, n, r, g, b):
		"""Update pixel at position n to the provided RGB color."""
		self.setPixelColor(n, color(r, g, b))

	def setPixelColor(self, n, c):
		"""Update pixel at position n to the provided 24 bit RGB color."""
		self._checkIndex(n)
		if not isinstance(c, int):
			raise ValueError('Expected integer value for color.')
		self._pixels[n] = c

	def setBrightness(self, b):
		"""Scale brightness of NeoPixels to provided value that is between 0 and
		1.0.  A value of 0 is completely dark and 1.0 is normal color brightness.
		Note that brightness is only reflected in the final output shown to the 
		hardware and not getPixels or getPixelColor."""
		if b < 0.0 or b > 1.0:
			raise ValueError('Brightness must be 0 to 1.0.')
		self._brightness = b

	def getPixels(self):
		"""Return all the pixels as an array of 24 bit RGB colors."""
		return self._pixels

	def numPixels(self):
		"""Return the number of NeoPixels."""
		return self._n

	def getPixelColor(self, n):
		"""Return the 24 bit RGB color of the pixel at position n."""
		self._checkIndex(n)
		return self._pixels[n]

	def _checkIndex(self, n):
		if n < 0 or n >= self._n:
			raise ValueError('Pixel id {0} is outside the range of expected values.'.format(n))
