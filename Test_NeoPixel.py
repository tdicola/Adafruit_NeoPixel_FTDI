import unittest

import Adafruit_NeoPixel_FTDI as neo


class MockMPSSE(object):

	def __init__(self):
		self.output = None

	def Start(self):
		pass

	def Stop(self):
		pass

	def Write(self, data):
		self.output = data


class Test_NeoPixel(unittest.TestCase):

	def test_build_byte_lookup(self):
		self.assertEqual(neo._byte_lookup[0b00000000], neo._ZERO*8)
		self.assertEqual(neo._byte_lookup[0b00000001], neo._ZERO*7 + neo._ONE)
		self.assertEqual(neo._byte_lookup[0b10010010], neo._ONE + neo._ZERO*2 + neo._ONE + neo._ZERO*2 + neo._ONE + neo._ZERO)
		self.assertEqual(neo._byte_lookup[0b10000000], neo._ONE + neo._ZERO*7)
		self.assertEqual(neo._byte_lookup[0b11111111], neo._ONE*8)

	def test_show_grb_pixel_output(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(1, mpsse=mpsse)
		pixels.setPixelColorRGB(0, 255, 128, 0)

		pixels.show()

		self.assertEqual(mpsse.output, '\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0')

	def test_show_rgb_pixel_output(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(1, mpsse=mpsse, neo_rgb=True)
		pixels.setPixelColorRGB(0, 255, 128, 0)

		pixels.show()

		self.assertEqual(mpsse.output, '\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0')

	def test_show_multiple_pixels(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(3, mpsse=mpsse)
		pixels.setPixelColorRGB(0, 255, 128, 0)
		pixels.setPixelColorRGB(1, 0, 128, 255)
		pixels.setPixelColorRGB(2, 255, 128, 0)

		pixels.show()

		self.assertEqual(mpsse.output, '\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0')

	def test_setPixelColor(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(1, mpsse=mpsse)

		pixels.setPixelColor(0, 0xFF8000)
		pixels.show()

		self.assertEqual(mpsse.output, '\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0')

	def test_setBrightness_zero(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(3, mpsse=mpsse)
		pixels.setPixelColorRGB(0, 255, 128, 0)
		pixels.setPixelColorRGB(1, 0, 128, 255)
		pixels.setPixelColorRGB(2, 255, 128, 0)

		pixels.setBrightness(0.0)
		pixels.show()

		self.assertEqual(mpsse.output, '\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0')

	def test_setBrightness_full(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(3, mpsse=mpsse)
		pixels.setPixelColorRGB(0, 255, 128, 0)
		pixels.setPixelColorRGB(1, 0, 128, 255)
		pixels.setPixelColorRGB(2, 255, 128, 0)

		pixels.setBrightness(1.0)
		pixels.show()

		self.assertEqual(mpsse.output, '\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0')

	def test_setBrightness_half(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(3, mpsse=mpsse)
		pixels.setPixelColorRGB(0, 255, 128, 0)
		pixels.setPixelColorRGB(1, 0, 128, 255)
		pixels.setPixelColorRGB(2, 255, 128, 0)

		pixels.setBrightness(0.5)
		pixels.show()

		self.assertEqual(mpsse.output, '\xE0\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xF8\xF8\xF8\xF8\xF8\xF8\xF8\xE0\xE0\xE0\xE0\xE0\xE0\xE0\xE0')

	def test_getPixels(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(3, mpsse=mpsse)
		pixels.setPixelColorRGB(0, 255, 128, 0)
		pixels.setPixelColorRGB(1, 0, 128, 255)
		pixels.setPixelColorRGB(2, 255, 128, 0)

		self.assertEqual(pixels.getPixels(), [0xFF8000, 0x0080FF, 0xFF8000])

	def test_numPixels(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(3, mpsse=mpsse)

		self.assertEqual(pixels.numPixels(), 3)

	def test_getPixelColor(self):
		mpsse = MockMPSSE()
		pixels = neo.Adafruit_NeoPixel(3, mpsse=mpsse)
		pixels.setPixelColorRGB(0, 255, 128, 0)
		pixels.setPixelColorRGB(1, 0, 128, 255)
		pixels.setPixelColorRGB(2, 255, 128, 0)

		self.assertEqual(pixels.getPixelColor(0), 0xFF8000)
		self.assertEqual(pixels.getPixelColor(1), 0x0080FF)
		self.assertEqual(pixels.getPixelColor(2), 0xFF8000)
