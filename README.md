Adafruit NeoPixel FTDI
======================

Python library for interfacing with [Adafruit NeoPixels](http://learn.adafruit.com/adafruit-neopixel-uberguide/overview) (WS2811, WS2812, etc.) using an [FTDI MPSSE](http://www.ftdichip.com/Support/Documents/AppNotes/AN_135_MPSSE_Basics.pdf) device like the [FT232H chip](http://www.ftdichip.com/Products/ICs/FT232H.htm) or [cable](http://www.ftdichip.com/Products/Cables/USBMPSSE.htm).

Note this is alpha/beta quality and is not yet built into a formal library.

Dependencies
------------

Install these libraries before using the library:

-   [libftdi](http://www.intra2net.com/en/developer/libftdi/) is used by libmpsse to talk to the FTDI device.

    -   With homebrew on Mac OS X execute:
        ````
        brew install libftdi
        ````

-   [libmpsse](https://code.google.com/p/libmpsse/) is used to send MPSSE commands.

    -   Follow the [steps here](https://code.google.com/p/libmpsse/wiki/Installation) to install. Make sure to compile and install with python support.  
    
        Note that if you install the libftdi depdency using homebrew on Mac OSX, you might need to add the /usr/local/include/libftdi1 include path to the makefile's CFLAGS.

Hardware
--------

If you're using [the FT232H cable](C232HM-EDHSL-0) make sure to use the 5 volt version (although in my testing the 3.3 volt cable seems to be work--your mileage may vary).  Hook the yellow serial out cable to the NeoPixel signal input and the black ground to NeoPixel power ground.  Don't try to power the NeoPixels from the cable, they pull too much power!

Important Note
--------------

Drivers for the FTDI 232H chip are included in recent linux kernels and Mac OS X Mavericks.  Unfortunately these drivers conflict with the libftdi driver so you must temporarily unload the drivers before running a program that uses libftdi, like this library!

On Mac OS X execute these commands to disable until the next login both the built in driver and any user installed driver:

````
sudo kextunload -b com.apple.driver.AppleUSBFTDI
sudo kextunload /System/Library/Extensions/FTDIUSBSerialDriver.kext
````

Timing
------

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
