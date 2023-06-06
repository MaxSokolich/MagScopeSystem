# acoustic class to generate waveforms

# import GPIO module
import Jetson.GPIO as GPIO
#from HallEffect import HallEffect
import time


class AcousticHandler:
    def __init__(self):
        # setup GPIO

        GPIO.setmode(GPIO.TEGRA_SOC)
        # GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(True)

        # Define GPIO pins

        self.W_CLK = "SPI1_MOSI"
        self.FQ_UD = "AUD_MCLK"
        self.DATA = "SPI1_SCK"
        self.RESET = "SPI1_MISO"

        #self.W_CLK = "SPI1_MOSI"
        #self.FQ_UD = "AUD_MCLK"
        #self.DATA = "SPI1_SCK"
        #self.RESET = "SPI1_MISO"

        # setup IO bits
        GPIO.setup(self.W_CLK, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.FQ_UD, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.DATA, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.RESET, GPIO.OUT, initial=GPIO.LOW)

    # Function to send a pulse to GPIO pin

    def pulseHigh(self, pin):
        GPIO.output(pin, True)
        GPIO.output(pin, True)
        GPIO.output(pin, False)

    # Function to send a byte to AD9850 module

    def tfr_byte(self, data):
        for i in range(0, 8):
            GPIO.output(self.DATA, data & 0x01)
            self.pulseHigh(self.W_CLK)
            data = data >> 1

    # Function to send frequency (assumes 125MHz xtal) to AD9850 module
    def sendFrequency(self, frequency):
        freq = int(frequency*4294967296/125000000)
        for b in range(0, 4):
            self.tfr_byte(freq & 0xFF)
            freq = freq >> 8
        self.tfr_byte(0x00)
        self.pulseHigh(self.FQ_UD)

    # start the DDS module
    def start(self, frequency):
        self.pulseHigh(self.RESET)
        self.pulseHigh(self.W_CLK)
        self.pulseHigh(self.FQ_UD)
        self.sendFrequency(frequency)

    # stop the DDS module
    def stop(self):
        self.pulseHigh(self.RESET)


if __name__ == "__main__":
    AcousticMod = AcousticHandler()
    print("starting waveform...")
    freqinput = 10000
    AcousticMod.start(freqinput)
    time.sleep(1)
    AcousticMod.stop()
    print("stopped waveform")
