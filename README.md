# Adafruit NeoPixel FTDI

Python library for interfacing with [Adafruit NeoPixels](http://learn.adafruit.com/adafruit-neopixel-uberguide/overview) (WS2811, WS2812, etc. addressable RGB LEDs) using an [FTDI MPSSE](http://www.ftdichip.com/Support/Documents/AppNotes/AN_135_MPSSE_Basics.pdf) device like the [FT232H chip](http://www.ftdichip.com/Products/ICs/FT232H.htm) or [cable](http://www.ftdichip.com/Products/Cables/USBMPSSE.htm).

<a href="http://imgur.com/zOVrXqp" title="Mobile Upload"><img src="http://i.imgur.com/zOVrXqpl.jpg" title="Hosted by imgur.com" alt="Mobile Upload"/></a>

## Dependencies

Install these libraries before using the library:

-   [libftdi](http://www.intra2net.com/en/developer/libftdi/) is used by libmpsse to talk to the FTDI device.

    -   With homebrew on Mac OS X execute:
        
        ````
        brew install libftdi
        ````
        
        On Ubuntu/Debian execute:
        
        ````
        sudo apt-get install libftdi-dev
        ````

-   [libmpsse](https://code.google.com/p/libmpsse/) is used to send MPSSE commands.

    -   Follow the [steps here](https://code.google.com/p/libmpsse/wiki/Installation) to install. Make sure to compile and install with python support.  
    
        Note that if you install the libftdi depdency using homebrew on Mac OSX, you might need to add the /usr/local/include/libftdi1 include path to the makefile's CFLAGS.

## Usage

If you're using [the FT232H cable](C232HM-EDHSL-0) make sure to use the 5 volt version (although in my testing the 3.3 volt cable seems to be work--your mileage may vary).  Hook the yellow serial out wire to the NeoPixel signal input and the black ground wire to NeoPixel power ground.  Don't try to power the NeoPixels from the cable, they pull too much power!

The library interface is almost exactly the same as the Arduino library interface, but with the following changes:

-   The Adafruit_NeoPixel object constructor takes an optional MPSSE object reference (from the libmpsse library) instead of a pin id.  If this is not set the library will automatically search for the first attached FTDI device with MPSSE support it can find.  The setPin function has been changed to setMPSSE and similarly takes a reference to an MPSSE object.  In practice you don't need to worry about setting this paramter unless you have multiple MPSSE devices and need to choose an explicit one (see the library code for how it creates one).

-   Bit flags in the constructor have been replaced with explicit boolean keyword arguments 'neo_rgb' and 'neo_khz400'.  If not specified the default is a 800khz GRB NeoPixels like in the Arduino library.

-   Added close function to shut down the connection to the MPSSE device.  It's not strictly necessary to call this unless you want to close the connection for some reason.

-   Added setPixelColorRGB function which replaces the overloaded setPixelColor function that takes RGB triples (python doesn't support method overloading).

-   Modified setBrightness to take a float value 0 to 1.0 instead of byte value 0 to 255.  A value of 0 is completely dark pixels and a value of 1.0 is normal brightness.  Note that at low brightness (below 0.25) I've noticed flickering and odd pixel behavior.

See the strandtest example port in strandtest.py for an example of using the library.

## Important Note

Drivers for the FTDI 232H chip are included in recent Linux kernels and Mac OS X Mavericks.  Unfortunately these drivers conflict with the libftdi driver so you must temporarily unload the drivers before running a program that uses libftdi, like this library!

On Mac OS X execute these commands to disable until the next login both the built in driver and any user installed driver:

````
sudo kextunload -b com.apple.driver.AppleUSBFTDI
sudo kextunload /System/Library/Extensions/FTDIUSBSerialDriver.kext
````

On Linux execute these commands (from this [application note](http://www.ftdichip.com/Support/Documents/AppNotes/AN_220_FTDI_Drivers_Installation_Guide_for_Linux%20.pdf)) to disable the drivers:

````
sudo rmmod ftdi_sio
sudo rmmod usbserial
````

## Timing

NeoPixels are based on the popular WS2811/WS2812 series of addressable RGB LEDs.  Pixel colors are adjusted by sending a signal of pulses on a single control line which is daisy chained across all pixels.  From the [NeoPixels guide](http://learn.adafruit.com/adafruit-neopixel-uberguide/advanced-coding), the timing requirements of the control signal are:

-   Each pixel requires 24 bits of color data (8 bits each for green, red, blue) sent in most significant bit order.

-   Pixels will latch to the first color they see and send future bits down the chain to later pixels.

-   Each pixel bit is represented by a 1.25 micro-second pulse.

-   A pixel zero bit pulse is represented by 0.4 micro-seconds high, followed by 0.85 micro-seconds low.

-   A pixel one bit pulse is represented by 0.8 micro-seconds high, followed by 0.45 micro-seconds low.

-   When the control signal is held low for 50 micro-seconds or more the pixel update is finished.

-   There is a tolerance of +/-150 nano-seconds for each pulse.

If the FTDI MPSSE device is configured to generate a 6 mhz SPI signal it's possible to generate a control signal that falls within the tolerances defined above.  Each pixel bit pulse is subdivided into 1 byte/8 bits of SPI bus data which is easy to align into a string of pixel values (where one 24 bit pixel color expands into 24 bytes of raw SPI data).  The timing of this control signal is:

-   Each pixel bit is represented by a 1.33 micro-second pulse (1/6mhz * 8 bits).

-   A pixel zero bit pulse is represented by the bits 1110 0000, which generate a 0.5 micro-second high and 0.83 
    micro-second low pulse.

-   A pixel one bit pulse is represented by the bits 1111 1000, which generate a 0.83 micro-second high and 0.5 
    micro-second low pulse.

Note that the SPI clock and input pins are ignored, only the output pin is used to send a signal to the device.

## Future Work

Some things to consider for future updates:

-   Package into a formal python library with setuptools/distribute.

-   Add gamma correction.

-   Consider putting animations and effects into their own part of the library.

-   Figure out the limits of how many pixels can be addressed.  At some point the latecy of USB messages might fall outside the 50 micro-second period for pixels to turn on, but it's unclear when this will happen (perhaps depends on libftdi's default 4096 byte write buffer?).  So far powering ~90 pixels seems to work fine.
